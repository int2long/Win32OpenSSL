import argparse

def generate_openssl_links(version: str):
    # 定义所有架构前缀
    arch_list = [
        "Win64",
        "Win32",
        "Win64ARM",
        "WinUniversal"
    ]
    base_url = "https://slproweb.com/download"
    link_list = []

    for arch in arch_list:
        # Light 版本
        light_exe = f"{base_url}/{arch}OpenSSL_Light-{version}.exe"
        link_list.append(light_exe)
        
        # WinUniversal 无 msi，特殊判断
        if arch != "WinUniversal":
            light_msi = f"{base_url}/{arch}OpenSSL_Light-{version}.msi"
            link_list.append(light_msi)

        # 完整标准版
        full_exe = f"{base_url}/{arch}OpenSSL-{version}.exe"
        link_list.append(full_exe)
        if arch != "WinUniversal":
            full_msi = f"{base_url}/{arch}OpenSSL-{version}.msi"
            link_list.append(full_msi)
    
    return link_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 Win OpenSSL 全版本下载链接")
    parser.add_argument("version", help="OpenSSL版本号，下划线分隔，例：3_0_21")
    args = parser.parse_args()

    links = generate_openssl_links(args.version)
    for url in links:
        print(url)
