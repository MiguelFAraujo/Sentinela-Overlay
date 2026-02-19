from mcp.server.fastmcp import FastMCP
import psutil
import os
import sqlite3
import datetime

# Database path configuration
# Priority: 
# 1. Environment Variable 'SENTINELA_DB_PATH'
# 2. Local 'db.sqlite3'
# 3. Hardcoded Default (for current user setup)
DEFAULT_DB_PATH = r"c:\Users\nigel\OneDrive\Documentos\WhatsApp-agent\db.sqlite3"
DB_PATH = os.getenv("SENTINELA_DB_PATH", DEFAULT_DB_PATH)

if not os.path.exists(DB_PATH) and os.path.exists("db.sqlite3"):
    DB_PATH = "db.sqlite3"

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
def get_recent_whatsapp_summary():
    """Lê as últimas 10 conversas do banco de dados Django (WhatsApp) e retorna um resumo."""
    try:
        if not os.path.exists(DB_PATH):
            return f"❌ Erro: O arquivo do banco de dados não foi encontrado em {DB_PATH}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query to fetch the last 10 messages from ChatHistory
        # Adjust table name 'whatsapp_gateway_chathistory' if needed based on app name
        query = """
            SELECT sender, original_message, ai_response, timestamp 
            FROM whatsapp_gateway_chathistory 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "📭 Nenhuma conversa recente encontrada no banco de dados."

        summary = ["📋 **Resumo das Últimas 10 Conversas do WhatsApp:**\n"]
        for row in rows:
            sender, message, response, timestamp = row
            # Format timestamp for better readability
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = str(timestamp)
            
            summary.append(f"- **{time_str}** | {sender}: {message[:50]}... -> IA: {response[:50]}..." if response else f"- **{time_str}** | {sender}: {message[:50]}...")

        return "\n".join(summary)

    except sqlite3.Error as e:
        return f"❌ Erro ao acessar o banco de dados: {e}"
    except Exception as e:
        return f"❌ Erro inesperado: {e}"

# Auto-update configuration
CURRENT_VERSION = "1.0.0"
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
