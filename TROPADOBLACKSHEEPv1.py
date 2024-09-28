import os
import threading
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
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
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
        retro_background_color = (0, 0, 1, 1)
        text_color = (1, 1, 1, 1)

        # Mapeia os botões às suas respectivas funções
        botoes = [
            ('SCRIPTS', self.mostrar_popup_scripts),
            ('COMBOS', self.mostrar_popup_comb),
            ('ADD-ONS', self.mostrar_popup_kodi),
            ('CONTATO', self.abrir_contato)  # Método a ser definido
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

        scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
        button_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        button_layout.bind(minimum_height=button_layout.setter('height'))

        for item in options:
            btn = Button(text=item['name'], size_hint_y=None, height=80)
            btn.bind(on_press=lambda x, url=item['url']: self.iniciar_download(url))
            button_layout.add_widget(btn)

        scroll_view.add_widget(button_layout)
        content.add_widget(scroll_view)

        close_btn = Button(text='Fechar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.popup = Popup(title=title, content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def iniciar_download(self, url):
        threading.Thread(target=self.download_file, args=(url,)).start()

    def download_file(self, url):
        try:
            self.atualizar_status('Baixando arquivo...')
            resposta = requests.get(url, stream=True)
            resposta.raise_for_status()

            total = int(resposta.headers.get('content-length', 0))
            downloaded = 0

            with open(os.path.join(self.pasta_download, url.split('/')[-1]), 'wb') as f:
                for data in resposta.iter_content(chunk_size=1024):
                    downloaded += len(data)
                    f.write(data)
                    self.atualizar_progresso_barra(downloaded, total)

            self.atualizar_status('Download concluído!')
        except Exception as e:
            logging.error(f"Erro ao baixar o arquivo: {str(e)}")
            self.atualizar_status(f'Erro: {str(e)}')

    def atualizar_progresso_barra(self, progresso, total):
        if total > 0:
            porcentagem = (progresso / total) * 100
            # Atualiza a barra de progresso
            Clock.schedule_once(lambda dt: self.atualizar_barra(porcentagem))

    def atualizar_barra(self, porcentagem):
        self.barra_progresso.value = porcentagem

    def atualizar_status(self, mensagem):
        self.label_status.text = mensagem

    def fechar_popup(self, instance):
        self.popup.dismiss()

    def abrir_contato(self, instance):
        # Lógica para abrir o contato ou um link, se necessário
        webbrowser.open("https://t.me/BLACKSHEEP_B")  # Exemplo de URL

class GerenciadorTela(ScreenManager):
    pass

class MeuApp(App):
    def build(self):
        gerenciador = GerenciadorTela(transition=NoTransition())
        gerenciador.add_widget(TelaChecker(name='checker'))
        gerenciador.add_widget(TelaTerminal(name='terminal'))
        return gerenciador

if __name__ == '__main__':
    MeuApp().run()