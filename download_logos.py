import os
import re
import requests
from urllib.parse import urlparse

# --- 配置区 ---
HTML_FILE = "index.html"  # 你的HTML文件名
SAVE_DIR = "logos"        # 图标保存文件夹
# 这里的API使用了 Clearbit，它能提供背景透明的高清PNG，非常适合你的UI
API_URL = "https://logo.clearbit.com/{domain}" 

def extract_sites_from_html(file_path):
    """从HTML文件的navData中提取网站名和URL"""
    sites = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 匹配 { name: "xxx", url: "xxx" } 格式
            pattern = re.compile(r'{\s*name:\s*["\'](.*?)["\'],\s*url:\s*["\'](.*?)["\']\s*}')
            matches = pattern.findall(content)
            for name, url in matches:
                sites.append({"name": name, "url": url})
    except Exception as e:
        print(f"读取文件失败: {e}")
    return sites

def download_logo(name, url):
    """执行下载逻辑"""
    domain = urlparse(url).netloc
    if not domain:
        return
    
    save_path = os.path.join(SAVE_DIR, f"{name}.png")
    
    # 如果本地已经有了，就跳过，节省时间
    if os.path.exists(save_path):
        print(f"[-] 已存在，跳过: {name}")
        return

    try:
        # 拼接高清图标API地址
        target_url = API_URL.format(domain=domain)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"[+] 成功下载: {name}")
        else:
            # 如果高清API没抓到，尝试用备选方案（Google提供的favicon）
            alt_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
            response = requests.get(alt_url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print(f"[!] 使用备选源下载: {name}")
            else:
                print(f"[x] 下载失败: {name} (状态码: {response.status_code})")
    except Exception as e:
        print(f"[x] 错误: {name} - {e}")

def main():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    print("正在解析 HTML 文件提取网址...")
    site_list = extract_sites_from_html(HTML_FILE)
    print(f"共发现 {len(site_list)} 个站点。")

    print("\n开始批量下载图标（请保持网络畅通）...")
    for site in site_list:
        download_logo(site['name'], site['url'])
    
    print("\n任务完成！请查看 logos 文件夹。")

if __name__ == "__main__":
    main()
