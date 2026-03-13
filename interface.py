from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QMessageBox
)

import sys
import subprocess


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Renomeador de Extratos")

        layout = QVBoxLayout()

        botao = QPushButton("Selecionar arquivos")
        botao.clicked.connect(self.selecionar)

        layout.addWidget(botao)

        self.setLayout(layout)
        self.setGeometry(100, 100, 500, 500)


    def selecionar(self):

        arquivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar arquivos",
            "",
            "PDF ou ZIP (*.pdf *.zip)"
        )

        if not arquivos:
            return

        for arquivo in arquivos:
            try:
                subprocess.run(
                    ["python", "main.py", arquivo],
                    check=True
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
                return

        QMessageBox.information(self, "OK", "Arquivos processados.")
        QMessageBox.information(
            self,
            "OK",
            f"{len(arquivos)} arquivo(s) processado(s)."
        )


app = QApplication(sys.argv)

janela = App()
janela.show()

app.exec()
