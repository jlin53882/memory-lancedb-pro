#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 任務封裝（Agent 用）

提供乾淨的 Python API，讓 OpenClaw sub-agent 可以直接 import 使用。
透過 subprocess 呼叫 Claude Code CLI，擷取輸出結果。

使用方式（Python）：
    from claude_task import run_claude_task, ClaudeAPI

    result = run_claude_task(
        prompt="請用繁體中文對以下程式碼進行 code review：\ndef foo(): pass",
        model="minimax-m2.7",
    )
    print(result.text)        # 回覆文字
    print(result.ok)          # True/False

使用方式（CLI）：
    python claude_task.py --prompt "請幫我分析這個函數" --model minimax-m2.7
"""

import subprocess
import json
import sys
import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import Optional, Any, List

# ─── 預設值 ───
DEFAULT_MODEL = "minimax-m2.7"
DEFAULT_TIMEOUT = 90  # 秒（API cold start 可能需要較久）


@dataclass
class TaskResult:
    ok: bool
    text: str = ""            # 提取出的文字回覆
    raw: Optional[str] = None  # 原始輸出
    session_id: str = ""
    error: str = ""


class ClaudeAPI:
    """
    封裝 Claude Code CLI 呼叫。

    支援：
    - 單次 / 多輪對話（透過 session-dir）
    - 指定模型（ANTHROPIC_MODEL 環境變數）
    - 自訂 system prompt
    - 額外 CLI 參數
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        session_dir: Optional[str] = None,
    ):
        self.model = model
        self.timeout = timeout
        self.session_dir = session_dir or tempfile.mkdtemp(prefix="claude_session_")
        self._env = os.environ.copy()

        # 確保 Claude Code 使用正確的環境變數（版本 2.x 使用 ANTHROPIC_API_KEY）
        # Windows: os.environ 可能未繼承 User-level env vars，主動從 registry 讀取
        # 優先順序：ANTHROPIC_API_KEY（新名）→ ANTHROPIC_AUTH_TOKEN（舊名，兼容性）
        if not self._env.get("ANTHROPIC_API_KEY"):
            key = (
                self._env.get("ANTHROPIC_API_KEY") or
                self._env.get("ANTHROPIC_AUTH_TOKEN") or
                ""
            )
            if not key and sys.platform == "win32":
                try:
                    # 先查 ANTHROPIC_API_KEY（新名）
                    r = subprocess.run(
                        ['powershell', '-NoProfile', '-Command',
                         '[System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")'],
                        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5
                    )
                    key = r.stdout.strip() if r.stdout else ""
                    # Fallback 舊名
                    if not key:
                        r = subprocess.run(
                            ['powershell', '-NoProfile', '-Command',
                             '[System.Environment]::GetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "User")'],
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5
                        )
                        key = r.stdout.strip() if r.stdout else ""
                except Exception:
                    pass
            self._env["ANTHROPIC_API_KEY"] = key
        # 確保 BASE_URL 也正確傳遞
        if "ANTHROPIC_BASE_URL" not in self._env or not self._env.get("ANTHROPIC_BASE_URL"):
            self._env["ANTHROPIC_BASE_URL"] = "https://api.minimax.io/anthropic"
        # 確保模型設定
        self._env["ANTHROPIC_MODEL"] = self.model

    def _build_command(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        cmd = ["claude"]

        # -p = --print，non-interactive 模式（必須）
        cmd.append("-p")

        # 確保 API key 傳遞（env 複製時已處理）
        # --no-session-persistence 避免 session 寫入磁碟
        cmd.append("--no-session-persistence")
        cmd.extend(["--output-format", "json"])

        # 系統提示
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        # 額外參數
        if extra_args:
            cmd.extend(extra_args)

        # positional prompt 必須是最後一個參數
        cmd.append(prompt)

        return cmd

    def send_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> TaskResult:
        """
        傳送訊息到 Claude Code。

        參數：
            prompt: 使用者 prompt
            system_prompt: 系統提示（可自訂 AI 行為）
            extra_args: 額外 CLI 參數
        """
        cmd = self._build_command(prompt, system_prompt, extra_args)

        try:
            # 執行 Claude Code
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=self.timeout,
                env=self._env,
            )

            if result.returncode == 0:
                # 嘗試解析 JSON 輸出
                try:
                    stdout = result.stdout.strip() if result.stdout else ""
                    output = json.loads(stdout)
                    # Claude Code JSON 輸出格式可能是 {"type": "text", "content": "..."}
                    if isinstance(output, dict):
                        text = output.get("result", output.get("content", output.get("text", stdout)))
                    else:
                        text = str(output)
                except json.JSONDecodeError:
                    text = result.stdout.strip() if result.stdout else ""

                return TaskResult(ok=True, text=text, raw=result.stdout if result.stdout else "")
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip() if result.stdout else "Unknown error"
                return TaskResult(ok=False, error=error_msg, raw=result.stderr if result.stderr else result.stdout if result.stdout else "")

        except subprocess.TimeoutExpired:
            return TaskResult(ok=False, error=f"逾時（{self.timeout}秒）")
        except FileNotFoundError:
            return TaskResult(ok=False, error="找不到 'claude' 命令，請確認已安裝並加入 PATH")
        except Exception as e:
            return TaskResult(ok=False, error=str(e))

    def extract_code_blocks(self, text: str) -> List[str]:
        """從回覆中提取程式碼區塊"""
        pattern = r"```[\w]*\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    def extract_json(self, text: str) -> Optional[dict]:
        """從回覆中提取 JSON"""
        pattern = r"\{[\s\S]*\}"
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None


def run_claude_task(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    session_dir: Optional[str] = None,
) -> TaskResult:
    """
    執行單次 Claude Code 任務。

    參數：
        prompt: 傳送的 prompt（必填）
        model: 模型 ID（預設 minimax-m2.7）
        system_prompt: 自訂系統提示
        extra_args: 額外 CLI 參數
        timeout: 逾時秒數
        session_dir: Session 目錄（多輪對話時使用）
    """
    client = ClaudeAPI(model=model, timeout=timeout, session_dir=session_dir)
    return client.send_message(prompt, system_prompt, extra_args)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code 任務封裝")
    parser.add_argument("--prompt", "-p", required=True, help="要傳送的 prompt")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="模型 ID")
    parser.add_argument("--system", "-s", help="自訂系統提示")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="逾時秒數")
    parser.add_argument("--session-dir", help="Session 目錄（多輪對話）")
    parser.add_argument("--json", "-j", action="store_true", help="輸出原始 JSON")
    parser.add_argument("--extra", "-e", nargs="*", help="額外 CLI 參數")

    args = parser.parse_args()

    result = run_claude_task(
        prompt=args.prompt,
        model=args.model,
        system_prompt=args.system,
        timeout=args.timeout,
        session_dir=args.session_dir,
        extra_args=args.extra,
    )

    if args.json:
        print(json.dumps({
            "ok": result.ok,
            "text": result.text,
            "session_id": result.session_id,
            "error": result.error,
            "raw": result.raw,
        }, ensure_ascii=False, indent=2))
    else:
        if not result.ok:
            print(f"[ERROR] {result.error}", file=sys.stderr)
            sys.exit(1)
        print(result.text)


if __name__ == "__main__":
    main()