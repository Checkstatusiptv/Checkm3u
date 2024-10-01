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

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Definindo a taxa de FPS
Config.set('graphics', 'max_fps', '60')

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
        self.versao_local = "v1.2-F[BETA]"
        self.url_menu_json = 'https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/main/version.json'
        self.layout = BoxLayout(orientation='vertical', padding=10)

        self.label_funcionalidade = Label(text="", size_hint=(1, None), height=100)
        self.label_funcionalidade.bind(size=self.label_funcionalidade.setter('text_size'))
        self.layout.add_widget(self.label_funcionalidade)

        python_version = "Python: 3.11.4 [GCC 11.4.0]"
        self.label_python_version = Label(text=python_version, size_hint=(1, None), height=30, color=(1, 1, 0, 1))
        self.layout.add_widget(self.label_python_version)

        os_version = sys.platform
        self.label_os_version = Label(text=f"Sistema Operacional: {os_version}", size_hint=(1, None), height=30, color=(0, 1, 1, 1))
        self.layout.add_widget(self.label_os_version)

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

        self.label_status = Label(text='Pronto... O usuário pode baixar diferentes arquivos tais como (scripts, combos, add-ons)', size_hint=(1, None), height=1020, color=(1, 1, 1, 1))
        self.layout.add_widget(self.label_status)

        self.label_versao = Label(text=f"{self.versao_local}", size_hint=(1, None), height=30, color=(0, 1, 0, 1))
        self.layout.add_widget(self.label_versao)

        self.add_widget(self.layout)

        self.marca_dagua = self.adicionar_marca_dagua('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/GITHUB-29-09-2024.png')
        self.layout.add_widget(self.marca_dagua)

        self.popup_download = None
        self.popup = None
        self.verificar_atualizacao()

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
        botoes = [
            ('SCRIPTS', self.mostrar_popup_scripts),
            ('COMBOS', self.mostrar_popup_comb),
            ('ADD-ONS', self.mostrar_popup_kodi),
            ('TELEGRAM', self.mostrar_popup_telegram)
        ]

        for texto, metodo in botoes:
            button = Button(
                text=texto,
                size_hint=(0.95, 1),
                on_press=metodo,
                background_color=(0, 0.5, 0, 1),  # Azul escuro
                color=(1, 1, 1, 1),  # Texto branco
                font_size=18,
                height=60,
                background_normal='',  # Remove a imagem padrão
            )

            with button.canvas.before:
                Color(0, 0, 0, 0.2)  # Cor da sombra
                button.shadow_rect = RoundedRectangle(size=button.size, pos=(button.x + 3, button.y - 3), radius=[10])
            
            button.bind(size=lambda instance, value: setattr(instance.shadow_rect, 'size', value))
            button.bind(pos=lambda instance, value: setattr(instance.shadow_rect, 'pos', (value[0] + 3, value[1] - 3)))
            
            layout.add_widget(button)

    def verificar_atualizacao(self):
        Thread(target=self._verificar_atualizacao_thread).start()

    def _verificar_atualizacao_thread(self):
        try:
            resposta = requests.get(self.url_menu_json)
            resposta.raise_for_status()
            dados = resposta.json()

            if dados['version'] != self.versao_local:
                Clock.schedule_once(lambda dt: self.mostrar_popup_nova_versao(dados['version'], dados['script_url']), 0)
            else:
                Clock.schedule_once(lambda dt: self.atualizar_status('O script já está atualizado.'), 0)
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
        
        btn_atualizar = Button(text='Atualizar Agora', size_hint_y=None, height=60)
        btn_atualizar.bind(on_press=lambda x: self.baixar_script(script_url))
        content.add_widget(btn_atualizar)

        close_btn = Button(text='Fechar', size_hint_y=None, height=60)
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
        Thread(target=self._baixar_script_thread, args=(url,)).start()

    def _baixar_script_thread(self, url):
        self.atualizar_status('Baixando script atualizado...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            nome_arquivo = os.path.basename(url)
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            Clock.schedule_once(lambda dt: self.atualizar_status('Script atualizado. Reiniciando...'), 0)
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.atualizar_status(f'Erro ao baixar o script: {str(e)}'), 0)

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

        scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))
        scroll_view.do_scroll_x = False

        box_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))

        for item in lista_downloads:
            button = Button(text=item['name'], size_hint_y=None, height=140)
            button.bind(on_press=lambda btn, url=item['url']: self.baixar_item(url))
            box_layout.add_widget(button)

        scroll_view.add_widget(box_layout)
        layout.add_widget(scroll_view)

        close_button = Button(text='Fechar', size_hint_y=None, height=60)
        close_button.bind(on_press=self.fechar_popup)
        layout.add_widget(close_button)

        self.popup_download = Popup(title=titulo, content=layout, size_hint=(0.6, 0.3))
        self.popup_download.open()

    def baixar_item(self, url):
        Thread(target=self._baixar_item_thread, args=(url,)).start()

    def _baixar_item_thread(self, url):
        self.atualizar_status('Baixando item...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            nome_arquivo = os.path.basename(url)
            caminho_arquivo = os.path.join(self.pasta_download, nome_arquivo)

            with open(caminho_arquivo, 'wb') as f:
                f.write(resposta.content)

            Clock.schedule_once(lambda dt: self.atualizar_status(f'Item {nome_arquivo} baixado com sucesso!'), 0)

            # Fechar o popup automaticamente após o download
            Clock.schedule_once(lambda dt: self.fechar_popup(None), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.atualizar_status(f'Erro ao baixar o item: {str(e)}'), 0)

    def mostrar_popup_telegram(self, instance):
        content = BoxLayout(orientation='vertical', padding=10)

        imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/redesocial.png')
        content.add_widget(imagem)

        close_btn = Button(text='Fechar', size_hint_y=None, height=60)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title='Telegram', content=content, size_hint=(0.7, 0.7))
        self.popup.open()

    def adicionar_marca_dagua(self, url):
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            img_data = BytesIO(resposta.content)
            textura = CoreImage(img_data, ext='png').texture
            marca_dagua = Image(texture=textura, size_hint=(None, None), size=(200, 200))
            marca_dagua.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            marca_dagua.opacity = 0.5
            return marca_dagua
        except Exception as e:
            logging.error(f"Erro ao adicionar a marca d'água: {str(e)}")
            return Label(text="Marca d'água não disponível.", color=(1, 1, 1, 1))

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