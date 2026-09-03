# Memorial Descritivo Importer

Reads a Brazilian land survey "memorial descritivo" PDF and imports its
vertex coordinates into a QGIS point layer — automatically detecting the
coordinate format (label, order, or table layout) instead of requiring
manual configuration.

## How detection works

1. Looks for real tables inside the PDF and reads column headers.
2. Tries common label pairs (N/E, Y/X, Norte/Este...) in both orders.
3. Falls back to a generic numeric pattern, using the typical magnitude
   of Brazilian UTM coordinates (Northing ≈ 1–10 million, Easting ≈
   100k–900k) to tell the two apart — this works even if the label or
   order in the PDF is unusual.

A manual mode is available for atypical formats.

## Privacy

The PDF and the extracted coordinates never leave your computer —
everything is read and processed locally. The only thing sent over the
network is your e-mail address, and only once your 3 free uses are
exhausted, to confirm an active subscription against a public,
read-only file.

## Pricing

The first 3 extractions are free. Continued use requires an active
subscription. The plugin checks subscription status against a public,
read-only file — no account or login is needed to use the free tier.

## Como funciona (PT-BR)

Lê um memorial descritivo em PDF e detecta sozinho o formato das
coordenadas (tabela, rótulo, ou padrão numérico pela grandeza típica de
UTM no Brasil), importando os vértices para uma camada de pontos do
QGIS. As primeiras 3 extrações são gratuitas; o uso contínuo exige
assinatura ativa.

## License

GPL v3 or later — see [LICENSE](LICENSE).
