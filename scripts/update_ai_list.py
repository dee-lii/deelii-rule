#!/usr/bin/env python3
"""重新生成 config/mihomo/config/ai.list（AI 平台合并规则集）

来源：
  - MetaCubeX/meta-rules-dat 的 AI 相关分类（.list，domain 格式）
  - ACL4SSR/ACL4SSR 的 AI.list（classical 格式，含 KEYWORD 匹配）

用法：
  python3 scripts/update_ai_list.py [--output 路径]

之后 mihomo 热重载生效：
  curl -X PUT http://127.0.0.1:9090/configs?force=true
"""
import argparse
import io
import urllib.request

META_BASE = "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/"
META_CATS = [
    "openai", "google-gemini", "xai", "groq", "anthropic", "perplexity", "poe",
    "github-copilot", "cursor", "jetbrains-ai", "windsurf", "trae", "manus",
]
ACL_URL = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/AI.list"
DEFAULT_OUT = "config/mihomo/config/ai.list"


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def build() -> str:
    rules = set()

    # meta-rules-dat：domain 格式 -> classical
    for cat in META_CATS:
        for line in fetch(META_BASE + cat + ".list").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("+."):
                rules.add(f"DOMAIN-SUFFIX,{line[2:]}")
            else:
                rules.add(f"DOMAIN,{line}")

    # ACL4SSR：本来就是 classical，原样保留
    for line in fetch(ACL_URL).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rules.add(line)

    header = (
        "# AI 平台合并规则集（classical 格式）\n"
        f"# 来源: meta-rules-dat({', '.join(META_CATS)}) + ACL4SSR AI.list\n"
        f"# 共 {len(rules)} 条\n"
    )
    return header + "\n".join(sorted(rules)) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=DEFAULT_OUT)
    args = ap.parse_args()
    io.open(args.output, "w", encoding="utf-8").write(build())
    print(f"已生成 {args.output}")


if __name__ == "__main__":
    main()
