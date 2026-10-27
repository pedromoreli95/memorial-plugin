# Memorial Descritivo Importer

Reads a Brazilian land survey "memorial descritivo" PDF and imports its
vertex coordinates into a QGIS point layer — automatically detecting the
coordinate format (label, order, or table layout) to reduce manual configuration.

## How detection works

1. Looks for real tables inside the PDF and reads column headers.
2. Tries common label pairs (N/E, Y/X, Norte/Este...) in both orders.
3. Falls back to a generic numeric pattern, using the typical magnitude
   of Brazilian UTM coordinates (Northing ≈ 1–10 million, Easting ≈
   100k–900k) to tell the two apart — this works even if the label or
   order in the PDF is unusual. Check the preview when labels are absent.

A manual mode is available for atypical formats.

## Privacy and pricing

The PDF and extracted coordinates are processed locally. The plugin is free,
with unlimited use and no subscription or account. Installing the optional
Python dependency requires an internet connection.

## Como funciona (PT-BR)

Lê um memorial descritivo em PDF e detecta sozinho o formato das
coordenadas (tabela, rótulo, ou padrão numérico pela grandeza típica de
UTM no Brasil), importando os vértices para uma camada de pontos do
QGIS. O uso é gratuito e ilimitado, sem assinatura ou cadastro.

## License

GPL v3 or later — see [LICENSE](LICENSE).

As ocorrências consecutivas com coordenadas iguais são preservadas, assim como
a repetição do ponto inicial no fechamento. Confira a prévia: em modo automático,
formatos sem rótulos dependem de uma inferência pela grandeza das coordenadas.
Os nomes fora de tabelas são gerados conforme o prefixo e a numeração configurados.
