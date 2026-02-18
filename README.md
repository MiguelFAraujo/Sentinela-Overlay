# 🛡️ Sentinela Pro v1.02

**Overlay de Monitoramento Avançado com Integração AI Local (Ollama/Qwen)**

O **Sentinela Pro** é um HUD (Heads-Up Display) flutuante para Windows que monitora hardware em tempo real (CPU, RAM, GPU) e conecta-se a uma Inteligência Artificial local para análise de contexto e assistência.

![Badge](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Ollama](https://img.shields.io/badge/AI-Ollama-orange)

## 🚀 Novidades v1.02
- **Integração Real com Ollama**: O status "AI" agora reflete a conexão real com o serviço Ollama local.
- **Suporte ao Qwen 2.5**: Configurado por padrão para usar o modelo `qwen2.5:7b` para performance e precisão.
- **Otimizações**: Redução de uso de CPU no monitoramento.
- **Instalador Corrigido**: Falha de caminho _MEIPASS resolvida.

## 📋 Pré-requisitos

1. **Python 3.10+** (para rodar código fonte)
2. **Ollama**: Necessário para a funcionalidade de IA.
   - Baixe em: [ollama.com](https://ollama.com)
   - Instale e execute.
   - Baixe o modelo recomendado:
     ```powershell
     ollama pull qwen2.5:7b
     ```

## 🔧 Instalação e Execução

### Rodando o Executável (Usuário Final)
1. Baixe o instalador `Sentinela Setup.exe` (ou descompacte a pasta `dist`).
2. Execute o instalador.
3. O Sentinela iniciará automaticamente.
4. **Nota**: Certifique-se de que o Ollama está rodando (`ollama serve` ou via systray).

### Rodando do Código Fonte (Desenvolvedor)
1. Clone o repositório:
   ```bash
   git clone https://github.com/MiguelFAraujo/Sentinela-Overlay.git
   cd Sentinela-Overlay
   ```
2. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute:
   ```bash
   python sentinela_hud.py
   ```

## 🏗️ Build (Criar Executável)

Para gerar o `.exe` standalone:

```bash
pyinstaller "Sentinela Pro.spec"
```
O arquivo será gerado em `dist/Sentinela Pro/`.

## ⚙️ Configuração
O arquivo `sentinela_config.json` permite ajustes finos:
```json
{
    "theme": "dark",
    "transparency": 150,
    "llm_model": "qwen2.5:7b" 
}
```
* **llm_model**: Nome do modelo Ollama a ser usado.

## 📁 Estrutura do Projeto
* `sentinela_hud.py`: Entry point e lógica da interface gráfica.
* `brain/`: Pacote contendo lógica de inteligência.
  * `llm.py`: Cliente de conexão com Ollama.
* `setup_wizard.py`: Script criador do instalador.
* `Sentinela Pro.spec`: Especificação de build PyInstaller.

## 🤝 Contribuição
Sinta-se livre para abrir Issues ou Pull Requests.

---
**Desenvolvido por Miguel Araujo**
