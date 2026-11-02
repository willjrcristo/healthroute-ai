import PyPDF2
import sys

sys.stdout.reconfigure(encoding='utf-8')

filename = "Relatório Técnico - Otimização de Rotas Médicas (Tech Challenge Fase 2).pdf"
with open(filename, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for i, page in enumerate(reader.pages):
        print(f"--- PAGE {i} ---")
        text = page.extract_text()
        print(text)
        print()
