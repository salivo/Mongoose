# 🐍 Mongoose – TZONATOR 2.0

Mongoose – TZONATOR 2.0 is a Python-based tool for working with **TZO (technical geometric objects)**.  
This guide helps you install and run the project on **Linux, macOS, or Windows**.

---

## 📦 Requirements

- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (comes with Python)
- (Optional) [Git](https://git-scm.com/) – if you’re cloning the repo

> ⚠️ Make sure Python and pip are available in your terminal:  
> ```bash
> python --version
> pip --version
> ```

---

## ⚙️ Installation

### 1. Clone or Download
```bash
git clone https://github.com/<your-username>/mongoose-tzonator.git
cd mongoose-tzonator
````

*(Or download the ZIP from GitHub and extract it.)*

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

> 📝 If `Activate.ps1` is blocked on Windows, run PowerShell as Administrator and execute:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process RemoteSigned
> ```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Mongoose processes `.mgs` scene files containing TZO (Technical Geometric Objects) definitions and visualizes them interactively. It supports creating points, lines, circles, planes, and geometric constructions like intersections, perpendiculars, and parallels.

### Basic Visualization

Run Mongoose with an input `.mgs` scene file to open an interactive visualization window:

```bash
python main.py tests/4_perpendicular.mgs
```

> On Linux/macOS use `python3` if `python` points to Python 2.x:
>
> ```bash
> python3 main.py tests/4_perpendicular.mgs
> ```

The visualization window allows you to view and interact with the geometric scene. The file watcher automatically reloads the scene when you modify the `.mgs` file.

### SVG Export

To export the geometric visualization to SVG format:

```bash
python main.py tests/4_perpendicular.mgs --export output.svg
```

You can also specify a work name and offsets:

```bash
python main.py work/mywork.mgs --export output.svg --name "Geometric Study 1" -x 10 -y 5
```

### Available Arguments

To see all available command-line arguments:

```bash
python main.py --help
```

**Arguments:**
- `file` — Path to the input `.mgs` scene file
- `--export <path>` — Export to SVG file (e.g., `output.svg`)
- `-n, --name <name>` — Name of the work (appears on exported SVG)
- `-x, --offset_x <value>` — X-axis offset for export
- `-y, --offset_y <value>` — Y-axis offset for export

### Configuration

Mongoose uses a configuration file to customize export behavior and personal information. The configuration file should be named `config.conf` and placed in either:
- The project root directory (`config.conf`), or
- Inside the `work/` directory (`work/config.conf`) for project-specific settings

#### Configuration File Format

```ini
[me]
lastname = Lastname
class = 4.X

[export]
point_style = dot
# Options: dot | plus

hiddenlines_style = normal
# Options: normal | none
```

#### Configuration Options

**`[me]` section** — Personal information for SVG exports:
- `lastname` — Your last name (appears on exported SVGs)
- `class` — Your class designation (appears on exported SVGs)

**`[export]` section** — Visual style options for SVG exports:
- `point_style` — How points are rendered
  - `dot` — Filled circles
  - `plus` — Plus symbols
- `hiddenlines_style` — How hidden/construction lines are displayed
  - `normal` — Show hidden lines with standard styling
  - `none` — Hide hidden lines in export

---
