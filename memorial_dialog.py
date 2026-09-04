# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtCore import QUrl, Qt

from qgis.PyQt.QtWidgets import (
    QDialog,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QPlainTextEdit,
    QMessageBox,
    QCheckBox,
    QWidget,
    QStyle,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
)
from qgis.PyQt.QtGui import QIcon, QFont, QDesktopServices

from qgis.core import (
    QgsProject,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)

from .extractor import extrair_vertices, auto_extract_vertices, build_regex
from . import deps
from . import licensing


PLUGIN_DIR = os.path.dirname(__file__)

QSS = """
QDialog {
    background-color: #f4f6f5;
}

QTabWidget::pane {
    border: 1px solid #d0d7d4;
    border-radius: 6px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: #e6ebe9;
    color: #2f4a3d;
    padding: 8px 18px;
    border: 1px solid #d0d7d4;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #23583f;
}

QGroupBox {
    font-weight: 600;
    color: #23583f;
    border: 1px solid #d5ddd9;
    border-radius: 8px;
    margin-top: 7px;
    padding-top: 5px;
    background-color: #fbfdfc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #1f6b47;
}

QLabel {
    color: #2b2b2b;
}

QLabel#previewRegex {
    color: #6b7570;
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 4px 2px;
}

QLineEdit, QComboBox, QSpinBox {
    border: 1px solid #c6cfca;
    border-radius: 5px;
    padding: 3px 6px;
    background: #ffffff;
    selection-background-color: #a9d8bf;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #2f8a5b;
}

QPushButton {
    background-color: #2f8a5b;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #256e48;
}

QPushButton:pressed {
    background-color: #1c5636;
}

QPushButton#botaoSecundario {
    background-color: #edf2ef;
    color: #23583f;
    border: 1px solid #c6cfca;
}

QPushButton#botaoSecundario:hover {
    background-color: #dfe8e2;
}

QPlainTextEdit {
    border: 1px solid #d5ddd9;
    border-radius: 6px;
    background-color: #0f1a14;
    color: #d7ecdf;
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 6px;
}

QCheckBox {
    spacing: 6px;
}

QFrame#separador {
    background-color: #d5ddd9;
    max-height: 1px;
    min-height: 1px;
}

QLabel#confiancaAlta {
    color: #1c8a4c;
    font-weight: 600;
    padding: 4px 2px;
}

QLabel#confiancaMedia {
    color: #b98a12;
    font-weight: 600;
    padding: 4px 2px;
}

QLabel#confiancaBaixa {
    color: #c0392b;
    font-weight: 600;
    padding: 4px 2px;
}

QLabel#textoAjuda {
    color: #6b7570;
    font-size: 11px;
    padding: 0 2px;
}

QLabel#explicacaoModo {
    color: #6b7570;
    font-size: 11px;
    padding: 2px 2px 2px 22px;
}

QTableWidget {
    border: 1px solid #d5ddd9;
    border-radius: 6px;
    background-color: #ffffff;
    gridline-color: #eaeeec;
}

QHeaderView::section {
    background-color: #e6ebe9;
    color: #23583f;
    padding: 4px;
    border: none;
    font-weight: 600;
}

QFrame#faixaStatus_livre {
    background-color: #fff4e0;
    border: 1px solid #e8c98a;
    border-radius: 8px;
}
QFrame#faixaStatus_livre QLabel {
    color: #8a6416;
    font-weight: 600;
    font-size: 12px;
}

QFrame#faixaStatus_ativo {
    background-color: #e7f5ec;
    border: 1px solid #a9d8bf;
    border-radius: 8px;
}
QFrame#faixaStatus_ativo QLabel {
    color: #1c8a4c;
    font-weight: 600;
    font-size: 12px;
}

QFrame#faixaStatus_bloqueado {
    background-color: #fdeceb;
    border: 1px solid #f0b8ae;
    border-radius: 8px;
}
QFrame#faixaStatus_bloqueado QLabel {
    color: #c0392b;
    font-weight: 600;
    font-size: 12px;
}

QPushButton#botaoAssinar {
    background-color: #c9922e;
}
QPushButton#botaoAssinar:hover {
    background-color: #a97a22;
}
"""


class MemorialDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Importador de Memorial Descritivo")
        self.resize(640, 600)
        self.setStyleSheet(QSS)

        icon_path = os.path.join(PLUGIN_DIR, "icon.png")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._pontos_extraidos = []
        self._dados_extraidos = []

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 12, 12, 12)
        layout_principal.setSpacing(8)

        titulo = QLabel("Importador de Memorial Descritivo")
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(12)
        fonte_titulo.setBold(True)
        titulo.setFont(fonte_titulo)
        titulo.setStyleSheet("color: #1f6b47;")
        layout_principal.addWidget(titulo)

        subtitulo = QLabel(
            "Extraia vertices de coordenadas de arquivos PDF e importe-os "
            "diretamente para uma camada de pontos do QGIS."
        )
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("color: #6b7570; font-size: 11px;")
        layout_principal.addWidget(subtitulo)

        # --- Faixa de status: usos gratis / assinatura, sempre visivel ---
        self.faixa_status = QFrame()
        self.faixa_status.setObjectName("faixaStatus")
        layout_faixa = QHBoxLayout(self.faixa_status)
        layout_faixa.setContentsMargins(12, 8, 10, 8)
        layout_faixa.setSpacing(10)

        self.label_status_assinatura = QLabel("")
        self.label_status_assinatura.setWordWrap(True)
        layout_faixa.addWidget(self.label_status_assinatura, 1)

        self.btn_assinar = QPushButton("Assinar agora")
        self.btn_assinar.setObjectName("botaoAssinar")
        self.btn_assinar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_assinar.setToolTip(
            "Importante: use o mesmo e-mail no pagamento e quando o plugin pedir depois."
        )
        self.btn_assinar.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(licensing.SUBSCRIBE_URL))
        )
        layout_faixa.addWidget(self.btn_assinar, 0)

        layout_principal.addWidget(self.faixa_status)
        self._atualizar_status_assinatura()

        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)

        self._montar_aba_configurar()
        self._montar_aba_resultado()
        self._montar_aba_dependencias()

        self._avisar_dependencia_ausente()

    def _avisar_dependencia_ausente(self):
        """
        Se a dependência ainda não estiver instalada, avisa assim que o
        plugin abre (em vez do usuário só descobrir na hora de extrair).
        Uma vez instalada, esse aviso para de aparecer sozinho.
        """
        if self._verificar_dependencias():
            return

        resposta = QMessageBox.question(
            self,
            "Instalar dependência",
            "Este plugin precisa do pacote 'pdfplumber' (usado só pra ler o "
            "texto do PDF) e ele ainda não está instalado.\n\n"
            "Quer instalar agora? É rápido e só acontece uma vez.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self.tabs.setCurrentIndex(2)  # aba "Dependências"
            self._instalar_dependencias()

    def _icone(self, standard_pixmap):
        return self.style().standardIcon(standard_pixmap)

    def _separador(self):
        linha = QFrame()
        linha.setObjectName("separador")
        linha.setFrameShape(QFrame.Shape.HLine)
        return linha

    # ------------------------------------------------------------------
    # ABA 1: IMPORTACAO
    # ------------------------------------------------------------------
    def _montar_aba_configurar(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(7)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Camada de destino ---
        grp_camada = QGroupBox("Camada de pontos de destino")
        layout_camada = QVBoxLayout()
        layout_camada.setSpacing(4)

        form_camada = QFormLayout()
        form_camada.setSpacing(6)
        self.combo_camadas = QComboBox()
        self._popular_camadas_pontos()
        btn_atualizar_camadas = QPushButton("Atualizar lista")
        btn_atualizar_camadas.setObjectName("botaoSecundario")
        btn_atualizar_camadas.setIcon(self._icone(QStyle.StandardPixmap.SP_BrowserReload))
        btn_atualizar_camadas.clicked.connect(self._popular_camadas_pontos)
        linha_camada = QHBoxLayout()
        linha_camada.addWidget(self.combo_camadas)
        linha_camada.addWidget(btn_atualizar_camadas)
        form_camada.addRow("Camada (qualquer nome):", linha_camada)
        layout_camada.addLayout(form_camada)

        ajuda_camada = QLabel(
            "A camada precisa já existir e ter pelo menos uma coluna (campo de texto) "
            "criada — pode estar vazia, sem nenhum ponto ainda. O nome de cada vértice "
            "(P0, P1...) é gravado automaticamente na primeira coluna que a camada tiver."
        )
        ajuda_camada.setObjectName("textoAjuda")
        ajuda_camada.setWordWrap(True)
        layout_camada.addWidget(ajuda_camada)

        grp_camada.setLayout(layout_camada)
        layout.addWidget(grp_camada)

        # --- Caminho do PDF ---
        grp_pdf = QGroupBox("Arquivo do memorial descritivo (PDF)")
        form_pdf = QFormLayout()
        form_pdf.setSpacing(6)
        self.edit_pdf_path = QLineEdit()
        self.edit_pdf_path.setPlaceholderText("Selecione o arquivo PDF do memorial...")
        btn_procurar_pdf = QPushButton("Procurar...")
        btn_procurar_pdf.setObjectName("botaoSecundario")
        btn_procurar_pdf.setIcon(self._icone(QStyle.StandardPixmap.SP_DialogOpenButton))
        btn_procurar_pdf.clicked.connect(self._selecionar_pdf)
        linha_pdf = QHBoxLayout()
        linha_pdf.addWidget(self.edit_pdf_path)
        linha_pdf.addWidget(btn_procurar_pdf)
        form_pdf.addRow("Caminho do PDF:", linha_pdf)
        grp_pdf.setLayout(form_pdf)
        layout.addWidget(grp_pdf)

        nota_privacidade = QLabel(
            "🔒 Seu PDF e as coordenadas extraídas ficam só no seu computador — "
            "nada disso é enviado para a internet em nenhuma etapa."
        )
        nota_privacidade.setWordWrap(True)
        nota_privacidade.setStyleSheet("color: #1f6b47; font-size: 11px; font-weight: 600; padding: 2px 2px 4px 2px;")
        layout.addWidget(nota_privacidade)

        # --- Modo de deteccao: automatico (padrao) ou manual ---
        grp_modo = QGroupBox("Como identificar as coordenadas no PDF")
        layout_modo = QVBoxLayout()
        layout_modo.setSpacing(3)

        self.radio_automatico = QRadioButton("Detecção automática (recomendado)")
        self.radio_manual = QRadioButton("Configurar manualmente")
        self.radio_automatico.setChecked(True)
        self.grupo_modo = QButtonGroup(self)
        self.grupo_modo.addButton(self.radio_automatico)
        self.grupo_modo.addButton(self.radio_manual)

        explicacao_auto = QLabel(
            "Testa sozinho os rótulos mais comuns e a grandeza típica de UTM no Brasil "
            "pra identificar Norte/Leste, mesmo com ordem invertida."
        )
        explicacao_auto.setObjectName("explicacaoModo")
        explicacao_auto.setWordWrap(True)

        layout_modo.addWidget(self.radio_automatico)
        layout_modo.addWidget(explicacao_auto)
        layout_modo.addWidget(self.radio_manual)
        grp_modo.setLayout(layout_modo)
        layout.addWidget(grp_modo)

        self.radio_automatico.toggled.connect(self._atualizar_modo_deteccao)

        # --- Configuracao do padrao de coordenadas (so aparece no modo manual) ---
        self.grp_padrao = QGroupBox("Padrão de representação das coordenadas")
        form_padrao = QFormLayout()
        form_padrao.setSpacing(6)

        self.edit_rotulo_norte = QLineEdit("N")
        self.edit_rotulo_norte.setPlaceholderText("Ex.: N, Y, Y=")
        form_padrao.addRow("Rótulo do Norte/Y:", self.edit_rotulo_norte)

        self.edit_rotulo_leste = QLineEdit("E")
        self.edit_rotulo_leste.setPlaceholderText("Ex.: E, X, X=")
        form_padrao.addRow("Rótulo do Leste/X:", self.edit_rotulo_leste)

        self.combo_ordem = QComboBox()
        self.combo_ordem.addItem("Norte/Y aparece primeiro (N ... E)", "N_FIRST")
        self.combo_ordem.addItem("Leste/X aparece primeiro (E ... N)", "E_FIRST")
        form_padrao.addRow("Ordem no texto:", self.combo_ordem)

        self.spin_casas_decimais = QSpinBox()
        self.spin_casas_decimais.setRange(0, 8)
        self.spin_casas_decimais.setValue(2)
        self.check_manter_casas_originais = QCheckBox(
            "Manter as casas decimais originais do PDF (não arredondar)"
        )
        self.check_manter_casas_originais.stateChanged.connect(
            lambda _: self.spin_casas_decimais.setDisabled(
                self.check_manter_casas_originais.isChecked()
            )
        )
        linha_casas = QHBoxLayout()
        linha_casas.addWidget(self.spin_casas_decimais)
        linha_casas.addWidget(self.check_manter_casas_originais)
        form_padrao.addRow("Casas decimais desejadas:", linha_casas)

        self.label_preview_regex = QLabel("Padrão (regex) gerado: -")
        self.label_preview_regex.setObjectName("previewRegex")
        self.label_preview_regex.setWordWrap(True)
        form_padrao.addRow(self.label_preview_regex)

        self.grp_padrao.setLayout(form_padrao)
        layout.addWidget(self.grp_padrao)

        for widget in (self.edit_rotulo_norte, self.edit_rotulo_leste):
            widget.textChanged.connect(self._atualizar_preview_regex)
        self.combo_ordem.currentIndexChanged.connect(self._atualizar_preview_regex)
        self._atualizar_preview_regex()

        # --- Nomenclatura dos vertices ---
        grp_vertices = QGroupBox("Nomenclatura dos vértices")
        layout_vertices = QVBoxLayout()
        layout_vertices.setSpacing(4)

        form_vertices = QFormLayout()
        form_vertices.setSpacing(6)
        self.edit_prefixo_vertice = QLineEdit("P")
        self.edit_prefixo_vertice.setPlaceholderText("Ex.: P, V, VERT-")
        form_vertices.addRow("Prefixo (ex.: P -> P0, P1...):", self.edit_prefixo_vertice)

        self.spin_inicio_vertice = QSpinBox()
        self.spin_inicio_vertice.setRange(0, 999)
        self.spin_inicio_vertice.setValue(0)
        form_vertices.addRow("Número inicial:", self.spin_inicio_vertice)
        layout_vertices.addLayout(form_vertices)

        ajuda_vertices = QLabel(
            "Esse nome (P0, P1...) é o que vai ser gravado na coluna da camada, "
            "conforme explicado acima."
        )
        ajuda_vertices.setObjectName("textoAjuda")
        ajuda_vertices.setWordWrap(True)
        layout_vertices.addWidget(ajuda_vertices)

        grp_vertices.setLayout(layout_vertices)
        layout.addWidget(grp_vertices)

        layout.addStretch()

        btn_extrair = QPushButton("  1. Extrair vértices do PDF")
        btn_extrair.setIcon(self._icone(QStyle.StandardPixmap.SP_FileDialogContentsView))
        btn_extrair.clicked.connect(self._extrair_vertices)
        layout.addWidget(btn_extrair)

        self.tabs.addTab(aba, "Configurar")
        self._atualizar_modo_deteccao()

    def _montar_aba_resultado(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(7)
        layout.setContentsMargins(10, 10, 10, 10)

        instrucao = QLabel(
            "Depois de clicar em \"1. Extrair vértices do PDF\", na aba Configurar, "
            "o resultado aparece aqui."
        )
        instrucao.setObjectName("textoAjuda")
        instrucao.setWordWrap(True)
        layout.addWidget(instrucao)

        self.label_resultado_deteccao = QLabel("")
        self.label_resultado_deteccao.setWordWrap(True)
        layout.addWidget(self.label_resultado_deteccao)

        layout.addWidget(QLabel("Prévia dos vértices extraídos:"))
        self.tabela_previa = QTableWidget(0, 3)
        self.tabela_previa.setHorizontalHeaderLabels(["Vértice", "Leste (E/X)", "Norte (N/Y)"])
        self.tabela_previa.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_previa.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_previa.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela_previa.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela_previa, 1)

        ajuda_inserir = QLabel(
            "Confira os números acima antes de inserir — depois de gravado na camada, "
            "a correção precisa ser feita manualmente no QGIS."
        )
        ajuda_inserir.setObjectName("textoAjuda")
        ajuda_inserir.setWordWrap(True)
        layout.addWidget(ajuda_inserir)

        linha_botoes = QHBoxLayout()
        linha_botoes.setSpacing(6)
        btn_inserir = QPushButton("  2. Inserir vértices na camada")
        btn_inserir.setIcon(self._icone(QStyle.StandardPixmap.SP_DialogApplyButton))
        btn_inserir.clicked.connect(self._inserir_vertices)
        linha_botoes.addWidget(btn_inserir)
        layout.addLayout(linha_botoes)

        btn_calcular_coords = QPushButton("  3. Gerar colunas de coordenadas reais ($x / $y)")
        btn_calcular_coords.setIcon(self._icone(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        btn_calcular_coords.clicked.connect(self._gerar_colunas_coordenadas)
        layout.addWidget(btn_calcular_coords)

        ajuda_colunas = QLabel(
            "Opcional: cria (ou atualiza) duas colunas coord_x e coord_y na camada, "
            "preenchidas com a coordenada real de cada ponto — útil pra exibir o "
            "valor na tabela de atributos sem precisar abrir a calculadora de campo."
        )
        ajuda_colunas.setObjectName("textoAjuda")
        ajuda_colunas.setWordWrap(True)
        layout.addWidget(ajuda_colunas)

        layout.addWidget(QLabel("Registro de eventos (detalhe técnico):"))
        self.log_importacao = QPlainTextEdit()
        self.log_importacao.setReadOnly(True)
        self.log_importacao.setMaximumHeight(65)
        layout.addWidget(self.log_importacao)

        self.tabs.addTab(aba, "Resultado")

    def _popular_camadas_pontos(self):
        self.combo_camadas.clear()
        for layer in QgsProject.instance().mapLayers().values():
            try:
                if layer.type() == layer.VectorLayer and layer.geometryType() == QgsWkbTypes.PointGeometry:
                    self.combo_camadas.addItem(layer.name(), layer.id())
            except Exception:  # nosec B112 - so pula camadas que nao respondem geometryType()
                continue

    def _selecionar_pdf(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar memorial descritivo (PDF)", "", "PDF (*.pdf)"
        )
        if caminho:
            self.edit_pdf_path.setText(caminho)

    def _atualizar_preview_regex(self):
        try:
            padrao, _ = build_regex(
                self.edit_rotulo_norte.text() or "N",
                self.edit_rotulo_leste.text() or "E",
                self.combo_ordem.currentData() or "N_FIRST",
            )
            self.label_preview_regex.setText(f"Padrao (regex) gerado: {padrao}")
        except Exception as e:
            self.label_preview_regex.setText(f"Padrao (regex) gerado: erro ({e})")

    def _atualizar_status_assinatura(self):
        restantes = licensing.usos_restantes()
        if restantes > 0:
            estado = "livre"
            texto = f"🎁 Você tem {restantes} uso(s) grátis restante(s)."
            mostrar_botao = True
        else:
            email = licensing.email_salvo()
            if email and licensing.verificar_assinatura(email, timeout_ms=6000):
                estado = "ativo"
                texto = f"✓ Assinatura ativa ({email})"
                mostrar_botao = False
            else:
                estado = "bloqueado"
                texto = "🔒 Seus usos grátis acabaram. Assine para continuar usando."
                mostrar_botao = True

        self.label_status_assinatura.setText(texto)
        self.btn_assinar.setVisible(mostrar_botao)

        self.faixa_status.setObjectName(f"faixaStatus_{estado}")
        self.faixa_status.style().unpolish(self.faixa_status)
        self.faixa_status.style().polish(self.faixa_status)

    def _pode_extrair_agora(self):
        """
        Checa o limite de usos gratuitos / assinatura ativa. Retorna
        True se pode seguir com a extração, ou False (já mostrando o
        aviso certo) se não pode.
        """
        if licensing.usos_restantes() > 0:
            licensing.registrar_uso()
            self._atualizar_status_assinatura()
            return True

        email = licensing.email_salvo()
        if not email:
            from qgis.PyQt.QtWidgets import QInputDialog
            email, ok = QInputDialog.getText(
                self,
                "E-mail da assinatura",
                "Seus 3 usos grátis acabaram.\n\n"
                "Digite EXATAMENTE o mesmo e-mail que você usou para pagar na "
                "Kiwify (ou cancele para ver como assinar). Se o e-mail for "
                "diferente do pagamento, não vai encontrar sua assinatura. "
                "Só esse e-mail é enviado para conferência — o PDF e as "
                "coordenadas continuam só no seu computador:",
            )
            if not ok or not email.strip():
                self._oferecer_assinatura()
                return False
            licensing.salvar_email(email)

        self.label_status_assinatura.setText("Verificando assinatura...")
        if licensing.verificar_assinatura(email):
            self._atualizar_status_assinatura()
            return True

        self._atualizar_status_assinatura()
        self._oferecer_assinatura()
        return False

    def _oferecer_assinatura(self):
        resposta = QMessageBox.question(
            self,
            "Assinatura necessária",
            "Não encontrei uma assinatura ativa com esse e-mail.\n\n"
            "Seus 3 usos grátis já foram usados. Para continuar importando "
            "memoriais, é necessário assinar.\n\n"
            "Quer abrir a página de assinatura agora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl(licensing.SUBSCRIBE_URL))

    def _atualizar_modo_deteccao(self):
        manual = self.radio_manual.isChecked()
        self.grp_padrao.setVisible(manual)

    def _log(self, msg):
        self.log_importacao.appendPlainText(str(msg))

    def _preencher_tabela_previa(self, dados):
        self.tabela_previa.setRowCount(len(dados))
        for linha, (nome, easting, northing) in enumerate(dados):
            self.tabela_previa.setItem(linha, 0, QTableWidgetItem(str(nome)))
            self.tabela_previa.setItem(linha, 1, QTableWidgetItem(str(easting)))
            self.tabela_previa.setItem(linha, 2, QTableWidgetItem(str(northing)))

    def _extrair_vertices(self):
        if not self._pode_extrair_agora():
            return

        pdf_path = self.edit_pdf_path.text().strip()
        if not pdf_path or not os.path.isfile(pdf_path):
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo PDF valido.")
            return

        ok_dep, _, instalado = deps.check_all()[0]
        if not instalado:
            QMessageBox.warning(
                self,
                "Dependencia ausente",
                "O pacote 'pdfplumber' nao esta instalado.\n"
                "Va ate a aba 'Dependencias' e instale antes de continuar.",
            )
            return

        decimal_places = (
            None if self.check_manter_casas_originais.isChecked()
            else self.spin_casas_decimais.value()
        )

        if self.radio_automatico.isChecked():
            try:
                resultado = auto_extract_vertices(
                    pdf_path=pdf_path,
                    vertex_prefix=self.edit_prefixo_vertice.text() or "P",
                    vertex_start=self.spin_inicio_vertice.value(),
                    decimal_places=decimal_places,
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro na extração", str(e))
                return

            pontos, dados = resultado['pontos'], resultado['dados']
            confianca = resultado['confianca']
            self._log(resultado['metodo_usado'])

            rotulo_confianca = {
                'alta': ("confiancaAlta", "✓ Alta confiança — "),
                'media': ("confiancaMedia", "⚠ Confiança média, confira a prévia abaixo — "),
                'baixa': ("confiancaBaixa", "⚠ Confiança baixa — considere usar o modo manual — "),
                'nenhuma': ("confiancaBaixa", ""),
            }
            objeto_nome, prefixo = rotulo_confianca.get(confianca, ("confiancaBaixa", ""))
            self.label_resultado_deteccao.setObjectName(objeto_nome)
            self.label_resultado_deteccao.setText(prefixo + resultado['metodo_usado'])
            self.label_resultado_deteccao.style().unpolish(self.label_resultado_deteccao)
            self.label_resultado_deteccao.style().polish(self.label_resultado_deteccao)
        else:
            try:
                pontos, dados, padrao = extrair_vertices(
                    pdf_path=pdf_path,
                    north_label=self.edit_rotulo_norte.text() or "N",
                    east_label=self.edit_rotulo_leste.text() or "E",
                    letter_order=self.combo_ordem.currentData() or "N_FIRST",
                    vertex_prefix=self.edit_prefixo_vertice.text() or "P",
                    vertex_start=self.spin_inicio_vertice.value(),
                    decimal_places=decimal_places,
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro na extração", str(e))
                return

            self._log(f"Padrão usado: {padrao}")
            self.label_resultado_deteccao.setObjectName("")
            self.label_resultado_deteccao.setText(
                "Modo manual — padrão configurado por você usado na extração."
            )
            self.label_resultado_deteccao.style().unpolish(self.label_resultado_deteccao)
            self.label_resultado_deteccao.style().polish(self.label_resultado_deteccao)

        self._pontos_extraidos = pontos
        self._dados_extraidos = dados
        self._preencher_tabela_previa(dados)
        self.tabs.setCurrentIndex(1)  # aba "Resultado"

        self._log(f"{len(dados)} vértices encontrados:")
        for nome, e, n in dados:
            self._log(f"  {nome}: E={e}  N={n}")

        if len(dados) < 3:
            self._log(
                "Aviso: menos de 3 vértices foram encontrados. Verifique o PDF, "
                "ou tente o modo manual configurando o rótulo/ordem corretos."
            )
            QMessageBox.warning(
                self,
                "Poucos vértices encontrados",
                f"Só {len(dados)} vértice(s) foram encontrados neste PDF.\n\n"
                "Isso normalmente significa que o formato de coordenadas não foi "
                "reconhecido. Tente o modo manual e confira o rótulo usado no PDF.",
            )

    def _inserir_vertices(self):
        if not self._dados_extraidos:
            QMessageBox.information(
                self, "Nada a inserir", "Execute a extracao (passo 1) primeiro."
            )
            return

        layer_id = self.combo_camadas.currentData()
        if not layer_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma camada de destino.")
            return

        camada = QgsProject.instance().mapLayer(layer_id)
        if camada is None:
            QMessageBox.warning(self, "Aviso", "Camada nao encontrada. Atualize a lista.")
            return

        if not camada.isEditable():
            camada.startEditing()

        novas_feicoes = []
        for nome_vertice, easting, northing in self._dados_extraidos:
            feicao = QgsFeature(camada.fields())
            feicao.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(easting, northing)))
            if camada.fields().count() > 0:
                # tenta escrever no primeiro campo de texto disponivel
                nome_campo = camada.fields()[0].name()
                feicao.setAttribute(nome_campo, nome_vertice)
            novas_feicoes.append(feicao)

        sucesso, _ = camada.dataProvider().addFeatures(novas_feicoes)
        camada.updateExtents()
        self.iface.mapCanvas().refresh()

        self._log(f"-> {len(novas_feicoes)} pontos inseridos na camada '{camada.name()}'.")
        QMessageBox.information(
            self, "Concluido", f"{len(novas_feicoes)} vertices inseridos com sucesso."
        )

    def _gerar_colunas_coordenadas(self):
        """
        Cria (se necessario) os campos 'coord_x' e 'coord_y' e os preenche
        usando as expressoes nativas do QGIS $x e $y, arredondadas para
        2 casas decimais, exatamente como na calculadora de campo.
        """
        layer_id = self.combo_camadas.currentData()
        if not layer_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma camada de destino.")
            return

        camada = QgsProject.instance().mapLayer(layer_id)
        if camada is None:
            QMessageBox.warning(self, "Aviso", "Camada nao encontrada. Atualize a lista.")
            return

        from qgis.core import QgsField, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils

        try:
            # QGIS 4 / Qt6: tipos de campo via QMetaType
            from qgis.PyQt.QtCore import QMetaType
            tipo_double = QMetaType.Type.Double
        except (ImportError, AttributeError):
            # QGIS 3 / Qt5: fallback para QVariant
            from qgis.PyQt.QtCore import QVariant
            tipo_double = QVariant.Double

        campos_existentes = [f.name() for f in camada.fields()]
        if not camada.isEditable():
            camada.startEditing()

        if "coord_x" not in campos_existentes:
            camada.dataProvider().addAttributes([QgsField("coord_x", tipo_double)])
        if "coord_y" not in campos_existentes:
            camada.dataProvider().addAttributes([QgsField("coord_y", tipo_double)])
        camada.updateFields()

        idx_x = camada.fields().indexOf("coord_x")
        idx_y = camada.fields().indexOf("coord_y")

        expr_x = QgsExpression("round($x, 2)")
        expr_y = QgsExpression("round($y, 2)")

        contexto = QgsExpressionContext()
        contexto.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(camada))

        atualizados = 0
        for feicao in camada.getFeatures():
            contexto.setFeature(feicao)
            valor_x = expr_x.evaluate(contexto)
            valor_y = expr_y.evaluate(contexto)
            camada.changeAttributeValue(feicao.id(), idx_x, valor_x)
            camada.changeAttributeValue(feicao.id(), idx_y, valor_y)
            atualizados += 1

        camada.updateExtents()
        self.iface.mapCanvas().refresh()

        self._log(
            f"-> Colunas 'coord_x' e 'coord_y' preenchidas via $x/$y "
            f"(2 casas decimais) em {atualizados} feicoes."
        )
        QMessageBox.information(
            self,
            "Concluido",
            "Colunas coord_x / coord_y geradas com as expressoes nativas "
            "$x e $y (arredondadas a 2 casas decimais).\n\n"
            "Nao esqueca de salvar as edicoes da camada.",
        )

    # ------------------------------------------------------------------
    # ABA 2: DEPENDENCIAS
    # ------------------------------------------------------------------
    def _montar_aba_dependencias(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(7)
        layout.setContentsMargins(10, 10, 10, 10)

        info = QLabel(
            "Este plugin depende do pacote Python 'pdfplumber' para ler o "
            "conteudo dos arquivos PDF. Verifique e instale abaixo, caso "
            "seja necessario."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #6b7570; font-size: 11px;")
        layout.addWidget(info)

        grp_status = QGroupBox("Status das dependencias")
        layout_status = QVBoxLayout()
        self.label_status_dep = QLabel()
        layout_status.addWidget(self.label_status_dep)
        grp_status.setLayout(layout_status)
        layout.addWidget(grp_status)

        linha_botoes = QHBoxLayout()
        linha_botoes.setSpacing(6)
        self.btn_verificar_dep = QPushButton("  Verificar dependências")
        self.btn_verificar_dep.setObjectName("botaoSecundario")
        self.btn_verificar_dep.setIcon(self._icone(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_verificar_dep.clicked.connect(self._verificar_dependencias)

        self.btn_instalar_dep = QPushButton("  Instalar dependências ausentes")
        self.btn_instalar_dep.setIcon(self._icone(QStyle.StandardPixmap.SP_ArrowDown))
        self.btn_instalar_dep.clicked.connect(self._instalar_dependencias)

        linha_botoes.addWidget(self.btn_verificar_dep)
        linha_botoes.addWidget(self.btn_instalar_dep)
        layout.addLayout(linha_botoes)

        self.progress_dependencias = QProgressBar()
        self.progress_dependencias.setRange(0, 0)  # indeterminado (nao sabemos quanto falta)
        self.progress_dependencias.hide()
        layout.addWidget(self.progress_dependencias)

        layout.addWidget(QLabel("Registro de eventos:"))
        self.log_dependencias = QPlainTextEdit()
        self.log_dependencias.setReadOnly(True)
        layout.addWidget(self.log_dependencias)

        self.tabs.addTab(aba, "Dependências")
        self._verificar_dependencias()

    def _verificar_dependencias(self):
        resultado = deps.check_all()
        linhas = []
        tudo_ok = True
        for import_name, pip_name, instalado in resultado:
            status = "OK - instalado" if instalado else "NÃO instalado"
            if not instalado:
                tudo_ok = False
            linhas.append(f"{pip_name}: {status}")
        self.label_status_dep.setText("\n".join(linhas))
        self.label_status_dep.setStyleSheet(
            "color: #1c8a4c; font-weight: 600;" if tudo_ok else "color: #c0392b; font-weight: 600;"
        )
        return tudo_ok

    def _instalar_dependencias(self):
        resultado = deps.check_all()
        self._fila_instalacao = [pip_name for _, pip_name, instalado in resultado if not instalado]

        if not self._fila_instalacao:
            self.log_dependencias.appendPlainText("Todas as dependências já estão instaladas.")
            return

        self.btn_instalar_dep.setEnabled(False)
        self.btn_verificar_dep.setEnabled(False)
        self.progress_dependencias.show()
        self._instalar_proximo_da_fila()

    def _instalar_proximo_da_fila(self):
        if not self._fila_instalacao:
            self.progress_dependencias.hide()
            self.btn_instalar_dep.setEnabled(True)
            self.btn_verificar_dep.setEnabled(True)
            self._verificar_dependencias()
            return

        pip_name = self._fila_instalacao.pop(0)
        self.log_dependencias.appendPlainText(f"Instalando {pip_name} em segundo plano...")

        self._install_thread = deps.InstallThread(pip_name)
        self._install_thread.linha_log.connect(self.log_dependencias.appendPlainText)
        self._install_thread.concluido.connect(self._on_instalacao_concluida)
        self._install_thread.start()

    def _on_instalacao_concluida(self, pip_name, ok):
        if ok:
            self.log_dependencias.appendPlainText(f"{pip_name} instalado com sucesso.")
        else:
            self.log_dependencias.appendPlainText(
                f"Falha ao instalar {pip_name}. Tente executar o QGIS como "
                "administrador ou instale manualmente pelo OSGeo4W Shell:\n"
                f"  python -m pip install {pip_name}"
            )
        self._instalar_proximo_da_fila()

        self._verificar_dependencias()
