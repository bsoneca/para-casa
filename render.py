"""Imprime uma página HTML num PDF A4 com o Chrome (ou o Edge) sem janela.

  <python da .venv> -I render.py pagina.html saida.pdf

Funciona no macOS, no Windows e no Linux: procura o Chrome e, no Windows, o
Edge, que já vem instalado. Sem cabeçalho, rodapé nem URL na folha.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def navegador():
    candidatos = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for base in filter(None, (os.environ.get(v) for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"))):
        candidatos += [
            os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
        ]
    candidatos += [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge")]
    for c in candidatos:
        if c and os.path.isfile(c):
            return c
    sys.exit("Não achei o Google Chrome nem o Microsoft Edge.")


def render(html, pdf):
    html, pdf = pathlib.Path(html).resolve(), pathlib.Path(pdf).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run(
            [navegador(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             "--no-first-run", f"--user-data-dir={perfil}", f"--print-to-pdf={pdf}", html.as_uri()],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
        )
    if not pdf.is_file():
        sys.exit(f"O navegador não gerou {pdf}")
    print(pdf)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
