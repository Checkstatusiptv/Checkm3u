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