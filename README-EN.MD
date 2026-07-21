# Win OpenSSL Mirror Repository

> 🌐 中文文档：[README.MD](README.MD)

## About This Repository

This repository is an **index of OpenSSL installers for Win32 / Win64 / ARM / Universal platforms**. The repository itself **stores no binary files** — all installers are distributed exclusively via GitHub Releases, and the repo only keeps documentation and a release index, so a clone is tiny and contains no exe/msi.

> Official homepage: [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
> Download: Get each version's installers from its `GitHub Release` page

### Purpose

1. **Release index** — Centralize the GitHub Release page for every OpenSSL version, so a clone gives you one record to find the download entry.
2. **Faster access in China** — Provide a reachable download entry via GitHub Releases, solving slow and unstable downloads from the overseas official site.
3. **Unified version archive** — Archive by Release tag per version, so `git checkout <version>` retrieves the corresponding release index.
4. **Traceable provenance** — The `From` column of every release record (and the Release notes table) keeps the original official download URL so file sources can be verified.

## Repository File Structure

A clone of this repository contains **only the following 4 files** and no exe/msi binary installers:

```
Repository root
├─ openssl_link_gen.py     # Generate official download links for all architectures of a version
├─ git_release_openssl.py  # Create GitHub Releases, upload installers, sync release records
├─ README.MD               # Documentation (Chinese)
└─ README-EN.MD            # Documentation (English)
```

> Installer binaries are uploaded to GitHub Releases by `git_release_openssl.py` and are **never committed to the Git repository**. After cloning, if you need an installer, go to its version's Release page — the `## Release History` section provides a clickable link for each version.

## Companion Python Scripts

Two companion automation scripts are provided at the repository root, used respectively to **generate download links and create GitHub Releases with synced release records**:

| Script | Purpose |
| --- | --- |
| `openssl_link_gen.py` | Generate the official download-link list for all architectures of a given version |
| `git_release_openssl.py` | Create a GitHub Release for the given version, upload installer assets, insert a clickable release record into the docs, commit, tag, and push branch & tags |

> Before using the scripts, Python3 and Git must be installed locally, and the Git user name / email must be configured.

### 1. Script `openssl_link_gen.py`

#### Function

Given an OpenSSL version number, prints the official download-link list for all architectures (Win32 / Win64 / Win64ARM / WinUniversal). Useful for verification, manual download, or auditing.

#### Usage

```
# Example: generate all architecture download links for version 3_0_21
python openssl_link_gen.py 3_0_21
```

Example output:

```
https://slproweb.com/download/Win64OpenSSL_Light-3_0_21.exe
https://slproweb.com/download/Win64OpenSSL_Light-3_0_21.msi
https://slproweb.com/download/Win64OpenSSL-3_0_21.exe
https://slproweb.com/download/Win64OpenSSL-3_0_21.msi
...
```

### 2. Script `git_release_openssl.py`

#### Function

1. Given one or more OpenSSL version numbers, automatically generate official download links for all architectures (Win32 / Win64 / Win64ARM / WinUniversal) of each version.
2. Recursively scan the repository (current directory by default; use `-p/--paths` for multiple directories) and detect all installers of that version.
3. Call the GitHub CLI (`gh release create`) to create a Release for the version and upload all installers as assets.
4. The release notes (`--notes`) is a Markdown table listing each installer's `name` and its official download URL `From`.
5. Insert a clickable record (linking to the corresponding Release page) into the "Release History" section of `README.MD` / `README-EN.MD`.
6. Commit the doc change (release record) to Git, create an annotated tag named after the version, then push the branch and tags — keeping the Git repository consistent with the GitHub Release. Installers are uploaded only to the GitHub Release and never committed to Git.

#### Usage

1. Requirements: Python3, Git, and the GitHub CLI (`gh`) installed locally, with `gh auth login` completed.
2. Open a terminal, navigate to the repository root, and run (version numbers use underscores; multiple versions are space-separated):

```
# Example: create Releases and upload installers for multiple versions
python git_release_openssl.py 1_1_1w 3_0_21 3_3_7 3_4_6 3_5_7 3_6_3 4_0_1

# Example: specify multiple scan directories (use -p/--paths, one or more; missing paths are skipped)
python git_release_openssl.py 3_0_21 -p 3_0_21 other_dir
```

> One or more versions may be given. The path option `-p/--paths` is optional and defaults to the current directory. Files matched by multiple versions/paths are de-duplicated automatically. Versions that already have a Release are skipped.

1. After execution, a release record is inserted into the docs, the change is committed and tagged with the version, and the branch & tags are pushed to the remote.

### File Types Matched by the Scripts

The scripts above auto-detect all of the following architectures and package types:

- Win32 / Win64 / Win64ARM standard & Light editions, `.exe` / `.msi`
- WinUniversal standard & Light editions, `.exe` (this architecture has no msi package)

## Release History

The repository contains no binary files. Click a link to download each version's installers from its GitHub Release page. This table is auto-populated by `git_release_openssl.py` after each release (newest on top).

| Version | Release |
| --- | --- |
| 3_5_7 | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/3_5_7) |
| 3_4_6 | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/3_4_6) |
| 3_3_7 | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/3_3_7) |
| 3_0_21 | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/3_0_21) |
| 1_1_1w | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/1_1_1w) |

## Important Notes

1. **Copyright** — All OpenSSL binaries are copyrighted by slproweb. This repository distributes installers via GitHub Releases as a mirror for personal offline archiving only; do not use it for commercial distribution.
2. **File verification** — Before downloading and using, it is recommended to verify the official file hashes to ensure integrity and that files have not been tampered with.
3. **Docs only in the repo** — The repository never commits binary installers; installers are distributed only via GitHub Releases, and Git commits contain only documentation / info changes.
4. **Version naming rule** — Version numbers uniformly use underscores (e.g. `3_0_21`), not dots.
5. **GitHub Release sync** — `git_release_openssl.py` relies on the GitHub CLI (`gh`) and requires `gh auth login` first. Each run inserts a clickable release record into the docs, auto-commits (docs only), creates an annotated tag named after the version, and pushes the branch & tags — keeping the Git repository consistent with the GitHub Release.

## Official Links

- Win OpenSSL product homepage: [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
