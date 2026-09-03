# -*- coding: utf-8 -*-
"""
Controle de uso gratuito e verificação de assinatura ativa.

Mesmo princípio do Tessela: sem servidor. A lista de e-mails com
assinatura ativa mora num arquivo público no GitHub, que este plugin
só LÊ (nunca escreve — quem escreve é o plugin separado "Memorial
Admin", de uso privado).
"""
import hashlib
import json
import time

from qgis.PyQt.QtCore import QSettings, QUrl, QEventLoop, QTimer
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Ajuste esses valores para onde a lista de assinantes realmente mora,
# e para o link de assinatura de verdade na Kiwify.
GITHUB_OWNER = "pedromoreli95"
GITHUB_REPO = "memorial-assinantes"
ASSINANTES_PATH = "assinantes.json"
SUBSCRIBE_URL = "https://pay.kiwify.com.br/fgdo6EK"

SETTINGS_USOS = "memorial/usos_gratuitos"
SETTINGS_EMAIL = "memorial/email"

USOS_GRATUITOS_MAX = 3


def _hash_email(email):
    """
    Transforma o e-mail num hash (SHA-256) antes de comparar ou guardar
    -- assim, o arquivo publico no GitHub nunca guarda o e-mail de
    verdade em texto puro, só essa "impressão digital" irreversível.
    """
    normalizado = (email or "").strip().lower()
    return hashlib.sha256(normalizado.encode("utf-8")).hexdigest()


def usos_restantes():
    usados = QSettings().value(SETTINGS_USOS, 0, type=int)
    return max(0, USOS_GRATUITOS_MAX - usados)


def registrar_uso():
    usados = QSettings().value(SETTINGS_USOS, 0, type=int)
    QSettings().setValue(SETTINGS_USOS, usados + 1)


def email_salvo():
    return QSettings().value(SETTINGS_EMAIL, "")


def salvar_email(email):
    QSettings().setValue(SETTINGS_EMAIL, (email or "").strip().lower())


def verificar_assinatura(email, timeout_ms=15000):
    """
    Retorna True se o e-mail estiver na lista pública de assinantes
    ativos. Em qualquer falha (rede, formato, etc.) retorna False —
    nunca libera por engano só porque não conseguiu confirmar.
    """
    email = (email or "").strip().lower()
    if not email:
        return False
    hash_email = _hash_email(email)

    url = (
        f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/"
        f"{ASSINANTES_PATH}?t={int(time.time())}"
    )
    manager = QNetworkAccessManager()
    request = QNetworkRequest(QUrl(url))

    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    reply = manager.get(request)
    reply.finished.connect(loop.quit)
    timer.start(timeout_ms)
    loop.exec()

    if not reply.isFinished():
        reply.abort()
        reply.deleteLater()
        return False

    if reply.error() != QNetworkReply.NetworkError.NoError:
        reply.deleteLater()
        return False

    try:
        lista = json.loads(bytes(reply.readAll()).decode("utf-8"))
        hashes_assinantes = {str(h).strip().lower() for h in lista}
    except Exception:
        reply.deleteLater()
        return False

    reply.deleteLater()
    return hash_email in hashes_assinantes
