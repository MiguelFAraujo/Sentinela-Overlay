# Overlay Pop-Up – Sentinela

Sistema de overlay inteligente desenvolvido em Python, com HUD persistente,
gerenciamento de estado via JSON e empacotamento em executável Windows.

## 🚀 Funcionalidades
- Overlay flutuante
- Persistência de memória (JSON)
- HUD interativo (PyQt6)
- Build em .exe com PyInstaller

## 📦 Requisitos
- Python 3.10+
- Windows

## 🔧 Instalação
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Execução
```bash
python sentinela_hud.py
```

## 🏗️ Build
```bash
pyinstaller "Sentinela Pro.spec"
```
O executável será gerado na pasta `dist/`.

## 📁 Estrutura
- `brain/`: Lógica central (mock)
- `sentinela_hud.py`: Entry point da aplicação
- `memory.json`: Persistência de dados
- `sentinela_config.json`: Configurações do HUD

## ⚠️ Observações
Não subir `.venv`, `build` ou arquivos temporários para o repositório.

## 👨‍💻 Sobre o Autor
Desenvolvido por **Miguel Araújo**.

Este projeto nasceu da necessidade de criar uma ferramenta de **Overaly e HUD (Heads-Up Display)** leve, eficiente e independente, focado em **monitoramento em tempo real** e **segurança defensiva (EDR)**. A ideia é ter um "Sentinela" digital sempre ativo, garantindo visibilidade e controle sem impactar a performance do sistema.

📧 **Contato:** [LinkedIn](https://www.linkedin.com/in/miguel-araujo/) *(Insira seu link real aqui se for diferente)*
🔗 **Portfólio:** [GitHub](https://github.com/MiguelFAraujo)
