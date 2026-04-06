#!/usr/bin/env python3
"""Check OpenAI Codex CLI rate limit status."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def find_latest_session_file():
    """Find the most recently modified session file.

    Prefer today/yesterday for speed, but fall back to scanning all sessions
    (useful on machines where Codex hasn't been used recently).
    """
    sessions_dir = Path.home() / ".codex" / "sessions"
    now = datetime.now()

    # Fast path: today + yesterday
    for day_offset in range(2):
        date = datetime(now.year, now.month, now.day)
        date = datetime.fromordinal(date.toordinal() - day_offset)
        day_dir = sessions_dir / f"{date.year:04d}" / f"{date.month:02d}" / f"{date.day:02d}"

        if not day_dir.exists():
            continue

        jsonl_files = list(day_dir.glob("*.jsonl"))
        if jsonl_files:
            return max(jsonl_files, key=lambda f: f.stat().st_mtime)

    # Slow path: any session file
    if sessions_dir.exists():
        all_files = list(sessions_dir.rglob("*.jsonl"))
        if all_files:
            return max(all_files, key=lambda f: f.stat().st_mtime)

    return None

def extract_rate_limits(file_path):
    """Extract rate limits from the last token_count event in a session file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if (event.get('payload', {}).get('type') == 'token_count' and
                event.get('payload', {}).get('rate_limits')):
                return event['payload']['rate_limits']
        except json.JSONDecodeError:
            continue
    
    return None

def format_window(minutes):
    """Format window duration in human-readable form."""
    if minutes >= 1440:
        days = minutes // 1440
        return f"{days} day{'s' if days != 1 else ''}"
    elif minutes >= 60:
        hours = minutes // 60
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        return f"{minutes} min"

def format_reset_time(unix_timestamp):
    """Format reset time with countdown."""
    reset_dt = datetime.fromtimestamp(unix_timestamp)
    now = datetime.now()
    delta = reset_dt - now
    
    time_str = reset_dt.strftime("%Y-%m-%d %H:%M")
    
    if delta.total_seconds() > 0:
        hours = int(delta.total_seconds()) // 3600
        minutes = (int(delta.total_seconds()) % 3600) // 60
        if hours > 0:
            return f"{time_str} (in {hours}h {minutes}m)"
        else:
            return f"{time_str} (in {minutes}m)"
    else:
        return f"{time_str} (passed)"

def progress_bar(percent, width=20):
    """Generate a progress bar string."""
    filled = int((percent / 100.0) * width)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + "]"

def unix_to_iso(timestamp):
    """Convert Unix timestamp to ISO 8601 string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def file_mod_time_iso(file_path):
    """Get file modification time as ISO 8601 string."""
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def file_mod_time_local(file_path):
    """Get file modification time in local timezone."""
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

def _serialize_limit(limit):
    """Serialize one rate-limit window, tolerating missing fields."""
    if not isinstance(limit, dict):
        return None
    required = ("used_percent", "window_minutes", "resets_at")
    if not all(k in limit and limit[k] is not None for k in required):
        return None
    return {
        "used_percent": limit["used_percent"],
        "window_minutes": limit["window_minutes"],
        "resets_at": unix_to_iso(limit["resets_at"]),
    }


def _print_limit_row(icon, label, limit):
    """Print one formatted window row if available."""
    if not isinstance(limit, dict):
        return False
    required = ("used_percent", "window_minutes", "resets_at")
    if not all(k in limit and limit[k] is not None for k in required):
        return False

    print(f"{icon} {label} ({format_window(limit['window_minutes'])} window)")
    print(f"   {progress_bar(limit['used_percent'])} {limit['used_percent']:.1f}%")
    print(f"   Resets: {format_reset_time(limit['resets_at'])}")
    print()
    return True


def output_json(limits, file_path):
    """Output rate limits as JSON."""
    output = {
        "primary": _serialize_limit(limits.get("primary")),
        "secondary": _serialize_limit(limits.get("secondary")),
        "updated_at": file_mod_time_iso(file_path)
    }
    print(json.dumps(output, indent=2))


def output_pretty(limits, file_path):
    """Output rate limits in human-readable format."""
    print()
    print("═══════════════════════════════════════════")
    print("           CODEX RATE LIMIT STATUS         ")
    print("═══════════════════════════════════════════")
    print()

    printed_primary = _print_limit_row("📊", "Primary", limits.get("primary"))
    printed_secondary = _print_limit_row("📈", "Secondary", limits.get("secondary"))

    if not printed_primary and not printed_secondary:
        print("⚠️  Rate-limit data exists but window fields are incomplete")
        print()

    print("═══════════════════════════════════════════")
    print(f"   Updated: {file_mod_time_local(file_path)}")
    print("═══════════════════════════════════════════")

def ping_codex():
    """Ping Codex to get fresh rate limit data."""
    import subprocess
    print("🔄 Pinging Codex for fresh rate limit data...")
    
    try:
        subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", "reply OK"],
            cwd=Path.home(),
            capture_output=True,
            timeout=60
        )
    except Exception as e:
        print(f"⚠️  Failed to ping Codex: {e}")
    
    import time
    time.sleep(0.5)
    return find_latest_session_file()

def list_accounts():
    """List all saved Codex accounts."""
    accounts_dir = Path.home() / ".codex" / "accounts"
    if not accounts_dir.exists():
        return []
    return [f.stem for f in accounts_dir.glob("*.json") if not f.name.startswith('.')]

def get_active_account():
    """Get currently active account name by comparing auth.json to saved accounts."""
    auth_file = Path.home() / ".codex" / "auth.json"
    accounts_dir = Path.home() / ".codex" / "accounts"
    
    if not auth_file.exists():
        return None
    
    try:
        current = auth_file.read_text()
        for acct_file in accounts_dir.glob("*.json"):
            if acct_file.read_text() == current:
                return acct_file.stem
    except:
        pass
    return None

def switch_account(name):
    """Switch to a different Codex account."""
    import shutil
    accounts_dir = Path.home() / ".codex" / "accounts"
    auth_file = Path.home() / ".codex" / "auth.json"
    account_file = accounts_dir / f"{name}.json"
    
    if not account_file.exists():
        return False
    
    shutil.copy(account_file, auth_file)
    return True

def update_all_accounts(want_json=False):
    """Update quota for all accounts and store in /tmp."""
    import time
    
    accounts = list_accounts()
    if not accounts:
        if want_json:
            print('{"error": "No accounts found"}')
        else:
            print("❌ No accounts found in ~/.codex/accounts/")
        return
    
    original_account = get_active_account()
    results = {}
    
    if not want_json:
        print(f"🔄 Updating quota for {len(accounts)} account(s)...")
        print()
    
    for account in accounts:
        if not want_json:
            print(f"  → {account}...", end=" ", flush=True)
        
        if not switch_account(account):
            if not want_json:
                print("❌ switch failed")
            results[account] = {"error": "switch failed"}
            continue
        
        # Ping codex to get fresh data
        session_file = ping_codex()
        
        if not session_file:
            if not want_json:
                print("❌ no session")
            results[account] = {"error": "no session file"}
            continue
        
        limits = extract_rate_limits(session_file)
        
        if not limits:
            if not want_json:
                print("❌ no limits")
            results[account] = {"error": "no rate limits"}
            continue
        
        p_ser = _serialize_limit(limits.get('primary'))
        s_ser = _serialize_limit(limits.get('secondary'))

        results[account] = {
            "primary": p_ser,
            "secondary": s_ser,
            "updated_at": file_mod_time_iso(session_file)
        }

        if not want_json:
            p_txt = f"{p_ser['used_percent']:.0f}%" if p_ser else "n/a"
            s_txt = f"{s_ser['used_percent']:.0f}%" if s_ser else "n/a"
            print(f"✓ primary {p_txt} / secondary {s_txt}")
    
    # Restore original account
    if original_account:
        switch_account(original_account)
    
    # Save to /tmp
    output_file = Path("/tmp/codex-quota-all.json")
    output_data = {
        "accounts": results,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    
    if want_json:
        print(json.dumps(output_data, indent=2))
    else:
        print()
        print(f"💾 Saved to {output_file}")
        print()
        
        # Summary table
        print("Account          Daily    Weekly")
        print("─" * 36)
        for acct, data in results.items():
            if "error" in data:
                print(f"{acct:<16} {data['error']}")
            else:
                p = data.get('primary', {}) or {}
                s = data.get('secondary', {}) or {}
                p_txt = f"{p.get('used_percent', 'n/a'):>5}" if p else "  n/a"
                s_txt = f"{s.get('used_percent', 'n/a'):>5}" if s else "  n/a"
                if p and isinstance(p.get('used_percent'), (int, float)):
                    p_txt = f"{p['used_percent']:>5.1f}%"
                if s and isinstance(s.get('used_percent'), (int, float)):
                    s_txt = f"{s['used_percent']:>5.1f}%"
                print(f"{acct:<16} {p_txt}   {s_txt}")

def main():
    args = set(sys.argv[1:])
    
    if "--help" in args or "-h" in args:
        print("""Usage: codex-quota.py [OPTIONS]

Shows OpenAI Codex rate limit status from session files.

Options:
  --fresh, -f    Ping Codex to get fresh rate limit data
  --all, -a      Update all accounts, save to /tmp/codex-quota-all.json
  --json, -j     Output as JSON
  --help, -h     Show this help

By default, uses the most recent session file (cached data).""")
        return
    
    want_fresh = "--fresh" in args or "-f" in args
    want_json = "--json" in args or "-j" in args
    want_all = "--all" in args or "-a" in args
    
    if want_all:
        update_all_accounts(want_json)
        return
    
    if want_fresh:
        session_file = ping_codex()
    else:
        session_file = find_latest_session_file()
    
    if not session_file:
        if want_json:
            print('{"error": "No session files found"}')
        else:
            print("❌ No session files found")
        sys.exit(1)
    
    limits = extract_rate_limits(session_file)
    
    if not limits:
        if want_json:
            print('{"error": "Could not extract rate limits"}')
        else:
            print("❌ Could not extract rate limits from session file")
            print(f"   File: {session_file}")
        sys.exit(1)
    
    if want_json:
        output_json(limits, session_file)
    else:
        output_pretty(limits, session_file)

if __name__ == "__main__":
    main()
