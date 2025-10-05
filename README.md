# 🐍 Sacrifices Must Be Made

A reimagined **Snake Game** built with **Pygame**, themed around choice and sacrifice.  
What will you give up to gain power?

---

## ✨ Features
- Classic Snake gameplay with twists:
  - 🍎 **Apple** → +10 points, snake grows
  - 🛕 **Altar** → Appears every 225 points, offering risky blessings
- **Altar Choices**:
  1. **Embrace Greed** → Gain +1–50 points (snake grows slightly)
  2. **Sacrifice Self** → Remove 3 length, -0.1x multiplier
  3. **Halve Thyself** → Snake shrinks by half, multiplier fixed at 0.5x
  4. **Twisted Fate** → Inverted controls but +1x multiplier (lasts 20s or 100 points)
- ⚡ **Score Multiplier** system that changes based on choices
- 🎶 **Background music** + sound effects (`eat`, `gameover`, `intro`)
- 🖼 **Custom assets**: background, apple, altar, intro screen
- 📊 **Altar Progress Bar** fills as score approaches altar threshold
- Intro menu with **New Game** / **Exit**

---

## 🎮 Controls
- **Arrow keys** → Move snake
- **E** → Interact with altar
- **P** → Pause game
- **R** → Restart after death
- **ESC** → Quit game
- **Enter / Space** → Confirm altar choice / menu selection
- **W/S or ↑/↓** → Navigate altar options / menu

---

## 📦 Requirements
Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## ▶️ Run Game
```bash
python snake.py
```
