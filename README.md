# 💡 Strobo Pro - Console de Iluminação Virtual

[![Python Version](https://img.shields.io/badge/python-3.12-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

O **Strobo Pro** é um software de controle de iluminação virtual projetado para transformar telões de LED e projetores em dispositivos de strobo dinâmicos. Desenvolvido para suprir demandas de eventos e cultos, ele oferece uma alternativa de baixo custo com recursos profissionais de sincronização rítmica.

## 🚀 Funcionalidades Principais
<img width="1366" height="727" alt="image" src="https://github.com/user-attachments/assets/d59ffbaf-e120-49d2-9816-64fb2cd69096" />



*   **BPM Sync (Tap Tempo):** Algoritmo de precisão para sincronizar flashes com o bumbo da música em tempo real via thread dedicada.
*   **Color Strobe:** Paleta de cores integrada (Azul, Âmbar, Vermelho, Roxo) para adequar o visual ao "clima" do ambiente.
*   **Gestão de Intensidade:** Slider para limitar o brilho máximo (essencial para o conforto visual da congregação).
*   **Suavidade (Fade Out):** Controle dinâmico da velocidade de extinção da luz, permitindo efeitos desde cortes secos até pulsações suaves.
*   **Overlay Multi-Monitor:** Detecção automática de todos os monitores e projeções conectados, aplicando a camada de strobo sem interferir na operação do software de letras (ex: Holyrics).

## 🛠️ Especificações Técnicas

*   **Linguagem:** Python 3.12.
*   **Interface Gráfica:** Tkinter com design customizado em Dark Mode.
*   **Concorrência:** Uso de `threading` para manter o metrônomo do BPM independente da interface principal.
*   **Captura de Eventos:** Biblioteca `pynput` para garantir que os atalhos funcionem mesmo quando a janela não está em foco.
*   **Portabilidade:** Compilação otimizada via PyInstaller com suporte a recursos embutidos (`_MEIPASS`).

## ⌨️ Atalhos de Operação

| Tecla | Função | Descrição |
| :--- | :--- | :--- |
| **I** | Instant | Flash máximo enquanto pressionado |
| **J** | Fade | Flash com decaimento suave (Suavidade) |
| **T** | Tap Tempo | Sincroniza o BPM com o ritmo da música |
| **B** | Blackout | Corte de segurança (apaga tudo) |
| **S** | Stop | Para a pulsação automática do BPM |
| **R** | Reset | Zera o contador e limpa os estados |

## 📦 Como Compilar

Para gerar o executável único com o ícone e a logo embutidos:

```powershell
pyinstaller --noconsole --onefile --icon="strobo-pro.ico" --add-data "Aplicação#11.png;." --add-data "strobo-pro.ico;." strobo.py
