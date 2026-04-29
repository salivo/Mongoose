# 🐍 Mongoose – TZONATOR 2.0

Python-based tool designed for Monge's projection (Descriptive Geometry). It accelerates the drafting process by automating repetitive tasks and complex calculations.

The tool generates perfectly scaled SVG files that ensure high precision. When printed and traced over (e.g., using a technical pen or pencil), the final result is significantly more accurate and cleaner than a traditional hand drawing.

---

## 📦 Requirements

- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (comes with Python)
- (Optional) [Git](https://git-scm.com/) – if you’re cloning the repo

---

## ⚙️ Installation

### 1. Clone or Download
```bash
git clone git@github.com:salivo/Mongoose.git
cd Mongoose
```

### 2. Create a Virtual Environment

#### Linux / macOS
```bash
python3 -m venv env
source env/bin/activate
```

#### Windows (PowerShell)
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Mongoose processes `.mgs` scene files containing definitions and visualizes them interactively. You can open a project by passing it as a command line argument:

```bash
python main.py tests/4_perpendicular.mgs
```

---

## ⌨️ Keyboard Shortcuts

### Project Management
| Shortcut | Action |
| :--- | :--- |
| **Ctrl + N** | New Project |
| **Ctrl + O** | Open Project (`.mgs`) |
| **Ctrl + S** | Save Project |
| **Ctrl + E** | Export to SVG (Prompts for Project Name & Work Number) |

### Geometry Tools
| Shortcut | Tool | Selection Required |
| :--- | :--- | :--- |
| **P** | **Create Point** | None (Prompts for coords) |
| **L** | **Create Line** | 2 Points |
| **C** | **Create Circle** | 1 Point (Center) |
| **O** | **Create Ellipse** | 3 Points (Center, Major Axis, Point on Ellipse) |
| **N** | **Create Plane** | None (Prompts for coords) |
| **S** | **Split Line** | 1 Line + 1+ cutting points/lines |
| **I** | **Intersect** | 2 Objects (Line/Circle/Plane) |
| **J** | **Parallel** | 1 Point + 1 Line |
| **R** | **Perp. Point** | 1 Point + 1 Line (Creates perp. at distance) |
| **F** | **Foot of Perp.** | 1 Point + 1 Line (Creates projection) |
| **D** | **Circle Range** | 1 Circle + 2 Points (Sets start/end angles) |
| **E** | **Extend Line** | 1 Line (Move mouse to set visual length, click to confirm) |

### Editing & History
| Shortcut | Action | Selection Required |
| :--- | :--- | :--- |
| **Ctrl + Z** | Undo last action | - |
| **Ctrl + Y** | Redo last action | - |
| **Delete** | **Destructive Delete** | Any object(s) |
| **H** | **Hide (Non-destructive)** | Any object(s) |
| **V** | **Style Popup** | Any object(s) |
| **Escape** | Clear selection | - |

### Navigation
- **Left Mouse Click**: Select object.
- **Ctrl + Left Click**: Add/Remove from selection.
- **Mouse Wheel**: Zoom in/out.
- **Middle Mouse Click + Drag**: Pan the canvas.

---