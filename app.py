import streamlit as st
from audio_recorder_streamlit import audio_recorder
from st_multimodal_chatinput import multimodal_chatinput

st.set_page_config(page_title='Multimodal chat', layout='wide')
# audio_bytes = audio_recorder(
#     text='Record audio'
# )
# NO_AUDIO_STR = b'RIFF,\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80\xbb\x00\x00\x00\xee\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00'
# if audio_bytes and audio_bytes != NO_AUDIO_STR:
#     print(audio_bytes)
#     print('Вызван!')    
#     st.audio(audio_bytes)
# st.button(icon=':material/publish:', key='icon_btn', label='Upload')
messages = st.container(height=750)
chat_input = multimodal_chatinput()
if chat_input:
    if len(chat_input['images']) > 0:
        images_str = '\n'.join([f'![Image]({file})' for file in chat_input['images']])
        with messages.chat_message(name='user'):
            st.markdown(f'{chat_input["text"]}')
            st.markdown(images_str)
            st.button(label='', key='kaka', icon=':material/volume_up:')
    else:
        with messages.chat_message(name='user'):
            st.markdown(f'{chat_input["text"]}')
            st.button(label='Ozvuchka', key='kaka')    
    