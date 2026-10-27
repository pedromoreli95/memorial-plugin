# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtCore import Qt

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
    QToolButton,
    QScrollArea,
)
from qgis.PyQt.QtGui import QIcon, QFont

from qgis.core import (
    QgsProject,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)

from .extractor import extrair_vertices, auto_extract_vertices, build_regex
from . import deps


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

QLabel#tituloEtapa {
    color: #1f6b47;
    font-size: 17px;
    font-weight: bold;
}

QPushButton:disabled {
    background-color: #cbd5cf;
    color: #68776e;
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
        self.setWindowTitle("memorial_plugin")
        self.resize(760, 680)
        self.setStyleSheet(QSS)

        icon_path = os.path.join(PLUGIN_DIR, "icon.png")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._pontos_extraidos = []
        self._dados_extraidos = []

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 12, 12, 12)
        layout_principal.setSpacing(8)

        titulo = QLabel("memorial_plugin")
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

        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)

        self._montar_aba_configurar()
        self._montar_aba_resultado()
        self._montar_aba_dependencias()
        for widget in (self.edit_pdf_path, self.edit_rotulo_norte, self.edit_rotulo_leste,
                       self.edit_prefixo_vertice):
            widget.textChanged.connect(self._invalidar_previa)
        for widget in (self.combo_ordem, self.spin_inicio_vertice, self.spin_casas_decimais):
            widget.currentIndexChanged.connect(self._invalidar_previa) if isinstance(widget, QComboBox) else widget.valueChanged.connect(self._invalidar_previa)
        self.radio_automatico.toggled.connect(self._invalidar_previa)
        self.check_manter_casas_originais.toggled.connect(self._invalidar_previa)

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
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("1  ·  Escolha o memorial")
        titulo.setObjectName("tituloEtapa")
        layout.addWidget(titulo)
        ajuda = QLabel("Selecione o PDF e veja as coordenadas antes de inserir na camada.")
        ajuda.setWordWrap(True)
        ajuda.setObjectName("textoAjuda")
        layout.addWidget(ajuda)

        linha_pdf = QHBoxLayout()
        self.edit_pdf_path = QLineEdit()
        self.edit_pdf_path.setPlaceholderText("Selecione um arquivo PDF")
        linha_pdf.addWidget(self.edit_pdf_path, 1)
        btn_pdf = QPushButton("Escolher PDF")
        btn_pdf.setObjectName("botaoSecundario")
        btn_pdf.setIcon(self._icone(QStyle.StandardPixmap.SP_DialogOpenButton))
        btn_pdf.clicked.connect(self._selecionar_pdf)
        linha_pdf.addWidget(btn_pdf)
        layout.addLayout(linha_pdf)

        nota = QLabel("O PDF é processado no seu computador. Coordenadas repetidas são preservadas.")
        nota.setWordWrap(True)
        nota.setObjectName("textoAjuda")
        layout.addWidget(nota)

        self.btn_opcoes = QToolButton()
        self.btn_opcoes.setText("Opções de extração")
        self.btn_opcoes.setCheckable(True)
        self.btn_opcoes.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_opcoes.setArrowType(Qt.ArrowType.RightArrow)
        layout.addWidget(self.btn_opcoes, 0, Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        opcoes = QWidget()
        detalhes = QVBoxLayout(opcoes)
        detalhes.setContentsMargins(0, 0, 0, 0)
        self.radio_automatico = QRadioButton("Identificar coordenadas automaticamente")
        self.radio_manual = QRadioButton("Informar rótulos e ordem manualmente")
        self.radio_automatico.setChecked(True)
        self.grupo_modo = QButtonGroup(self)
        self.grupo_modo.addButton(self.radio_automatico)
        self.grupo_modo.addButton(self.radio_manual)
        detalhes.addWidget(self.radio_automatico)
        detalhes.addWidget(self.radio_manual)

        self.grp_padrao = QGroupBox("Rótulos no PDF")
        form_padrao = QFormLayout(self.grp_padrao)
        self.edit_rotulo_norte = QLineEdit("N")
        self.edit_rotulo_leste = QLineEdit("E")
        self.combo_ordem = QComboBox()
        self.combo_ordem.addItem("Norte antes de Leste", "N_FIRST")
        self.combo_ordem.addItem("Leste antes de Norte", "E_FIRST")
        form_padrao.addRow("Norte / Y:", self.edit_rotulo_norte)
        form_padrao.addRow("Leste / X:", self.edit_rotulo_leste)
        form_padrao.addRow("Ordem:", self.combo_ordem)
        self.label_preview_regex = QLabel()
        self.label_preview_regex.setObjectName("previewRegex")
        self.label_preview_regex.setWordWrap(True)
        form_padrao.addRow(self.label_preview_regex)
        detalhes.addWidget(self.grp_padrao)

        grupo_saida = QGroupBox("Nomes e precisão")
        form_saida = QFormLayout(grupo_saida)
        self.edit_prefixo_vertice = QLineEdit("P")
        self.spin_inicio_vertice = QSpinBox()
        self.spin_inicio_vertice.setRange(0, 999999)
        self.spin_casas_decimais = QSpinBox()
        self.spin_casas_decimais.setRange(0, 8)
        self.spin_casas_decimais.setValue(2)
        self.check_manter_casas_originais = QCheckBox("Não arredondar coordenadas")
        self.check_manter_casas_originais.setChecked(True)
        self.spin_casas_decimais.setEnabled(False)
        self.check_manter_casas_originais.toggled.connect(self.spin_casas_decimais.setDisabled)
        form_saida.addRow("Prefixo dos vértices:", self.edit_prefixo_vertice)
        form_saida.addRow("Número inicial:", self.spin_inicio_vertice)
        form_saida.addRow(self.check_manter_casas_originais)
        form_saida.addRow("Casas decimais ao arredondar:", self.spin_casas_decimais)
        detalhes.addWidget(grupo_saida)
        detalhes.addStretch()
        scroll.setWidget(opcoes)
        scroll.hide()
        self.btn_opcoes.toggled.connect(scroll.setVisible)
        self.btn_opcoes.toggled.connect(lambda aberto: self.btn_opcoes.setArrowType(
            Qt.ArrowType.DownArrow if aberto else Qt.ArrowType.RightArrow))
        layout.addWidget(scroll, 1)
        layout.addStretch()

        btn_extrair = QPushButton("Ler PDF e mostrar prévia  →")
        btn_extrair.clicked.connect(self._extrair_vertices)
        layout.addWidget(btn_extrair)
        self.tabs.addTab(aba, "1  Arquivo")
        self.radio_automatico.toggled.connect(self._atualizar_modo_deteccao)
        for widget in (self.edit_rotulo_norte, self.edit_rotulo_leste):
            widget.textChanged.connect(self._atualizar_preview_regex)
        self.combo_ordem.currentIndexChanged.connect(self._atualizar_preview_regex)
        self._atualizar_preview_regex()
        self._atualizar_modo_deteccao()

    def _montar_aba_resultado(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(7)
        layout.setContentsMargins(10, 10, 10, 10)

        titulo = QLabel("2  ·  Confira e importe")
        titulo.setObjectName("tituloEtapa")
        layout.addWidget(titulo)
        self.label_contagem = QLabel("Leia um PDF para ver os vértices aqui.")
        self.label_contagem.setObjectName("textoAjuda")
        self.label_contagem.setWordWrap(True)
        layout.addWidget(self.label_contagem)

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

        destino = QGroupBox("Camada de destino")
        layout_destino = QVBoxLayout(destino)
        linha_camada = QHBoxLayout()
        self.combo_camadas = QComboBox()
        self._popular_camadas_pontos()
        linha_camada.addWidget(self.combo_camadas, 1)
        atualizar = QPushButton("Atualizar")
        atualizar.setObjectName("botaoSecundario")
        atualizar.clicked.connect(self._popular_camadas_pontos)
        linha_camada.addWidget(atualizar)
        layout_destino.addLayout(linha_camada)
        ajuda = QLabel("Escolha uma camada de pontos com o mesmo sistema de coordenadas do PDF. "
                       "Os nomes são gravados no primeiro campo de texto disponível.")
        ajuda.setObjectName("textoAjuda")
        ajuda.setWordWrap(True)
        layout_destino.addWidget(ajuda)
        layout.addWidget(destino)
        self.btn_inserir = QPushButton("Inserir vértices na camada")
        self.btn_inserir.setEnabled(False)
        self.btn_inserir.clicked.connect(self._inserir_vertices)
        layout.addWidget(self.btn_inserir)
        dica = QLabel("Confira a prévia e depois salve as edições da camada no QGIS.")
        dica.setObjectName("textoAjuda")
        dica.setWordWrap(True)
        layout.addWidget(dica)
        btn_calcular_coords = QPushButton("Opcional: preencher campos coord_x e coord_y")
        btn_calcular_coords.setObjectName("botaoSecundario")
        btn_calcular_coords.setToolTip("Cria ou atualiza os campos para todos os pontos da camada.")
        btn_calcular_coords.clicked.connect(self._gerar_colunas_coordenadas)
        layout.addWidget(btn_calcular_coords)
        self.log_importacao = QPlainTextEdit()
        self.log_importacao.setReadOnly(True)
        self.log_importacao.setMaximumHeight(90)
        self.log_importacao.hide()
        btn_log = QToolButton()
        btn_log.setText("Mostrar registro de eventos")
        btn_log.setCheckable(True)
        btn_log.toggled.connect(self.log_importacao.setVisible)
        layout.addWidget(btn_log)
        layout.addWidget(self.log_importacao)

        self.tabs.addTab(aba, "2  Prévia e importação")

    def _popular_camadas_pontos(self):
        selecionada = self.combo_camadas.currentData()
        self.combo_camadas.clear()
        for layer in QgsProject.instance().mapLayers().values():
            try:
                if layer.type() == layer.VectorLayer and layer.geometryType() == QgsWkbTypes.PointGeometry:
                    self.combo_camadas.addItem(layer.name(), layer.id())
            except Exception:  # nosec B112 - so pula camadas que nao respondem geometryType()
                continue
        indice = self.combo_camadas.findData(selecionada) if selecionada else -1
        if indice >= 0:
            self.combo_camadas.setCurrentIndex(indice)

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

    def _invalidar_previa(self, *_):
        # Alterar o arquivo ou as opções exige uma nova extração.
        self._pontos_extraidos = []
        self._dados_extraidos = []
        self._preencher_tabela_previa([])
        self.label_resultado_deteccao.clear()
        self.label_contagem.setText("Leia um PDF para ver os vértices aqui.")
        self.btn_inserir.setEnabled(False)

    def _extrair_vertices(self):
        self._invalidar_previa()
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
        self.label_contagem.setText(f"{len(dados)} vértice(s) encontrados. Confira a sequência e as coordenadas.")
        self.btn_inserir.setEnabled(bool(dados))
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

        if not camada.isEditable() and not camada.startEditing():
            QMessageBox.critical(self, "Erro", "Não foi possível iniciar a edição da camada.")
            return

        novas_feicoes = []
        for nome_vertice, easting, northing in self._dados_extraidos:
            feicao = QgsFeature(camada.fields())
            feicao.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(easting, northing)))
            from qgis.PyQt.QtCore import QVariant
            for campo in camada.fields():
                if campo.type() == QVariant.String:
                    feicao.setAttribute(campo.name(), nome_vertice)
                    break
            novas_feicoes.append(feicao)

        if not camada.addFeatures(novas_feicoes):
            QMessageBox.critical(self, "Erro", "Não foi possível inserir os vértices na camada.")
            return
        camada.updateExtents()
        self.iface.mapCanvas().refresh()

        self._log(f"-> {len(novas_feicoes)} pontos inseridos na camada '{camada.name()}'.")
        QMessageBox.information(
            self, "Concluido", f"{len(novas_feicoes)} vértices inseridos. Salve as edições da camada no QGIS."
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
        if not camada.isEditable() and not camada.startEditing():
            QMessageBox.critical(self, "Erro", "Não foi possível iniciar a edição da camada.")
            return

        for nome in ("coord_x", "coord_y"):
            if nome not in campos_existentes and not camada.addAttribute(QgsField(nome, tipo_double)):
                QMessageBox.critical(self, "Erro", f"Não foi possível criar o campo {nome}.")
                return
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
            if not camada.changeAttributeValue(feicao.id(), idx_x, valor_x) or not camada.changeAttributeValue(feicao.id(), idx_y, valor_y):
                QMessageBox.critical(self, "Erro", "Não foi possível preencher as coordenadas. Confira as edições da camada.")
                return
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
