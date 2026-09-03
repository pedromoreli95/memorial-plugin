# -*- coding: utf-8 -*-
"""Verificacao e instalacao de dependencias Python usadas pelo plugin."""

import importlib
import os
import subprocess
import sys

from qgis.PyQt.QtCore import QThread, pyqtSignal

REQUIRED_PACKAGES = [
    # (nome_import, nome_pip)
    ("pdfplumber", "pdfplumber"),
]


def _find_python_executable():
    """
    No QGIS para Windows, sys.executable costuma apontar para o
    qgis-bin.exe (o proprio QGIS), nao para o Python de verdade -- o
    que faz o "pip install" na verdade tentar abrir outro QGIS com
    argumentos que ele nao entende. sys.exec_prefix, por outro lado,
    aponta para a pasta real do Python embutido, entao usamos ele para
    montar o caminho certo do interpretador.
    """
    candidatos = []

    if sys.platform.startswith("win"):
        candidatos.append(os.path.join(sys.exec_prefix, "python.exe"))
        candidatos.append(os.path.join(sys.exec_prefix, "python3.exe"))
    else:
        candidatos.append(os.path.join(sys.exec_prefix, "bin", "python3"))

    candidatos.append(sys.executable)  # funciona na maioria do Linux/Mac

    for caminho in candidatos:
        if caminho and os.path.isfile(caminho):
            return caminho

    return sys.executable  # ultimo recurso


def check_dependency(import_name):
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def check_all():
    """Retorna lista de (import_name, pip_name, instalado_bool)."""
    resultado = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        resultado.append((import_name, pip_name, check_dependency(import_name)))
    return resultado


def install_dependency(pip_name, log_callback=None):
    """
    Instala um pacote via pip usando o mesmo interpretador Python do QGIS.
    log_callback(str) e chamado com cada linha de saida, se fornecido.
    """
    python_exe = _find_python_executable()
    cmd = [python_exe, "-m", "pip", "install", "--user", pip_name]

    if log_callback:
        log_callback(f"Usando interpretador Python: {python_exe}")
        log_callback(f"Executando: {' '.join(cmd)}")

    try:
        kwargs = {}
        if sys.platform.startswith("win"):
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        processo = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            **kwargs,
        )
        for linha in processo.stdout:
            if log_callback:
                log_callback(linha.rstrip())
        processo.wait()
        return processo.returncode == 0
    except Exception as e:
        if log_callback:
            log_callback(f"Erro ao instalar {pip_name}: {e}")
        return False


class InstallThread(QThread):
    """
    Roda a instalacao do pacote numa thread separada, pra nao travar a
    interface do QGIS enquanto o pip baixa (isso podia levar de
    segundos a mais de um minuto, deixando a tela toda congelada).
    """
    linha_log = pyqtSignal(str)
    concluido = pyqtSignal(str, bool)  # pip_name, sucesso

    def __init__(self, pip_name):
        super().__init__()
        self.pip_name = pip_name

    def run(self):
        ok = install_dependency(self.pip_name, log_callback=self.linha_log.emit)
        self.concluido.emit(self.pip_name, ok)
