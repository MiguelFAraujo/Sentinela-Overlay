from mcp.server.fastmcp import FastMCP
import psutil
import os
import subprocess
import platform
import sys

def get_platform_info():
    """Retorna informações sobre o sistema operacional operante."""
    system = platform.system()
    release = platform.release()
    return f"{system} {release}"

# Create the MCP server with the project name
mcp = FastMCP("Sentinela Hub")

@mcp.tool()
def check_hardware_health():
    """Monitora o uso de CPU e Memória em qualquer sistema (Windows, Linux, Android, Mac)."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    os_info = get_platform_info()
    return f"🛡️ Status do Sistema ({os_info}): CPU: {cpu}% | RAM: {ram}%"

@mcp.tool()
def get_sentinela_status():
    """Verifica se o processo do Sentinela EDR está ativo."""
    # Look for processes related to Sentinela
    # This is generic enough to work if the process name is consistent
    sentinela_active = any("agente_sentinela" in p.name().lower() for p in psutil.process_iter())
    status = "ATIVO ✅" if sentinela_active else "INATIVO ❌"
    return f"Monitoramento EDR: {status}"

@mcp.tool()
def ping_maker_devices(device_ip: str):
    """Verifica se dispositivos (ESP32, Raspberry Pi, etc) estão online na rede local."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', device_ip]
    
    try:
        # Use subprocess for better control and cross-platform compatibility
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Dispositivo ONLINE 📡" if result.returncode == 0 else "Dispositivo OFFLINE ⚠️"
    except Exception as e:
        return f"❌ Erro ao executar ping: {e}"

@mcp.tool()
def run_command(command: str):
    """Executa um comando no terminal do sistema (PowerShell no Windows, Bash no Linux/Mac/Android)."""
    system = platform.system().lower()
    
    try:
        if system == 'windows':
            shell_cmd = ["powershell", "-Command", command]
        else:
            # Linux, Mac, Android (Termux)
            shell_cmd = ["/bin/sh", "-c", command]

        # Security Note: This allows arbitrary command execution.
        result = subprocess.run(shell_cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return f"✅ Sucesso ({system}):\n{output}"
        else:
            return f"❌ Erro (Código {result.returncode}):\n{error}\nOutput:\n{output}"
    except Exception as e:
        return f"❌ Falha na execução: {e}"

# Auto-update configuration
CURRENT_VERSION = "1.2.0"
GITHUB_REPO_URL = "https://raw.githubusercontent.com/MiguelFAraujo/Sentinela-Overlay/main/mcp-sentinela"
VERSION_URL = f"{GITHUB_REPO_URL}/version.txt"
EXE_URL = f"{GITHUB_REPO_URL}/SentinelaHub.exe" # Only relevant for Windows .exe users

@mcp.tool()
def check_and_update_server():
    """Verifica se há atualizações disponíveis e aplica automaticamente."""
    try:
        import requests
        
        # Check remote version
        try:
            response = requests.get(VERSION_URL, timeout=5)
            if response.status_code != 200:
                return f"❌ Erro ao verificar atualizações: HTTP {response.status_code}"
            remote_version = response.text.strip()
        except Exception as e:
            return f"❌ Não foi possível conectar ao GitHub: {e}"
        
        if remote_version == CURRENT_VERSION:
            return f"✅ O servidor está atualizado (Versão {CURRENT_VERSION})."
        
        # Update available
        if getattr(sys, 'frozen', False):
            # Running as executable (Windows typically)
            current_exe = sys.executable
            old_exe = current_exe + ".old"
            
            # Rename current executable
            if os.path.exists(old_exe):
                os.remove(old_exe)
            os.rename(current_exe, old_exe)
            
            # Download new executable
            return_msg = f"⬇️ Atualizando executável de {CURRENT_VERSION} para {remote_version}..."
            
            with requests.get(EXE_URL, stream=True) as r:
                r.raise_for_status()
                with open(current_exe, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return f"{return_msg}\n✅ Atualização concluída! Reinicie o servidor para aplicar."
        else:
            # Running from source (Linux, Mac, Android, or Dev Windows)
            return f"⚠️ Atualização disponível ({remote_version}).\nComo você está rodando o script Python, por favor execute: 'git pull'"

    except Exception as e:
        return f"❌ Falha na atualização: {e}"

if __name__ == "__main__":
    print(f"🚀 Sentinela Hub v{CURRENT_VERSION} Iniciado!")
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    print("📡 Aguardando comandos MCP...")
    mcp.run()
