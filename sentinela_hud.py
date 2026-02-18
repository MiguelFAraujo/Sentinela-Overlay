import sys
import json
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

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

# --- Thread de Monitoramento (PowerShell) ---
class HardwareMonitor(QThread):
    stats_updated = pyqtSignal(dict)

    def run(self):
        # Comandos PowerShell otimizados
        ps_script = """
        $cpu = (Get-CimInstance Win32_Processor).LoadPercentage
        $os = Get-CimInstance Win32_OperatingSystem
        $ram_total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        $ram_free = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $ram_used = $ram_total - $ram_free
        $gpu = (Get-CimInstance Win32_VideoController | Select-Object -First 1).Name
        
        @{
            CPU = $cpu
            RAM_Used = $ram_used
            RAM_Total = $ram_total
            GPU = $gpu
        } | ConvertTo-Json
        """
        
        try:
            # Executa PowerShell e captura JSON
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.stats_updated.emit(data)
        except Exception as e:
            print(f"Erro monitoramento: {e}")

class SentinelaHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_json(CONFIG_FILE, {"theme": "dark", "transparency": 150})
        self.initUI()
        
        # Thread worker
        self.monitor_thread = HardwareMonitor()
        self.monitor_thread.stats_updated.connect(self.update_ui)
        
    def initUI(self):
        # Janela sem bordas, sempre no topo e transparente
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.label = QLabel("🛡️ Sentinela v1.01\nCarregando...")
        
        # Estilo visual baseado na config
        transparency = self.config.get("transparency", 150)
        self.label.setStyleSheet(f"color: #00ff00; font-family: Consolas; font-weight: bold; font-size: 12px; background-color: rgba(0, 0, 0, {transparency}); padding: 10px; border-radius: 5px;")
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Posiciona no canto superior direito
        self.setGeometry(10, 50, 220, 100)
        
        # Timer para disparar a thread
        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor_thread.start)
        self.timer.start(2000) # Atualiza a cada 2 segundos (Hardware é pesado)

    def update_ui(self, stats):
        cpu = stats.get('CPU', 0)
        ram_used = stats.get('RAM_Used', 0)
        ram_total = stats.get('RAM_Total', 0)
        gpu = stats.get('GPU', 'N/A')
        
        status_text = f"🛡️ Sentinela: VIGILANTE\n" \
                      f"🔥 CPU: {cpu}%\n" \
                      f"🧠 RAM: {ram_used}GB / {ram_total}GB\n" \
                      f"🎮 GPU: {gpu}\n" \
                      f"🤖 AI: Online"
                      
        self.label.setText(status_text)
        
def main():
    app = QApplication(sys.argv)
    hud = SentinelaHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
