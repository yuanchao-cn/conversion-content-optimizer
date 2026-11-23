#!/usr/bin/env python3
"""拉取公开云端增量知识，带优雅降级。

只使用 Python 标准库。任何失败都返回 fallback 状态而不是抛异常中断 Skill。

默认行为：脚本内置公开 URL（BUILTIN_URL），用户零配置即可拉取增量。
可选配置文件：~/.workbuddy/conversion-content-optimizer/knowledge-source.json
  {"url": "https://example.com/public/knowledge.json"}
  - 文件缺失 / 无有效 url -> 使用内置 URL
  - url 有效 -> 覆盖内置 URL（自建镜像、内网地址等）
  - 显式 {"enabled": false} -> 完全禁用云端，走包内基线
任何失败都降级到包内基线，不中断 Skill。

用法：
  python3 scripts/fetch_knowledge.py --out data/knowledge_snapshot.json
  python3 scripts/fetch_knowledge.py --config /path/to/config.json --out out.json --timeout 15

输出（stdout，JSON）：
  ok       -> {"status":"ok","version":...,"updated_at":...,"out":...,"counts":{...}}
  fallback -> {"status":"fallback","reason":...,"out":...}
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_CONFIG = os.path.join(
    os.path.expanduser("~"), ".workbuddy", "conversion-content-optimizer", "knowledge-source.json"
)
# 内置默认增量源：所有安装者零配置即可拉取；可被本机 config 的 url 覆盖，可被 enabled:false 关闭。
BUILTIN_URL = "https://gist.githubusercontent.com/yuanchao-cn/673dd03c7a8958f4481f9fda39f3762e/raw/320f8682353490faa79e79deace82e6a089c0004/knowledge.json"
MAX_BYTES = 2 * 1024 * 1024  # 2MB，防止超大响应拖慢 Skill
REQUIRED_KEYS = ("version",)


def fallback(reason, out):
    payload = {
        "status": "fallback",
        "reason": reason,
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    if out:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"status": "fallback", "reason": reason, "methodology_addenda": [],
                           "cases": []}, f, ensure_ascii=False, indent=2)
            payload["out"] = out
        except OSError:
            pass
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=DEFAULT_CONFIG)
    p.add_argument("--out", default="")
    p.add_argument("--timeout", type=int, default=15)
    args = p.parse_args()

    # 本机配置是可选的覆盖层：缺失/损坏 -> 内置 URL；显式禁用 -> 基线；有效 url -> 覆盖内置
    cfg = {}
    if os.path.exists(args.config):
        try:
            with open(args.config, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                cfg = loaded
        except (OSError, json.JSONDecodeError):
            pass  # 配置损坏按未配置处理，继续走内置 URL

    enabled = cfg.get("enabled", True)
    if enabled is False or str(enabled).lower() in ("false", "0", "no"):
        return fallback("disabled", args.out)

    url = BUILTIN_URL
    url_source = "builtin"
    if cfg:
        candidate = str(cfg.get("url") or "").strip()
        if candidate.startswith(("https://", "http://")):
            url = candidate
            url_source = "config"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WorkBuddy-Skill-KnowledgeFetch/1.0"})
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            raw = resp.read(MAX_BYTES + 1)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return fallback(f"fetch_failed: {type(exc).__name__}", args.out)

    if len(raw) > MAX_BYTES:
        return fallback("response_too_large", args.out)

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fallback("invalid_json", args.out)

    if not isinstance(data, dict) or any(k not in data for k in REQUIRED_KEYS):
        return fallback("schema_missing_version", args.out)

    for key in ("methodology_addenda", "cases"):
        if not isinstance(data.get(key, []), list):
            return fallback(f"schema_invalid_{key}", args.out)
        data.setdefault(key, [])

    snapshot = dict(data)
    snapshot["status"] = "ok"
    snapshot["fetched_at"] = datetime.now(timezone.utc).astimezone().isoformat()
    snapshot["source_url"] = url

    if args.out:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            return fallback(f"write_failed: {type(exc).__name__}", "")

    print(json.dumps({
        "status": "ok",
        "version": snapshot.get("version"),
        "updated_at": snapshot.get("updated_at"),
        "out": args.out,
        "source": url_source,
        "counts": {
            "methodology_addenda": len(snapshot["methodology_addenda"]),
            "cases": len(snapshot["cases"]),
        },
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
