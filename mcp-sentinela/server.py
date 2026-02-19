from mcp.server.fastmcp import FastMCP
import psutil
import os
import sqlite3
import datetime

# Database path for WhatsApp Agent
# Verify this path is correct based on your setup
DB_PATH = r"c:\Users\nigel\OneDrive\Documentos\WhatsApp-agent\db.sqlite3"

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

if __name__ == "__main__":
    mcp.run()
