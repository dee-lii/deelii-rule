#!/usr/bin/env python3
"""同步上游 XiaoM-OVO/Mihomo-Toolkit 的 pure-nodes.js 并应用本地补丁。

本地补丁（保留节点原名 + 末尾追加 IP 识别的国家/地区）：
  1. enableStandardRename: true -> false（不重写名字）
  2. enableIpEnrich: false -> true（开启 IP 溯源）
  3. 保留原名分支追加 "{icon}{region}" 后缀

安全设计：任一补丁未命中（上游改版）立即报错退出，绝不写出坏文件。

用法：
  python3 scripts/apply-pure-nodes-patch.py [--output scripts/pure-nodes.js]
"""
import argparse
import io
import sys
import urllib.request

UPSTREAM_URL = "https://raw.githubusercontent.com/XiaoM-OVO/Mihomo-Toolkit/main/src/pure-nodes.js"
DEFAULT_OUT = "scripts/pure-nodes.js"

# (旧文本, 新文本, 描述)
PATCHES = [
    (
        "    enableStandardRename: true,   // 标准化重命名: 关闭则保留节点原名(防吞词)",
        "    enableStandardRename: false,  // 标准化重命名: 关闭则保留节点原名，末尾追加 IP 识别的国家/地区",
        "关闭标准化重命名",
    ),
    (
        "    enableIpEnrich: false,        // 🌍 API 总开关 (调用 ip-api.com)",
        "    enableIpEnrich: true,         // 🌍 API 总开关 (调用 ip-api.com)",
        "开启 IP 溯源",
    ),
    (
        "                } else {\n"
        "                    finalName = `${myPrefix}${item.rawName}`;\n"
        "                }",
        "                } else {\n"
        "                    // 保留原名，末尾追加 IP 识别的国家/地区\n"
        "                    finalName = `${myPrefix}${item.rawName} ${regionInfo.icon}${regionInfo.name}`\n"
        "                        .replace(/\\s{2,}/g, \" \")\n"
        "                        .trim();\n"
        "                }",
        "原名+国家后缀",
    ),
]


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=DEFAULT_OUT)
    args = ap.parse_args()

    content = fetch(UPSTREAM_URL)

    for old, new, desc in PATCHES:
        if old not in content:
            print(f"[失败] 补丁未命中: {desc}（上游源码可能改版，需人工处理）", file=sys.stderr)
            sys.exit(1)
        content = content.replace(old, new, 1)
        print(f"[OK] {desc}")

    io.open(args.output, "w", encoding="utf-8").write(content)
    print(f"已写入 {args.output}")


if __name__ == "__main__":
    main()
