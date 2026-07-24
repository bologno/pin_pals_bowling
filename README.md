# pin_pals_bowling
Back End service for bowling score service.

# Project Name

A short description of your project.

## Requirements Setup with pyenv

Follow these steps to set up the correct Python version and install project dependencies.

### 1. Install Build Dependencies
Before installing a Python version via `pyenv`, ensure your system has the required build tools:
- **Ubuntu/Debian:** `sudo apt update && sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git`
- **macOS:** `brew install openssl readline sqlite3 xz zlib tcl-tk`

### 2. Install Python Version
Install the specified Python version for this project (e.g., `3.12.6`):
```bash
pyenv install 3.12.6
pyenv local 3.12.6
```

### 3. Install Project Requirements
Upgrade pip and install the dependencies from your `requirements.txt` file:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## MIT License

Copyright (c) [Year] [FullName/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
