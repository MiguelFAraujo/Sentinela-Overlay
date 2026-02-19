from mcp.server.fastmcp import FastMCP
import psutil
import os
import subprocess

# Create the MCP server with the project name
mcp = FastMCP("Sentinela Hub")

@mcp.tool()
def check_hardware_health():
    """Monitora o uso de CPU (i5) e Memória para garantir que a IA local não trave o PC."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"🛡️ Status do Sistema: CPU: {cpu}% | RAM: {ram}%"

@mcp.tool()
def get_sentinela_status():
    """Verifica se o processo do Sentinela EDR está ativo no Windows."""
    # Look for processes related to Sentinela
    sentinela_active = any("agente_sentinela" in p.name().lower() for p in psutil.process_iter())
    status = "ATIVO ✅" if sentinela_active else "INATIVO ❌"
    return f"Monitoramento EDR: {status}"

@mcp.tool()
def ping_maker_devices(device_ip: str):
    """Verifica se seus dispositivos (ESP32 ou Raspberry Pi) estão online na rede local."""
    # Useful for robotics and local automation
    response = os.system(f"ping -n 1 {device_ip}")
    return "Dispositivo ONLINE 📡" if response == 0 else "Dispositivo OFFLINE ⚠️"

@mcp.tool()
def run_powershell(command: str):
    """Executa um comando direto no PowerShell do Windows."""
    try:
        # Security Note: This allows arbitrary command execution.
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return f"✅ Sucesso:\n{output}"
        else:
            return f"❌ Erro (Código {result.returncode}):\n{error}\nOutput:\n{output}"
    except Exception as e:
        return f"❌ Falha na execução: {e}"

# Auto-update configuration
CURRENT_VERSION = "1.1.0"
GITHUB_REPO_URL = "https://raw.githubusercontent.com/MiguelFAraujo/Sentinela-Overlay/main/mcp-sentinela"
VERSION_URL = f"{GITHUB_REPO_URL}/version.txt"
EXE_URL = f"{GITHUB_REPO_URL}/SentinelaHub.exe"

@mcp.tool()
def check_and_update_server():
    """Verifica se há atualizações disponíveis e aplica automaticamente."""
    try:
        import requests
        import sys
        
        # Check remote version
        response = requests.get(VERSION_URL)
        if response.status_code != 200:
            return f"❌ Erro ao verificar atualizações: HTTP {response.status_code}"
        
        remote_version = response.text.strip()
        
        if remote_version == CURRENT_VERSION:
            return f"✅ O servidor está atualizado (Versão {CURRENT_VERSION})."
        
        # Update available
        if getattr(sys, 'frozen', False):
            # Running as executable
            current_exe = sys.executable
            old_exe = current_exe + ".old"
            
            # Rename current executable
            if os.path.exists(old_exe):
                os.remove(old_exe)
            os.rename(current_exe, old_exe)
            
            # Download new executable
            return_msg = f"⬇️ Atualizando de {CURRENT_VERSION} para {remote_version}..."
            
            with requests.get(EXE_URL, stream=True) as r:
                r.raise_for_status()
                with open(current_exe, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return f"{return_msg}\n✅ Atualização concluída! Reinicie o servidor para aplicar."
        else:
            return f"⚠️ Atualização disponível ({remote_version}), mas não pode ser aplicada em modo script. Faça um 'git pull'."

    except Exception as e:
        return f"❌ Falha na atualização: {e}"

if __name__ == "__main__":
    mcp.run()
