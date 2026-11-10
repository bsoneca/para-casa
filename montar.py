"""Junta o PDF do para casa com páginas das apostilas, na ordem dada.

  .venv/bin/python -I montar.py saida.pdf parte.pdf apostila.pdf:56-57,60 outra.pdf ...

Cada argumento é um PDF inteiro ou `arquivo.pdf:páginas` (números do PDF,
começando em 1; não os números impressos na apostila).

  .venv/bin/python -I montar.py --achar apostila.pdf "ATIVIDADE 36"

lista as páginas do PDF que contêm o texto, com o número impresso no rodapé.

Toda página do PDF final, inclusive as das apostilas, ganha no pé, ao centro,
"<Nome> · página N de T". O nome vem do arquivo de saída ("2026-11-04 Ana.pdf").
"""
import io
import os
import re
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def paginas(spec, total):
    out = []
    for parte in spec.split(","):
        a, _, b = parte.partition("-")
        out += range(int(a), int(b or a) + 1)
    return [p - 1 for p in out if 1 <= p <= total]


def achar(arquivo, texto):
    alvo = re.sub(r"\s+", " ", texto).lower()
    for i, pagina in enumerate(PdfReader(arquivo).pages):
        t = re.sub(r"\s+", " ", pagina.extract_text() or "").strip()
        if alvo in t.lower():
            impresso = re.search(r"(\d+)$", t)
            print(f"PDF {i + 1} (impresso {impresso.group(1) if impresso else '?'})")


def carimbo(largura, altura, texto):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(largura, altura))
    c.setFont("Helvetica", 8)
    w = c.stringWidth(texto, "Helvetica", 8)
    x, y = (largura - w) / 2, 14  # ~5 mm do pé da folha
    c.setFillColorRGB(1, 1, 1)
    c.rect(x - 4, y - 3, w + 8, 12, stroke=0, fill=1)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(x, y, texto)
    c.save()
    return PdfReader(buf).pages[0]


def numerar(w, nome):
    total = len(w.pages)
    for n, pagina in enumerate(w.pages, 1):
        caixa = pagina.mediabox
        texto = f"{nome} · página {n} de {total}" if nome else f"página {n} de {total}"
        selo = carimbo(float(caixa.width), float(caixa.height), texto)
        pagina.merge_transformed_page(selo, (1, 0, 0, 1, float(caixa.left), float(caixa.bottom)))


def montar(saida, partes):
    w = PdfWriter()
    for parte in partes:
        arquivo, _, spec = parte.rpartition(":") if re.search(r":[\d,-]+$", parte) else (parte, "", "")
        r = PdfReader(arquivo)
        for i in paginas(spec, len(r.pages)) if spec else range(len(r.pages)):
            w.add_page(r.pages[i])
    nome = re.sub(r"^\d{4}-\d{2}-\d{2}\s*", "", os.path.splitext(os.path.basename(saida))[0])
    numerar(w, nome)
    w.compress_identical_objects()
    with open(saida, "wb") as f:
        w.write(f)
    print(saida, len(w.pages), "páginas")


if __name__ == "__main__":
    if sys.argv[1] == "--achar":
        achar(sys.argv[2], sys.argv[3])
    else:
        montar(sys.argv[1], sys.argv[2:])
