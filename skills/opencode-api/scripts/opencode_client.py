#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode HTTP API Client
用於 OpenClaw 透過 HTTP API 呼叫 OpenCode Server

使用方式：
    python opencode_client.py --task <task> --dir <repo_path> --prompt "<prompt>" [--file <file>]
    python opencode_client.py --session <session_id> --prompt "<prompt>"
    python opencode_client.py --health
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "http://127.0.0.1:4096"
DEFAULT_TIMEOUT = 120
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 4096


class OpenCodeClient:
    """封裝 OpenCode Server HTTP API 呼叫，支援自動啟動"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        auto_start: bool = True,
        opencode_cmd: str = "opencode",
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auto_start = auto_start
        self.opencode_cmd = opencode_cmd
        self._session_cache: Optional[dict] = None
        self._server_process: Optional[object] = None

    def is_server_running(self) -> bool:
        import requests
        try:
            r = requests.get(f"{self.base_url}/global/health", timeout=3)
            return r.status_code == 200 and r.json().get("healthy", False)
        except Exception:
            return False

    def ensure_server(self, wait_seconds: int = 15) -> bool:
        import requests
        import subprocess
        import urllib.parse

        if self.is_server_running():
            return True
        if not self.auto_start:
            return False

        print(f"[INFO] OpenCode Server 未運行，嘗試自動啟動...", file=sys.stderr)

        try:
            parsed = urllib.parse.urlparse(self.base_url)
            host = parsed.hostname or DEFAULT_SERVER_HOST
            port = parsed.port or DEFAULT_SERVER_PORT
        except Exception:
            host, port = DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT

        try:
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                subprocess.Popen(
                    ["cmd", "/c", "start", "OpenCode Server",
                     self.opencode_cmd, "serve",
                     "--port", str(port), "--hostname", host],
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    [self.opencode_cmd, "serve",
                     "--port", str(port), "--hostname", host],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except FileNotFoundError:
            print(f"[ERROR] 找不到 '{self.opencode_cmd}'，請確認已安裝並加入 PATH", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] 啟動失敗: {e}", file=sys.stderr)
            return False

        for i in range(wait_seconds):
            time.sleep(1)
            if self.is_server_running():
                print(f"[INFO] OpenCode Server 已就緒（耗時 {i+1}s）", file=sys.stderr)
                return True
        print(f"[ERROR] OpenCode Server 啟動逾時（等待 {wait_seconds}s）", file=sys.stderr)
        return False

    def stop_server(self):
        if self._server_process:
            try:
                self._server_process.terminate()
                self._server_process.wait(timeout=5)
            except Exception:
                try:
                    self._server_process.kill()
                except Exception:
                    pass
            self._server_process = None

    def _ensure(self):
        if not self.is_server_running():
            if not self.ensure_server():
                raise RuntimeError("OpenCode Server 未運行且無法自動啟動。請手動執行：opencode serve --port 4096")

    def _get(self, path: str) -> dict:
        import requests
        self._ensure()
        r = requests.get(f"{self.base_url}{path}", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        import requests
        self._ensure()
        r = requests.post(f"{self.base_url}{path}", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def health(self) -> dict:
        return self._get("/global/health")

    def list_sessions(self) -> list:
        return self._get("/session")

    def create_session(self, title: Optional[str] = None, parent_id: Optional[str] = None) -> dict:
        body = {}
        if title:
            body["title"] = title
        if parent_id:
            body["parentID"] = parent_id
        return self._post("/session", body)

    def get_session(self, session_id: str) -> dict:
        return self._get(f"/session/{session_id}")

    def send_message(
        self,
        session_id: str,
        prompt: str,
        parts: Optional[list] = None,
        model: Optional[str] = None,
        reasoning: Optional[str] = None,
        agent: Optional[str] = None,
        no_reply: bool = False,
    ) -> dict:
        if parts is None:
            parts = [{"type": "text", "text": prompt}]

        body: dict = {"parts": parts}
        if model:
            if reasoning and ":" not in model:
                body["model"] = f"{model}:{reasoning}"
            else:
                body["model"] = model
        elif reasoning:
            body["reasoningEffort"] = reasoning
        if agent:
            body["agent"] = agent
        if no_reply:
            body["noReply"] = True

        path = f"/session/{session_id}/message"
        if no_reply:
            self._post(path, body)
            return {"status": "queued"}
        return self._post(path, body)

    def extract_text(self, response: dict) -> str:
        parts = response.get("parts", [])
        texts = []
        for p in parts:
            if p.get("type") == "text":
                txt = p.get("text", "").strip()
                if txt:
                    texts.append(txt)
        return "\n".join(texts)

    def review_code(
        self,
        code: str,
        language: str = "python",
        dir_path: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        prompt = (
            f"請用繁體中文對以下 {language} 程式碼進行 code review，"
            f"指出：\n"
            f"1. 程式碼問題或 Bug\n"
            f"2. 安全性疑慮\n"
            f"3. 程式碼風格與可讀性\n"
            f"4. 改進建議（附上修正後的範例程式碼）\n\n"
            f"=== 程式碼 ===\n{code}"
        )
        session = self.create_session(title=f"Code Review - {language}")
        session_id = session["id"]
        response = self.send_message(session_id, prompt, model=model)
        return self.extract_text(response)

    def analyze_file(self, file_path: str, dir_path: str, model: Optional[str] = None) -> str:
        content = ""
        try:
            full_path = Path(dir_path) / file_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")
                if len(content) > 3000:
                    content = content[:3000] + "\n... (已截斷)"
        except Exception:
            content = "[無法讀取檔案內容]"

        prompt = (
            f"請用繁體中文分析以下檔案 ({file_path}) 的架構與邏輯：\n\n"
            f"=== 檔案內容 ===\n{content}"
        )
        session = self.create_session(title=f"分析 - {file_path}")
        session_id = session["id"]
        response = self.send_message(session_id, prompt, model=model)
        return self.extract_text(response)

    def batch_review(
        self,
        files: dict,
        dir_path: str,
        task: str = "review",
        model: Optional[str] = None,
    ) -> str:
        parts = [{"type": "text", "text": f"請用繁體中文對以下檔案進行 {task}，回覆時標明每個檔案的問題與建議：\n"}]
        for fname, content in files.items():
            truncated = content[:2000] + "..." if len(content) > 2000 else content
            parts.append({"type": "text", "text": f"\n=== {fname} ===\n{truncated}"})

        session = self.create_session(title=f"Batch {task}")
        session_id = session["id"]
        response = self.send_message(session_id, "", parts=parts, model=model)
        return self.extract_text(response)


def main():
    parser = argparse.ArgumentParser(description="OpenCode HTTP API Client")
    parser.add_argument("--health", action="store_true", help="健康檢查")
    parser.add_argument("--task", choices=["review", "analyze", "custom"], help="任務類型")
    parser.add_argument("--dir", help="專案目錄")
    parser.add_argument("--prompt", help="要傳送的 prompt")
    parser.add_argument("--file", help="要分析的檔案")
    parser.add_argument("--session", help="現有 session ID")
    parser.add_argument("--model", help="指定模型（如 minimax/MiniMax-M2.7）")
    parser.add_argument("--reasoning", choices=["none", "minimal", "low", "medium", "high", "xhigh"],
                        help="思考深度")
    parser.add_argument("--code", help="直接傳送程式碼")
    parser.add_argument("--async", dest="async_mode", action="store_true", help="非同步模式")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--auto-start", dest="auto_start", action="store_true", default=True)
    parser.add_argument("--no-auto-start", dest="auto_start", action="store_false")
    parser.add_argument("--opencode-cmd", default="opencode")

    args = parser.parse_args()
    client = OpenCodeClient(
        base_url=args.base_url,
        timeout=args.timeout,
        auto_start=args.auto_start,
        opencode_cmd=args.opencode_cmd,
    )

    try:
        if args.health:
            result = client.health()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(0)

        if not args.session and not args.task:
            parser.error("--task 或 --session 至少要一個")

        if args.task and not args.prompt and not args.code and not args.file:
            parser.error(f"--task {args.task} 需要 --prompt、--code 或 --file")

        if args.session:
            session_id = args.session
        else:
            title = f"OpenClaw - {args.task}"
            session = client.create_session(title=title)
            session_id = session["id"]
            print(f"[INFO] 建立 session: {session_id}", file=sys.stderr)

        prompt = args.prompt or ""

        if args.code:
            prompt = f"請用繁體中文對以下 {args.task} 進行分析，指出問題與改進建議：\n\n{args.code}"

        if args.file and args.dir:
            result = client.analyze_file(args.file, args.dir, model=args.model)
            print(result)
            sys.exit(0)

        if args.task in ("review", "analyze") and args.code:
            result = client.review_code(args.code, dir_path=args.dir, model=args.model)
            print(result)
            sys.exit(0)

        response = client.send_message(
            session_id,
            prompt,
            model=args.model,
            reasoning=args.reasoning,
            no_reply=args.async_mode,
        )

        if args.async_mode:
            print(json.dumps(response, ensure_ascii=False), file=sys.stderr)
            print(f"[INFO] 已非同步傳送，session: {session_id}")
            sys.exit(0)

        text = client.extract_text(response)
        if text:
            print(text)
        else:
            print(json.dumps(response, ensure_ascii=False, indent=2))

    except ImportError:
        print("[ERROR] 缺少 requests 模組，請先執行：pip install requests", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
