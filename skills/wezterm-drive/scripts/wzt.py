# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
wzt — WezTerm control CLI for agents (and humans).

Wraps `wezterm cli` with the missing operational conveniences:
  * friendly names for panes (registry file, auto-pruned, per-machine state)
  * one-shot `exec`: inject a command, wait for completion, return output + exit code
    (start/end marker technique: echo __WZT_S_<token>__ ; <cmd> ; echo __WZT_E_<token>_<code>__)
  * bracketed-paste injection + CR submit (LF does not submit in PSReadLine/readline)

Zero dependencies. Run with:  uv run wzt.py <cmd>   (or: python wzt.py <cmd>)

PANE arguments accept either a numeric pane-id or a registered name.
State dir: $WZT_STATE_DIR, else %LOCALAPPDATA%\\wzt (Windows) or
$XDG_STATE_HOME/wzt / ~/.local/state/wzt — pane ids are machine-local,
so the registry must never live inside a synced repo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

WEZTERM = os.environ.get("WZT_WEZTERM", "wezterm")
SUBPROC_TIMEOUT = 30  # seconds; wezterm cli calls are local RPC, 30s is generous


def _default_state_dir() -> Path:
    if os.environ.get("WZT_STATE_DIR"):
        return Path(os.environ["WZT_STATE_DIR"])
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "wzt"
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "wzt"


STATE_DIR = _default_state_dir()
STATE_FILE = STATE_DIR / "panes.json"


# ---------------------------------------------------------------- primitives

def _run(args: list[str], input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            [WEZTERM, "cli", *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=check,
            timeout=SUBPROC_TIMEOUT,
        )
    except FileNotFoundError:
        raise SystemExit("wezterm not found on PATH (set WZT_WEZTERM to the full path)")
    except subprocess.TimeoutExpired:
        raise SystemExit(f"wezterm cli {' '.join(args)} timed out after {SUBPROC_TIMEOUT}s "
                         "(is a wezterm GUI / mux server running?)")


def list_panes() -> list[dict]:
    out = _run(["list", "--format", "json"]).stdout
    return json.loads(out)


def _live_pane_ids() -> set[int]:
    return {p["pane_id"] for p in list_panes()}


def _default_context_pane() -> int:
    """Pane to anchor spawn/split when none is given.

    Newer wezterm versions REFUSE to guess (no WEZTERM_PANE in a headless/ssh
    caller => error out), so resolve the GUI's active pane explicitly.
    """
    panes = list_panes()
    if not panes:
        raise SystemExit("no panes exist — is a wezterm GUI running?")
    for p in panes:
        if p.get("is_active"):
            return p["pane_id"]
    return panes[0]["pane_id"]


# ------------------------------------------------------------------ registry

def _load_registry() -> dict[str, int]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_registry(reg: dict[str, int]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    # atomic write: a concurrent reader never sees a truncated file
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


def register(name: str, pane_id: int) -> None:
    reg = _load_registry()
    reg[name] = pane_id
    _save_registry(reg)


def resolve_pane(ref: str) -> int:
    """Accept a numeric pane-id or a registered name."""
    if re.fullmatch(r"\d+", ref):
        return int(ref)
    reg = _load_registry()
    if ref not in reg:
        raise SystemExit(f"unknown pane name: {ref!r} (known: {', '.join(reg) or 'none'})")
    pid = reg[ref]
    if pid not in _live_pane_ids():
        del reg[ref]
        _save_registry(reg)
        raise SystemExit(f"pane {pid} ({ref!r}) no longer exists; name unregistered")
    return pid


# ------------------------------------------------------------------ commands

def cmd_list(args) -> None:
    panes = list_panes()
    reg = _load_registry()
    live = {p["pane_id"] for p in panes}
    # prune dead names
    dead = [n for n, pid in reg.items() if pid not in live]
    if dead:
        for n in dead:
            del reg[n]
        _save_registry(reg)
    names_by_id = {pid: n for n, pid in reg.items()}
    if args.json:
        for p in panes:
            p["name"] = names_by_id.get(p["pane_id"])
        print(json.dumps(panes, indent=2, ensure_ascii=False))
        return
    rows = [("PANE", "NAME", "TAB", "WIN", "SIZE", "TITLE", "CWD")]
    for p in panes:
        rows.append((
            str(p["pane_id"]),
            names_by_id.get(p["pane_id"], ""),
            str(p["tab_id"]),
            str(p["window_id"]),
            f"{p['size']['cols']}x{p['size']['rows']}",
            (p.get("title") or "")[:40],
            (p.get("cwd") or "").replace("file://", "")[:60],
        ))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print("  ".join(c.ljust(widths[i]) for i, c in enumerate(r)))


def cmd_spawn(args) -> None:
    cli = ["spawn"]
    # Default posture: a NEW window in the dedicated workspace, so agent
    # activity never rearranges the user's existing window/tab layout
    # (the tmux community's "private socket" isolation convention).
    # --tab (or --window-id) opts back into the current window.
    tab_mode = args.tab or args.window_id is not None
    if args.tab and args.new_window:
        raise SystemExit("--tab and --new-window conflict; pick one")
    if tab_mode:
        if args.workspace:
            raise SystemExit("--workspace requires new-window mode (drop --tab/--window-id)")
        if args.window_id is not None:
            cli += ["--window-id", str(args.window_id)]
    else:
        cli.append("--new-window")
        cli += ["--workspace", args.workspace or "agents"]
    if args.domain:
        cli += ["--domain-name", args.domain]
    # --pane-id doubles as the domain anchor; always pass it (defaulting to
    # the GUI's active pane) because newer wezterm refuses to guess.
    pane_id = resolve_pane(args.pane_id) if args.pane_id is not None else _default_context_pane()
    cli += ["--pane-id", str(pane_id)]
    if args.cwd:
        cli += ["--cwd", args.cwd]
    if args.prog:
        cli += ["--", *args.prog]
    pid = int(_run(cli).stdout.strip())
    if args.name:
        register(args.name, pid)
    print(json.dumps({"pane_id": pid, "name": args.name}, ensure_ascii=False))


def cmd_split(args) -> None:
    cli = ["split-pane"]
    for d in ("left", "right", "top", "bottom"):
        if getattr(args, d):
            cli.append(f"--{d}")
    if args.horizontal:
        cli.append("--horizontal")
    if args.top_level:
        cli.append("--top-level")
    if args.percent is not None:
        cli += ["--percent", str(args.percent)]
    if args.cells is not None:
        cli += ["--cells", str(args.cells)]
    if args.pane_id is None:
        raise SystemExit(
            "split requires --pane-id (pane id or registered name): the active "
            "pane usually belongs to the user — never split it implicitly. "
            "Spawn your own pane first (wzt spawn --name X ...), then split that.")
    cli += ["--pane-id", str(resolve_pane(args.pane_id))]
    if args.domain:
        cli += ["--domain-name", args.domain]
    if args.cwd:
        cli += ["--cwd", args.cwd]
    if args.prog:
        cli += ["--", *args.prog]
    pid = int(_run(cli).stdout.strip())
    if args.name:
        register(args.name, pid)
    print(json.dumps({"pane_id": pid, "name": args.name}, ensure_ascii=False))


def _send_text(pane_id: int, text: str) -> None:
    """Inject text as a (bracketed) paste; does NOT submit."""
    _run(["send-text", "--pane-id", str(pane_id)], input_text=text)


def _send_enter(pane_id: int) -> None:
    """Submit: CR via --no-paste. LF does not accept the line in PSReadLine/readline."""
    _run(["send-text", "--pane-id", str(pane_id), "--no-paste", "\r"])


def cmd_send(args) -> None:
    pane_id = resolve_pane(args.pane)
    text = " ".join(args.text) if args.text else sys.stdin.read()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    try:
        _send_text(pane_id, text)
        if not args.no_enter:
            _send_enter(pane_id)
    except subprocess.CalledProcessError as e:
        if "no such pane" in (e.stderr or ""):
            raise SystemExit(f"pane {pane_id} exited before send completed")
        raise SystemExit(f"wezterm cli send-text failed: {(e.stderr or '').strip()}")


class PaneGone(RuntimeError):
    pass


def _get_text(pane_id: int, start_line: int | None = None) -> str:
    """get-text that raises PaneGone (instead of CalledProcessError) when the pane died."""
    cli = ["get-text", "--pane-id", str(pane_id)]
    if start_line is not None:
        cli += ["--start-line", str(start_line)]
    cp = _run(cli, check=False)
    if cp.returncode != 0:
        if "no such pane" in cp.stderr:
            raise PaneGone(f"pane {pane_id} exited")
        raise SystemExit(f"wezterm cli get-text failed: {cp.stderr.strip()}")
    return cp.stdout


def cmd_read(args) -> None:
    pane_id = resolve_pane(args.pane)
    start = None
    if args.all:
        start = -100000
    elif args.lines is not None:
        start = -abs(args.lines)
    try:
        sys.stdout.write(_get_text(pane_id, start))
    except PaneGone as e:
        raise SystemExit(str(e))


_MARKER_SHELLS = {
    # (prefix, suffix) wrapping the command with start/end markers.
    # pwsh: command is wrapped in try/catch so that a *terminating* error
    # (e.g. -ErrorAction Stop) cannot skip the end marker; LASTEXITCODE is
    # reset first so stale codes don't leak; catch sets 1 explicitly.
    "pwsh": ('echo __WZT_S_{token}__ ; $global:LASTEXITCODE = 0 ; try {{ ',
             ' }} catch {{ Write-Host ($_ | Out-String) ; $global:LASTEXITCODE = 1 }}'
             ' ; echo "__WZT_E_{token}_$($LASTEXITCODE)__"'),
    "powershell": ('echo __WZT_S_{token}__ ; $global:LASTEXITCODE = 0 ; try {{ ',
                   ' }} catch {{ Write-Host ($_ | Out-String) ; $global:LASTEXITCODE = 1 }}'
                   ' ; echo "__WZT_E_{token}_$($LASTEXITCODE)__"'),
    "bash": ('echo __WZT_S_{token}__ ; ', ' ; echo "__WZT_E_{token}_${{?}}__"'),
    "sh": ('echo __WZT_S_{token}__ ; ', ' ; echo "__WZT_E_{token}_${{?}}__"'),
    "zsh": ('echo __WZT_S_{token}__ ; ', ' ; echo "__WZT_E_{token}_${{?}}__"'),
    "cmd": ('echo __WZT_S_{token}__ & ', ' & echo __WZT_E_{token}_%ERRORLEVEL%__'),
}


def cmd_exec(args) -> None:
    pane_id = resolve_pane(args.pane)
    command = " ".join(args.command) if args.command else sys.stdin.read().rstrip("\n")
    token = uuid.uuid4().hex[:8]
    pre, post = _MARKER_SHELLS[args.shell]
    wrapped = pre.format(token=token) + command + post.format(token=token)
    try:
        _send_text(pane_id, wrapped)
        _send_enter(pane_id)

        deadline = time.monotonic() + args.timeout
        final = None
        exit_code = None
        # get-text pads rows to full width and long command echoes wrap across
        # rows, so tolerate whitespace inside the marker.
        end_pat = re.compile(r"__WZT_E_" + token + r"_\s*(-?\d*?)\s*__")
        while time.monotonic() < deadline:
            time.sleep(args.interval)
            buf = _get_text(pane_id, -100000)
            m = end_pat.search(buf)
            if m:
                final = buf
                exit_code = int(m.group(1)) if m.group(1) else None
                break
    except PaneGone as e:
        print(json.dumps({"ok": False, "pane_gone": True, "pane_id": pane_id,
                          "detail": str(e)}, ensure_ascii=False))
        sys.exit(3)
    if final is None:
        try:
            partial = _get_text(pane_id, -100000)
            tail_lines = [ln.rstrip() for ln in partial.splitlines()]
            while tail_lines and not tail_lines[-1]:
                tail_lines.pop()
            tail = "\n".join(tail_lines[-40:])
        except PaneGone as e:
            print(json.dumps({"ok": False, "pane_gone": True, "pane_id": pane_id,
                              "detail": str(e)}, ensure_ascii=False))
            sys.exit(3)
        print(json.dumps({
            "ok": False, "timeout": True, "pane_id": pane_id,
            "output_tail": tail,
        }, ensure_ascii=False))
        sys.exit(2)

    lines = final.splitlines()
    # output = rows strictly between the start-marker row and the end-marker row.
    # Locate by character offset (robust to marker wrapping across rows), and
    # skip the composite command's own echo: the REAL start marker is the LAST
    # occurrence before the end marker.
    e_pos = end_pat.search(final).start()
    s_pos = final.rfind(f"__WZT_S_{token}__", 0, e_pos)
    e_idx = final[:e_pos].count("\n")
    if s_pos < 0:
        # the pane's buffer was cleared mid-run (cls/clear) — start marker is
        # gone; fall back to everything before the end marker, flagged.
        out_lines = [ln.rstrip() for ln in lines[:e_idx]][-200:]
        print(json.dumps({
            "ok": True, "pane_id": pane_id, "exit_code": exit_code,
            "buffer_cleared": True,
            "output": "\n".join(out_lines),
        }, ensure_ascii=False))
        return
    s_idx = final[:s_pos].count("\n")
    out_lines = [ln.rstrip() for ln in lines[s_idx + 1:e_idx]]
    while out_lines and not out_lines[-1]:
        out_lines.pop()
    print(json.dumps({
        "ok": True,
        "pane_id": pane_id,
        "exit_code": exit_code,
        "output": "\n".join(out_lines),
    }, ensure_ascii=False))


def cmd_kill(args) -> None:
    pane_id = resolve_pane(args.pane)
    _run(["kill-pane", "--pane-id", str(pane_id)])
    reg = _load_registry()
    removed = [n for n, pid in reg.items() if pid == pane_id]
    for n in removed:
        del reg[n]
    _save_registry(reg)
    print(json.dumps({"killed": pane_id, "name": removed[0] if removed else None},
                     ensure_ascii=False))


def cmd_names(args) -> None:
    reg = _load_registry()
    live = _live_pane_ids()
    for n, pid in reg.items():
        status = "live" if pid in live else "DEAD"
        print(f"{n}\t{pid}\t{status}")


def cmd_doctor(args) -> None:
    """Install/verification aid: is wezterm reachable, is a GUI/mux up?"""
    ok = True

    def check(label, fn):
        nonlocal ok
        try:
            print(f"[ok] {label}: {fn()}")
        except Exception as e:
            ok = False
            print(f"[FAIL] {label}: {e}")

    check("wezterm binary", lambda: subprocess.run(
        [WEZTERM, "--version"], capture_output=True, text=True, timeout=SUBPROC_TIMEOUT
    ).stdout.strip() or WEZTERM)
    check("mux connection", lambda: f"{len(list_panes())} pane(s) visible")
    print(f"[info] state dir: {STATE_DIR}")
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------------- main

def main() -> None:
    # pane content may contain arbitrary Unicode (prompt glyphs etc.) while the
    # Windows console defaults to cp1252 — always emit UTF-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="wzt", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list panes (with registered names)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("spawn", help="spawn a new window (default) or tab, prints pane-id")
    p.add_argument("--name")
    p.add_argument("--cwd")
    p.add_argument("--new-window", action="store_true",
                   help="(default) create a new window in the agent workspace")
    p.add_argument("--tab", action="store_true",
                   help="opt back into a tab in the current window (only when the user asked)")
    p.add_argument("--window-id", type=int, help="implies --tab: tab in this window")
    p.add_argument("--pane-id", help="context pane: id or registered name (default: active pane)")
    p.add_argument("--workspace", help="workspace for the new window (default: agents)")
    p.add_argument("--domain", help="wezterm domain, e.g. SSH:<host> / SSHMUX:<host> / WSL:<distro>")
    p.add_argument("prog", nargs=argparse.REMAINDER, help="-- prog args...")
    p.set_defaults(fn=cmd_spawn)

    p = sub.add_parser("split", help="split a pane, prints new pane-id (--pane-id required)")
    p.add_argument("--name")
    p.add_argument("--pane-id", help="pane to split: id or registered name (required)")
    p.add_argument("--domain", help="wezterm domain, e.g. SSH:<host> / SSHMUX:<host> / WSL:<distro>")
    p.add_argument("--left", action="store_true")
    p.add_argument("--right", action="store_true")
    p.add_argument("--top", action="store_true")
    p.add_argument("--bottom", action="store_true")
    p.add_argument("--horizontal", action="store_true")
    p.add_argument("--top-level", action="store_true")
    p.add_argument("--percent", type=int)
    p.add_argument("--cells", type=int)
    p.add_argument("--cwd")
    p.add_argument("prog", nargs=argparse.REMAINDER)
    p.set_defaults(fn=cmd_split)

    p = sub.add_parser("send", help="inject text (paste) + Enter; stdin when no TEXT")
    p.add_argument("pane")
    p.add_argument("text", nargs="*")
    p.add_argument("--file")
    p.add_argument("--no-enter", action="store_true", help="leave text in the edit buffer")
    p.set_defaults(fn=cmd_send)

    p = sub.add_parser("exec", help="run a command, wait for completion, return output+exit code as JSON")
    p.add_argument("pane")
    p.add_argument("command", nargs="*", help="command text; stdin when omitted")
    p.add_argument("--shell", default="pwsh", choices=sorted(_MARKER_SHELLS),
                   help="shell dialect for the exit-code marker (default: pwsh)")
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--interval", type=float, default=0.4, help="poll interval seconds")
    p.set_defaults(fn=cmd_exec)

    p = sub.add_parser("read", help="print pane text (default: visible screen)")
    p.add_argument("pane")
    p.add_argument("--lines", type=int, help="last N lines incl. scrollback")
    p.add_argument("--all", action="store_true", help="entire scrollback")
    p.set_defaults(fn=cmd_read)

    p = sub.add_parser("kill", help="kill a pane")
    p.add_argument("pane")
    p.set_defaults(fn=cmd_kill)

    p = sub.add_parser("names", help="show name registry")
    p.set_defaults(fn=cmd_names)

    p = sub.add_parser("doctor", help="verify wezterm connectivity and print environment info")
    p.set_defaults(fn=cmd_doctor)

    args = ap.parse_args()
    # strip leading "--" that argparse.REMAINDER keeps
    if hasattr(args, "prog") and args.prog and args.prog[0] == "--":
        args.prog = args.prog[1:]
    args.fn(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        # last-resort guard: turn raw wezterm failures into a clean message
        detail = (e.stderr or "").strip() or str(e)
        print(f"wzt: wezterm cli failed: {detail}", file=sys.stderr)
        sys.exit(1)
