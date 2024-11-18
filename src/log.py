from datetime import datetime
import os
import queue
import threading

class GerenciadorLog:
    _instances = {}  # Dicionário para armazenar instâncias únicas por host
    
    @classmethod
    def get_instance(cls, host=None):
        """Implementa o padrão Singleton por host"""
        if host not in cls._instances:
            cls._instances[host] = cls(host)
        return cls._instances[host]
    
    def __init__(self, host=None):
        self.host = host
        self.log_queue = queue.Queue()
        self.running = True
        self._criar_diretorio_logs()
        self.log_file = self._criar_arquivo_log()
        # Inicia o thread para salvar logs
        self.log_thread = threading.Thread(target=self.salvar_logs, daemon=True)
        self.log_thread.start()
        
    def _criar_diretorio_logs(self):
        """Cria o diretório de logs se não existir"""
        os.makedirs('logs', exist_ok=True)
        
    def _criar_arquivo_log(self):
        """Cria o nome do arquivo de log baseado no host"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self.host:
            return f"logs/log_{self.host}_{timestamp}.txt"
        return f"logs/ping_multi_log_{timestamp}.txt"
        
    def registrar_log(self, log_entry):
        """Adiciona uma entrada de log à fila"""
        self.log_queue.put(log_entry)
        
    def registrar_log_notificacao(self, resultados_notificacao):
        """Registra os resultados das tentativas de notificação"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for tipo, sucesso in resultados_notificacao.items():
            # TODO: Foi feito pra relatar só sucesso. Pois acrescentei um log de aguardando no lugar da "falha"
            # Depois verificar isso para melhorar esse log, caso ocorre mesmo uma falha
            #status = "Sucesso" if sucesso else "Falha"
            if sucesso == True:
                status = "Sucesso"
                self.registrar_log({
                    'timestamp': timestamp,
                    'host': self.host,
                    'tipo_notificacao': tipo,
                    'status': 'Sucesso'
                })
            
    def salvar_logs(self):
        """Salva os logs em arquivo"""
        while self.running:
            try:
                log_entry = self.log_queue.get(timeout=1)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    if 'tipo' in log_entry:
                        if log_entry['tipo'] == 'erro_notificacao':
                            f.write(f"[{log_entry['timestamp']}] ERRO {log_entry['servico']}: "
                                   f"{log_entry['mensagem']}\n")
                        elif log_entry['tipo'] == 'aguardando_intervalo':
                            f.write(f"[{log_entry['timestamp']}] Host: {log_entry['host']} - "
                                   f"Notificação {log_entry['servico']}: Aguardando "
                                   f"({int(log_entry['tempo_restante'])}s restantes)\n")
                    elif 'tipo_notificacao' in log_entry:
                        f.write(f"[{log_entry['timestamp']}] Host: {log_entry['host']} - "
                               f"Notificação {log_entry['tipo_notificacao']}: {log_entry['status']}\n")
                    else:
                        f.write(f"[{log_entry['timestamp']}] Host: {log_entry['host']} - "
                               f"Ping: {log_entry['ping']}ms - Status: {log_entry['status']}\n")
            except queue.Empty:
                continue
                
    def parar(self):
        """Para o gerenciador de logs"""
        self.running = False
        if self.log_thread.is_alive():
            self.log_thread.join()
