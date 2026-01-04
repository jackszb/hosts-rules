#!/usr/bin/env python3
import os
import json
import requests

OUTPUT_DIR = "json"
RULES_FILE = "rules_list.json"

# 确保 json 文件夹存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_domains_from_ip_list(text):
    """从 IP + 域名格式中提取域名"""
    domains = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        parts = line.split()
        if len(parts) == 2 and parts[0] == "0.0.0.0":  # 确保是 IP + 域名格式
            domains.add(parts[1])
    return sorted(domains)

def filename_from_url(url):
    """根据 URL 生成唯一文件名"""
    name = url.split("/")[-1]
    if name.endswith(".txt"):
        name = name[:-4]
    name = name.replace("-", "_").replace(".", "_")
    return f"{name}_blocked.json"

def main():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    for url in urls:
        output = filename_from_url(url)
        print(f"Processing {url} → {output}")

        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue

        domains = extract_domains_from_ip_list(resp.text)
        result = {
            "version": 3,
            "rules": [
                {
                    "domain_suffix": domains
                }
            ]
        }

        out_path = os.path.join(OUTPUT_DIR, output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(domains)} domains to {out_path}")

if __name__ == "__main__":
    main()
