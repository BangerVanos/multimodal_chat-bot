import reflex as rx
from .states.chat_state import ChatState
import MultimodalChatbot.frontend.style as style


def qa_component(prompt: str, response: str) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.box(
                rx.markdown(prompt, style=style.question_style),
                text_align="right",
            ),
            justify='end'
        ),
        rx.flex(
            rx.box(
                rx.markdown(response, style=style.answer_style),
                text_align="left",
            ),
            justify='start'
        ),        
        margin_y="1em",
    )

def messages_component() -> rx.Component:    
    return rx.scroll_area(
        rx.flex(
            rx.foreach(
                ChatState.chat_history,
                lambda qa: qa_component(qa[0], qa[1])
            ),
            direction='column',
            spacing='2'
        ),            
        scrollbars='vertical',
        style={'height': '90%'},
        type='hover',            
    )   


def chat_view() -> rx.Component:
    return rx.flex(
        rx.vstack(
            messages_component(),
            rx.hstack(
                rx.input(placeholder='Enter your prompt here...', value=ChatState.prompt, on_change=ChatState.set_prompt, width='80%'),
                rx.button(rx.icon(tag='share'), variant='ghost'),
                rx.button(rx.icon(tag='mic'), variant='ghost'),
                rx.button(rx.icon(tag='send'), variant='ghost', on_click=ChatState.get_answer),                
                width='100%'
            ),
            width='80%'                       
        ),
        height='100vh',
        width='100%',
        justify='center',
        spacing='1',        
        padding='2em',                
    )
