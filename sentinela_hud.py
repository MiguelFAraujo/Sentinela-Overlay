import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

# --- Configuração de Caminhos ---
BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "memory.json"
STATUS_FILE = BASE_DIR / "sentinela_status.json"
CONFIG_FILE = BASE_DIR / "sentinela_config.json"

# --- Funções Utilitárias ---
def ensure_file(path: Path, default_content: dict):
    """Garante que o arquivo existe com conteúdo padrão."""
    if not path.exists():
        safe_save_json(path, default_content)

def safe_save_json(path: Path, data: dict):
    """Salva JSON de forma segura com encoding UTF-8."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {path.name}: {e}")

def load_json(path: Path, default_content: dict = None) -> dict:
    """Carrega JSON com fallback para padrão."""
    if not path.exists():
        if default_content is not None:
            ensure_file(path, default_content)
            return default_content
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {path.name}: {e}")
        return default_content if default_content is not None else {}

# --- Inicialização de Arquivos ---
ensure_file(MEMORY_FILE, {"last_run": "", "events": []})
ensure_file(STATUS_FILE, {"status": "ativo", "last_check": ""})
ensure_file(CONFIG_FILE, {"theme": "dark", "transparency": 150})

class SentinelaHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_json(CONFIG_FILE, {"theme": "dark", "transparency": 150})
        self.initUI()
        
    def initUI(self):
        # Janela sem bordas, sempre no topo e transparente
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.label = QLabel("🛡️ Sentinela: Ativo\n🤖 WhatsApp: Online")
        
        # Estilo visual baseado na config
        transparency = self.config.get("transparency", 150)
        self.label.setStyleSheet(f"color: #00ff00; font-weight: bold; font-size: 14px; background-color: rgba(0, 0, 0, {transparency}); padding: 10px; border-radius: 5px;")
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Posiciona no canto superior direito (ajuste conforme sua resolução)
        self.setGeometry(10, 50, 200, 80)
        
        # Timer para atualizar dados
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(5000) # Atualiza a cada 5 segundos

    def update_stats(self):
        # Tenta ler o status mais recente
        status_data = load_json(STATUS_FILE)
        status_text = status_data.get("status", "Desconhecido")
        
        # Atualiza a UI
        self.label.setText(f"🛡️ Sentinela: {status_text}\n🔥 GPU: Ativa\n💬 Bot: Aguardando")

        # Exemplo de persistência segura (opcional, só para teste)
        # memory = load_json(MEMORY_FILE)
        # memory["last_check"] = "agora" # (Idealmente usar timestamp real)
        # safe_save_json(MEMORY_FILE, memory)

def main():
    app = QApplication(sys.argv)
    hud = SentinelaHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
