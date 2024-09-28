import os
import logging
import requests
import webbrowser
import sys
from io import BytesIO
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
from kivy.graphics import Color, RoundedRectangle

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

class TelaTerminal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        self.terminal = TextInput(size_hint=(1, None), height=300, readonly=True, multiline=True)
        self.layout.add_widget(self.terminal)
        self.add_widget(self.layout)

    def atualizar_terminal(self, mensagem):
        self.terminal.text += mensagem + '\n'
        self.terminal.cursor = (0, 0)

class TelaChecker(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.versao_local = "BETAv1.2"  # Nome da versão pode ser alterado conforme necessário
        self.url_menu_json = 'https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/version.json'
        self.layout = BoxLayout(orientation='vertical', padding=10)

        with self.layout.canvas.before:
            Color(0, 0, 0, 1)  # Cor de fundo preto
            self.rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[10])

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.label_funcionalidade = Label(text="", size_hint=(1, None), height=110)
        self.label_funcionalidade.bind(size=self.label_funcionalidade.setter('text_size'))
        self.layout.add_widget(self.label_funcionalidade)

        self.criar_pasta_download()

        self.imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/scriptbyblacksheep.png')
        self.imagem.allow_stretch = True
        self.imagem.size_hint_y = 0.3
        self.layout.add_widget(self.imagem)

        button_spinner_layout = BoxLayout(size_hint=(1, None), height=80)
        self.adicionar_botoes(button_spinner_layout)
        self.layout.add_widget(button_spinner_layout)

        self.barra_progresso = ProgressBar(max=100, size_hint=(1, None), height=50)
        self.layout.add_widget(self.barra_progresso)

        self.label_status = Label(text='Pronto... O usuário pode baixar diferentes arquivos tais como (scripts, combos, add-ons)', size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        self.layout.add_widget(self.label_status)

        self.label_versao = Label(text=f"SCRIPT VERSÃO: {self.versao_local}", size_hint=(1, None), height=30, color=(0, 1, 0, 1))
        self.layout.add_widget(self.label_versao)

        self.add_widget(self.layout)
        self.verificar_atualizacao()

    def _update_rect(self, *args):
        self.rect.pos = self.layout.pos
        self.rect.size = self.layout.size

    def criar_pasta_download(self):
        self.pasta_download = os.path.join('/storage/emulated/0', 'TROPADOBLACKSHEEP') if platform == 'android' else os.path.join(os.path.expanduser("~"), "TROPADOBLACKSHEEP")
        os.makedirs(self.pasta_download, exist_ok=True)

    def baixar_e_exibir_imagem(self, url):
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            img_data = BytesIO(resposta.content)
            textura = CoreImage(img_data, ext='png').texture
            imagem = Image(texture=textura)
            imagem.allow_stretch = True
            return imagem
        except Exception as e:
            logging.error(f"Erro ao baixar a imagem: {str(e)}")
            return Label(text="Imagem não disponível. Tente mais tarde.", color=(1, 1, 1, 1))

    def adicionar_botoes(self, layout):
        retro_background_color = (1, 0.5, 0, 1)  # Cor laranja para os botões
        text_color = (1, 1, 1, 1)

        # Mapeia os botões às suas respectivas funções
        botoes = [
            ('SCRIPTS', self.mostrar_popup_scripts),
            ('COMBOS', self.mostrar_popup_comb),
            ('ADD-ONS', self.mostrar_popup_kodi),
            ('CONTATO', self.abrir_contato)  # Método definido abaixo
        ]

        for texto, metodo in botoes:
            button = Button(text=texto, size_hint=(0.95, 1), on_press=metodo,
                            background_color=retro_background_color, color=text_color, font_size=18)
            layout.add_widget(button)

    def verificar_atualizacao(self):
        try:
            resposta = requests.get(self.url_menu_json)
            resposta.raise_for_status()
            dados = resposta.json()

            if dados['version'] != self.versao_local:
                self.mostrar_popup_nova_versao(dados['version'], dados['script_url'])
            else:
                self.atualizar_status('O script já está atualizado.')
        except Exception as e:
            logging.error(f"Erro ao verificar atualização: {str(e)}")

    def mostrar_popup_nova_versao(self, nova_versao, script_url):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f'Uma nova versão ({nova_versao}) está disponível!', size_hint_y=None, height=40))
        
        btn_atualizar = Button(text='Atualizar Agora', size_hint_y=None, height=50)
        btn_atualizar.bind(on_press=lambda x: self.baixar_script(script_url))
        content.add_widget(btn_atualizar)

        close_btn = Button(text='Fechar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title='Atualização Disponível', content=content, size_hint=(0.9, 0.4))
        self.popup.open()

    def fechar_popup(self, instance):
        self.popup.dismiss()

    def baixar_script(self, url):
        self.atualizar_status('Baixando script atualizado...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            # Extrai o nome do arquivo da URL
            nome_arquivo = url.split('/')[-1]
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            self.atualizar_status('Script atualizado. Reiniciando...')
            os.execv(sys.executable, ['python'] + sys.argv)  # Reinicia o aplicativo
        except Exception as e:
            self.atualizar_status(f'Erro ao baixar o script: {str(e)}')

    def carregar_dados_github(self):
        url = 'https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/Menu.json'
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            dados = resposta.json()
            return dados
        except Exception as e:
            logging.error(f"Erro ao carregar dados do GitHub: {str(e)}")
            return None

    def mostrar_popup_scripts(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            self.mostrar_popup_download("SCRIPTS", dados['scripts'], "Scripts usados para executar em Python")

    def mostrar_popup_comb(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            self.mostrar_popup_download("COMBOS", dados['combos'], "Combos usados para executar em Python")

    def mostrar_popup_kodi(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            self.mostrar_popup_download("ADD-ONS", dados['addons'], "Add-ons usados para executar em Python")

    def mostrar_popup_download(self, title, options, info_text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Adiciona um Label com o texto desejado
        info_label = Label(text=info_text, size_hint_y=None, height=40, color=(1, 1, 1, 1))
        content.add_widget(info_label)

        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=50)
        content.add_widget(self.progress_bar)

        for option in options:
            button = Button(text=option, size_hint=(1, None), height=40)
            button.bind(on_press=lambda instance, url=options[option]: self.baixar_arquivo(url))
            content.add_widget(button)

        close_btn = Button(text='Fechar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title=title, content=content, size_hint=(0.9, 0.6))
        self.popup.open()

    def baixar_arquivo(self, url):
        self.atualizar_status(f'Baixando {url}...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            # Extrai o nome do arquivo da URL
            nome_arquivo = url.split('/')[-1]
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            self.atualizar_status(f'{nome_arquivo} baixado com sucesso!')
        except Exception as e:
            self.atualizar_status(f'Erro ao baixar o arquivo: {str(e)}')

    def abrir_contato(self, instance):
        url = 'https://t.me/BLACKSHEEP_B'  # Altere para o link desejado
        webbrowser.open(url)

    def atualizar_status(self, mensagem):
        self.label_status.text = mensagem
        logging.info(mensagem)

class GerenciadorTela(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(TelaChecker(name='checker'))
        self.add_widget(TelaTerminal(name='terminal'))

class MeuApp(App):
    def build(self):
        return GerenciadorTela()

if __name__ == '__main__':
    MeuApp().run()