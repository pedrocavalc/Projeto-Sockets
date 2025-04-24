# Projeto-Sockets

# 🕹️ Seega - Jogo de Tabuleiro Multiplayer em Python

Este projeto é uma implementação multiplayer do jogo de tabuleiro **Seega**, usando **Tkinter** para a interface gráfica e **sockets** para comunicação cliente-servidor.

---

## 📦 Tecnologias Utilizadas

- 🐍 Python 3
- 🎨 Tkinter (GUI)
- 🔌 Sockets (TCP/IP)
- 🧠 Lógica de jogo customizada

---

## 🎮 Regras Básicas do Seega

- O tabuleiro é 5x5.
- Fase 1: cada jogador posiciona suas 12 peças alternadamente (2 por turno).
- Fase 2: os jogadores movem peças uma casa por vez (horizontal/vertical).
- Capturas ocorrem quando uma peça inimiga é cercada por duas suas (linha ou coluna).
- Vitória ocorre se:
  - Um jogador perder todas as peças,
  - Um jogador fizer uma linha/coluna com 5 peças,
  - O oponente desistir.

---

## 🚀 Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seega-python.git
cd seega-python
```
### 2. Requisitos
Python 3.9+

Tkinter (já incluso com Python padrão)

### 3. Executar o servidor
```bash
python server.py
```

### 4. Executar os clientes de maneira separadas
```bash
python ui.py
```

### Rodar por arquivo .exe (OPCIONAL)

- Os jogos podem ser rodados pelos executaveis dentro da pasta `dist`, rode primeiro o servidor.exe e após isso abra duas janelas para os clientes.
