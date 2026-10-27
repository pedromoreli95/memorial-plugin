# -*- coding: utf-8 -*-
"""
Motor de extracao de coordenadas de memoriais descritivos em PDF.

Tres estrategias sao tentadas, da mais confiavel pra menos confiavel:

  1. Tabelas de verdade dentro do PDF (quando o memorial apresenta as
     coordenadas em formato de tabela -- o mais confiavel, porque usa o
     proprio cabecalho da tabela pra saber qual coluna e qual).
  2. Rotulos conhecidos em texto corrido (N/E, Y/X, Norte/Este...),
     testados nas duas ordens possiveis.
  3. Um padrao numerico generico, sem depender de rotulo nenhum, usando
     so a grandeza tipica de coordenadas UTM no Brasil pra filtrar
     ruido (azimutes, distancias, numeros de pagina etc.)

Os rotulos e cabecalhos indicam a ordem das coordenadas. A grandeza
serve para avaliar a confianca e, na ausencia de rotulos, inferir a ordem;
por isso a deteccao generica exige conferencia pelo usuario.
"""

import re
import unicodedata


def _build_number_pattern():
    return r'((?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?))'


def build_regex(north_label, east_label, letter_order, unit_hint=True):
    """
    Monta a regex dinamicamente a partir dos rotulos e da ordem informados.

    north_label / east_label: strings como 'N', 'E', 'Y=', 'X=', 'Y', 'X'
    letter_order: 'N_FIRST' ou 'E_FIRST'
    """
    num = _build_number_pattern()

    n_label_raw = north_label.strip()
    e_label_raw = east_label.strip()

    n_label = re.escape(n_label_raw)
    e_label = re.escape(e_label_raw)

    if n_label_raw.endswith('=') or n_label_raw.endswith(':'):
        sep_n = r'\s*'
    else:
        sep_n = r'\s*[:=]?\s*'

    if e_label_raw.endswith('=') or e_label_raw.endswith(':'):
        sep_e = r'\s*'
    else:
        sep_e = r'\s*[:=]?\s*'

    if unit_hint:
        meio = r'[\s,;]*(?:m\b)?[\s,;]*(?:e|and)?[\s,;]*'
    else:
        meio = r'[\s,;]*'

    if letter_order == 'N_FIRST':
        padrao = rf'{n_label}{sep_n}{num}{meio}{e_label}{sep_e}{num}'
        grupos = ('north', 'east')
    else:
        padrao = rf'{e_label}{sep_e}{num}{meio}{n_label}{sep_n}{num}'
        grupos = ('east', 'north')

    return padrao, grupos


def _parse_number(raw):
    """Converte string numerica (pt-BR ou padrao) para float."""
    raw = str(raw).strip()
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif ',' in raw and '.' not in raw:
        raw = raw.replace(',', '.')
    return float(raw)


def extract_text_from_pdf(pdf_path):
    import pdfplumber
    texto_bruto = ""
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto_bruto += pagina.extract_text() or ""
            texto_bruto += "\n"
    return " ".join(texto_bruto.split())


def _matches_com_nomes(texto, padrao):
    """Associa um identificador explícito de vértice ao par que o segue."""
    anterior = 0
    for match in re.finditer(padrao, texto, flags=re.IGNORECASE):
        trecho = texto[anterior:match.start()]
        nomes = list(re.finditer(
            r"\bv[eé]rtice\s+([\w-]+)\s*,?\s*(?:de\s+)?coordenadas?\s*$",
            trecho, flags=re.IGNORECASE,
        ))
        nome = nomes[-1].group(1) if nomes else None
        yield match.group(1), match.group(2), nome
        anterior = match.end()


def _remover_fechamento_explicito(pares):
    """Omite apenas a referência final ao mesmo vértice e coordenadas iniciais."""
    if len(pares) > 1:
        primeiro, ultimo = pares[0], pares[-1]
        if (primeiro[2] and ultimo[2]
                and primeiro[2].casefold() == ultimo[2].casefold()
                and primeiro[:2] == ultimo[:2]):
            return pares[:-1], True
    return pares, False


def extrair_vertices(
    pdf_path,
    north_label='N',
    east_label='E',
    letter_order='N_FIRST',
    vertex_prefix='P',
    vertex_start=0,
    decimal_places=2,
    remove_consecutive_duplicates=False,
):
    """Extracao manual (modo avancado): usa exatamente o rotulo/ordem informado."""
    texto_continuo = extract_text_from_pdf(pdf_path)

    padrao, grupos = build_regex(north_label, east_label, letter_order)
    matches = list(_matches_com_nomes(texto_continuo, padrao))
    matches = [(_parse_number(a), _parse_number(b), nome) for a, b, nome in matches]
    matches, _ = _remover_fechamento_explicito(matches)

    pontos, dados = [], []
    contador = vertex_start

    for grupo in matches:
        val1, val2, _ = grupo
        if grupos == ('north', 'east'):
            northing = _parse_number(val1)
            easting = _parse_number(val2)
        else:
            easting = _parse_number(val1)
            northing = _parse_number(val2)

        if decimal_places is not None:
            easting = round(easting, decimal_places)
            northing = round(northing, decimal_places)

        ponto = (easting, northing)
        if remove_consecutive_duplicates and pontos and pontos[-1] == ponto:
            continue

        pontos.append(ponto)
        dados.append((f"{vertex_prefix}{contador}", easting, northing))
        contador += 1

    return pontos, dados, padrao


# ---------------------------------------------------------------------
# DETECCAO AUTOMATICA
# ---------------------------------------------------------------------

# Leste (E/X): sempre entre ~100.000 e ~900.000 no UTM
#              (origem falsa de 500.000 no meridiano central do fuso).
# Norte (N/Y), hemisferio sul (quase todo o Brasil): entre ~1.000.000
#              (perto do equador) e ~10.000.000 (origem falsa no polo sul).
#
# Excecao conhecida: memoriais ao norte do equador (ex.: Roraima, Amapa)
# podem ter Norte tambem abaixo de 1.000.000 -- nesse caso raro, a
# magnitude sozinha fica ambigua (confianca cai pra 'media'/'baixa').
NORTHING_SOUTH_MIN = 1_100_000

# Rotulos mais comuns vistos em memoriais descritivos brasileiros,
# testados automaticamente (nas duas ordens possiveis).
LABEL_CANDIDATES = [
    ("N", "E"),
    ("Y", "X"),
    ("NORTE", "ESTE"),
    ("COORDENADA N", "COORDENADA E"),
    ("COORD. N", "COORD. E"),
    ("COORD.N", "COORD.E"),
    ("NORTHING", "EASTING"),
    ("NORTH", "EAST"),
    ("N(m)", "E(m)"),
    ("Y(m)", "X(m)"),
]

# Cabecalhos de coluna reconhecidos quando o memorial apresenta as
# coordenadas em formato de tabela real dentro do PDF.
NORTHING_HEADER_CANDIDATES = ['NORTE', 'NORTHING', 'COORDENADA N', 'COORD N', 'COORD. N', 'Y']
EASTING_HEADER_CANDIDATES = ['ESTE', 'EASTING', 'COORDENADA E', 'COORD E', 'COORD. E', 'X']
VERTEX_HEADER_CANDIDATES = ['VERTICE', 'VÉRTICE', 'PONTO', 'MARCO', 'ESTACA', 'V']


def _normalizar(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode('ascii')
    return s.strip().upper()


def _classify_by_magnitude(val_a, val_b):
    """
    Decide qual dos dois valores e o Norte e qual e o Leste, usando a
    faixa tipica de UTM no Brasil. Retorna (northing, easting), ou None
    se a magnitude nao permitir decidir com confianca.
    """
    a_is_northing = val_a >= NORTHING_SOUTH_MIN
    b_is_northing = val_b >= NORTHING_SOUTH_MIN

    if a_is_northing and 100_000 <= val_b <= 900_000 and val_a <= 10_000_000:
        return val_a, val_b
    if b_is_northing and 100_000 <= val_a <= 900_000 and val_b <= 10_000_000:
        return val_b, val_a
    return None


def _generic_pair_pattern():
    """Dois numeros com cara de coordenada UTM, com ate ~25 caracteres entre eles."""
    num = r'((?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d{5,8}(?:[.,]\d+)?))'
    meio = r'[^\d]{1,25}?'
    return rf'{num}{meio}{num}'


def _find_column_index(header_row, candidates):
    for i, cell in enumerate(header_row or []):
        if not cell:
            continue
        texto = _normalizar(cell)
        for cand in candidates:
            candidato = _normalizar(cand)
            if re.search(r"(?<![A-Z0-9])" + re.escape(candidato) + r"(?![A-Z0-9])", texto):
                return i
    return None


def _extract_from_tables(pdf_path):
    """
    Le tabelas de verdade do PDF (quando existirem) e usa o cabecalho
    pra identificar as colunas de Norte/Leste (e, se houver, o nome do
    vertice) -- mais confiavel do que reconhecer padroes em texto
    corrido, porque nao depende de regex nenhuma.

    Retorna lista de (valor_norte, valor_leste, nome_vertice_ou_None).
    """
    import pdfplumber

    resultados = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            for tabela in (pagina.extract_tables() or []):
                if not tabela or len(tabela) < 2:
                    continue
                cabecalho = tabela[0]
                idx_n = _find_column_index(cabecalho, NORTHING_HEADER_CANDIDATES)
                idx_e = _find_column_index(cabecalho, EASTING_HEADER_CANDIDATES)
                if idx_n is None or idx_e is None or idx_n == idx_e:
                    continue
                idx_v = _find_column_index(cabecalho, VERTEX_HEADER_CANDIDATES)

                for linha in tabela[1:]:
                    if idx_n >= len(linha) or idx_e >= len(linha):
                        continue
                    try:
                        val_n = _parse_number(linha[idx_n])
                        val_e = _parse_number(linha[idx_e])
                    except (TypeError, ValueError):
                        continue
                    nome = None
                    if idx_v is not None and idx_v < len(linha) and linha[idx_v]:
                        nome = str(linha[idx_v]).strip()
                    resultados.append((val_n, val_e, nome))
    return resultados


def auto_extract_vertices(
    pdf_path,
    vertex_prefix='P',
    vertex_start=0,
    decimal_places=2,
    remove_consecutive_duplicates=False,
):
    """
    Tenta descobrir sozinho o formato de coordenadas do memorial.
    Retorna um dict: pontos, dados, metodo_usado, confianca
    ('alta', 'media', 'baixa' ou 'nenhuma').
    """

    def _montar_saida(pares, metodo_usado, confianca, usar_nomes_da_tabela=False):
        pares, fechou = _remover_fechamento_explicito(pares)
        if fechou:
            metodo_usado += " Referência final ao vértice inicial omitida."
        pontos, dados = [], []
        contador = vertex_start
        for item in pares:
            northing, easting, nome = item
            if not usar_nomes_da_tabela:
                nome = None
            if decimal_places is not None:
                northing = round(northing, decimal_places)
                easting = round(easting, decimal_places)
            ponto = (easting, northing)
            if remove_consecutive_duplicates and pontos and pontos[-1] == ponto:
                continue
            pontos.append(ponto)
            dados.append((nome or f"{vertex_prefix}{contador}", easting, northing))
            contador += 1
        return {'pontos': pontos, 'dados': dados, 'metodo_usado': metodo_usado, 'confianca': confianca}

    # --- Estrategia 1: tabelas de verdade no PDF (a mais confiavel) ---
    try:
        tabela_resultados = _extract_from_tables(pdf_path)
    except Exception:
        tabela_resultados = []

    if len(tabela_resultados) >= 3:
        pares_confirmados = tabela_resultados
        return _montar_saida(
            pares_confirmados,
            f"Detectado em formato de tabela no PDF ({len(pares_confirmados)} linhas), "
            f"identificando as colunas de Norte e Leste pelo cabeçalho da tabela.",
            'alta',
            usar_nomes_da_tabela=True,
        )

    # --- Estrategia 2: rotulos conhecidos em texto corrido ---
    texto = extract_text_from_pdf(pdf_path)
    tentativas = []

    for n_label, e_label in LABEL_CANDIDATES:
        for ordem, desc_ordem in (
            ('N_FIRST', f"'{n_label}' antes de '{e_label}'"),
            ('E_FIRST', f"'{e_label}' antes de '{n_label}'"),
        ):
            try:
                padrao, grupos = build_regex(n_label, e_label, ordem)
                matches = list(_matches_com_nomes(texto, padrao))
            except re.error:
                continue
            if not matches:
                continue
            pares = [(_parse_number(v1), _parse_number(v2), grupos, nome) for v1, v2, nome in matches]
            tentativas.append((f"rótulos '{n_label}'/'{e_label}' ({desc_ordem})", pares))

    # --- Estrategia 3: padrao generico, sem rotulo, filtrado pela grandeza ---
    # (so aceita pares onde a grandeza confirma um Norte/Leste plausivel --
    # isso descarta automaticamente azimutes, distancias, areas, numeros
    # de pagina etc. que aparecem no mesmo documento)
    pares_genericos = []
    for a, b, nome in _matches_com_nomes(texto, _generic_pair_pattern()):
        va, vb = _parse_number(a), _parse_number(b)
        if _classify_by_magnitude(va, vb) is not None:
            pares_genericos.append((va, vb, None, nome))
    if pares_genericos:
        tentativas.append(("padrão numérico genérico, filtrado pela grandeza (sem rótulo)", pares_genericos))

    if not tentativas:
        return {
            'pontos': [],
            'dados': [],
            'metodo_usado': "Nenhum padrão de coordenadas foi reconhecido no PDF.",
            'confianca': 'nenhuma',
        }

    melhor = None
    for descricao, pares in tentativas:
        classificados = 0
        pares_resolvidos = []
        for v1, v2, grupos, nome in pares:
            resultado = _classify_by_magnitude(v1, v2)
            if grupos is not None:
                par = (v1, v2) if grupos == ('north', 'east') else (v2, v1)
                pares_resolvidos.append((*par, nome))
                if resultado == par:
                    classificados += 1
            elif resultado is not None:
                classificados += 1
                pares_resolvidos.append((*resultado, nome))

        pontuacao = (pares[0][2] is not None, len(pares_resolvidos), classificados)
        if melhor is None or pontuacao > melhor[0]:
            melhor = (pontuacao, descricao, pares_resolvidos)

    (_, total, classificados_por_magnitude), descricao, pares_northing_easting = melhor

    if total < 3:
        confianca = 'baixa'
    elif classificados_por_magnitude == total:
        confianca = 'alta'
    elif classificados_por_magnitude >= total * 0.7:
        confianca = 'media'
    else:
        confianca = 'baixa'

    metodo_usado = (
        f"Detectado: {descricao}. {classificados_por_magnitude} de {total} pares "
        f"confirmados pela grandeza típica de coordenadas UTM no Brasil "
        f"(Norte entre 1 e 10 milhões, Leste entre 100 mil e 900 mil)."
    )
    return _montar_saida(pares_northing_easting, metodo_usado, confianca)
