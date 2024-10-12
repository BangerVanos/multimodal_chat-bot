import streamlit as st
from audiorecorder import audiorecorder
import json
from typing import Literal
from PIL import Image
from io import BytesIO
import base64
from st_copy_to_clipboard import st_copy_to_clipboard
from MultimodalChatbot.backend.tts import text_to_speech
from MultimodalChatbot.backend.stt import speech_to_text


st.set_page_config(page_title='Multimodal chat', layout='wide')
NO_AUDIO_STR = b'RIFF,\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80\xbb\x00\x00\x00\xee\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00'


SUPPORTED_LANGUAGES = {
    'eng'
}


if not 'chat_messages' in st.session_state:
    st.session_state['chat_messages'] = []


def make_message(role: Literal['system', 'user', 'assistant'], content: str) -> None:
    st.session_state['chat_messages'].append(
        {
            'role': role,
            'content': content
        }
    )
    print(f'New {role} message!')


def get_image_base_64(raw_image: Image):
    buffer = BytesIO()
    raw_image.save(buffer, format=raw_image.format)
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

def render_settings_layout() -> None:
    with st.sidebar:
        st.selectbox('Choose language')

def render_chat_layout() -> None:
    messages = st.container(height=750)    
    img_upload_col, audio_record_col, chat_input_col = st.columns([1, 1, 20])
    with img_upload_col:
        with st.popover(label='', icon=':material/upload:'):
            uploaded_image = st.file_uploader(label='Upload images', key='img_uploader',
                                              type=['jpeg', 'jpg', 'png'], accept_multiple_files=False)
    with audio_record_col:
        audio_info = audiorecorder(key='voice', start_prompt='⏺️', stop_prompt='⏹️',
                                   show_visualizer=True)
    with chat_input_col:
        chat_input = st.chat_input(placeholder='Type your prompt here')
    for msg_ind, message in enumerate(st.session_state['chat_messages']):
        with messages.chat_message(name=message['role']):
            st.markdown(f'{message["content"]}')            
            render_chat_buttons(msg_ind, message["content"])
    if len(audio_info) > 0:  
        # recognition_result = speech_to_text(audio_info.export().read(), 'ru')
        recognition_result = '{"text": "ЗАТЫЧКА"}'
        chat_input = json.loads(recognition_result)['text']     
    if chat_input:        
        if uploaded_image:
            img_type = uploaded_image.type
            raw_image = Image.open(uploaded_image)
            image_str = f'![{uploaded_image.name}](data:{img_type};base64,{get_image_base_64(raw_image)})'            
            make_message(role='user', content=f'{chat_input}\n\n{image_str}')
            uploaded_image = None
        else:
            make_message(role='user', content=chat_input)
        make_message(role='assistant', content='ECHO!!!') # CHANGE TO NORMAL AI ANSWER
        last_user_msg = st.session_state['chat_messages'][-2]
        last_ai_msg = st.session_state['chat_messages'][-1]

        # RENDER NEW USER MESSAGE        
        with messages.chat_message(last_user_msg['role']):
            st.markdown(f'{last_user_msg["content"]}')            
            render_chat_buttons(len(st.session_state['chat_messages']) - 2, last_user_msg['content'])

        # RENDER NEW AI MESSAGE 
        with messages.chat_message(last_ai_msg['role']):
            st.markdown(f'{last_ai_msg["content"]}')            
            render_chat_buttons(len(st.session_state['chat_messages']) - 1, last_ai_msg['content'])           
        

def render_chat_buttons(msg_index: int, copy_text: str) -> None:
    _, voice_col, copy_col = st.columns([20, 1, 1])
    with voice_col:
        st.button(label='', key=f'voice_{msg_index}', icon=':material/volume_up:',
                  help='Voice text of the message', on_click=voice_message,
                  args=(msg_index,))
    with copy_col:
        st_copy_to_clipboard(copy_text, before_copy_label='💾', key=f'copy_{msg_index}')
        # st.button(label='', key=f'copy_{msg_index}', icon=':material/content_copy:',
        #           help='Copy message text')

def voice_message(msg_index: int) -> None:
    text = st.session_state['chat_messages'][msg_index]['content']
    audio_bytes = text_to_speech(text)        
    b64 = base64.b64encode(audio_bytes.content).decode()
    md = f'<audio autoplay="true" src="data:audio/wav;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)

render_chat_layout() 
    