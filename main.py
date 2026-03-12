import zipfile
import os
import re
import shutil
import sys
import fitz
import pytesseract
import cv2
import numpy as np
import csv

INPUT_ZIP = sys.argv[1]

TEMP_DIR = "tmp_pdf"
OUTPUT_DIR = "renomeados"
OUTPUT_ZIP = "pdfs_renomeados.zip"


def extrair_zip():

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    os.makedirs(TEMP_DIR)

    with zipfile.ZipFile(INPUT_ZIP, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)


def extrair_texto(pdf_path):

    texto = ""

    with fitz.open(pdf_path) as doc:
        for page in doc:
            texto += page.get_text()

    if len(texto.strip()) > 50:
        return texto

    texto = ""

    with fitz.open(pdf_path) as doc:
        for page in doc:

            pix = page.get_pixmap(dpi=300)

            img = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(pix.h, pix.w, pix.n)

            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            texto += pytesseract.image_to_string(img)

    return texto


def detectar_conta(texto):

    texto_lower = texto.lower()

    # caso especial: conta corrente
    if "conta corrente" in texto_lower:

        padrao = r'conta corrente\s*(\d+-?\d*)'
        m = re.search(padrao, texto_lower)

        if m:
            return m.group(1)

    # padrão agência / conta
    padroes = [
        r'Ag[êe]ncia\s*/\s*Conta\s*\d+-?\d*\s*/\s*(\d+-?\d*)',
        r'Conta\s*:\s*(\d+-?\d*)',
        r'Conta\s*(\d+-?\d*)',
        r'/\s*(\d+-\d)'
    ]

    for p in padroes:

        m = re.search(p, texto)

        if m:
            return m.group(1)

    return None


def detectar_tipo(texto):

    t = texto.lower()

    if "poupança" in t or "poupanca" in t:
        return "POUP"

    if "conta corrente" in t:
        return "CC"

    if (
        "aplica" in t or
        "invest" in t or
        "fundo" in t or
        "tesouro" in t
    ):
        return "AP"

    return "UNK"


def processar():

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR)

    relatorio = []

    for root, dirs, files in os.walk(TEMP_DIR):

        for file in files:

            if not file.lower().endswith(".pdf"):
                continue

            caminho = os.path.join(root, file)

            texto = extrair_texto(caminho)

            conta = detectar_conta(texto)
            tipo = detectar_tipo(texto)

            if not conta:
                conta = "CONTA_NAO_ENCONTRADA"

            novo_nome = f"{conta} {tipo}.pdf"

            destino = os.path.join(OUTPUT_DIR, novo_nome)

            i = 1

            while os.path.exists(destino):
                destino = os.path.join(
                    OUTPUT_DIR,
                    f"{conta} {tipo}_{i}.pdf"
                )
                i += 1

            shutil.copy(caminho, destino)

            relatorio.append([
                file,
                os.path.basename(destino),
                conta,
                tipo
            ])

    with open("relatorio.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "arquivo_original",
            "arquivo_renomeado",
            "conta",
            "tipo"
        ])

        writer.writerows(relatorio)


def criar_zip():

    with zipfile.ZipFile(OUTPUT_ZIP, 'w') as zipf:

        for file in os.listdir(OUTPUT_DIR):

            caminho = os.path.join(OUTPUT_DIR, file)

            zipf.write(caminho, file)


def main():

    if len(sys.argv) < 2:

        print("Uso:")
        print("python script.py arquivo.zip")
        sys.exit(1)

    print("Extraindo ZIP...")
    extrair_zip()

    print("Processando PDFs...")
    processar()

    print("Criando ZIP final...")
    criar_zip()

    print("Concluído!")
    print("Arquivo final:", OUTPUT_ZIP)


if __name__ == "__main__":
    main()
