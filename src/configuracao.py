import json
import os

class Configuracao:
    def __init__(self):
        self.CONFIG_FILE = 'config.json'
        self.configuracoes_padrao = {
            'intervalo_ping': 1,
            'max_hosts': 9,
            'tipos_notificacao': ['desktop'],
            # Configurar envio de email
            'email_remetente': None,
            'senha_remetente': None,
            'email_destinatario': None,
            # Configurar envio no Telegram
            'token_bot_telegram': None,
            'chat_id_telegram': None,
            # Configurar envio no SMS
            'account_sid_twilio': None,
            'auth_token_twilio': None,
            'numero_remetente_twilio': None,
            'numero_destinatario_twilio': None,
            # Configurar envio no WhatsApp
            'url_whatsapp': None,
            'token_whatsapp': None,
            'numero_destinatario_whatsapp': None
        }
        self.carregar_configuracoes()

    def carregar_configuracoes(self):
        """Carrega as configurações do arquivo JSON ou cria um novo com configurações padrão"""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Atualiza as configurações com os valores do arquivo, mantendo os padrões se não existirem
                for chave, valor in self.configuracoes_padrao.items():
                    setattr(self, chave, config.get(chave, valor))
                return config
        else:
            # Salva as configurações padrão
            self.salvar_configuracoes(self.configuracoes_padrao)
            # Define as configurações padrão na instância
            for chave, valor in self.configuracoes_padrao.items():
                setattr(self, chave, valor)
            return self.configuracoes_padrao

    def salvar_configuracoes(self, configuracoes):
        """Salva as configurações atuais no arquivo JSON"""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(configuracoes, f, indent=4)

    def configurar(self):
        """Menu principal para configuração dos módulos"""
        try:
            while True:
                print("\n=== Menu de Configuração ===")
                print("1. Configurações de Monitoramento")
                print("2. Configurações de Notificação")
                print("3. Configurações de Log")
                print("4. Sair")
                
                escolha = input("Escolha um módulo para configurar (1-4): ")
                
                if escolha == '1':
                    self.configurar_monitoramento()
                elif escolha == '2':
                    self.configurar_notificacao()
                elif escolha == '3':
                    self.configurar_log()
                elif escolha == '4':
                    print("Saindo do menu de configuração.")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
                    
                    
                # Salva todas as configurações
            self.salvar_configuracoes({
                'intervalo_ping': self.intervalo_ping,
                'max_hosts': self.max_hosts,
                'tipos_notificacao': self.tipos_notificacao,
                # Adicionando as configurações específicas de cada notificação
                'account_sid_twilio': getattr(self, 'account_sid_twilio', None),
                'auth_token_twilio': getattr(self, 'auth_token_twilio', None),
                'numero_remetente_twilio': getattr(self, 'numero_remetente_twilio', None),
                'numero_destinatario_twilio': getattr(self, 'numero_destinatario_twilio', None),
                'email_remetente': getattr(self, 'email_remetente', None),
                'senha_remetente': getattr(self, 'senha_remetente', None),
                'email_destinatario': getattr(self, 'email_destinatario', None),
                'token_bot_telegram': getattr(self, 'token_bot_telegram', None),
                'chat_id_telegram': getattr(self, 'chat_id_telegram', None),
                'url_whatsapp': getattr(self, 'url_whatsapp', None),
                'token_whatsapp': getattr(self, 'token_whatsapp', None),
                'numero_destinatario_whatsapp': getattr(self, 'numero_destinatario_whatsapp', None)
            })

            print("\nNovas configurações:")
            # Filtra e exibe apenas as configurações que foram alteradas
            configuracoes_exibicao = {
                'intervalo_ping': self.intervalo_ping,
                'max_hosts': self.max_hosts,
                'tipos_notificacao': self.tipos_notificacao
            }
            print(json.dumps(configuracoes_exibicao, indent=4))
            
        except ValueError as e:
            print(f"Erro na configuração: {str(e)}")
            print("Usando configurações padrão.")
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            print("Usando configurações padrão.")


    def configurar_monitoramento(self):
        """Configura o monitoramento de hosts"""
        print("\n=== Configuração do Monitoramento ===")
        
        """Configura o intervalo de ping"""
        intervalo_input = input(f"Digite o intervalo de ping em segundos (padrão {self.intervalo_ping}s): ")
        self.intervalo_ping = int(intervalo_input) if intervalo_input else self.intervalo_ping
        
        """Configura o número máximo de hosts a serem monitorados"""
        max_hosts_input = input(f"Digite o número máximo de hosts a serem monitorados (padrão {self.max_hosts}): ")
        self.max_hosts = int(max_hosts_input) if max_hosts_input else self.max_hosts

    def configurar_notificacao(self):
        """Configura as opções de notificação"""
        print("\n=== Configuração de Notificação ===")
        print("Escolha os tipos de notificação (separados por vírgula):")
        print("1. desktop")
        print("2. sms")
        print("3. email")
        print("4. telegram")
        print("5. whatsapp")
        
        opcoes_notificacao = input("\nDigite os números das opções desejadas (padrão: 1): ") or '1'
        
        tipos_notificacao = {
            '1': 'desktop',
            '2': 'sms',
            '3': 'email',
            '4': 'telegram',
            '5': 'whatsapp'
        }
        
        self.tipos_notificacao = [tipos_notificacao[numero] for numero in opcoes_notificacao.split(',') if numero in tipos_notificacao]
        
        if not self.tipos_notificacao:
            self.tipos_notificacao = ['desktop']

        # Executa a configuração para cada tipo de notificação escolhido
        for tipo in self.tipos_notificacao:
            if tipo == 'sms':
                self.configurar_sms()
            elif tipo == 'email':
                self.configurar_email()
            elif tipo == 'telegram':
                self.configurar_telegram()
            elif tipo == 'whatsapp':
                self.configurar_whatsapp()

    def configurar_log(self):
        """Configura as opções de log"""
        print("\n=== Configuração de Log ===")
        nivel_log = input("Digite o nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL): ")
        self.nivel_log = nivel_log
        print(f"Nível de log configurado para: {self.nivel_log}")

    def configurar_sms(self):
        """Configura as opções de SMS (Twilio)"""
        print("Configuração do SMS (Twilio):")
        self.account_sid_twilio = input("Account SID Twilio: ")
        self.auth_token_twilio = input("Auth Token Twilio: ")
        self.numero_remetente_twilio = input("Número remetente Twilio (formato: +1234567890): ")
        self.numero_destinatario_twilio = input("Número destinatário (formato: +1234567890): ")

    def configurar_email(self):
        """Configura as opções de Email"""
        print("Configuração do Email:")
        self.email_remetente = input("Email remetente: ")
        self.senha_remetente = input("Senha do email remetente: ")
        self.email_destinatario = input("Email destinatário: ")

    def configurar_telegram(self):
        """Configura as opções de Telegram"""
        print("Configuração do Telegram:")
        self.token_bot_telegram = input("Token do Bot Telegram: ")
        self.chat_id_telegram = input("Chat ID Telegram: ")

    def configurar_whatsapp(self):
        """Configura as opções de WhatsApp"""
        print("Configuração do WhatsApp:")
        self.url_whatsapp = input("URL da API do WhatsApp (padrão: https://graph.facebook.com/v13.0/YOUR_PHONE_NUMBER_ID/messages): ")
        self.token_whatsapp = input("Token de acesso do WhatsApp: ")
        self.numero_destinatario_whatsapp = input("Número destinatário WhatsApp (formato: 5599993451333): ")
