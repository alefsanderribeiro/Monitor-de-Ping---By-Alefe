import sys
from cx_Freeze import setup, Executable
import os
from src import __version__

# Adiciona o caminho do diretório src ao sistema
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

build_exe_options = {
    "packages": [
        "os", 
        "sys", 
        "subprocess", 
        "json", 
        "datetime", 
        "time", 
        "platform", 
        "queue", 
        "threading", 
        "smtplib", 
        "email", 
        "requests", 
        "plyer", 
        "twilio"
    ],
    "include_files": [
        "Monitor de Ping.ico",  # Inclua o ícone se estiver na pasta src
    ],
    "excludes": []
}

install_requires = [
]

base = None
if sys.platform == "win32":
    base = "Console"  # Use "Win32GUI" para aplicações sem console

setup(
    name="Monitor de Ping - By: Alefe",
    version=__version__,
    description="Monitoramento de Ping com Histórico",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "src/main.py",
            base=base,
            icon="Monitor de Ping.ico",
            target_name="Monitor de Ping.exe"
        )
    ],
    install_requires=install_requires
)
