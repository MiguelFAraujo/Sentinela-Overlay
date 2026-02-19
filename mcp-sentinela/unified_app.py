import sys
import json
import subprocess
import platform
import threading
import psutil
import os
from pathlib import Path

# --- Configuration for Paths ---
# We try to use the parent directory config if it exists, to preserve user settings
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent

CONFIG_FILE_NAME = "sentinela_config.json"
MEMORY_FILE_NAME = "memory.json"
STATUS_FILE_NAME = "sentinela_status.json"

if (PARENT_DIR / CONFIG_FILE_NAME).exists():
    BASE_DIR = PARENT_DIR
else:
    BASE_DIR = CURRENT_DIR

MEMORY_FILE = BASE_DIR / MEMORY_FILE_NAME
STATUS_FILE = BASE_DIR / STATUS_FILE_NAME
CONFIG_FILE = BASE_DIR / CONFIG_FILE_NAME

# --- GUI Imports (PyQt6) ---
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
except ImportError:
    print("CRITICAL: PyQt6 not found. Please install it.", file=sys.stderr)
    sys.exit(1)

# --- MCP Imports ---
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("CRITICAL: FastMCP not found.", file=sys.stderr)
    sys.exit(1)

# --- Brain Imports ---
# Ensure we can import from the local 'brain' folder
sys.path.append(str(CURRENT_DIR))
try:
    from brain.llm import OllamaClient
except ImportError:
    # Fail gracefully if brain is missing
    class OllamaClient:
        def __init__(self, model="", base_url=""): pass
        def is_running(self): return False
        def chat(self, msg, sys=""): return "AI Module Missing"
    print("WARNING: 'brain' module not found.", file=sys.stderr)


# =============================================================================
# UTILITIES
# =============================================================================
def ensure_file(path: Path, default_content: dict):
    if not path.exists():
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_content, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating file {path}: {e}", file=sys.stderr)

def load_json(path: Path, default_content: dict = None) -> dict:
    if not path.exists():
        if default_content is not None:
            ensure_file(path, default_content)
            return default_content
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_content if default_content is not None else {}

# Initialize files
ensure_file(MEMORY_FILE, {"last_run": "", "events": []})
ensure_file(STATUS_FILE, {"status": "ativo", "last_check": ""})
ensure_file(CONFIG_FILE, {"theme": "dark", "transparency": 150, "llm_model": "qwen2.5:7b"})


# =============================================================================
# HARDWARE MONITOR (GUI Thread)
# =============================================================================
class HardwareMonitor(QThread):
    stats_updated = pyqtSignal(dict)

    def run(self):
        # Optimized PowerShell command for detailed stats
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
            # CREATE_NO_WINDOW is essential to avoid popping up windows
            flags = 0x08000000 if platform.system() == 'Windows' else 0
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, creationflags=flags
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.stats_updated.emit(data)
        except Exception as e:
            print(f"Monitor error: {e}", file=sys.stderr)

class AIStatusMonitor(QThread):
    status_updated = pyqtSignal(bool, str)

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.client = OllamaClient(model=model_name)

    def run(self):
        is_running = self.client.is_running()
        if is_running:
            self.status_updated.emit(True, f"Ollama Online ({self.model_name})")
        else:
            self.status_updated.emit(False, "Ollama Offline")

# =============================================================================
# GUI HUD (PyQt6 Widget)
# =============================================================================
class SentinelaHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_json(CONFIG_FILE, {"theme": "dark", "transparency": 150, "llm_model": "qwen2.5:7b"})
        self.initUI()
        
        # Hardware Thread
        self.monitor_thread = HardwareMonitor()
        self.monitor_thread.stats_updated.connect(self.update_stats)
        
        # AI Thread
        self.ai_status = "Verificando..."
        self.ai_thread = AIStatusMonitor(self.config.get("llm_model", "qwen2.5:7b"))
        self.ai_thread.status_updated.connect(self.update_ai_status)
        
        # Timers
        self.timer_hw = QTimer()
        self.timer_hw.timeout.connect(self.monitor_thread.start)
        self.timer_hw.start(3000) 
        self.monitor_thread.start()

        self.timer_ai = QTimer()
        self.timer_ai.timeout.connect(self.ai_thread.start)
        self.timer_ai.start(10000) 
        self.ai_thread.start()

        self.last_stats = {}

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.label = QLabel("🛡️ Sentinela v2.0\nIniciando...")
        
        transparency = self.config.get("transparency", 150)
        self.label.setStyleSheet(f"color: #00ff00; font-family: Consolas; font-weight: bold; font-size: 12px; background-color: rgba(0, 0, 0, {transparency}); padding: 10px; border-radius: 5px;")
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setGeometry(10, 50, 220, 110)

    def update_stats(self, stats):
        self.last_stats = stats
        self.refresh_ui()
    
    def update_ai_status(self, online, message):
        self.ai_status = message if online else "⚠️ AI Offline"
        self.refresh_ui()

    def refresh_ui(self):
        cpu = self.last_stats.get('CPU', 0)
        ram_used = self.last_stats.get('RAM_Used', 0)
        ram_total = self.last_stats.get('RAM_Total', 0)
        gpu = self.last_stats.get('GPU', 'N/A')
        
        status_text = f"🛡️ Sentinela: VIGILANTE\n" \
                      f"🔥 CPU: {cpu}%\n" \
                      f"🧠 RAM: {ram_used}GB / {ram_total}GB\n" \
                      f"🎮 GPU: {gpu}\n" \
                      f"🤖 {self.ai_status}"
                      
        self.label.setText(status_text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

# =============================================================================
# MCP SERVER (FastMCP)
# =============================================================================
mcp = FastMCP("Sentinela Hub")

@mcp.tool()
def check_hardware_health():
    """Monitora o uso de CPU e Memória."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"🛡️ Status do Sistema: CPU: {cpu}% | RAM: {ram}%"

@mcp.tool()
def get_sentinela_status():
    """Verifica se o HUD está rodando."""
    return "ATIVO ✅ (Interface Integrada)"

@mcp.tool()
def run_command(command: str):
    """Executa um comando no terminal do sistema (PowerShell/Bash)."""
    system = platform.system().lower()
    try:
        shell_cmd = ["powershell", "-Command", command] if system == 'windows' else ["/bin/sh", "-c", command]
        # CREATE_NO_WINDOW for Windows
        flags = 0x08000000 if system == 'windows' else 0
        
        result = subprocess.run(shell_cmd, capture_output=True, text=True, timeout=30, creationflags=flags)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return f"✅ Sucesso:\n{output}"
        else:
            return f"❌ Erro ({result.returncode}):\n{error}\n{output}"
    except Exception as e:
        return f"❌ Falha: {e}"

# Auto-update configuration
VERSION = "2.0.0"
GITHUB_REPO_URL = "https://raw.githubusercontent.com/MiguelFAraujo/Sentinela-Overlay/main/mcp-sentinela"
VERSION_URL = f"{GITHUB_REPO_URL}/version.txt"
EXE_URL = f"{GITHUB_REPO_URL}/Sentinela.exe"

@mcp.tool()
def check_and_update_server():
    """Verifica atualizações e aplica."""
    try:
        import requests
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code != 200: return f"Erro HTTP {response.status_code}"
        
        remote_version = response.text.strip()
        if remote_version == VERSION: return f"✅ Atualizado ({VERSION})."
        
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
            old_exe = current_exe + ".old"
            if os.path.exists(old_exe): os.remove(old_exe)
            os.rename(current_exe, old_exe)
            
            with requests.get(EXE_URL, stream=True) as r:
                r.raise_for_status()
                with open(current_exe, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            return f"✅ Atualizado para {remote_version}. Reinicie o app."
        return f"⚠️ Atualização disponível ({remote_version})."
    except Exception as e:
        return f"❌ Falha: {e}"

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    # 1. Start FastMCP in Background Thread
    # We must start this BEFORE the GUI loop, but run it concurrently.
    # FastMCP blocks, so we put it in a thread.
    print(f"🚀 Sentinela Unified v{VERSION} - Starting Server & HUD...", file=sys.stderr)
    
    server_thread = threading.Thread(target=mcp.run, daemon=True)
    server_thread.start()
    
    # 2. Start GUI in Main Thread
    app = QApplication(sys.argv)
    hud = SentinelaHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
