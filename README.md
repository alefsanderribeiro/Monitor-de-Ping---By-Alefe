# Monitor de Ping

Um programa simples e eficiente para monitoramento contínuo de ping com registro de histórico e logs.

## 📋 Características

- Interface de console amigável
- Histórico dos últimos endereços monitorados
- Logs detalhados com data e hora
- Suporte para Windows e Linux
- Monitoramento em tempo real
- Salvamento automático de logs
- Notificações via Email, SMS, Telegram, WhatsApp e Desktop

## 🚀 Instalação

### Pré-requisitos

- Python 3.6 ou superior


### Instalando as dependências
Para instalar as dependências, utilize o UV com o seguinte comando:

```bash
uv sync
```

Caso não tneha o UV instalado, você pode usar o seguinte comando:

```bash
pip install uv
```


### Criando o executável

```bash
python setup.py build
```

## 💻 Como usar

1. Execute o programa:
   - Via Python: `python src/main.py`
   - Ou use o executável gerado: `Monitor de Ping.exe`

2. Selecione uma opção:
   - Escolha um endereço do histórico ou digite 'D' para inserir um novo endereço.
   - Digita 'S' para iniciar o monitoramento.

3. O programa iniciará o monitoramento e mostrará:
   - Status da conexão
   - Tempo de resposta em ms
   - Logs em tempo real

4. Para encerrar, pressione `Ctrl+C`

## 📁 Estrutura de arquivos

```
Monitor de Ping/
│
├── src/
│   ├── main.py              # Código principal
│   ├── configuracao.py      # Configurações do monitoramento
│   ├── log.py               # Gerenciamento de logs
│   ├── notificação.py        # Notificadores (Email, SMS, etc.)
│   ├── logo_alefe.py        # Logo do programa
│   └── historico_ping.json   # Arquivo de histórico
│
├── setup.py                 # Configuração para criar executável
├── pyproject.toml           # Dependências do projeto
├── README.md                # Documentação do projeto
├── LICENSE                  # Licença do projeto
└── .gitignore               # Arquivos a serem ignorados pelo Git
```

## 📊 Formato do Log

Os logs são salvos em arquivos de texto com o seguinte formato:
```
[YYYY-MM-DD HH:MM:SS] Host: [endereço] - Ping: [tempo]ms - Status: [status]

```

## 🤝 Contribuindo

Sinta-se à vontade para contribuir com este projeto:

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Faça o Commit de suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Faça o Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Autor

Alefsander - [GitHub](https://github.com/alefsanderribeiro)

## 🔄 Versão

- Versão atual: 0.2.0

## 📞 Suporte

- Abra uma issue neste repositório
- Entre em contato via [email](alefsander.pvh14@gmail.com)

---
⌨️ com ❤️ por [Alefe](https://github.com/alefsanderribeiro)


