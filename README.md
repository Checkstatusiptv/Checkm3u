<style>
        body {
            background-color: #000000;
            color: #00FF00;
        }

        .container {
            text-align: left;
            margin-top: 10px;
            padding: 20px;
            border-radius: 10px;
        }
        
        body::before {
            content: "";
            background: url("https://media4.giphy.com/media/WwGrm4cUFnRRcG6wMH/giphy.gif?cid=6c09b952jytl4483rhhy5e70bun4nspmhfdvclglegexqi8q&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g") center center no-repeat fixed;
            background-size: cover; /* Adaptar a imagem ao tamanho da tela */
            opacity: 0.2; /* Ajuste a opacidade conforme necessário */
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            pointer-events: none;
        }

        .info-container {
            margin-top: 20px;
            text-align: left;
        }

        .info-label {
            font-weight: bold;
            color: white;
        }

        .camuflado {
            color: #FFFF00;
        }

        .erro {
            color: red;
        }

        .separador {
            margin-top: 10px;
        }

        #resultados-container {
            margin-top: 20px;
            text-align: left;
        }

        #output-results {
            margin-top: 20px;
            text-align: center; /* Alinhamento centralizado */
        }

        .progress-container {
            width: 100%;
            margin-top: 15px;
        }

        .progress {
            height: 25px;
        }

        #busca-container {
            margin-top: 15px;
            text-align: center; /* Alinhamento centralizado */
        }

        #inputBusca {
            width: 100%; /* Largura total */
            margin-bottom: 10px; /* Espaçamento inferior */
        }

        #entrar {
            width: 95%; /* Largura total */
        }

        #canal-encontrado {
            margin-top: 20px;
            text-align: left;
        }
    </style>
