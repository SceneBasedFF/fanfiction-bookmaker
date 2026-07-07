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
    chapter1.yml
    chapter2.yml
  scenes/
    scene1.md
    scene2.md
```

### chapters.yml example

```yaml
chapters:
  - chapter1
  - chapter2
```

### chapters/hogwarts.yml example

```yaml
chapter:
  name: Chapter name
  scenes:
    - name: Scene name
      file: scene1
    - name: Scene name
      file: scene2
```

### fanfic.yml example (optional)

```yaml
title: Fanfic title
author: Your Name
description: Short description shown in the repo README
subtitle: Optional subtitle
language: en-GB
```

If `fanfic.yml` is missing, defaults are used.

## Local Setup

Run these commands in PowerShell from this repository folder.

```powershell
cd <path>\fanfiction-bookmaker

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

## Output Files

The compiler writes files into `outputs/` inside your writing repo:

- `README.md` at the writing repo root, containing title, author, description, and a link to the story markdown
- `outputs/assets/style.css`
- `outputs/<book-title>.md`
- `outputs/<book-title>-stats.md`
- `outputs/chapters/ch01-<chapter-name>.html`
- `outputs/chapters/ch01-<chapter-name>.docx`
- `outputs/<book-title>.html`
- `outputs/<book-title>.docx`

Chapter titles are numbered in the generated documents, for example `Chapter 1: Hogwarts`.

## Rebuild Quickly

For later runs, you only need:

```powershell
cd C:\<path>\fanfiction-bookmaker
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

## Automatic Scene File Renaming

During each compile run, scene files are normalized to this naming scheme:

- `Cxx_Sxx_scene-name.md`

Where:

- `Cxx` is the chapter index from `chapters.yml` (for example, `C01`)
- `Sxx` is the scene index inside that chapter file (for example, `S03`)
- `scene-name` is the base scene name in kebab-case (`-` separated)

If a scene contains HTML comments, it is considered in development and gets a `-INC` suffix before `.md`:

- `Cxx_Sxx_scene-name-INC.md`

Examples:

- `C02_S03_scene-name.md` (no HTML comments)
- `C02_S03_scene-name-INC.md` (contains HTML comments / in development)

If scenes move within a chapter, move to another chapter, or chapter order changes, files are automatically renamed on the next run so prefixes stay accurate.

Chapter YAML `file` references are also normalized to the stable base name (for example, `scene-name`) so future reordering continues to work.

Chapter YAML files are also normalized each run to match chapter order:

- `chapters/Cxx_chapter-slug.yml`

If chapter order changes in `chapters.yml`, chapter filenames are automatically renumbered on the next compile run.

### Build succeeds but outputs do not change

Generated files are rewritten each run. If content is unchanged, outputs may look the same.
