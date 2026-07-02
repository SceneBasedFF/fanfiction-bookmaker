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
    - name: 'The Great Hall'
      file: the-great-hall
    - name: 'Extraction'
      file: extraction
    - name: 'The Visit'
      file: the-visit
```

`scenes/the-visit.md` can contain Markdown and embedded HTML.

## What gets generated

For each chapter, the compiler writes:

- `outputs/chapters/ch01-<chapter-name>.html`
- `outputs/chapters/ch01-<chapter-name>.docx`

For the whole book, it writes:

- `outputs/<book-title>.html`
- `outputs/<book-title>.docx`

It also writes:

- `outputs/assets/style.css`

## What the exports look like

- Chapter HTML starts with numbered chapter titles such as `Chapter 1: Hogwarts`, then each scene title as a section heading.
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

You do not run this repository directly on your writing repo. Instead, your writing repo adds a tiny workflow that calls the reusable workflow in this repository.

### What the workflow does

The reusable workflow in this repository:

- checks out the writing repo
- installs Python
- runs `fanfic-bookmaker`
- uploads the generated `outputs/` folder as a GitHub Actions artifact
- can optionally commit `outputs/` back into the writing repo

### The easiest setup path

If this is your first time using GitHub Actions, the simplest approach is:

1. Put this repository on GitHub.
2. Add the workflow file from `examples/writing-repo-workflow.yml` to your writing repo.
3. Let it run on `push` to `main` and on pull requests into `main`.

### 1. Add this repository to GitHub

If you have not already published this compiler repo, push it to GitHub first. For the simplest setup, keep this compiler repo public so the writing repos can call the reusable workflow without permission issues.

You need the repository name for the next step. For example, if the repo URL is:

- `https://github.com/SceneBasedFF/fanfic-bookmaker`

then the reusable workflow reference will be:

- `SceneBasedFF/fanfic-bookmaker/.github/workflows/build-books.yml@main`

You can change `@main` to a release tag later if you want to pin a stable version.

### 2. Add the workflow file to your writing repo

In the writing repo, create this file:

- `.github/workflows/build-books.yml`

Its contents can be copied from [examples/writing-repo-workflow.yml](examples/writing-repo-workflow.yml).

That workflow file is what GitHub watches. When you push to `main`, GitHub starts the job automatically. When you open a pull request into `main`, GitHub can also run it so you can catch problems before merge.

### 3. The exact workflow you want in the writing repo

```yaml
name: Build books

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    uses: SceneBasedFF/fanfic-bookmaker/.github/workflows/build-books.yml@main
    with:
      config-file: fanfic.yml
      output-dir: outputs
      python-version: '3.11'
```

### 4. What each part means

- `push: branches: [main]` means run after a commit lands on `main`.
- `pull_request: branches: [main]` means run when someone opens or updates a pull request aimed at `main`.
- `workflow_dispatch` adds a button in the GitHub Actions page so you can run it manually.
- `uses: .../.github/workflows/build-books.yml@main` tells GitHub to use the reusable workflow from this repository.
- `config-file: fanfic.yml` tells the compiler where to read book settings from.
- `output-dir: outputs` tells it where to write the generated files.

### 5. How to add it on the GitHub website

If you want to do this entirely in the browser, follow these steps in your writing repo:

1. Open the repository on github.com.
2. Click the `Add file` button.
3. Choose `Create new file`.
4. In the file name box, type `.github/workflows/build-books.yml`.
5. Paste the workflow YAML above into the editor.
6. Scroll down to the commit box.
7. Choose `Commit directly to the main branch` if you are ready.
8. Click `Commit new file`.

If the repository already has a branch-based review flow, you can commit it to a new branch instead and open a pull request.
If GitHub shows a message saying workflows are disabled, click the button that enables Actions for the repository and then retry the commit.

### 6. How to check whether it worked

After the commit lands on `main`:

1. Open the writing repo on GitHub.
2. Click the `Actions` tab.
3. Click the `Build books` workflow run.
4. Open the latest job.
5. Look for the `Upload exports` step.

If the job succeeds, the generated files are attached to the run as an artifact named `book-exports`.

### 7. If you want the outputs committed back into the repo

The default setup uploads artifacts only. That is usually the safest choice because it avoids Git history loops.

If you want the generated HTML and DOCX files committed back into the writing repo, use the reusable workflow with `commit-outputs: true`.

The commit version is in [examples/writing-repo-workflow-commit.yml](examples/writing-repo-workflow-commit.yml).

That version:

- commits the `outputs/` folder only when the workflow runs on a push
- skips the commit step on pull request runs
- avoids an infinite loop by ignoring push runs that only touch `outputs/`

The exact copy/paste workflow for the writing repo is:

```yaml
name: Build books

on:
  push:
    branches: [main]
    paths-ignore:
      - outputs/**
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    uses: SceneBasedFF/fanfic-bookmaker/.github/workflows/build-books.yml@main
    with:
      config-file: fanfic.yml
      output-dir: outputs
      python-version: '3.11'
      commit-outputs: true
      commit-message: 'chore: update generated book exports'
```

### Click-by-click setup for the commit-back version

Use this if you want GitHub to regenerate and commit the exports automatically.

1. Open your writing repo on github.com.
2. Click `Add file`.
3. Click `Create new file`.
4. Type `.github/workflows/build-books.yml` as the file name.
5. Paste the commit-back workflow above.
6. Scroll to the bottom and click `Commit new file`.
7. Open the repo’s `Settings` tab if GitHub says Actions are not enabled.
8. Make sure repository Actions are allowed.
9. Go back to the repo and open the `Actions` tab.
10. Run the workflow once manually if you want to test it before waiting for a push.

What to look for on each page:

- Settings: look for `Actions` in the left sidebar, then choose `General` or `Actions` depending on what GitHub shows for your repo.
- Actions tab: look for the list of workflow names on the left and recent runs in the middle of the page.
- Workflow run page: look for the job name, then open the latest job and scan the step list until you see `Upload exports` or `Commit generated outputs`.

Two important things to know about this version:

1. It will make the repository history include the generated HTML, DOCX, and CSS files.
2. It is more likely to create noisy history than the artifact-only version, so I recommend starting with artifacts first unless you really want the outputs versioned.
3. The `paths-ignore: outputs/**` line is what prevents an infinite loop: when the workflow commits only files inside `outputs/`, GitHub does not start the workflow again.

### 8. Public vs private repos

For free GitHub-hosted Actions minutes:

- public repos are the easiest path
- private repos may use paid minutes unless you use your own self-hosted runner

If your writing repo is private and you want to keep the build free, the self-hosted runner option is the usual solution.

### 9. Self-hosted runner option

This is only needed if the writing repo is private and you want to avoid GitHub-hosted usage.

That means:

1. Install the GitHub Actions runner on your machine.
2. Register it with the writing repo.
3. Change `runs-on: ubuntu-latest` in the reusable workflow to your runner label.

That keeps the build on your own hardware.

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
3. A separate optional British English spellcheck job.
4. Custom front matter and back matter.
5. Extra formatting rules for special HTML in scene files.
