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

Run TZONATOR with an input `.mgs` file:

```bash
python main.py tests/3_perpendicular.mgs
```

> On Linux/macOS use `python3` if `python` points to Python 2.x:
>
> ```bash
> python3 main.py tests/3_perpendicular.mgs
> ```

To export the result to SVG:

```bash
python main.py work/kc-x.mgs --export output.svg
```

to see all available arguments:

```bash
python main.py --help
```

---
