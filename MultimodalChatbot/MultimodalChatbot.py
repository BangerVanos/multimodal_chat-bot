"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from .frontend.chat_view import chat_view

app = rx.App()
app.add_page(chat_view, route='/')
