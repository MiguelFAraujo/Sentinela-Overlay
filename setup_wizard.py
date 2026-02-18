import sys
import os
import shutil
import winshell
from pathlib import Path
import requests
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, 
                             QLabel, QMessageBox, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# --- Configuração ---
APP_NAME = "Sentinela Pro"
EXE_NAME = "Sentinela Pro.exe"

def get_source_dir():
    """Retorna o diretório base, seja rodando como script ou .exe congelado."""
    if getattr(sys, 'frozen', False):
        # Se rodando como .exe (PyInstaller), os arquivos estão em _MEIPASS
        base_path = Path(sys._MEIPASS)
        return base_path / "Sentinela Pro"
    else:
        # Se rodando como script, assume que 'dist/Sentinela Pro' está acessível relativemente
        return Path("dist/Sentinela Pro")

SOURCE_DIR = get_source_dir()
INSTALL_DIR = Path(os.environ["LOCALAPPDATA"]) / "Sentinela"

class OllamaCheckThread(QThread):
    result_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            response = requests.get("http://localhost:11434", timeout=2)
            if response.status_code == 200:
                self.result_signal.emit(True, "Ollama detectado com sucesso!")
            else:
                self.result_signal.emit(False, f"Ollama respondeu com erro: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.result_signal.emit(False, "Ollama não está rodando. Verifique se o serviço está ativo.")
        except Exception as e:
            self.result_signal.emit(False, f"Erro ao conectar: {e}")

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Bem-vindo ao Instalador do Sentinela Pro v1.02")
        self.setSubTitle("Guia de instalação do Sentinela Pro com Monitoramento Profundo.")
        
        layout = QVBoxLayout()
        label = QLabel("O Sentinela Pro v1.02 é uma ferramenta de EDR e monitoramento avançado.\n\n"
                       "🚀 NOVIDADES v1.02:\n"
                       "- CORREÇÃO CRÍTICA: Erro de caminho na instalação corrigido.\n"
                       "- Otimização de monitoramento de hardware.\n\n"
                       "⚠️ REQUISITO OBRIGATÓRIO: OLLAMA\n"
                       "Verificaremos se o serviço Ollama está ativo na porta 11434.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)

# ... (LicensePage and PreRequisitePage skipped for brevity in this replace call if context permits, 
# but simply targeting the InstallPage logic is better split if IntroPage is far away. 
# I will supply the IntroPage update here and do the InstallPage fix in a separate chunk or same tool call if contiguous enough.
# They are far apart. I'll do IntroPage first).

class LicensePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Contrato de Licença")
        self.setSubTitle("Por favor, leia e aceite os termos.")
        
        layout = QVBoxLayout()
        self.license_text = QLabel("Este software é fornecido 'como está', sem garantias.\n"
                                   "O uso é de total responsabilidade do usuário final.\n"
                                   "É proibido o uso para fins maliciosos.\n\n"
                                   "Copyright © 2026 Miguel Araújo.")
        self.license_text.setWordWrap(True)
        layout.addWidget(self.license_text)
        
        self.checkbox = QCheckBox("Eu aceito os termos do contrato")
        layout.addWidget(self.checkbox)
        self.registerField("license_accepted*", self.checkbox) # * torna obrigatório
        self.setLayout(layout)

class PreRequisitePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Verificação de Requisitos")
        self.setSubTitle("Verificando se o Ollama está ativo...")
        
        layout = QVBoxLayout()
        self.status_label = QLabel("Aguardando verificação...")
        layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminado
        layout.addWidget(self.progress)
        
        self.retry_btn = QCheckBox("Tentar novamente (marque para retestar)")
        self.retry_btn.stateChanged.connect(self.check_ollama)
        self.retry_btn.setVisible(False)
        layout.addWidget(self.retry_btn)

        self.ollama_ready = False
        self.setLayout(layout)

    def initializePage(self):
        self.check_ollama()

    def check_ollama(self):
        self.status_label.setText("Verificando conexão com Ollama (localhost:11434)...")
        self.progress.setVisible(True)
        self.retry_btn.setVisible(False)
        self.completeChanged.emit() # Recalcula isComplete
        
        self.thread = OllamaCheckThread()
        self.thread.result_signal.connect(self.on_check_finished)
        self.thread.start()

    def on_check_finished(self, success, message):
        self.progress.setVisible(False)
        self.status_label.setText(message)
        if success:
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.ollama_ready = True
        else:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_label.setText(f"{message}\n\nPor favor, inicie o Ollama e tente novamente.")
            self.retry_btn.setVisible(True)
            self.retry_btn.setChecked(False)
            self.ollama_ready = False
        
        self.completeChanged.emit()

    def isComplete(self):
        return self.ollama_ready

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Instalando")
        self.setSubTitle("Copiando arquivos...")
        
        layout = QVBoxLayout()
        self.label = QLabel("Preparando instalação...")
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def initializePage(self):
        self.start_install()

    def start_install(self):
        # Simulação de instalação (cópia de arquivos)
        # Em um cenário real, você copiaria de um resource temporário
        # Aqui vamos assumir que estamos rodando da pasta onde está o build
        
        self.label.setText(f"Criando diretório: {INSTALL_DIR}")
        self.progress.setValue(10)
        
        try:
            if INSTALL_DIR.exists():
                shutil.rmtree(INSTALL_DIR)
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivos
            # Usa SOURCE_DIR que já resolve o caminho correto (_MEIPASS ou dist)
            src = SOURCE_DIR
            
            if not src.exists():
                raise FileNotFoundError(f"Arquivos de origem não encontrados em {src.absolute()}\n(Esperado: {SOURCE_DIR})")

            self.label.setText(f"Copiando de: {src.name}...")
            # Copia recursiva
            shutil.copytree(src, INSTALL_DIR, dirs_exist_ok=True)
            self.progress.setValue(70)

            # Criar atalho
            self.label.setText("Criando atalhos...")
            desktop = Path(winshell.desktop())
            shortcut_path = desktop / f"{APP_NAME}.lnk"
            target = INSTALL_DIR / EXE_NAME
            
            with winshell.shortcut(str(shortcut_path)) as link:
                link.path = str(target)
                link.description = "Overlay Sentinela Pro"
                link.working_directory = str(INSTALL_DIR)
            
            self.progress.setValue(100)
            self.label.setText("Instalação concluída com sucesso!")
            
        except Exception as e:
            self.label.setText(f"Erro na instalação: {e}")
            self.label.setStyleSheet("color: red")

class SentinelaInstaller(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalador - Sentinela Pro")
        self.setFixedSize(600, 400)
        
        self.addPage(IntroPage())
        self.addPage(LicensePage())
        self.addPage(PreRequisitePage())
        self.addPage(InstallPage())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wizard = SentinelaInstaller()
    wizard.show()
    sys.exit(app.exec())
