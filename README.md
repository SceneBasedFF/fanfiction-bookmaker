# Fanfic Bookmaker

Fanfic Bookmaker compiles a scene-based writing repository into:

- chapter HTML files
- chapter DOCX files
- one full-book HTML file
- one full-book DOCX file
- a shared CSS file

This README is intentionally local-only. It explains how to install Python on Windows and run the compiler on your own machine.

## Prerequisites (Windows)

1. Install Python 3.11 or newer.
2. Make sure `python` works in PowerShell.

### Option A: Install Python with winget

Open PowerShell and run:

```powershell
winget install -e --id Python.Python.3.11
```

Then verify:

```powershell
python --version
python -m pip --version
```

### Option B: Install Python from python.org

1. Download Python 3.11+ from https://www.python.org/downloads/windows/
2. Run the installer.
3. Important: check `Add python.exe to PATH` during install.
4. Open a new PowerShell window and verify:

```powershell
python --version
python -m pip --version
```

## Expected Writing Repo Structure

Your writing repository should look like this:

```text
writing-repo/
  fanfic.yml
  chapters.yml
  chapters/
    hogwarts.yml
    aftermath.yml
  scenes/
    the-great-hall.md
    extraction.md
```

### chapters.yml example

```yaml
chapters:
  - hogwarts
  - aftermath
```

### chapters/hogwarts.yml example

```yaml
chapter:
  name: Hogwarts
  scenes:
    - name: The Great Hall
      file: the-great-hall
    - name: Extraction
      file: extraction
```

### fanfic.yml example (optional)

```yaml
title: The Boy in the Card
author: Your Name
subtitle: Optional subtitle
language: en-GB
```

If `fanfic.yml` is missing, defaults are used.

## Local Setup

Run these commands in PowerShell from this repository folder.

```powershell
cd C:\Users\ana.claudia.martins\Documents\fanfiction-bookmaker

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .
```

## Run The Compiler Locally

Set your writing repo path and run:

```powershell
$writingRepo = 'C:\path\to\your-writing-repo'

.\.venv\Scripts\python.exe -m fanfic_bookmaker --root $writingRepo --config-file fanfic.yml --output-dir outputs
```

### Example with your current paths

```powershell
cd C:\Users\ana.claudia.martins\Documents\fanfiction-bookmaker
$writingRepo = 'C:\Users\ana.claudia.martins\Documents\the-boy-in-the-card'

.\.venv\Scripts\python.exe -m fanfic_bookmaker --root $writingRepo --config-file fanfic.yml --output-dir outputs
```

## Output Files

The compiler writes files into `outputs/` inside your writing repo:

- `outputs/assets/style.css`
- `outputs/chapters/ch01-<chapter-name>.html`
- `outputs/chapters/ch01-<chapter-name>.docx`
- `outputs/<book-title>.html`
- `outputs/<book-title>.docx`

Chapter titles are numbered in the generated documents, for example `Chapter 1: Hogwarts`.

## Rebuild Quickly

For later runs, you only need:

```powershell
cd C:\Users\ana.claudia.martins\Documents\fanfiction-bookmaker
.\.venv\Scripts\Activate.ps1

$writingRepo = 'C:\path\to\your-writing-repo'
.\.venv\Scripts\python.exe -m fanfic_bookmaker --root $writingRepo --config-file fanfic.yml --output-dir outputs
```

## Troubleshooting (Local)

### `python` is not recognized

1. Reopen PowerShell.
2. Verify Python installation.
3. If needed, reinstall Python and ensure `Add python.exe to PATH` is checked.

### PowerShell script execution is blocked

If venv activation is blocked, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Close and reopen PowerShell, then activate venv again.

### Missing scene or chapter file errors

- Make sure `chapters.yml` exists at writing repo root.
- Make sure each chapter slug in `chapters.yml` has a matching file in `chapters/`.
- Make sure each scene `file` has a matching Markdown file in `scenes/`.

### Build succeeds but outputs do not change

Generated files are rewritten each run. If content is unchanged, outputs may look the same.
