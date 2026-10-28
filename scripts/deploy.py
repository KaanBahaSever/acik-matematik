#!/usr/bin/env python3
"""
Açık Matematik — builds the site on this machine and publishes it to Cloudflare Pages.

There is no CI. A push to main is built and deployed right here:

    git push  ->  .git/hooks/pre-push  ->  deploy.py --after-push NEW OLD   (returns at once)
              ->  a detached deploy.py waits until main on GitHub has moved,
                  brings the deploy checkout to origin/main, runs scripts/build.py
                  there, checks _site and runs `wrangler pages deploy`.

The deploy checkout is a separate clone that only this script touches, so the
site is always built from exactly what is on main: never from a working tree
with uncommitted changes, drafts or half-made figures. Its _site, its _book
directories and its .build-cache.json survive between runs, so only the
courses that changed are rendered.

Everything lives outside the repository, in ~/.acik-matematik. Not in
%LOCALAPPDATA%: a packaged (MSIX) app such as an editor or an agent redirects
the AppData writes of every process it starts into its own private folder, so
a push made from inside it and one made from a terminal would see two
different checkouts.

    checkout/     the deploy clone
    wrangler/     a pinned wrangler install
    logs/         one log per run (the newest 30 are kept)
    state.json    the commit that is live and the outcome of the last run
    deploy.lock   held while a deployment runs, so runs never overlap

The Cloudflare token is read from CLOUDFLARE_API_TOKEN (the process
environment or the user's environment variables) and never printed. A
background run reports its outcome as a Windows notification.

Usage:
    python scripts/deploy.py                  # deploy origin/main now, in the foreground
    python scripts/deploy.py --force          # ... even if that commit is already live
    python scripts/deploy.py --install-hook   # deploy after every push to main
    python scripts/deploy.py --status         # what is live, is a deployment running
    python scripts/deploy.py --wait           # block until a running deployment ends
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = Path.home() / ".acik-matematik"
CHECKOUT = STATE_DIR / "checkout"
WRANGLER_DIR = STATE_DIR / "wrangler"
LOG_DIR = STATE_DIR / "logs"
STATE_FILE = STATE_DIR / "state.json"
LOCK_FILE = STATE_DIR / "deploy.lock"

PROJECT = "acik-matematik"          # the Cloudflare Pages project
BRANCH = "main"                     # the branch Cloudflare serves as production
WRANGLER_VERSION = "4.135.0"
KEEP_LOGS = 30
LAND_TIMEOUT = 5 * 60               # how long a push may take to reach GitHub
BUILD_TIMEOUT = 150 * 60            # a hung render must not hold the lock forever
PUBLISH_TIMEOUT = 30 * 60

# A change to these never changes a single page, so a push that touches only
# them is marked live without building or uploading anything.
IGNORED = ("README.md", "LICENCE", "docs/*", ".gitignore", "CLAUDE.md", ".claude/*")

HOOK_MARKER = "acik-matematik deploy hook"
HOOK = f"""#!/bin/sh
# {HOOK_MARKER}, installed by scripts/deploy.py --install-hook.
# After a push to main the site is built and deployed on this machine in the
# background; the push itself does not wait for it.
[ "$1" = origin ] || exit 0
zero=0000000000000000000000000000000000000000
if command -v python >/dev/null 2>&1; then py=python; else py="py -3"; fi
while read -r local_ref local_sha remote_ref remote_sha; do
    [ "$remote_ref" = refs/heads/main ] || continue
    [ "$local_sha" = "$zero" ] && continue
    script="$(git rev-parse --show-toplevel)/scripts/deploy.py"
    if [ -f "$script" ]; then
        $py "$script" --after-push "$local_sha" "$remote_sha" || echo "deploy: scripts/deploy.py could not be started" >&2
    else
        echo "deploy: this checkout has no scripts/deploy.py; run it from one that does" >&2
    fi
done
exit 0
"""

# Windows process creation flags.
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_NO_WINDOW = 0x08000000
# Child processes get a hidden console instead of flashing a window each.
NO_WINDOW = CREATE_NO_WINDOW if os.name == "nt" else 0

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


class DeployError(Exception):
    """A step failed; the message names the step."""


# ------------------------------------------------------------------- logging

class Log:
    """Writes to the run's log file and, in the foreground, to the console."""

    def __init__(self, path: Path, echo: bool):
        self.path = path
        self.echo = echo
        self.fh = open(path, "a", encoding="utf-8", newline="\n")

    def __call__(self, message: str) -> None:
        self.fh.write(f"{datetime.now():%H:%M:%S} [deploy] {message}\n")
        self.fh.flush()
        if self.echo:
            print(f"[deploy] {message}", flush=True)

    def output(self, line: str) -> None:
        """A line of a child process's output, unstamped."""
        self.fh.write(line + "\n")
        self.fh.flush()
        if self.echo:
            print(line, flush=True)


def new_log(tag: str, echo: bool) -> Log:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old = sorted(LOG_DIR.glob("*.log"))
    for path in old[:max(0, len(old) - (KEEP_LOGS - 1))]:
        path.unlink(missing_ok=True)
    return Log(LOG_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{tag}.log", echo)


def notify(title: str, body: str) -> None:
    """A Windows toast: a background run has no console to report to."""
    if os.name != "nt":
        return

    def quote(text: str) -> str:
        return "'" + text.replace("'", "''") + "'"

    script = "; ".join([
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
        "ContentType = WindowsRuntime] | Out-Null",
        "$xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
        "[Windows.UI.Notifications.ToastTemplateType]::ToastText02)",
        "$text = $xml.GetElementsByTagName('text')",
        f"$text.Item(0).AppendChild($xml.CreateTextNode({quote(title)})) | Out-Null",
        f"$text.Item(1).AppendChild($xml.CreateTextNode({quote(body)})) | Out-Null",
        # A toast must come from a registered application; this is PowerShell's id.
        "$app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe'",
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show("
        "[Windows.UI.Notifications.ToastNotification]::new($xml))",
    ])
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                       capture_output=True, timeout=60, creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        pass


# ----------------------------------------------------------------- processes

def kill_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                       capture_output=True, creationflags=NO_WINDOW)
    else:
        os.kill(pid, 9)


def run(cmd: list, log: Log, cwd: Path, timeout: int, env: dict | None = None) -> tuple[int, str]:
    """Run a command, streaming its output into the log; returns (exit code, output)."""
    cmd = [str(part) for part in cmd]
    log("$ " + " ".join([Path(cmd[0]).name, *cmd[1:]]))
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            creationflags=NO_WINDOW)
    expired = threading.Event()

    def expire() -> None:
        expired.set()
        kill_tree(proc.pid)

    timer = threading.Timer(timeout, expire)
    timer.start()
    lines = []
    try:
        for raw in proc.stdout:
            line = ANSI.sub("", raw.decode("utf-8", "replace").rstrip("\r\n"))
            lines.append(line)
            log.output(line)
        code = proc.wait()
    finally:
        timer.cancel()
    if expired.is_set():
        raise DeployError(f"{Path(cmd[0]).name} did not finish within {timeout // 60} minutes")
    return code, "\n".join(lines)


def git(*args: str, cwd: Path = CHECKOUT, check: bool = True) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
    if check and out.returncode != 0:
        raise DeployError(f"git {args[0]} failed: {out.stderr.strip()}")
    return out.stdout.strip()


# ---------------------------------------------------------------- lock, state

def _lock(fh) -> bool:
    fh.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def acquire_lock(wait: bool, log: Log | None = None):
    """The lock file's handle, or None when another run holds it and wait is False.

    The operating system drops the lock when its process dies, so a crashed
    run never leaves a stale lock behind.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    fh = open(LOCK_FILE, "a+b")
    announced = False
    while not _lock(fh):
        if not wait:
            fh.close()
            return None
        if log and not announced:
            log("another deployment is running; waiting for it to finish")
            announced = True
        time.sleep(5)
    return fh


def release_lock(fh) -> None:
    fh.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    finally:
        fh.close()


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


# --------------------------------------------------------------- environment

def user_env(name: str) -> str | None:
    """A variable from the user's environment, for processes started before it was set."""
    if os.name != "nt":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return str(winreg.QueryValueEx(key, name)[0]) or None
    except OSError:
        return None


def build_env() -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def cloudflare_env() -> dict:
    env = build_env()
    for name in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        if not env.get(name):
            value = user_env(name)
            if value:
                env[name] = value
    if not env.get("CLOUDFLARE_API_TOKEN"):
        raise DeployError("CLOUDFLARE_API_TOKEN is not set (an API token with the Cloudflare Pages: Edit permission)")
    env["CI"] = "1"                         # never prompt: nobody is there to answer
    env["WRANGLER_SEND_METRICS"] = "false"
    return env


def wrangler(log: Log) -> list[str]:
    """The command that runs the pinned wrangler, installing it on first use."""
    package = WRANGLER_DIR / "node_modules" / "wrangler"
    try:
        installed = json.loads((package / "package.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        installed = None
    if installed != WRANGLER_VERSION:
        npm = shutil.which("npm")
        if not npm:
            raise DeployError("npm is not on PATH (wrangler needs Node.js)")
        WRANGLER_DIR.mkdir(parents=True, exist_ok=True)
        log(f"installing wrangler {WRANGLER_VERSION}")
        code, _ = run([npm, "install", "--prefix", WRANGLER_DIR, "--no-audit", "--no-fund",
                       f"wrangler@{WRANGLER_VERSION}"], log, STATE_DIR, 10 * 60)
        if code:
            raise DeployError(f"wrangler could not be installed (npm exit code {code})")
    node = shutil.which("node")
    if not node:
        raise DeployError("node is not on PATH")
    return [node, str(package / "bin" / "wrangler.js")]


# --------------------------------------------------------------------- steps

def ensure_checkout(log: Log) -> None:
    if (CHECKOUT / ".git").exists():
        return
    url = git("remote", "get-url", "origin", cwd=ROOT)
    log(f"cloning {url}; the first build renders every course")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    git("clone", "--quiet", url, str(CHECKOUT), cwd=STATE_DIR)


def remote_main() -> str | None:
    out = git("ls-remote", "origin", "refs/heads/main", check=False)
    return out.split()[0] if out else None


def wait_for_push(new: str, old: str) -> bool:
    """True once main on GitHub has moved off OLD, to NEW or past it.

    The pre-push hook runs before anything is sent, so the push may still be
    in flight, or GitHub may reject it.
    """
    deadline = time.time() + LAND_TIMEOUT
    while time.time() < deadline:
        head = remote_main()
        if head and (head == new or head != old):
            return True
        time.sleep(5)
    return False


def site_unchanged(old: str, new: str) -> bool:
    """True when every file that changed between two commits is outside the site."""
    out = subprocess.run(["git", "diff", "--name-only", old, new], cwd=CHECKOUT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         creationflags=NO_WINDOW)
    if out.returncode != 0:                 # e.g. the old commit vanished in a force push
        return False
    files = [f for f in out.stdout.splitlines() if f]
    return all(any(fnmatch(f, pattern) for pattern in IGNORED) for f in files)


def verify_site(log: Log) -> str:
    site = CHECKOUT / "_site"
    for rel in ("index.html", "dersler/index.html"):
        if not (site / rel).is_file():
            raise DeployError(f"_site/{rel} was not produced")
    files = [p for p in site.rglob("*") if p.is_file()]
    count = {ext: sum(1 for p in files if p.suffix.lower() == ext) for ext in (".html", ".pdf", ".epub")}
    if count[".pdf"] == 0:
        raise DeployError("no PDF was produced (scripts/export.py)")
    # Every course that advertises downloads must actually ship them. Only books
    # count: a hub page (dersler/analiz, dersler/soyut-cebir) has no _quarto.yml,
    # and a directory that used to be a book can still hold its old manifest.
    for course in sorted((CHECKOUT / "dersler").iterdir()):
        if (course / "_quarto.yml").is_file() and (course / "_downloads.json").is_file():
            if not any((site / "dersler" / course.name).glob("*.pdf")):
                raise DeployError(f"_site/dersler/{course.name} has a download manifest but no PDF")
    size = sum(p.stat().st_size for p in files) / 2 ** 20
    summary = (f"{count['.html']} HTML pages, {count['.pdf']} PDF, {count['.epub']} EPUB, "
               f"{len(files)} files, {size:,.0f} MB")
    log(summary)
    return summary


def publish(log: Log, env: dict) -> str:
    cmd = [*wrangler(log), "pages", "deploy", "_site", f"--project-name={PROJECT}",
           f"--branch={BRANCH}", "--commit-dirty=true"]
    code, output = run(cmd, log, CHECKOUT, PUBLISH_TIMEOUT, env)
    if code:
        raise DeployError(f"wrangler pages deploy failed (exit code {code})")
    urls = re.findall(r"https://[\w.-]+\.pages\.dev", output)
    return urls[-1] if urls else ""


def deploy(log: Log, *, force: bool = False, pushed: tuple[str, str] | None = None) -> int:
    started = time.time()
    lock = acquire_lock(wait=True, log=log)
    state = load_state()
    head = ""
    try:
        ensure_checkout(log)
        if pushed:
            new, old = pushed
            log(f"waiting for {new[:7]} to reach GitHub")
            if not wait_for_push(new, old):
                log("main on GitHub did not move: the push was rejected or never sent; nothing to deploy")
                return 0
        git("fetch", "--quiet", "origin", "main")
        head = git("rev-parse", "FETCH_HEAD")
        subject = git("log", "-1", "--format=%s", head)
        log(f"origin/main is {head[:7]} {subject}")
        live = state.get("live")
        if live == head and not force:
            log("this commit is already live")
            return 0
        if live and not force and site_unchanged(live, head):
            log("no file the site is built from has changed; marked live without a deployment")
            state.update(live=head, live_subject=subject)
            return 0

        env = cloudflare_env()              # fail in seconds, not after the build
        git("reset", "--hard", "--quiet", head)
        code, _ = run([sys.executable, "scripts/build.py"], log, CHECKOUT, BUILD_TIMEOUT, build_env())
        # A full rebuild renders several books at once, and when the machine is
        # busy some renders die for lack of memory although the books are fine.
        # The build cache keeps every book that did render, so a second pass
        # repeats only the failed ones, one at a time. An export failure (exit
        # code 2) is already recorded in the cache and is not retried.
        if code == 1:
            log("some books failed to render; retrying them one at a time")
            code, _ = run([sys.executable, "scripts/build.py", "--serial"], log, CHECKOUT,
                          BUILD_TIMEOUT, build_env())
        if code:
            raise DeployError(f"the build failed (exit code {code})")
        summary = verify_site(log)
        url = publish(log, env)
        minutes = (time.time() - started) / 60
        log(f"live: {head[:7]} in {minutes:.1f} min {url}")
        state.update(live=head, live_subject=subject, live_url=url,
                     deployed_at=datetime.now().isoformat(timespec="seconds"))
        state["last_run"] = {"commit": head, "result": "deployed", "summary": summary,
                             "minutes": round(minutes, 1), "log": str(log.path)}
        notify("Açık Matematik yayında", f"{head[:7]} {subject} ({minutes:.0f} dk)")
        return 0
    except Exception as exc:                # noqa: BLE001 - every failure is reported
        if not isinstance(exc, DeployError):
            log.output(traceback.format_exc())
        log(f"FAILED: {exc}")
        state["last_run"] = {"commit": head, "result": "failed", "error": str(exc),
                             "at": datetime.now().isoformat(timespec="seconds"), "log": str(log.path)}
        notify("Açık Matematik yayınlanamadı", f"{exc}. Günlük: {log.path.name}")
        return 1
    finally:
        save_state(state)
        release_lock(lock)


# ------------------------------------------------------------------ commands

def start_in_background(new: str, old: str) -> int:
    """Called by the pre-push hook: start the deployment and return at once."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--run-after-push", new, old]
    if os.name == "nt":
        base = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
        # Break away from the job of whatever ran `git push` (a terminal, an
        # editor, an agent's shell), or closing it would kill the deployment.
        attempts = [{"creationflags": base | CREATE_BREAKAWAY_FROM_JOB}, {"creationflags": base}]
    else:
        attempts = [{"start_new_session": True}]
    for extra in attempts:
        try:
            subprocess.Popen(cmd, cwd=STATE_DIR, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True, **extra)
            break
        except OSError:
            continue
    else:
        print("deploy: the background deployment could not be started", file=sys.stderr)
        return 1
    print(f"deploy: {new[:7]} will be built and published in the background "
          f"(python scripts/deploy.py --status; logs in {LOG_DIR})", file=sys.stderr)
    return 0


def run_after_push(new: str, old: str) -> int:
    log = new_log(new[:7], echo=False)
    return deploy(log, pushed=(new, old))


def install_hook() -> int:
    hooks = Path(git("rev-parse", "--git-path", "hooks", cwd=ROOT))
    if not hooks.is_absolute():
        hooks = (ROOT / hooks).resolve()
    hook = hooks / "pre-push"
    if hook.exists() and HOOK_MARKER not in hook.read_text(encoding="utf-8", errors="replace"):
        print(f"{hook} exists and was not written by this script; merge the two by hand")
        return 1
    hooks.mkdir(parents=True, exist_ok=True)
    hook.write_text(HOOK, encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    print(f"installed {hook}; every worktree of this repository uses it")
    return 0


def status() -> int:
    state = load_state()
    lock = acquire_lock(wait=False)
    if lock:
        release_lock(lock)
    live = state.get("live", "")
    print(f"live      {live[:7] or '-'} {state.get('live_subject', '')}")
    if state.get("deployed_at"):
        print(f"          deployed {state['deployed_at']} {state.get('live_url', '')}")
    last = state.get("last_run")
    if last:
        detail = last.get("summary") or last.get("error") or ""
        print(f"last run  {last.get('result')} {last.get('commit', '')[:7]} {detail}")
        print(f"          {last.get('log', '')}")
    print(f"running   {'no' if lock else 'yes'}")
    if (CHECKOUT / ".git").exists():
        head = remote_main()
        if head:
            print(f"GitHub    main is {head[:7]} ({'live' if head == live else 'not live yet'})")
    return 0


def wait() -> int:
    lock = acquire_lock(wait=True)
    release_lock(lock)
    return status()


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 3 and argv[0] == "--after-push":
        return start_in_background(argv[1], argv[2])
    if len(argv) == 3 and argv[0] == "--run-after-push":
        return run_after_push(argv[1], argv[2])
    if argv == ["--install-hook"]:
        return install_hook()
    if argv == ["--status"]:
        return status()
    if argv == ["--wait"]:
        return wait()
    if argv in ([], ["--force"]):
        return deploy(new_log("manual", echo=True), force=bool(argv))
    print(f"unknown arguments: {' '.join(argv)} (see the top of scripts/deploy.py)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
