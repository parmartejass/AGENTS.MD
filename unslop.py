#!/usr/bin/env python3
"""
unslop: Empirically detect and eliminate AI output patterns.

Uses Claude Code to generate samples, identify repetitive patterns ("slop"),
and produce a skill file that eliminates them.

Usage:
  python unslop.py --domain "blog writing"
  python unslop.py --domain "React landing pages" --type visual --count 100
"""

import argparse
import asyncio
import json
import os
import re
import signal
import shutil
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path


# ── Defaults ───────────────────────────────────────────────────────────────

DEFAULT_COUNT = 50
DEFAULT_CONCURRENCY = 5
DEFAULT_TIMEOUT = 600
DEFAULT_RETRIES = 1
DEFAULT_ANALYSIS_TIMEOUT = 1800


@dataclass(frozen=True)
class ClaudeConfig:
    model: str | None = None
    effort: str | None = None
    timeout: int = DEFAULT_TIMEOUT


# ── Helpers ────────────────────────────────────────────────────────────────

class TerminalUI:
    def __init__(self):
        self.is_tty = sys.stdout.isatty()
        self.color_enabled = self.is_tty and not os.getenv("NO_COLOR")
        self.live_enabled = self.is_tty and os.getenv("TERM", "dumb") != "dumb"
        self._live_active = False
        self.spinner_frames = (
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            if self.live_enabled
            else ["-", "\\", "|", "/"]
        )
        self.icons = {
            "info": "›",
            "success": "✓",
            "warn": "!",
            "error": "✗",
            "work": "◌",
        }
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "dim": "\033[2m",
            "cyan": "\033[36m",
            "blue": "\033[34m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "magenta": "\033[35m",
            "white": "\033[97m",
        }

    def style(self, text: str, *tokens: str) -> str:
        if not self.color_enabled or not tokens:
            return text
        filtered = [token for token in tokens if token and token not in {"white", "dim"}]
        if not filtered:
            return text
        prefix = "".join(self.colors[token] for token in filtered if token in self.colors)
        return f"{prefix}{text}{self.colors['reset']}"

    def icon(self, tone: str) -> str:
        color_map = {
            "info": "cyan",
            "success": "green",
            "warn": "yellow",
            "error": "red",
            "work": "blue",
        }
        return self.style(self.icons.get(tone, "•"), color_map.get(tone, "white"), "bold")

    def terminal_width(self) -> int:
        return shutil.get_terminal_size((100, 20)).columns

    def clip(self, text: str, max_width: int) -> str:
        if max_width <= 0 or len(text) <= max_width:
            return text
        if max_width <= 3:
            return text[:max_width]
        return text[: max_width - 3] + "..."

    def format_duration(self, seconds: float) -> str:
        total = max(0, int(seconds))
        minutes, secs = divmod(total, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def progress_bar(self, done: int, total: int) -> str:
        width = max(12, min(30, self.terminal_width() - 58))
        if total <= 0:
            total = 1
        filled = int(width * done / total)
        empty = width - filled
        if self.live_enabled:
            bar = f"{self.style('█' * filled, 'cyan')}{'░' * empty}"
        else:
            bar = "#" * filled + "-" * empty
        return f"[{bar}]"

    def _clear_live(self) -> None:
        if self.live_enabled and self._live_active:
            print("\r\033[2K", end="", flush=True)
            self._live_active = False

    def _write_live(self, text: str) -> None:
        if not self.live_enabled:
            return
        print(f"\r\033[2K{text}", end="", flush=True)
        self._live_active = True

    def line(self, text: str = "") -> None:
        self._clear_live()
        print(text, flush=True)

    def log(self, msg: str, indent: int = 0) -> None:
        tone = "info"
        if msg.startswith("ERROR"):
            tone = "error"
        elif msg.startswith("WARNING"):
            tone = "warn"
        prefix = self.icon(tone)
        text = self.style(msg, "red" if tone == "error" else "yellow" if tone == "warn" else "")
        self.line(f"{'  ' * indent}{prefix} {text}")

    def banner(self, title: str) -> None:
        width = max(34, len(title) + 8)
        top = f"┌{'─' * width}┐"
        middle = f"│{title.center(width)}│"
        bottom = f"└{'─' * width}┘"
        self.line("")
        self.line(f"  {self.style(top, 'cyan')}")
        self.line(f"  {self.style(middle, 'bold')}")
        self.line(f"  {self.style(bottom, 'cyan')}")
        self.line("")

    def step(self, step: int, total: int, msg: str) -> None:
        divider = self.style("─" * 68, "blue")
        chip = self.style(f" STEP {step}/{total} ", "bold", "cyan")
        title = self.style(msg, "bold")
        self.line("")
        self.line(divider)
        self.line(f"  {chip} {title}")
        self.line(divider)
        self.line("")

    def progress(self, done: int, total: int, label: str, index: int, state: str, started_at: float, detail: str | None = None) -> None:
        tone = {
            "ok": "success",
            "retry": "warn",
            "fail": "error",
        }.get(state, "info")
        marker = {
            "ok": "OK",
            "retry": "RETRY",
            "fail": "FAIL",
        }.get(state, state.upper())
        elapsed = self.format_duration(time.monotonic() - started_at)
        line = f"{self.progress_bar(done, total)} {done:>2}/{total:<2} {label} {index + 1:<3} {self.style(marker, 'bold', 'green' if tone == 'success' else 'yellow' if tone == 'warn' else 'red')} {elapsed}"
        if detail:
            line += f"  {detail}"
        self.line(f"  {line}")


class LiveSpinner:
    def __init__(self, ui: TerminalUI, message: str):
        self.ui = ui
        self.message = message
        self.started_at = time.monotonic()
        self._running = False
        self._task: asyncio.Task | None = None

    async def _animate(self) -> None:
        i = 0
        while self._running:
            frame = self.ui.spinner_frames[i % len(self.ui.spinner_frames)]
            elapsed = self.ui.format_duration(time.monotonic() - self.started_at)
            self.ui._write_live(f"  {self.ui.style(frame, 'blue', 'bold')} {self.message} {elapsed}")
            i += 1
            await asyncio.sleep(0.12)

    async def start(self) -> None:
        self._running = True
        if self.ui.live_enabled:
            self._task = asyncio.create_task(self._animate())
        else:
            self.ui.line(f"  {self.ui.icon('work')} {self.message}")

    async def stop(self, success: bool = True, detail: str | None = None) -> None:
        self._running = False
        if self._task:
            await self._task
        self.ui._clear_live()
        tone = "success" if success else "error"
        label = detail or self.message
        elapsed = f"({self.ui.format_duration(time.monotonic() - self.started_at)})"
        self.ui.line(f"  {self.ui.icon(tone)} {label} {elapsed}")


class LiveClaudeFeed:
    def __init__(self, ui: TerminalUI, message: str):
        self.ui = ui
        self.message = message
        self.started_at = time.monotonic()
        self.phase = "starting"
        self.detail = ""
        self.preview = ""
        self._running = False
        self._task: asyncio.Task | None = None

    def _tool_phase(self, name: str) -> str:
        labels = {
            "Read": "reading files",
            "Glob": "listing files",
            "Grep": "searching files",
            "Write": "writing files",
            "Edit": "editing files",
            "WebFetch": "fetching pages",
            "WebSearch": "searching the web",
        }
        return labels.get(name, f"using {name}")

    def _summarize_value(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        if "/" in value:
            parts = [part for part in value.split("/") if part]
            if len(parts) >= 2:
                return "/".join(parts[-2:])
        return value

    def _tool_detail(self, payload) -> str:
        if not isinstance(payload, dict):
            return self._summarize_value(str(payload)) if payload else ""
        for key in ("path", "file_path", "filename", "pattern", "q", "query", "ref_id", "command"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return self._summarize_value(value)
        return ""

    def _set_preview(self, text: str) -> None:
        compact = re.sub(r"\s+", " ", text).strip()
        if compact:
            self.preview = compact[-120:]

    def handle(self, packet: dict) -> None:
        packet_type = packet.get("type")
        if packet_type == "stream_event":
            event = packet.get("event", {})
            event_type = event.get("type")
            if event_type == "message_start":
                self.phase = "thinking"
                self.detail = ""
                self.preview = ""
            elif event_type == "content_block_start":
                block = event.get("content_block", {})
                block_type = block.get("type")
                if block_type == "thinking":
                    self.phase = "thinking"
                    self.detail = ""
                    self.preview = ""
                elif block_type == "text":
                    self.phase = "drafting output"
                    self.detail = ""
                elif block_type == "tool_use":
                    name = block.get("name", "tool")
                    self.phase = self._tool_phase(name)
                    self.detail = self._tool_detail(block.get("input"))
                    self.preview = ""
            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                delta_type = delta.get("type")
                if delta_type == "thinking_delta":
                    self.phase = "thinking"
                elif delta_type == "text_delta":
                    self.phase = "drafting output"
                    self._set_preview(self.preview + delta.get("text", ""))
            elif event_type == "message_stop":
                self.phase = "finishing"
                self.detail = ""
        elif packet_type == "assistant":
            message = packet.get("message", {})
            for block in message.get("content", []):
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    self.phase = self._tool_phase(block.get("name", "tool"))
                    self.detail = self._tool_detail(block.get("input"))
                elif block.get("type") == "text":
                    self.phase = "drafting output"
                    self._set_preview(block.get("text", ""))
        elif packet_type == "user" and packet.get("tool_use_result"):
            self.phase = "processing results"
        elif packet_type == "result":
            self.phase = "finishing"
            self.detail = ""

    async def _animate(self) -> None:
        i = 0
        while self._running:
            frame = self.ui.spinner_frames[i % len(self.ui.spinner_frames)]
            elapsed = self.ui.format_duration(time.monotonic() - self.started_at)
            status = f"{self.message} {elapsed} | {self.phase}"
            if self.phase == "drafting output" and self.preview:
                max_preview = max(22, self.ui.terminal_width() - len(status) - 14)
                status += f" | {self.ui.clip(self.preview, max_preview)}"
            elif self.detail:
                max_detail = max(18, self.ui.terminal_width() - len(status) - 12)
                status += f" | {self.ui.clip(self.detail, max_detail)}"
            self.ui._write_live(f"  {self.ui.style(frame, 'blue', 'bold')} {status}")
            i += 1
            await asyncio.sleep(0.12)

    async def start(self) -> None:
        self._running = True
        if self.ui.live_enabled:
            self._task = asyncio.create_task(self._animate())
        else:
            self.ui.line(f"  {self.ui.icon('work')} {self.message}")

    async def stop(self, success: bool = True, detail: str | None = None) -> None:
        self._running = False
        if self._task:
            await self._task
        self.ui._clear_live()
        tone = "success" if success else "error"
        label = detail or self.message
        elapsed = f"({self.ui.format_duration(time.monotonic() - self.started_at)})"
        self.ui.line(f"  {self.ui.icon(tone)} {label} {elapsed}")


UI = TerminalUI()


async def run_with_spinner(message: str, work, success_msg: str | None = None):
    spinner = LiveSpinner(UI, message)
    await spinner.start()
    try:
        result = await work
    except Exception:
        await spinner.stop(success=False, detail=f"{message} failed")
        raise
    await spinner.stop(success=True, detail=success_msg or message)
    return result


async def run_claude_with_updates(
    message: str,
    prompt: str,
    cwd: str | None = None,
    config: ClaudeConfig | None = None,
    success_msg: str | None = None,
):
    feed = LiveClaudeFeed(UI, message)
    await feed.start()
    try:
        result = await claude(prompt, cwd=cwd, config=config, stream_handler=feed.handle)
    except Exception:
        await feed.stop(success=False, detail=f"{message} failed")
        raise
    await feed.stop(success=True, detail=success_msg or message)
    return result


def log(msg: str, indent: int = 0):
    UI.log(msg, indent=indent)


def log_step(step: int, total: int, msg: str):
    UI.step(step, total, msg)


# ── Claude Code Interface ─────────────────────────────────────────────────

async def claude(
    prompt: str,
    cwd: str | None = None,
    config: ClaudeConfig | None = None,
    stream_handler=None,
) -> str:
    """Run a prompt through `claude -p` and return the response."""
    config = config or ClaudeConfig()
    cmd = ["claude", "-p"]
    if stream_handler:
        cmd.extend(
            [
                "--permission-mode",
                "acceptEdits",
                "--verbose",
                "--output-format",
                "stream-json",
                "--include-partial-messages",
            ]
        )
    if config.model:
        cmd.extend(["--model", config.model])
    if config.effort:
        cmd.extend(["--effort", config.effort])
    cmd.append(prompt)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd or os.getcwd(),
        start_new_session=True,
    )

    stderr_task: asyncio.Task | None = None
    try:
        if not stream_handler:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
            if proc.returncode != 0:
                err = stderr.decode().strip()
                raise RuntimeError(f"claude -p failed (exit {proc.returncode}): {err}")
            return stdout.decode().strip()

        stderr_task = asyncio.create_task(proc.stderr.read())
        deadline = time.monotonic() + config.timeout
        final_result = ""
        text_chunks: list[str] = []
        permission_denials: list[dict] = []

        def handle_packet(packet: dict) -> None:
            nonlocal final_result
            try:
                stream_handler(packet)
            except Exception:
                pass

            packet_type = packet.get("type")
            if packet_type == "assistant":
                message = packet.get("message", {})
                for block in message.get("content", []):
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if text:
                            final_result = text
            elif packet_type == "stream_event":
                event = packet.get("event", {})
                if event.get("type") == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text_chunks.append(delta.get("text", ""))
            elif packet_type == "result":
                result = packet.get("result")
                if isinstance(result, str) and result:
                    final_result = result
                denials = packet.get("permission_denials")
                if isinstance(denials, list):
                    permission_denials.extend(d for d in denials if isinstance(d, dict))

        def handle_line(raw_line: bytes) -> None:
            decoded = raw_line.decode(errors="replace").strip()
            if not decoded:
                return
            try:
                packet = json.loads(decoded)
            except json.JSONDecodeError:
                return
            handle_packet(packet)

        buffer = bytearray()

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise asyncio.TimeoutError

            chunk = await asyncio.wait_for(proc.stdout.read(65536), timeout=remaining)
            if not chunk:
                break
            buffer.extend(chunk)
            while True:
                newline_at = buffer.find(b"\n")
                if newline_at < 0:
                    break
                raw_line = bytes(buffer[:newline_at])
                del buffer[: newline_at + 1]
                handle_line(raw_line)

        if buffer:
            handle_line(bytes(buffer))

        remaining = deadline - time.monotonic()
        if proc.returncode is None:
            await asyncio.wait_for(proc.wait(), timeout=max(0.1, remaining))
        stderr = await asyncio.wait_for(stderr_task, timeout=max(0.1, deadline - time.monotonic()))
    except asyncio.TimeoutError:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if stderr_task:
            stderr_task.cancel()
            try:
                await stderr_task
            except BaseException:
                pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except Exception:
            pass
        raise RuntimeError(f"claude -p timed out after {config.timeout}s")

    if proc.returncode != 0:
        err = stderr.decode().strip()
        raise RuntimeError(f"claude -p failed (exit {proc.returncode}): {err}")
    if stream_handler and permission_denials:
        denial = permission_denials[-1]
        tool_name = denial.get("tool_name", "tool")
        tool_input = denial.get("tool_input", {})
        target = ""
        if isinstance(tool_input, dict):
            target = tool_input.get("file_path") or tool_input.get("command") or ""
        raise RuntimeError(f"claude -p could not get {tool_name} permission for {target or 'the requested action'}")
    return (final_result or "".join(text_chunks)).strip()


async def claude_batch(
    prompts: list[str],
    concurrency: int,
    cwd: str | None = None,
    label: str = "sample",
    config: ClaudeConfig | None = None,
    retries: int = DEFAULT_RETRIES,
    on_success=None,
) -> dict[int, str]:
    """Run many `claude -p` calls with bounded concurrency."""
    sem = asyncio.Semaphore(concurrency)
    total = len(prompts)
    done = 0
    started_at = time.monotonic()

    async def _run(idx: int, prompt: str) -> tuple[int, str]:
        nonlocal done
        async with sem:
            last_exc: Exception | None = None
            for attempt in range(1, retries + 2):
                try:
                    result = await claude(prompt, cwd=cwd, config=config)
                    if on_success:
                        on_success(idx, result)
                    done += 1
                    detail = None if attempt == 1 else f"after retry {attempt - 1}"
                    UI.progress(done, total, label, idx, "ok", started_at, detail=detail)
                    return idx, result
                except Exception as exc:
                    last_exc = exc
                    if attempt <= retries:
                        UI.progress(
                            done + 1,
                            total,
                            label,
                            idx,
                            "retry",
                            started_at,
                            detail=f"{exc}",
                        )
                        await asyncio.sleep(min(5 * attempt, 15))
                        continue

            done += 1
            UI.progress(done, total, label, idx, "fail", started_at, detail=f"{last_exc}")
            return idx, ""

    tasks = [_run(i, p) for i, p in enumerate(prompts)]
    results = await asyncio.gather(*tasks)
    return {i: text for i, text in results if text}


# ── Step 1: Generate Prompts ──────────────────────────────────────────────

async def step_generate_prompts(
    domain: str,
    count: int,
    out: Path,
    config: ClaudeConfig,
) -> list[str]:
    prompts_path = out / "prompts.json"
    if prompts_path.exists():
        try:
            existing = json.loads(prompts_path.read_text())
            if isinstance(existing, list) and len(existing) == count and all(isinstance(p, str) for p in existing):
                log(f"Reusing existing prompts.json with {len(existing)} prompts", indent=1)
                return existing
            log("Existing prompts.json does not match the requested count; regenerating.", indent=1)
        except Exception:
            log("Existing prompts.json could not be parsed; regenerating.", indent=1)

    prompt = f"""Generate exactly {count} diverse, realistic prompts for the domain: "{domain}"

Each prompt should be something a real person would ask an AI to produce.
Vary across these dimensions:
- Sub-topic / subject matter
- Specificity (vague → highly detailed)
- Expected output length
- Audience and tone
- Complexity and format

Output ONLY a valid JSON array of strings. No markdown fences, no commentary."""

    raw = await run_with_spinner(
        "Asking Claude for a prompt set",
        claude(prompt, config=config),
        success_msg="Prompt set ready",
    )

    # Extract the JSON array
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        raise ValueError("Could not parse prompt list. Raw output:\n" + raw[:500])

    prompts = json.loads(m.group())
    prompts_path.write_text(json.dumps(prompts, indent=2))
    log(f"Generated {len(prompts)} prompts → prompts.json", indent=1)
    return prompts


# ── Step 2: Run Samples ──────────────────────────────────────────────────

async def step_run_samples(
    prompts: list[str],
    domain: str,
    dtype: str,
    concurrency: int,
    out: Path,
    config: ClaudeConfig,
    retries: int,
) -> None:
    samples = out / "samples"
    samples.mkdir(exist_ok=True)

    ext = ".html" if dtype == "visual" else ".md"
    expected_sample_names = {f"sample_{i:04d}{ext}" for i in range(len(prompts))}
    stale_samples = [
        path
        for path in sorted(samples.glob(f"*{ext}"))
        if path.name not in expected_sample_names
    ]
    for path in stale_samples:
        path.unlink()
    if stale_samples:
        log(f"Removed {len(stale_samples)} stale sample files from ./samples/", indent=1)

    run_prompts = prompts
    if dtype == "visual":
        run_prompts = [
            f"{p}\n\nIMPORTANT: Respond with ONLY a complete, self-contained HTML file. "
            f"All CSS and JS must be inline. You may use popular CDN links (Tailwind, Google Fonts, etc). "
            f"Keep it concise but complete: aim for roughly 250-500 lines total and avoid bloated filler sections. "
            f"No markdown wrapping, no explanation — just the raw HTML starting with <!DOCTYPE html>."
            for p in prompts
        ]

    def normalize_content(content: str) -> str:
        if dtype == "visual":
            # Try to extract clean HTML if wrapped in markdown
            m = re.search(r"(<!DOCTYPE html>.*</html>)", content, re.DOTALL | re.IGNORECASE)
            if m:
                content = m.group(1)
            stripped = content.lstrip()
            lowered = stripped.lower()
            if lowered.startswith("<!doctype html>") or lowered.startswith("<html"):
                return stripped
            return ""
        return content

    existing = {}
    pending_indices = []
    pending_prompts = []
    for i, prompt in enumerate(run_prompts):
        dest = samples / f"sample_{i:04d}{ext}"
        if dest.exists():
            normalized_existing = normalize_content(dest.read_text())
            if normalized_existing:
                existing[i] = normalized_existing
                if normalized_existing != dest.read_text():
                    dest.write_text(normalized_existing)
                continue
            log(f"Ignoring invalid existing {dest.name}; regenerating.", indent=1)

        pending_indices.append(i)
        pending_prompts.append(prompt)

    if existing:
        log(f"Reusing {len(existing)} existing samples from ./samples/", indent=1)

    def save_pending_result(batch_idx: int, content: str) -> None:
        sample_idx = pending_indices[batch_idx]
        dest = samples / f"sample_{sample_idx:04d}{ext}"
        normalized = normalize_content(content)
        if normalized:
            dest.write_text(normalized)

    results = dict(existing)
    if pending_prompts:
        batch_results = await claude_batch(
            pending_prompts,
            concurrency,
            label="sample",
            config=config,
            retries=retries,
            on_success=save_pending_result,
        )
        for batch_idx, content in batch_results.items():
            normalized = normalize_content(content)
            if normalized:
                results[pending_indices[batch_idx]] = normalized

    if len(results) != len(prompts):
        log(f"Saved {len(results)} of {len(prompts)} samples to ./samples/", indent=1)
    else:
        log(f"Saved {len(results)} samples to ./samples/", indent=1)


# ── Step 3: Render Screenshots ───────────────────────────────────────────

async def step_render_screenshots(out: Path) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log("ERROR: Playwright is required for visual domains.", indent=1)
        log("  pip install playwright && playwright install chromium", indent=1)
        sys.exit(1)

    samples = out / "samples"
    screenshots = out / "screenshots"
    screenshots.mkdir(exist_ok=True)

    html_files = sorted(samples.glob("*.html"))
    expected_screenshot_names = {f"{f.stem}.png" for f in html_files}
    stale_screenshots = [
        path
        for path in sorted(screenshots.glob("*.png"))
        if path.name not in expected_screenshot_names
    ]
    for path in stale_screenshots:
        path.unlink()
    if stale_screenshots:
        log(f"Removed {len(stale_screenshots)} stale screenshots from ./screenshots/", indent=1)

    log(f"Rendering {len(html_files)} pages...", indent=1)
    started_at = time.monotonic()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        for i, f in enumerate(html_files):
            try:
                await page.goto(f"file://{f.absolute()}")
                await page.wait_for_timeout(1500)
                dest = screenshots / f"{f.stem}.png"
                await page.screenshot(path=str(dest), full_page=True)
                UI.progress(i + 1, len(html_files), "shot", i, "ok", started_at, detail=dest.name)
            except Exception as exc:
                UI.progress(i + 1, len(html_files), "shot", i, "fail", started_at, detail=f"{exc}")

        await browser.close()


# ── Step 4: Analyze Patterns ─────────────────────────────────────────────

async def step_analyze(out: Path, domain: str, dtype: str, expected_count: int, config: ClaudeConfig) -> None:
    ext = "*.html" if dtype == "visual" else "*.md"
    actual_count = len(list((out / "samples").glob(ext)))
    if actual_count == 0:
        log("ERROR: No samples were generated, so analysis cannot run.", indent=1)
        return

    if actual_count != expected_count:
        log(
            f"Proceeding with {actual_count} successful samples out of {expected_count} requested.",
            indent=1,
        )

    if dtype == "visual":
        prompt = f"""You are an expert design pattern analyst. Your job is to find "slop" —
repetitive visual and structural patterns showing an AI falling back on defaults.

I generated {actual_count} AI-produced websites/pages for the domain "{domain}".

- HTML source files: ./samples/
- Rendered screenshots: ./screenshots/

Do this:
1. Look at the screenshots with your eyes. Go through them one by one and pay attention to
   what keeps showing up again and again.
2. Read through the HTML/CSS source to find code-level patterns.
3. Document every repetitive pattern you find:
   - Layout structures (hero sections, grid arrangements, etc.)
   - Color palettes and gradients
   - Typography choices and sizing
   - Component styles (buttons, cards, navbars, footers)
   - Decorative elements (blobs, shadows, rounded corners, etc.)
   - Spacing and proportion habits
   - Code patterns (class names, CSS property clusters, structural markup)
4. Be extremely specific. Don't say "similar layouts" — describe exactly what the layout is
   and what makes it repetitive.
5. Quantify. For each pattern, count how many of the {actual_count} samples exhibit it.

Write your full analysis to ./analysis.md"""
    else:
        prompt = f"""You are an expert writing pattern analyst. Your job is to find "slop" —
repetitive phrases, structures, and stylistic habits showing an AI falling back on defaults.

I generated {actual_count} AI-produced text outputs for the domain "{domain}".
They are all in the ./samples/ directory.

Do this:
1. Read through the sample files carefully. Look at every one.
2. Document every repetitive pattern you find:
   - Exact phrases that recur (quote them)
   - Sentence structures and constructions used too often
   - Opening patterns
   - Closing/concluding patterns
   - Transition phrases
   - Organizational/structural patterns
   - Tonal habits (hedging, enthusiasm, false authority)
   - Word choices and vocabulary clusters
   - Rhetorical devices used as crutches
3. Be extremely specific. Quote exact phrases.
4. Quantify. For each pattern, count how many of the {actual_count} samples use it.
5. Look for subtle patterns too — not just obvious phrases but deeper structural habits.

Write your full analysis to ./analysis.md"""

    log("Claude is reading every sample and screenshot.", indent=1)
    await run_claude_with_updates(
        "Analyzing patterns across the full sample set",
        prompt,
        cwd=str(out),
        config=config,
        success_msg="Analysis draft ready",
    )

    if (out / "analysis.md").exists():
        log("Analysis complete → analysis.md", indent=1)
    else:
        log("WARNING: analysis.md was not created. The analysis step may have failed.", indent=1)


# ── Step 5: Generate Skill File ──────────────────────────────────────────

async def step_generate_skill(out: Path, domain: str, config: ClaudeConfig) -> None:
    prompt = f"""Read ./analysis.md in this directory.

Based on those findings, create a skill file at ./skill.md that can be used as
instructions to prevent the identified slop patterns in the domain "{domain}".

Rules for the skill file:

1. Focus on what to AVOID. The bulk of the file should be specific things NOT to do.
   Do NOT prescribe specific alternatives — that just creates a new flavor of slop.

2. Be specific and actionable. Don't say "avoid clichéd openings." List the exact
   openings to avoid. Don't say "don't use generic color schemes." Name the exact
   colors and patterns to stop using.

3. Organize by category (e.g., "Phrases to never use", "Structural patterns to avoid",
   "Visual defaults to break away from", etc.)

4. Start with a one-line description: "Unslop profile for {domain}."

5. End with a short section that says something like: instead of reaching for any of
   these defaults, be creative. Vary your approach. If you catch yourself about to use
   any of the patterns listed above, stop and do something different.

6. The tone should be direct and terse — working instructions, not an essay.

Write the file to ./skill.md"""

    await run_claude_with_updates(
        "Generating the unslop profile",
        prompt,
        cwd=str(out),
        config=config,
        success_msg="Skill draft ready",
    )

    if (out / "skill.md").exists():
        log("Skill file created → skill.md", indent=1)
    else:
        log("WARNING: skill.md was not created.", indent=1)


# ── Step 6: Before / After ──────────────────────────────────────────────

async def step_before_after(
    out: Path,
    prompts: list[str],
    domain: str,
    dtype: str,
    config: ClaudeConfig,
) -> None:
    ba = out / "before-after"
    ba.mkdir(exist_ok=True)

    # Pick a prompt from the middle of the list
    test_prompt = prompts[len(prompts) // 2]
    (ba / "test-prompt.txt").write_text(test_prompt)

    ext = ".html" if dtype == "visual" else ".md"

    # ── Before (vanilla) ──
    log("Running test prompt vanilla (before)...", indent=1)
    if dtype == "visual":
        before_prompt = (
            f"{test_prompt}\n\nRespond with ONLY a complete, self-contained HTML file. "
            f"All CSS/JS inline. Keep it concise but complete: aim for roughly 250-500 lines total and avoid bloated filler sections. "
            f"No markdown, no explanation — just the raw HTML."
        )
    else:
        before_prompt = test_prompt

    before = await run_with_spinner(
        "Generating vanilla comparison page",
        claude(before_prompt, config=config),
        success_msg="Vanilla page ready",
    )
    if dtype == "visual":
        m = re.search(r"(<!DOCTYPE html>.*</html>)", before, re.DOTALL | re.IGNORECASE)
        if m:
            before = m.group(1)
    (ba / f"before{ext}").write_text(before)

    # ── After (with skill) ──
    log("Running test prompt with unslop profile (after)...", indent=1)
    skill = (out / "skill.md").read_text()
    after_prompt = f"""Follow these instructions for the task below:\n\n{skill}\n\n---\n\nTask:\n\n{before_prompt if dtype == 'visual' else test_prompt}"""

    after = await run_with_spinner(
        "Generating unslop comparison page",
        claude(after_prompt, config=config),
        success_msg="Unslop page ready",
    )
    if dtype == "visual":
        m = re.search(r"(<!DOCTYPE html>.*</html>)", after, re.DOTALL | re.IGNORECASE)
        if m:
            after = m.group(1)
    (ba / f"after{ext}").write_text(after)

    # ── Screenshots (visual only) ──
    if dtype == "visual":
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={"width": 1280, "height": 900})

                for name in ("before", "after"):
                    path = ba / f"{name}.html"
                    await page.goto(f"file://{path.absolute()}")
                    await page.wait_for_timeout(1500)
                    await page.screenshot(path=str(ba / f"{name}.png"), full_page=True)

                await browser.close()

            log("Screenshots: before.png, after.png", indent=1)
        except ImportError:
            log("Skipping screenshots (playwright not installed)", indent=1)

    log(f"Comparison saved to ./before-after/", indent=1)


# ── CLI ───────────────────────────────────────────────────────────────────

async def run(args: argparse.Namespace) -> None:
    # Verify claude is installed
    if not shutil.which("claude"):
        print("Error: `claude` CLI not found.")
        print("Install Claude Code: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    out = Path(args.output or "unslop-output").resolve()
    out.mkdir(parents=True, exist_ok=True)
    config = ClaudeConfig(
        model=args.model,
        effort=args.effort,
        timeout=args.timeout,
    )
    analysis_config = replace(config, timeout=max(args.analysis_timeout, args.timeout))

    is_visual = args.type == "visual"
    total = 4 + (1 if is_visual else 0) + (0 if args.skip_comparison else 1)

    UI.banner("unslop")
    log(f"Domain:      {args.domain}")
    log(f"Type:        {args.type}")
    log(f"Samples:     {args.count}")
    log(f"Concurrency: {args.concurrency}")
    log(f"Timeout:     {args.timeout}s")
    log(f"Analysis:    {analysis_config.timeout}s timeout")
    if args.model:
        log(f"Model:       {args.model}")
    if args.effort:
        log(f"Effort:      {args.effort}")
    log(f"Output:      {out}")

    step = 0

    # 1 — Generate prompts
    step += 1
    log_step(step, total, "Generate prompts")
    prompts = await step_generate_prompts(args.domain, args.count, out, config)

    # 2 — Run samples
    step += 1
    log_step(step, total, f"Run {len(prompts)} samples through Claude Code")
    await step_run_samples(
        prompts,
        args.domain,
        args.type,
        args.concurrency,
        out,
        config,
        args.retries,
    )

    # 3 — Screenshots (visual only)
    if is_visual:
        step += 1
        log_step(step, total, "Render screenshots")
        await step_render_screenshots(out)

    # 4 — Analyze
    step += 1
    log_step(step, total, "Analyze patterns")
    await step_analyze(out, args.domain, args.type, args.count, analysis_config)

    # 5 — Skill file
    step += 1
    log_step(step, total, "Generate unslop profile file")
    await step_generate_skill(out, args.domain, config)

    # 6 — Before / after
    if not args.skip_comparison:
        step += 1
        log_step(step, total, "Before / after comparison")
        await step_before_after(out, prompts, args.domain, args.type, config)

    # ── Summary ──
    UI.banner("done")
    log(f"Skill file:  {out / 'skill.md'}")
    log(f"Analysis:    {out / 'analysis.md'}")
    if not args.skip_comparison:
        log(f"Comparison:  {out / 'before-after/'}")
    UI.line("")
    log("To use the skill file:")
    log("  • Claude Code: copy skill.md into your project and add it as a skill", indent=1)
    log("  • CLAUDE.md: paste the contents into your CLAUDE.md", indent=1)
    log("  • Any LLM: prepend the contents to your system prompt", indent=1)
    UI.line("")


def main():
    parser = argparse.ArgumentParser(
        description="unslop — empirically detect and eliminate AI output patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python unslop.py --domain "blog writing"
  python unslop.py --domain "React landing pages" --type visual
  python unslop.py --domain "marketing emails" --count 20
  python unslop.py --domain "Python tutorials" --count 100 --concurrency 10
        """,
    )
    parser.add_argument(
        "--domain", required=True,
        help='domain to analyze (e.g. "blog writing", "React landing pages")',
    )
    parser.add_argument(
        "--type", choices=["text", "visual"], default="text",
        help="text = writing/code/prose, visual = websites/HTML (default: text)",
    )
    parser.add_argument(
        "--count", type=int, default=DEFAULT_COUNT,
        help=f"number of samples to generate (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=f"max parallel Claude Code calls (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Claude model alias/name to pass through (e.g. sonnet, opus)",
    )
    parser.add_argument(
        "--effort", choices=["low", "medium", "high", "max"], default=None,
        help="Claude effort level to pass through",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"seconds to wait per Claude call before failing (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--analysis-timeout", type=int, default=DEFAULT_ANALYSIS_TIMEOUT,
        help=f"seconds to wait for the analysis pass (default: {DEFAULT_ANALYSIS_TIMEOUT})",
    )
    parser.add_argument(
        "--retries", type=int, default=DEFAULT_RETRIES,
        help=f"retries per failed Claude call (default: {DEFAULT_RETRIES})",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="output directory (default: ./unslop-output)",
    )
    parser.add_argument(
        "--skip-comparison", action="store_true",
        help="skip the before/after comparison step",
    )

    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
