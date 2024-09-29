import os
import logging
import requests
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
        self.terminal = TextInput(size_hint=(1, 0.7), readonly=True, multiline=True)
        self.layout.add_widget(self.terminal)
        self.outro_widget = Button(text="Outro widget", size_hint=(1, 0.3))
        self.layout.add_widget(self.outro_widget)
        self.add_widget(self.layout)

    def atualizar_terminal(self, mensagem):
        self.terminal.text += mensagem + '\n'
        self.terminal.cursor = (0, 0)

class TelaChecker(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.versao_local = "v1.2.0"
        self.url_menu_json = 'https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/main/version.json'
        self.layout = BoxLayout(orientation='vertical', padding=10)

        with self.layout.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[10])

        self.bind(size=self._update_rect, pos=self._update_rect)
        self.label_funcionalidade = Label(text="", size_hint=(1, None), height=110)
        self.label_funcionalidade.bind(size=self.label_funcionalidade.setter('text_size'))
        self.layout.add_widget(self.label_funcionalidade)

        self.criar_pasta_download()
        self.imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/main/scriptbyblacksheep.png')
        self.imagem.allow_stretch = True
        self.imagem.size_hint_y = 0.3
        self.layout.add_widget(self.imagem)

        button_spinner_layout = BoxLayout(size_hint=(1, None), height=80)
        self.adicionar_botoes(button_spinner_layout)
        self.layout.add_widget(button_spinner_layout)

        self.barra_progresso = ProgressBar(max=100, size_hint=(1, None), height=50)
        self.layout.add_widget(self.barra_progresso)

        self.label_status = Label(text='Pronto... O usuário pode baixar diferentes arquivos tais como (scripts, combos, add-ons)', size_hint=(1, None), height=1400, color=(1, 1, 1, 1))
        self.layout.add_widget(self.label_status)

        self.label_versao = Label(text=f"SCRIPT: {self.versao_local}", size_hint=(1, None), height=30, color=(0, 1, 0, 1))
        self.layout.add_widget(self.label_versao)

        self.add_widget(self.layout)
        self.popup_download = None
        self.popup = None  # Inicializa a variável popup
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
        retro_background_color = (1, 0, 0, 1)
        text_color = (1, 1, 1, 1)

        botoes = [
            ('SCRIPTS', self.mostrar_popup_scripts),
            ('COMBOS', self.mostrar_popup_comb),
            ('ADD-ONS', self.mostrar_popup_kodi),
            ('TELEGRAM', self.mostrar_popup_telegram)  # Botão TELEGRAM
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

    def atualizar_status(self, mensagem):
        self.label_status.text = mensagem
        logging.info(mensagem)

    def mostrar_popup_nova_versao(self, nova_versao, script_url):
        content = BoxLayout(orientation='vertical', padding=10)

        imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/atualizacao.png')
        content.add_widget(imagem)

        content.add_widget(Label(text=f'Uma nova versão ({nova_versao}) está disponível!', size_hint_y=None, height=40))
        
        btn_atualizar = Button(text='Atualizar Agora', size_hint_y=None, height=50)
        btn_atualizar.bind(on_press=lambda x: self.baixar_script(script_url))
        content.add_widget(btn_atualizar)

        close_btn = Button(text='Fechar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title='Atualização Disponível', content=content, size_hint=(0.7, 0.3))
        self.popup.open()

    def fechar_popup(self, instance):
        if self.popup:
            self.popup.dismiss()
            self.popup = None

        if self.popup_download:
            self.popup_download.dismiss()
            self.popup_download = None

    def baixar_script(self, url):
        self.atualizar_status('Baixando script atualizado...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            nome_arquivo = os.path.basename(url)
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            self.atualizar_status('Script atualizado. Reiniciando...')
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            self.atualizar_status(f'Erro ao baixar o script: {str(e)}')

    def carregar_dados_github(self):
        url = 'https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/main/Menu.json'
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            dados = resposta.json()
            return dados
        except Exception as e:
            logging.error(f"Erro ao carregar dados: {str(e)}")
            return None

    def mostrar_popup_scripts(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            if not dados.get('scripts'):
                self.atualizar_status("Nenhum script disponível para download.")
                return
            self.mostrar_popup_download("SCRIPTS", dados['scripts'], "Scripts usados para executar em Python")

    def mostrar_popup_comb(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            if not dados.get('combos'):
                self.atualizar_status("Nenhum combo disponível para download.")
                return
            self.mostrar_popup_download("COMBOS", dados['combos'], "Combos disponíveis para download")

    def mostrar_popup_kodi(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            if not dados.get('addons'):
                self.atualizar_status("Nenhum add-on disponível para download.")
                return
            self.mostrar_popup_download("ADD-ONS", dados['addons'], "Add-ons disponíveis para download")

    def mostrar_popup_download(self, titulo, lista_downloads, descricao):
        layout = BoxLayout(orientation='vertical', padding=10)
        layout.add_widget(Label(text=descricao, size_hint_y=None, height=40))

        scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        scroll_view.do_scroll_x = False

        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))

        for item in lista_downloads:
            button = Button(text=item['name'], size_hint_y=None, height=40)
            button.bind(on_press=lambda btn, url=item['url']: self.baixar_item(url))
            box_layout.add_widget(button)

        scroll_view.add_widget(box_layout)
        layout.add_widget(scroll_view)

        close_button = Button(text='Fechar', size_hint_y=None, height=50)
        close_button.bind(on_press=self.fechar_popup)
        layout.add_widget(close_button)

        self.popup_download = Popup(title=titulo, content=layout, size_hint=(0.7, 0.7))
        self.popup_download.open()

    def baixar_item(self, url):
        self.atualizar_status('Baixando item...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            nome_arquivo = os.path.basename(url)
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            self.atualizar_status(f'Item {nome_arquivo} baixado com sucesso!')

            # Fechar o popup automaticamente após o download
            if self.popup_download:
                self.popup_download.dismiss()
        except Exception as e:
            self.atualizar_status(f'Erro ao baixar o item: {str(e)}')

    def mostrar_popup_telegram(self, instance):
        content = BoxLayout(orientation='vertical', padding=10)

        imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/redesocial.png')  # Substitua pela URL da sua imagem
        content.add_widget(imagem)

        close_btn = Button(text='Fechar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title='Telegram', content=content, size_hint=(0.7, 0.7))
        self.popup.open()

class GerenciadorTela(ScreenManager):
    pass

class MeuApp(App):
    def build(self):
        self.tela_manager = GerenciadorTela()
        self.tela_manager.add_widget(TelaChecker(name='tela_checker'))
        self.tela_manager.add_widget(TelaTerminal(name='tela_terminal'))
        return self.tela_manager

if __name__ == '__main__':
    MeuApp().run()