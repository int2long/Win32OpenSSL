#!/usr/bin/env python3
"""
git_release_openssl.py

为指定的一个或多个 OpenSSL 版本创建 GitHub Release，
将该版本所有安装包作为 release 资产（assets）上传，并保持 Git 仓库与 Release 一致：

  1. 调用 GitHub CLI 创建 Release 并上传安装包；
  2. Release 说明（--notes）是一张 Markdown 表格：

        | name | From |

     其中 name = 安装包文件名，From = 对应官方原始下载地址（slproweb）；
  3. 在 README.MD / README-EN.MD 的「版本发布记录」中插入一条
     可点击跳转到对应 Release 页面的记录；
  4. 将文档改动（发布记录）提交到 Git，并以版本号创建 annotated 标签；
  5. 推送分支与标签。

注意：安装包二进制文件仅通过 `gh release create` 上传到 GitHub Release，
**绝不纳入 Git 仓库**——Git 仓库只保留说明文档与发布索引，避免仓库体积膨胀。

依赖：本地已安装并登录 GitHub CLI（gh），且当前目录为 Git 仓库。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

# 复用 openssl_link_gen.py 的链接生成逻辑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openssl_link_gen  # noqa: E402

# gh 可执行文件解析：优先 PATH，其次 Windows 常见安装路径
GH_FALLBACK = r"C:\Program Files\GitHub CLI\gh.exe"


def resolve_gh() -> str:
    p = shutil.which("gh")
    if p:
        return p
    if os.path.isfile(GH_FALLBACK):
        return GH_FALLBACK
    return "gh"


GH = resolve_gh()


def find_installers(root_dir: str, target_names: set) -> list:
    """递归查找匹配文件名的安装包，返回相对仓库根（当前工作目录）的正斜杠路径。"""
    matched = []
    if not os.path.isdir(root_dir):
        print(f"[WARN] 路径不存在，已跳过: {root_dir}", file=sys.stderr)
        return matched
    cwd = os.getcwd()
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn in target_names:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, cwd).replace(os.sep, "/")
                matched.append(rel)
    return matched


def build_notes(rows) -> str:
    """rows: list of (name, from_url) -> 生成 release notes 文本。"""
    lines = ["## 更新日志", ""]
    lines.append("| name | From |")
    lines.append("| --- | --- |")
    for name, from_url in rows:
        lines.append(f"| {name} | {from_url} |")
    return "\n".join(lines)


def release_exists(version: str) -> bool:
    r = subprocess.run(
        [GH, "release", "view", version, "--json", "tagName"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return r.returncode == 0


def get_release_url(version: str) -> str:
    """获取 Release 页面 URL：优先用 gh，失败则根据 git remote 推断。"""
    r = subprocess.run(
        [GH, "release", "view", version, "--json", "url", "-q", ".url"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return fallback_release_url(version)


def fallback_release_url(version: str) -> str:
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        url = r.stdout.strip()
        m = re.match(r"git@github\.com:([^/]+)/(.+?)(?:\.git)?$", url)
        if m:
            base = f"https://github.com/{m.group(1)}/{m.group(2)}"
        else:
            base = url.replace("git+", "")
            if base.endswith(".git"):
                base = base[:-4]
            base = base.rstrip("/")
        return f"{base}/releases/tag/{version}"
    except Exception:
        return f"https://github.com/OWNER/REPO/releases/tag/{version}"


def insert_release_record(path: str, heading: str, header_row: str,
                          sep_row: str, row: str) -> bool:
    """在文档的「版本发布记录」表中插入一行（无该章节则自动创建）。"""
    if not os.path.isfile(path):
        print(f"[WARN] 文档不存在，跳过插入: {path}", file=sys.stderr)
        return False
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == heading:
            idx = i
            break

    if idx is None:
        # 章节不存在：在文件末尾追加
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.append(heading)
        lines.append("")
        lines.append(header_row)
        lines.append(sep_row)
        lines.append(row)
        lines.append("")
    else:
        # 找到分隔行（| --- |）
        sep_i = None
        for j in range(idx + 1, len(lines)):
            if lines[j].strip().startswith("|") and "---" in lines[j]:
                sep_i = j
                break
        if sep_i is None:
            # 有标题但还没表格：在标题后建表
            at = idx + 1
            lines.insert(at, "")
            lines.insert(at + 1, header_row)
            lines.insert(at + 2, sep_row)
            sep_i = at + 2
        # 在分隔行之后插入（最新记录置顶）
        lines.insert(sep_i + 1, row)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


def ensure_gh():
    try:
        subprocess.run(
            [GH, "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("[ERROR] 未找到 gh 命令，请先安装 GitHub CLI: https://cli.github.com/",
              file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("[ERROR] gh 命令执行失败，请确认 GitHub CLI 已正确安装并登录（gh auth login）。",
              file=sys.stderr)
        sys.exit(1)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="为指定的一个或多个 OpenSSL 版本创建 GitHub Release 并上传安装包")
    parser.add_argument(
        "ver", nargs="+",
        help="OpenSSL 版本号，下划线分隔，可指定多个、空格分隔，示例：1_1_1w 3_0_21")
    parser.add_argument(
        "-p", "--paths", nargs="*", default=["."],
        help="扫描目录（可选，可多个），默认当前目录；不存在的路径自动跳过")
    args = parser.parse_args()

    ensure_gh()

    # 文档规范： (文件路径, 章节标题, 表头, 分隔行, 行格式化函数)
    # 发布记录只保留「版本 + 发布链接」，不记录发布时间
    doc_specs = [
        ("README.MD", "## 版本发布记录",
         "| 版本 | 发布链接 |", "| --- | --- |",
         lambda v, u: f"| {v} | [GitHub Release]({u}) |"),
        ("README-EN.MD", "## Release History",
         "| Version | Release |", "| --- | --- |",
         lambda v, u: f"| {v} | [GitHub Release]({u}) |"),
    ]

    base_commit = git("rev-parse", "HEAD").stdout.strip()

    released = []  # (version, url)
    for version in args.ver:
        print(f"\n===== 处理版本 {version} =====")
        if release_exists(version):
            print(f"[SKIP] 版本 {version} 的 Release 已存在，跳过。", file=sys.stderr)
            continue

        links = openssl_link_gen.generate_openssl_links(version)
        name_to_url = {os.path.basename(u): u for u in links}
        target_names = set(name_to_url.keys())

        found, seen = [], set()
        for p in args.paths:
            for rel in find_installers(p, target_names):
                if rel not in seen:
                    seen.add(rel)
                    found.append(rel)

        if not found:
            print(f"[WARN] 版本 {version} 未找到任何匹配的安装包，跳过。", file=sys.stderr)
            continue

        rows = [(os.path.basename(rel), name_to_url.get(os.path.basename(rel), "未知"))
                for rel in found]
        notes = build_notes(rows)

        cmd = [GH, "release", "create", version,
               "--title", version, "--notes", notes, *found]
        print(">>> " + " ".join(cmd))
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            print(f"[ERROR] 版本 {version} Release 创建失败（gh 返回码 {rc}）。",
                  file=sys.stderr)
            continue

        url = get_release_url(version)
        released.append((version, url))
        print(f"[OK] 版本 {version} Release 已创建: {url}")

    if not released:
        print("\n没有需要发布的版本，结束。")
        return

    # 文档插入发布记录
    for version, url in released:
        for path, heading, hdr, sep, fmt in doc_specs:
            row = fmt(version, url)
            insert_release_record(path, heading, hdr, sep, row)
    print(f"\n[OK] 已在文档插入 {len(released)} 条发布记录。")

    # Git 提交（仅文档：安装包只上传到 GitHub Release，绝不纳入 Git 仓库，避免仓库体积膨胀）
    stage = ["README.MD", "README-EN.MD"]
    git("add", *stage)
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("[INFO] 没有需要提交的改动。")
    else:
        msg = "release: " + ", ".join(v for v, _ in released)
        git("commit", "-m", msg)
        print(f"[OK] 已提交：{msg}")

    # 打标签（指向发布前的基线提交，与 gh 创建的远程标签一致）
    for version, _ in released:
        if git("rev-parse", f"refs/tags/{version}").returncode == 0:
            print(f"[SKIP] 标签 {version} 已存在。")
            continue
        git("tag", "-a", version, "-m", version, base_commit)
        print(f"[OK] 已创建标签：{version}")

    # 推送分支与标签
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    pr = git("push", "origin", branch, "--follow-tags")
    if pr.returncode != 0:
        print("[ERROR] 推送失败，请检查远程配置与登录状态：", file=sys.stderr)
        print(pr.stderr, file=sys.stderr)
    else:
        print("[OK] 已推送分支与标签。")

    print("\n完成。")


if __name__ == "__main__":
    main()
