# Win OpenSSL 镜像仓库

> 🌐 English version: [README-EN.MD](README-EN.MD)

## 仓库说明

本仓库是 **Win32/Win64/ARM/Universal 平台 OpenSSL 安装包索引仓库**。仓库本身**不保存任何二进制文件**，所有安装包仅通过 GitHub Release 分发；仓库内只保留说明文档与发布索引，clone 后体积极小、不含 exe/msi。

> 官方主页：[https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
> 下载入口：各版本安装包请前往 `GitHub Release` 页面下载

### 仓库用途

1. **发布索引**：集中记录每个 OpenSSL 版本的 GitHub Release 发布页，clone 后一条记录即可找到下载入口；
2. **国内加速访问**：通过 GitHub Release 提供可访问的下载入口，解决官网境外下载慢、不稳定的问题；
3. **版本统一归档**：以 Release 标签（tag）按版本归档，便于按版本号 `git checkout <版本>` 取回对应发布索引；
4. **溯源可查**：每条发布记录的 `From` 列及 Release 说明表格均保留官方原始下载地址，可核对文件来源。

## 仓库文件结构规范

仓库（clone 后）**仅包含以下 4 个文件**，不含任何 exe/msi 二进制安装包：

```
仓库根目录
├─ openssl_link_gen.py     # 生成指定版本全部架构的官方下载链接
├─ git_release_openssl.py  # 创建 GitHub Release 并上传安装包、同步发布记录
├─ README.MD               # 说明文档（中文）
└─ README-EN.MD            # 说明文档（英文）
```

> 安装包二进制文件由 `git_release_openssl.py` 上传到 GitHub Release，**不纳入 Git 仓库**。clone 本仓库后如需安装包，请前往对应版本发布页下载——仓库内 `## 版本发布记录` 提供每个版本的可跳转链接。

## 配套 Python 脚本说明

仓库根目录提供两个配套自动化脚本，分别用于**生成下载链接、创建 GitHub Release 并同步发布记录**：

| 脚本 | 用途 |
| --- | --- |
| `openssl_link_gen.py` | 根据版本号生成全部架构安装包的官方下载链接列表 |
| `git_release_openssl.py` | 为指定版本创建 GitHub Release，上传安装包资产，并在文档插入可跳转的发布记录、提交并打标签、推送分支与标签 |

> 使用脚本前，需本地已安装 Python3 与 Git，并配置好 Git 用户名 / 邮箱。

### 1. 脚本 `openssl_link_gen.py`

#### 功能

根据传入的 OpenSSL 版本号，输出该版本全部架构（Win32/Win64/Win64ARM/WinUniversal）安装包的官方下载链接列表，用于核对、手动下载或审计。

#### 使用方法

```
# 示例：生成 3_0_21 版本全部架构下载链接
python openssl_link_gen.py 3_0_21
```

输出示例：

```
https://slproweb.com/download/Win64OpenSSL_Light-3_0_21.exe
https://slproweb.com/download/Win64OpenSSL_Light-3_0_21.msi
https://slproweb.com/download/Win64OpenSSL-3_0_21.exe
https://slproweb.com/download/Win64OpenSSL-3_0_21.msi
...
```

### 2. 脚本 `git_release_openssl.py`

#### 脚本功能

1. 根据传入的一个或多个 OpenSSL 版本号，自动生成对应版本全部架构（Win32/Win64/Win64ARM/WinUniversal）安装包的官方下载链接；
2. 递归扫描仓库（默认当前目录，可用 `-p/--paths` 指定多个目录），识别该版本的全部安装包；
3. 调用 GitHub CLI（`gh release create`）为版本创建 Release，并将所有安装包作为资产上传；
4. Release 说明（--notes）为一张 Markdown 表格，列出每个安装包的 `name` 与官方原始下载地址 `From`；
5. 在 `README.MD` / `README-EN.MD` 的「版本发布记录」中插入一条可点击跳转到对应 Release 页面的记录；
6. 将文档改动（发布记录）提交到 Git，并以版本号创建 annotated 标签，最后推送分支与标签，保持 Git 仓库与 GitHub Release 一致；安装包仅上传到 GitHub Release，绝不纳入 Git 仓库。

#### 脚本使用方法

1. 环境依赖：本地已安装 Python3、Git、GitHub CLI（`gh`），并已执行 `gh auth login` 登录；
2. 打开终端，进入仓库根目录，执行命令（版本号下划线分隔，可指定多个、空格分隔）：

```
# 示例：为多个版本创建 Release 并上传安装包
python git_release_openssl.py 1_1_1w 3_0_21 3_3_7 3_4_6 3_5_7 3_6_3 4_0_1

# 示例：指定多个扫描目录（用 -p/--paths，可传一个或多个，不存在的路径自动跳过）
python git_release_openssl.py 3_0_21 -p 3_0_21 other_dir
```

> 版本可指定一个或多个；路径参数 `-p/--paths` 可选，省略时默认扫描当前目录；多版本/多路径命中同一文件会自动去重；已存在同名 Release 的版本会自动跳过。

1. 执行完成后，文档中已插入发布记录、改动已提交并打好版本标签，并推送分支与标签到远程仓库。

### 脚本匹配的全部文件类型

以上脚本可自动识别以下所有架构、类型安装包：

- Win32 / Win64 / Win64ARM 标准版 & Light 精简版 `.exe` / `.msi`
- WinUniversal 标准版 & Light 精简版 `.exe`（该架构无 msi 安装包）

## 版本发布记录

仓库不含二进制安装包，各版本安装包请点击对应链接前往 GitHub Release 页面下载。本表由 `git_release_openssl.py` 在每次发布后自动插入最新记录（最新置顶）。

| 版本 | 发布链接 |
| --- | --- |
| 3_0_21 | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/3_0_21) |
| 1_1_1w | [GitHub Release](https://github.com/int2long/Win32OpenSSL/releases/tag/1_1_1w) |

## 重要说明

1. **版权声明**：所有 OpenSSL 二进制文件版权归属 slproweb 官方；本仓库通过 GitHub Release 提供安装包镜像分发，仅供个人离线存档使用，请勿用于商用分发；
2. **文件校验建议**：下载使用前建议核对官网文件哈希值，保证文件完整性、未被篡改；
3. **仓库只存文档**：仓库不纳入任何二进制安装包，安装包仅通过 GitHub Release 上传分发；Git 提交只包含文档 / 说明信息的改动；
4. **版本命名规则**：版本号统一使用下划线分隔（如 `3_0_21`），不使用小数点；
5. **GitHub Release 同步**：`git_release_openssl.py` 依赖 GitHub CLI（`gh`）且需先 `gh auth login` 登录；每次发布会在文档插入可跳转的发布记录、自动提交（仅文档）、以版本号打 annotated 标签并推送分支与标签，保证 Git 仓库与 GitHub Release 一致。

## 官方链接汇总

- Win OpenSSL 产品主页：[https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
