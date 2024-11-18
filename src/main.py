import sys
import os
import threading
import platform
import subprocess
import time
from datetime import datetime
import json
from notificação import configurar_notificacoes
from log import GerenciadorLog
from logo_alefe import Apresentação
from configuracao import Configuracao

# Adiciona o caminho do diretório pai ao sistema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import __version__

# Nome dos arquivos de histórico e configuração
HISTORICO_FILE = 'historico_endereço_ping.json'
CONFIG_FILE = 'config.json'

# Classe para gerenciar o monitoramento de múltiplos hosts
class MonitorHost:
    def __init__(self, host):
        """Inicializa o monitoramento de um host específico."""
        self.host = host
        self.ultimo_ping = None
        self.status = "Iniciando..."
        self.historico = []
        self.falhas = 0
        self.ultima_falha = None
        self.tempo_total_falhas = 0
        self.ultima_notificacao_enviada = None  # Novo atributo para controlar notificações
        
    def adicionar_resultado(self, ping, status):
        """Adiciona um novo resultado de ping e atualiza as estatísticas."""
        self.ultimo_ping = ping
        self.status = status
        tempo_atual = datetime.now()
        
        # Registra o resultado no histórico
        self.historico.append({
            'timestamp': tempo_atual.strftime("%Y-%m-%d %H:%M:%S"),
            'ping': ping,
            'status': status
        })
        
        # Atualiza contagem de falhas e tempo
        if status != "Sucesso":
            self.falhas += 1
            if self.ultima_falha:
                delta = (tempo_atual - self.ultima_falha).total_seconds()
                self.tempo_total_falhas += delta
            self.ultima_falha = tempo_atual
        else:
            self.ultima_falha = None
            
    def deve_notificar(self):
        """Verifica se deve enviar uma nova notificação."""
        return True if self.status != "Sucesso" else False


class MonitorMultiplosHosts:
    def __init__(self):
        """Inicializa o monitoramento de múltiplos hosts."""
        self.hosts = {}
        self.running = False
        self.threads = []
        self.lock = threading.Lock()
        self.historico = self.carregar_historico()
        
        self.config = Configuracao()  # Mantenha a instância da configuração, mas não atualize ainda

    def atualizar_configuracoes(self):
        """Atualiza todas as configurações e recria o notificador."""
        configs = self.config.carregar_configuracoes()
        self.notificador = configurar_notificacoes(configs)
        self.intervalo_ping = self.config.intervalo_ping
        self.max_hosts = self.config.max_hosts
        self.tipos_notificacao = self.config.tipos_notificacao

    def carregar_historico(self):
        """Carrega o histórico de hosts monitorados."""
        if os.path.exists(HISTORICO_FILE):
            try:
                with open(HISTORICO_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def adicionar_ao_historico(self, host):
        """Adiciona um host ao histórico, evitando duplicatas."""
        if host not in self.historico:
            self.historico.insert(0, host)  # Adiciona no início da lista
            if len(self.historico) > 9:  # Mantém apenas os 9 últimos
                self.historico.pop()
        elif host in self.historico:  # Se já existe, move para o topo
            self.historico.remove(host)
            self.historico.insert(0, host)
        self.salvar_historico()  # Salva o histórico

    def salvar_historico(self):
        """Salva o histórico de hosts monitorados."""
        with open(HISTORICO_FILE, 'w') as f:
            json.dump(self.historico, f)

    def adicionar_host(self, hosts):
        """Adiciona um ou mais hosts ao monitoramento."""
        for host in hosts:
            if host not in self.hosts:
                self.hosts[host] = MonitorHost(host)
                print(f"Host {host} adicionado para monitoramento.")
            else:
                print(f"Host {host} já está sendo monitorado.")

    def remover_host(self, host):
        """Remove um host do monitoramento e do histórico."""
        with self.lock:
            if host in self.hosts:
                del self.hosts[host]
                self.historico.remove(host)
                self.salvar_historico()

    def verificar_ping(self, host):
        """Verifica o ping para um host específico."""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        try:
            comando = ['ping', param, '1', host]
            encoding = 'cp1252' if platform.system().lower() == 'windows' else 'utf-8'
            resultado = subprocess.check_output(comando, timeout=5).decode(encoding)
            
            if platform.system().lower() == 'windows':
                if 'tempo=' in resultado:
                    ms = float(resultado.split('tempo=')[1].split('ms')[0].strip())
                    return ms, "Sucesso"
            else:
                if 'time=' in resultado:
                    ms = float(resultado.split('time=')[1].split('ms')[0].strip())
                    return ms, "Sucesso"
                    
            return None, "Timeout"
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except subprocess.CalledProcessError:
            return None, "Falha na conexão"
        except Exception as e:
            return None, f"Erro: {str(e)}"

    def monitor_thread(self, host):
        """Thread para monitorar um host específico."""
        gerenciador_log = GerenciadorLog.get_instance(host)
        
        while self.running:
            ms, status = self.verificar_ping(host)
            
            with self.lock:
                monitor: MonitorHost = self.hosts[host]
                monitor.adicionar_resultado(ms, status)
                
                gerenciador_log.registrar_log({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'host': host,
                    'ping': ms,
                    'status': status
                })
                
                if monitor.deve_notificar():
                    mensagem = f"Falha detectada no host {host}\nStatus: {status}"
                    titulo = f"Alerta de Conexão - {host}"
                    
                    resultados = self.notificador.enviar_notificacao(
                        mensagem=mensagem,
                        titulo=titulo,
                        tipos=self.tipos_notificacao,
                        host=host
                    )
                    
                    gerenciador_log.registrar_log_notificacao(resultados)
            
            time.sleep(self.intervalo_ping)

    def iniciar_monitoramento(self):
        """Inicia o monitoramento de todos os hosts."""
        self.atualizar_configuracoes()  # Mova a atualização de configurações para cá
        self.running = True
        
        for host in list(self.hosts.keys())[:self.max_hosts]:
            thread = threading.Thread(target=self.monitor_thread, args=(host,))
            thread.daemon = True
            self.threads.append(thread)
            thread.start()

    def parar_monitoramento(self):
        """Para o monitoramento de todos os hosts."""
        self.running = False
        for thread in self.threads:
            thread.join()
        self.threads.clear()
        
    def obter_estatisticas(self):
        """Retorna estatísticas de todos os hosts monitorados."""
        estatisticas = {}
        with self.lock:
            for host, monitor in self.hosts.items():
                pings = [h['ping'] for h in monitor.historico if h['ping'] is not None]
                estatisticas[host] = {
                    'último_ping': monitor.ultimo_ping,
                    'status': monitor.status,
                    'média_ping': sum(pings) / len(pings) if pings else 0,
                    'min_ping': min(pings) if pings else 0,
                    'max_ping': max(pings) if pings else 0,
                    'total_falhas': monitor.falhas,
                    'tempo_total_falhas': monitor.tempo_total_falhas,
                    'última_falha': monitor.ultima_falha.strftime("%Y-%m-%d %H:%M:%S") if monitor.ultima_falha else None
                }
        return estatisticas

    def configurar_monitoramento(self):
        """Configura o monitoramento e atualiza o notificador."""
        self.config.configurar()
        self.atualizar_configuracoes()  # Atualiza todas as configurações incluindo o notificador

    def selecionar_host(self):
        """Permite ao usuário selecionar um ou mais hosts do histórico ou digitar novos."""
        historico = self.carregar_historico()
        hosts_selecionados = []  # Lista para armazenar os hosts selecionados

        while True:
            try:
                if historico:
                    print("\nÚltimos endereços pesquisados:")
                    for i, host in enumerate(historico, 1):
                        print(f"{i}. {host}")
                    print("D. Digitar novo endereço")
                    print("C. Configurar o monitor")
                
                    opcao = input("\nEscolha uma opção ou digite os números separados por vírgula): ")

                else:
                    print("D. Digitar novo endereço")
                    print("C. Configurar o monitor")
                
                    opcao = input("\nEscolha uma opção: ")
                    
                if opcao.upper() == "C":
                    self.configurar_monitoramento()  # Chama a nova função de configuração
                elif opcao.upper() == 'D':
                    # Permite ao usuário digitar um novo endereço
                    host = input("\nDigite o endereço para monitorar: ").strip()
                    if host:  # Verifica se o usuário digitou algo
                        self.adicionar_ao_historico(host)  # Adiciona ao histórico
                        hosts_selecionados.append(host)
                    else:
                        print("Você deve digitar um endereço válido.")
                else:
                    # Permite selecionar múltiplos hosts
                    numeros_selecionados = [int(num) for num in opcao.replace(' ', '').split(',') if num.isdigit()]
                    for numero in numeros_selecionados:
                        if 1 <= numero <= len(historico):
                            hosts_selecionados.append(historico[numero - 1])
                        else:
                            print(f"Opção {numero} é inválida!")

                # Se o usuário escolheu hosts, retorna a lista de hosts selecionados
                if hosts_selecionados:
                    return hosts_selecionados

                print("Nenhum host selecionado. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Por favor, digite números válidos.")
        
        # Se não há histórico ou usuário escolheu digitar novo endereço
        host = input("\nDigite o endereço para monitorar (ou pressione Enter para usar 8.8.8.8): ").strip() or "8.8.8.8"
        self.adicionar_ao_historico(host)  # Adiciona ao histórico
        return [host]  # Retorna uma lista com o host


def main():
    """Função principal que inicia o programa."""
    
    print(" By: ".center(120, "—"))
    print(Apresentação())
    print(f" Versão: {__version__}".center(120, "—"))
    print("Seja Bem-vindo ao Monitor de Redes!")
    print("Este programa monitora a conectividade de múltiplos hosts.")
    print("Você pode adicionar, remover e monitorar hosts de sua escolha.")
    print("Também é possível configurar notificações para alertá-lo em caso de falha.")
    print("Pressione Enter para continuar...")
    input()
    
    MonitorMultiplo = MonitorMultiplosHosts()
    # Solicita ao usuário para adicionar hosts para monitoramento
    while True:
        hosts = MonitorMultiplo.selecionar_host()  # Agora retorna uma lista de hosts
        if hosts:
            MonitorMultiplo.adicionar_host(hosts)  # Passa a lista de hosts
            iniciar = input("\nDeseja iniciar o monitoramento? (s/n): ").strip().lower()
            if iniciar.upper() == 'S':
                break
        
    if not MonitorMultiplo.hosts:
        print("Nenhum host foi adicionado para monitoramento. Encerrando.")
        return  # Sai se não houver hosts para monitorar

    print("Hosts selecionados para monitoramento:")
    for host in MonitorMultiplo.hosts.keys():
        print(f"- {host}")

    print("Iniciando monitoramento de múltiplos hosts...")
    print("Pressione Ctrl+C para parar")
    
    try:
        MonitorMultiplo.iniciar_monitoramento()
        
        while True:
            # Exibe estatísticas a cada 5 segundos
            estatisticas = MonitorMultiplo.obter_estatisticas()
            os.system('cls' if platform.system().lower() == 'windows' else 'clear')
            print("\nEstatísticas de Monitoramento:")
            print("-" * 50)
            
            for host, stats in estatisticas.items():
                print(f"\nHost: {host}")
                print(f"Status: {stats['status']}")
                print(f"Último ping: {stats['último_ping']}ms")
                print(f"Média: {stats['média_ping']:.1f}ms")
                print(f"Mín/Máx: {stats['min_ping']:.1f}ms / {stats['max_ping']:.1f}ms")
                print(f"Total de falhas: {stats['total_falhas']}")
                print(f"Tempo total em falha: {stats['tempo_total_falhas']:.1f}s")
                if stats['última_falha']:
                    print(f"Última falha: {stats['última_falha']}")
                print("-" * 30)
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nParando monitoramento...")
        MonitorMultiplo.parar_monitoramento()
        print("Monitoramento finalizado!")
        
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        input("Pressione Enter para sair...")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoramento finalizado!")
