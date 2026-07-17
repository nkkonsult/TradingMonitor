# Configuration latexmk pour le mémoire M1
# Enchaîne automatiquement pdflatex -> biber -> pdflatex (x2)

$pdf_mode = 1;                 # produire un PDF via pdflatex
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O %S';
$bibtex_use = 2;               # utiliser biber/bibtex automatiquement
$biber = 'biber %O %S';

# Fichiers auxiliaires à nettoyer avec `latexmk -c`
$clean_ext = 'bbl bcf run.xml synctex.gz';
