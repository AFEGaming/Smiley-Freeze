# Smiley Freeze

A lightweight **Windows-only Python macro** that temporarily suspends
foreground or whitelisted applications by **suspending processes or specific threads**.

Designed for experimentation, learning, and offline use cases where precise
application freezing is required.

---

## ✨ Features
- Hold **or** Toggle freeze modes
- Freeze **foreground window** automatically
- Executable-based **whitelist system**
- Optional timeout handling while holding hotkey
- GUI-based whitelist picker (visible GUI apps only)
- Advanced **thread-level suspension mode**
- Safe resume logic to prevent permanent freezes
- Configuration stored in JSON

---

## 🖥 Requirements
- Windows 10 / Windows 11
- Python **3.9+**
- Administrator privileges (recommended)

---

## 📦 Installation

[Click here to download as an exe file](https://github.com/AFEGaming/Smiley-Freeze/releases/download/Relase/Process_Thread_Suspension.exe)

### OR

Install dependencies:

```bash
pip install psutil keyboard pywin32
````

Clone the repository:

```bash
git clone https://github.com/USERNAME/smiley-freeze.git
cd smiley-freeze
```

Build the file

```bash
pyinstaller --onefile --noconsole Process_Thread_Suspension.py
```

---

## ▶ Usage

Run the script:

```bash
python Process_Thread_Suspension.py
```

On first launch, a configuration file will be created automatically:

```
SmileyConf.json
```

---

## ⚙ Configuration

All settings are stored in `SmileyConf.json`.

You can configure:

* Freeze mode (hold / toggle)
* Whitelisted executables
* Scan interval
* Timeout duration
* Thread-based suspension targets (advanced)

⚠ Thread mode is intended for **advanced users only**.

If you still want to use it, this program will be help a lot.
https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer

Incorrect thread suspension may cause application instability.

---

## ⚠ Important Warnings

* Suspending **system or critical processes can crash applications or Windows**
* Do **not** use with applications protected by anti-cheat systems
* Intended for **offline, experimental, or educational use only**
* Use at your own risk

---

## 📚 Educational Notice

This project is provided for **educational and experimental purposes only**.
It demonstrates low-level Windows process and thread suspension techniques.

The author assumes **no responsibility** for misuse or damage caused by this software.

---

## 📜 License

GNU General Public License v3.0 (GPL-3.0)
