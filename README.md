# Fanfic Bookmaker

Fanfic Bookmaker is a small free compiler for scene-based writing repositories.

It reads the structure you already use:

- `chapters.yml` at the repo root
- one chapter YAML file per chapter in `chapters/`
- one Markdown file per scene in `scenes/`

Then it generates:

- one HTML and one DOCX file per chapter
- one full-book HTML and one full-book DOCX file
- a shared CSS file for the HTML exports

The generated files go into `outputs/` in the writing repo.

## What this project does

This repository is the reusable compiler. You keep your writing in a separate repo, and that repo runs this compiler from GitHub Actions.

The compiler is free to use because it relies on:

- GitHub Actions on public repositories, which are free
- Python packages from PyPI, which are free
- no paid conversion service

If your writing repo is private and you want to avoid paid GitHub Actions minutes, use a self-hosted runner on your own machine. I explain both options below.

## Expected input structure

Your writing repo should look like this:

```text
writing-repo/
  chapters.yml
  chapters/
    hogwarts.yml
    aftermath.yml
    burial.yml
  scenes/
    the-great-hall.md
    extraction.md
    the-visit.md
```

`chapters.yml`:

```yaml
chapters:
  - hogwarts
  - aftermath
  - burial
```

`chapters/aftermath.yml`:

```yaml
chapter:
  name: Aftermath
  scenes:
    - name: "The Great Hall"
      file: the-great-hall
    - name: "Extraction"
      file: extraction
    - name: "The Visit"
      file: the-visit
```

`scenes/the-visit.md` can contain Markdown and embedded HTML.

## What gets generated

For each chapter, the compiler writes:

- `outputs/chapters/<chapter-slug>.html`
- `outputs/chapters/<chapter-slug>.docx`

For the whole book, it writes:

- `outputs/book.html`
- `outputs/book.docx`

It also writes:

- `outputs/assets/style.css`
- `outputs/spellcheck-report.md`
- `outputs/spellcheck-report.json`

## What the exports look like

- Chapter HTML starts with the chapter title, then each scene title as a section heading.
- Book HTML starts with the book title, then chapter headings, then scene headings.
- DOCX files follow the same structure and preserve common Markdown formatting.

## What is supported

The compiler supports the usual Markdown elements:

- headings
- paragraphs
- bold and italic
- links
- inline code and code blocks
- lists
- blockquotes
- tables
- raw HTML in the source Markdown

Embedded HTML is passed through to HTML output. In DOCX output, common HTML tags are converted when possible.

## What is not perfect yet

DOCX conversion is intentionally practical rather than perfect. Very custom HTML may not translate exactly into Word formatting. If you use unusual tags, the HTML export will be more faithful than the DOCX export.

That is a normal tradeoff for a free, automated tool.

## Optional config file

You can add a top-level `fanfic.yml` file in the writing repo.

Example:

```yaml
title: My Fanfiction Book
author: Your Name
subtitle: A helpful extra line under the title
language: en-GB
```

If this file is missing, the compiler still works. It falls back to:

- title: `Untitled Book`
- language: `en-GB`
- empty author and subtitle

## How to use this in a writing repo

### 1. Add this compiler repo as a GitHub Action source

After you publish this repository to GitHub, note its owner and repository name.

For example, if the repo is:

- `https://github.com/SceneBasedFF/fanfic-bookmaker`

then the action reference will be:

- `SceneBasedFF/fanfic-bookmaker@v1`

Later, when you are happy with the first version, create a release tag like `v1` so your writing repos can pin to a stable version.

### 2. Add a workflow to the writing repo

Create `.github/workflows/build-books.yml` in the writing repo with this content:

```yaml
name: Build books

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Check out writing repo
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Compile exports
        uses: SceneBasedFF/fanfic-bookmaker@v1
        with:
          config-file: fanfic.yml
          output-dir: outputs

      - name: Upload exports
        uses: actions/upload-artifact@v4
        with:
          name: book-exports
          path: outputs
```

That workflow does three things:

- runs automatically after a push to `main`
- generates the exports into `outputs/`
- uploads the generated files as a downloadable artifact

You do not have to commit generated outputs to the writing repo. In fact, I recommend not committing them by default if they are always generated from source. Keeping them as workflow artifacts makes the history cleaner and avoids accidental edit loops.

If you specifically want the generated files checked into the repo, you can add a commit step later. It is optional, not required.

### 3. Push the workflow

Commit the workflow file to the writing repo and push it to GitHub.

When the workflow runs, it will create or update the exports in `outputs/`.

## GitHub configuration you need

### If the writing repo is public

This is the easiest setup and the most likely to stay free.

1. Make the repository public.
2. Use the workflow above.
3. Make sure repository Actions are enabled.

Public repositories on GitHub Actions are free within GitHub's standard limits.

### If the writing repo is private

If you want to avoid paid GitHub-hosted minutes, use a self-hosted runner on your own computer.

That means:

1. Install the GitHub Actions runner on your machine.
2. Register it with the writing repo.
3. Change `runs-on: ubuntu-latest` to your self-hosted runner label.

This keeps the build free because the work happens on your own hardware.

## Local use

You can also run the compiler locally if you want to test before pushing.

### 1. Install Python dependencies

From this compiler repo:

```bash
python -m pip install -e .
```

### 2. Run the compiler against a writing repo

```bash
python -m fanfic_bookmaker --root /path/to/writing-repo
```

You can also pass a custom config file:

```bash
python -m fanfic_bookmaker --root /path/to/writing-repo --config-file fanfic.yml --output-dir outputs
```

## British English spelling and grammar

I did not hard-wire a heavy grammar service into the first version, because you asked for a free solution and this part is optional.

The simplest free next step is to add a separate spellcheck job later, for example using:

- the bundled spellcheck report this project now generates
- or a stricter external checker such as `aspell` with the `en_GB` dictionary

If you want, I can add that as a follow-up after you try the export pipeline once.

## How the compiler works internally

The compiler does this in order:

1. Reads `chapters.yml` to get chapter order.
2. Reads each `chapters/<chapter>.yml` file.
3. Reads each referenced scene Markdown file from `scenes/`.
4. Builds chapter Markdown with chapter and scene headings.
5. Builds book Markdown with book, chapter, and scene headings.
6. Renders HTML from Markdown.
7. Renders DOCX from the same content.
8. Writes everything into `outputs/`.

## Repository files in this project

- `src/fanfic_bookmaker/cli.py` - command line entry point
- `src/fanfic_bookmaker/compiler.py` - parsing, validation, rendering, output generation
- `action.yml` - GitHub Action definition
- `requirements.txt` - runtime dependencies
- `pyproject.toml` - package metadata

## Troubleshooting

### The workflow says a scene file is missing

Check that the scene file exists in `scenes/` and that the chapter YAML references the filename without `.md`.

### The workflow says `chapters.yml` is missing

Make sure `chapters.yml` exists at the root of the writing repo.

### The workflow runs but nothing changes

That usually means the generated exports are identical to the previous run.

### DOCX formatting looks plain

That is expected at first. The output is still valid Word format, but the styling is intentionally minimal and reliable.

## Next improvements you can add later

1. Custom chapter and book templates.
2. A dedicated title page.
3. A more advanced British English spellcheck job.
4. Custom front matter and back matter.
5. Extra formatting rules for special HTML in scene files.

## Spellcheck report

The compiler now generates a report even when spellcheck finds problems. It does not stop the export.

The report files are:

- `outputs/spellcheck-report.md`
- `outputs/spellcheck-report.json`

Each finding includes:

- chapter
- scene
- line
- the exact word written
- the suggested replacement
- a small context snippet from the line

You can turn spellcheck off in `fanfic.yml` if you want:

```yaml
spellcheck:
  enabled: false
```

You can also ignore custom names or terms:

```yaml
spellcheck:
  enabled: true
  ignore_words:
    - Hogwarts
    - Hermione
```
