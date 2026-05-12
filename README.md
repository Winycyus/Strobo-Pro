💡 Strobo Pro - Console de Iluminação Virtual
O Strobo Pro é um software de controle de iluminação virtual desenvolvido em Python, projetado especificamente para ambientes de eventos e igrejas que utilizam telões de LED ou projeções. Ele transforma a saída de vídeo em um strobo dinâmico e sincronizado, oferecendo uma alternativa acessível e altamente personalizável aos equipamentos de hardware tradicionais.

🚀 Funcionalidades Principais
BPM Sync (Tap Tempo): Algoritmo que permite sincronizar os flashes com o ritmo da música em tempo real através de uma thread dedicada.

Controle de Color Strobe: Paleta de cores integrada para adaptar o clima visual ao contexto do evento (Azul, Âmbar, Vermelho, etc.).

Gestão de Intensidade e Suavidade: Sliders em tempo real para ajustar o brilho máximo e a velocidade do fade out, garantindo o conforto visual da congregação.

Overlay Universal: Sistema que detecta automaticamente todos os monitores conectados e aplica a camada de strobo de forma sobreposta.

Atalhos Rápidos: Mapeamento de teclado global (Hotkeys) para operações críticas como Blackout de segurança, Reset e Stop.

🛠️ Especificações Técnicas
Linguagem: Python 3.12.

Interface Gráfica: Tkinter (Customizada em Dark Mode Amarelo/Preto).

Concorrência: Utilização de threading para o metrônomo do BPM, garantindo que a interface permaneça responsiva durante a pulsação.

Manipulação de Hardware: Integração com pynput para captura de eventos de teclado e screeninfo para gerenciamento de múltiplos monitores.

Distribuição: Compilado via PyInstaller com suporte a caminhos de recursos dinâmicos (_MEIPASS) para portabilidade em executável único.

📖 Como Usar
Baixe o executável na aba Releases.

Execute o strobo.exe como Administrador.

Utilize o botão Tap Tempo (T) no ritmo da música para iniciar a sincronia automática.

Ajuste a Intensidade conforme a sensibilidade do ambiente.

🎓 Contexto Acadêmico
Este projeto foi desenvolvido por Kauã Winycyus, estudante de Engenharia de Software na UFLA (Universidade Federal de Lavras), como uma solução prática para desafios reais de operação de mídia em ambientes litúrgicos e eventos de grande porte.
