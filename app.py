import streamlit as st
from audio_recorder_streamlit import audio_recorder
from st_multimodal_chatinput import multimodal_chatinput
from typing import Literal
from PIL import Image
from io import BytesIO
import base64
from st_copy_to_clipboard import st_copy_to_clipboard

st.set_page_config(page_title='Multimodal chat', layout='wide')
NO_AUDIO_STR = b'RIFF,\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80\xbb\x00\x00\x00\xee\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00'
# audio_bytes = audio_recorder(
#     text='Record audio'
# )

# if audio_bytes and audio_bytes != NO_AUDIO_STR:
#     print(audio_bytes)
#     print('Вызван!')    
#     st.audio(audio_bytes)
# st.button(icon=':material/publish:', key='icon_btn', label='Upload')


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

def render_chat_layout() -> None:
    messages = st.container(height=750)
    audio_bytes = None
    img_upload_col, audio_record_col, chat_input_col = st.columns([1, 1, 20])
    with img_upload_col:
        with st.popover(label='', icon=':material/upload:'):
            uploaded_image = st.file_uploader(label='Upload images', key='img_uploader',
                                              type=['jpeg', 'jpg', 'png'], accept_multiple_files=False)
    with audio_record_col:
        audio_bytes = audio_recorder(text='', icon_size='2x', neutral_color='#5c5c5c')
    with chat_input_col:
        chat_input = st.chat_input(placeholder='Type your prompt here')
    for msg_ind, message in enumerate(st.session_state['chat_messages']):
        with messages.chat_message(name=message['role']):
            st.markdown(f'{message["content"]}')            
            render_chat_buttons(msg_ind, message["content"])    
    if chat_input:        
        if uploaded_image:
            img_type = uploaded_image.type
            raw_image = Image.open(uploaded_image)
            image_str = f'![{uploaded_image.name}](data:{img_type};base64,{get_image_base_64(raw_image)})'            
            make_message(role='user', content=f'{chat_input}\n\n{image_str}')
            uploaded_image = None
        else:
            make_message(role='user', content=chat_input)
        last_msg = st.session_state['chat_messages'][-1]
        with messages.chat_message(last_msg['role']):
            st.markdown(f'{last_msg["content"]}')            
            render_chat_buttons(len(st.session_state['chat_messages']) - 1, last_msg['content'])        
        

def render_chat_buttons(msg_index: int, copy_text: str) -> None:
    _, voice_col, copy_col = st.columns([20, 1, 1])
    with voice_col:
        st.button(label='', key=f'voice_{msg_index}', icon=':material/volume_up:',
                  help='Voice text of the message')
    with copy_col:
        st_copy_to_clipboard(copy_text, before_copy_label='💾')
        # st.button(label='', key=f'copy_{msg_index}', icon=':material/content_copy:',
        #           help='Copy message text')

render_chat_layout() 
    