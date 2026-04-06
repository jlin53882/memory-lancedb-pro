#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode 任務封裝（Agent 用）

提供乾淨的 Python API，讓 OpenClaw sub-agent 可以直接 import 使用。
不依賴 CLI，直接對 OpenCode HTTP API 發請求。

使用方式（Python）：
    from opencode_task import run_opencode_task, OpenCodeAPI

    result = run_opencode_task(
        prompt="請用繁體中文對以下程式碼進行 code review：\ndef foo(): pass",
        model="minimax/MiniMax-M2.7",
        reasoning="high",
    )
    print(result.text)        # 回覆文字
    print(result.session_id)  # session ID（可後續繼續對話）
    print(result.ok)          # True/False

使用方式（CLI）：
    python opencode_task.py --prompt "請幫我分析這個函數" --model minimax/MiniMax-M2.7 --reasoning high
"""

import argparse
import json
import sys
import time
import subprocess
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass
from typing import Optional

# ─── 預設值 ───
DEFAULT_BASE_URL = "http://127.0.0.1:4096"
DEFAULT_MODEL = "minimax/MiniMax-M2.7"
DEFAULT_REASONING = "medium"
DEFAULT_TIMEOUT = 120  # 秒


@dataclass
class TaskResult:
    ok: bool
    text: str = ""           # 提取出的文字回覆
    raw: Optional[dict] = None  # API 原始回應
    session_id: str = ""
    error: str = ""


class OpenCodeAPI:
    """輕量封裝 OpenCode HTTP API"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        auto_start: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auto_start = auto_start
        self._session_id: Optional[str] = None

    def _req(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code}: {body_text[:300]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"無法連線到 OpenCode Server ({url}): {e.reason}")

    def get(self, path: str) -> dict:
        return self._req("GET", path)

    def post(self, path: str, body: Optional[dict] = None) -> dict:
        return self._req("POST", path, body)

    def is_healthy(self) -> bool:
        try:
            r = self.get("/global/health")
            return r.get("healthy", False)
        except Exception:
            return False

    def ensure_server(self, wait: int = 15) -> bool:
        if self.is_healthy():
            return True
        if not self.auto_start:
            return False

        print(f"[INFO] OpenCode Server 未運行，嘗試自動啟動...", file=sys.stderr)

        # 取出 host/port
        try:
            parsed = urllib.parse.urlparse(self.base_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 4096
        except Exception:
            host, port = "127.0.0.1", 4096

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(
                ["cmd", "/c", "start", "OpenCode Server",
                 "opencode", "serve", "--port", str(port), "--hostname", host],
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            print("[ERROR] 找不到 'opencode'，請確認已安裝並加入 PATH", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] 啟動失敗: {e}", file=sys.stderr)
            return False

        for i in range(wait):
            time.sleep(1)
            if self.is_healthy():
                print(f"[INFO] Server 就緒（耗時 {i+1}s）", file=sys.stderr)
                return True
        return False

    def create_session(self, title: Optional[str] = None) -> str:
        self.ensure_server()
        body = {"title": title or "OpenClaw Task"}
        r = self.post("/session", body)
        self._session_id = r["id"]
        return self._session_id

    def send_message(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        reasoning: Optional[str] = None,
    ) -> dict:
        self.ensure_server()
        sid = session_id or self._session_id
        if not sid:
            sid = self.create_session()

        body: dict = {"parts": [{"type": "text", "text": prompt}]}
        if model:
            # Parse providerID and modelID from "provider/model" format
            if "/" in model:
                providerID, modelID = model.split("/", 1)
            else:
                providerID, modelID = model, model
            model_obj: dict = {"name": modelID, "providerID": providerID, "modelID": modelID}
            if reasoning:
                model_obj["reasoningEffort"] = reasoning
            body["model"] = model_obj
        elif reasoning:
            body["reasoningEffort"] = reasoning

        r = self.post(f"/session/{sid}/message", body)
        self._session_id = sid
        return r

    def extract_text(self, response: dict) -> str:
        parts = response.get("parts", [])
        return "\n".join(
            p.get("text", "").strip()
            for p in parts
            if p.get("type") == "text" and p.get("text", "").strip()
        )


def run_opencode_task(
    prompt: str,
    model: str = DEFAULT_MODEL,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
    title: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    auto_start: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> TaskResult:
    client = OpenCodeAPI(base_url=base_url, timeout=timeout, auto_start=auto_start)
    try:
        if not session_id:
            session_id = client.create_session(title=title)
        response = client.send_message(
            prompt=prompt,
            session_id=session_id,
            model=model,
            reasoning=reasoning,
        )
        text = client.extract_text(response)
        return TaskResult(ok=True, text=text, raw=response, session_id=session_id)
    except RuntimeError as e:
        return TaskResult(ok=False, error=str(e), session_id=session_id or "")


def main():
    parser = argparse.ArgumentParser(description="OpenCode 任務封裝（支援 auto-start）")
    parser.add_argument("--prompt", "-p", required=True, help="要傳送的 prompt")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="模型 ID")
    parser.add_argument("--reasoning", "-r",
                        choices=["none", "minimal", "low", "medium", "high", "xhigh"],
                        help="思考深度")
    parser.add_argument("--session", "-s", help="沿用現有 session ID（多輪對話）")
    parser.add_argument("--title", "-t", help="Session 標題")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--json", "-j", action="store_true", help="輸出完整 JSON")
    parser.add_argument("--no-auto-start", action="store_true", help="關閉自動啟動")

    args = parser.parse_args()

    result = run_opencode_task(
        prompt=args.prompt,
        model=args.model,
        reasoning=args.reasoning,
        session_id=args.session or None,
        title=args.title,
        base_url=args.base_url,
        auto_start=not args.no_auto_start,
    )

    if args.json:
        print(json.dumps({
            "ok": result.ok,
            "text": result.text,
            "session_id": result.session_id,
            "error": result.error,
        }, ensure_ascii=False, indent=2))
    else:
        if not result.ok:
            print(f"[ERROR] {result.error}", file=sys.stderr)
            sys.exit(1)
        print(result.text)


if __name__ == "__main__":
    main()
