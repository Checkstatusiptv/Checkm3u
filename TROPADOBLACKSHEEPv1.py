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

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

class TelaTerminal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        
        self.terminal = TextInput(size_hint=(1, 0.9), readonly=True, multiline=True)
        self.layout.add_widget(self.terminal)
        
        self.add_widget(self.layout)

    def atualizar_terminal(self, mensagem):
        self.terminal.text += mensagem + '\n'
        self.terminal.cursor = (0, 0)

class TelaChecker(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.versao_local = "1.0.0"  # Defina sua versão local
        self.url_menu_json = 'URL_DO_SEU_JSON'  # URL do JSON com a versão
        self.layout = BoxLayout(orientation='vertical', padding=10)

        # Label para mostrar a versão do script
        self.label_versao = Label(text=f"Script versão: {self.versao_local}", size_hint=(1, None), height=40)
        self.layout.add_widget(self.label_versao)

        self.criar_pasta_download()
        self.imagem = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/tropadoback.jpg')
        self.imagem.allow_stretch = True
        self.imagem.size_hint_y = 0.6
        self.layout.add_widget(self.imagem)

        self.label_funcionalidade = Label(text="", size_hint=(1, None), height=110)
        self.label_funcionalidade.bind(size=self.label_funcionalidade.setter('text_size'))
        self.layout.add_widget(self.label_funcionalidade)

        button_spinner_layout = BoxLayout(size_hint=(1, None), height=80)
        self.adicionar_botoes(button_spinner_layout)
        self.layout.add_widget(button_spinner_layout)

        self.barra_progresso = ProgressBar(max=100, size_hint=(1, None), height=50)
        self.layout.add_widget(self.barra_progresso)

        self.label_status = Label(text='Pronto... O usuário pode baixar diferentes arquivos tais como (scripts, combos, add-ons)', size_hint=(1, None), height=1500)
        self.layout.add_widget(self.label_status)

        self.imagem_assinatura = self.baixar_e_exibir_imagem('https://raw.githubusercontent.com/Checkstatusiptv/Checkm3u/refs/heads/main/TROPA-DO-BLACKSHEEP-N-VIDA-27-09-2024.png')
        self.imagem_assinatura.allow_stretch = True
        self.imagem_assinatura.size_hint_y = 0.2
        self.layout.add_widget(self.imagem_assinatura)

        self.add_widget(self.layout)

        # Verifica atualização no início
        self.verificar_atualizacao()

    def criar_pasta_download(self):
        self.pasta_download = os.path.join('/storage/emulated/0', 'TROPADOBLACKSHEEP') if platform == 'android' else os.path.join(os.path.expanduser("~"), "TROPADOBLACKSHEEP")
        os.makedirs(self.pasta_download, exist_ok=True)

    def baixar_e_exibir_imagem(self, url):
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            img_data = BytesIO(resposta.content)
            textura = CoreImage(img_data, ext='jpg').texture
            return Image(texture=textura)
        except Exception as e:
            logging.error(f"Erro ao baixar a imagem: {str(e)}")
            return Label(text="Imagem não disponível. Tente mais tarde.")

    def adicionar_botoes(self, layout):
        retro_background_color = (0.5, 0.2, 0.8, 1)
        text_color = (1, 1, 1, 1)

        for texto, metodo in [('SCRIPTS', self.mostrar_popup_scripts),
                              ('COMBOS', self.mostrar_popup_comb),
                              ('ADD-ONS', self.mostrar_popup_kodi),
                              ('CONTATO', self.abrir_contato)]:
            button = Button(text=texto, size_hint=(0.95, 1), on_press=metodo,
                            background_color=retro_background_color, color=text_color, font_size=18)
            layout.add_widget(button)

    def verificar_atualizacao(self):
        try:
            resposta = requests.get(self.url_menu_json)
            resposta.raise_for_status()
            dados = resposta.json()

            if dados['version'] != self.versao_local:
                self.baixar_script(dados['script_url'])
            else:
                self.atualizar_status('O script já está atualizado.')
        except Exception as e:
            logging.error(f"Erro ao verificar atualização: {str(e)}")

    def baixar_script(self, url):
        self.atualizar_status('Baixando script atualizado...')
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()

            with open('seuscript.py', 'wb') as f:
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
            self.mostrar_popup_download("SCRIPTS", dados['scripts'])

    def mostrar_popup_comb(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            self.mostrar_popup_download("COMBOS", dados['combos'])

    def mostrar_popup_kodi(self, instance):
        dados = self.carregar_dados_github()
        if dados:
            self.mostrar_popup_download("ADD-ONS", dados['addons'])

    def mostrar_popup_download(self, title, options):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
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

        close_btn = Button(text='Fechar', size_hint_y=None, height=60)
        close_btn.bind(on_press=self.fechar_popup)
        content.add_widget(close_btn)

        self.script_popup = Popup(title=title, content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        self.script_popup.open()

    def iniciar_download(self, url):
        self.label_status.text = 'Baixando...'
        self.barra_progresso.value = 0
        self.desabilitar_botoes(True)
        threading.Thread(target=self.download_file, args=(url,)).start()

    def download_file(self, url, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                total_length = response.headers.get('content-length')

                if total_length is None:
                    Clock.schedule_once(lambda dt: self.finalizar_download(url))
                    return

                total_length = int(total_length)
                downloaded = 0
                filename = os.path.join(self.pasta_download, url.split("/")[-1])

                with open(filename, 'wb') as f:
                    for data in response.iter_content(chunk_size=100):
                        if data:
                            f.write(data)
                            downloaded += len(data)
                            progress = (downloaded / total_length) * 100
                            Clock.schedule_once(lambda dt, p=progress: setattr(self.barra_progresso, 'value', p))

                Clock.schedule_once(lambda dt: self.finalizar_download(filename))
                break  # Exit loop on successful download
            except requests.ConnectionError:
                if attempt < retries - 1:
                    self.atualizar_status('Conexão falhou, tentando novamente...')
                else:
                    self.atualizar_status('Erro: Falha na conexão.')
            except requests.Timeout:
                if attempt < retries - 1:
                    self.atualizar_status('Tempo de conexão excedido, tentando novamente...')
                else:
                    self.atualizar_status('Erro: Tempo de conexão excedido.')
            except Exception as e:
                self.atualizar_status(f'Erro: {str(e)}')
                break  # Exit loop on other exceptions
            finally:
                Clock.schedule_once(lambda dt: self.enable_buttons())

    def desabilitar_botoes(self, desabilitar):
        for child in self.layout.children:
            if isinstance(child, Button):
                child.disabled = desabilitar

    def enable_buttons(self):
        self.desabilitar_botoes(False)

    def atualizar_status(self, message):
        self.label_status.text = message

    def finalizar_download(self, filename):
        self.label_status.text = f'{filename} concluído!'
        self.barra_progresso.value = 100
        self.atualizar_terminal(f'Arquivo baixado: {filename}')  # Atualiza o terminal

    def atualizar_terminal(self, mensagem):
        terminal_screen = self.manager.get_screen('terminal')
        terminal_screen.atualizar_terminal(mensagem)

    def abrir_contato(self, instance):
        webbrowser.open('https://t.me/BLACKSHEEP_B')

    def fechar_popup(self, instance):
        if hasattr(self, 'script_popup') and self.script_popup:
            self.script_popup.dismiss()
            self.script_popup = None

class MeuApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(TelaChecker(name='checker'))
        sm.add_widget(TelaTerminal(name='terminal'))  # Adiciona a tela de terminal
        return sm

if __name__ == '__main__':
    MeuApp().run()