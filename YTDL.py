#!/usr/bin/env python3
"""
YTDL v2.0 - YouTube Downloader
Coded By Shivam Raj
https://github.com/BetterCallShiv
"""


#  Imports

import importlib.util
import subprocess
import sys
if not importlib.util.find_spec("rich") or not importlib.util.find_spec("requests"):
    print("\n[!] Missing required Python packages: rich, requests")
    if input("    Install them now? [Y/n]: ").strip().lower() in ("", "y", "yes"):
        cmd = [sys.executable, "-m", "pip", "install", "-q", "rich", "requests"]
        if subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            cmd.insert(5, "--break-system-packages")
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        sys.exit(1)
import argparse
import json
import os
import platform
import re
import shutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Callable
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from rich.rule import Rule
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


#  Constants

VERSION = "2.0"
AUTHOR = "Shivam Raj"
GITHUB = "github.com/BetterCallShiv"
GITHUB_URL = "https://github.com/BetterCallShiv/YTDL"
FONT_URL = "https://github.com/BetterCallShiv/YTDL/raw/main/fonts.zip"
FONT_NAME = "Montara Gothic"
EXTENSION = "mkv"
VALID_QUALITIES = ("144", "240", "360", "480", "720", "1080", "1440", "2160", "best")
MAX_RETRIES = 3
DEFAULT_WORKERS = 3
MAX_WORKERS = 5
_CREATION_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)
BANNER = (
    "[bold green]"
    "\u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588"
    "\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588"
    "\u2557 \u2588\u2588\u2557     \n"
    "\u255a\u2588\u2588\u2557 \u2588\u2588\u2554\u255d\u255a\u2550\u2550"
    "\u2588\u2588\u2554\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550"
    "\u2588\u2588\u2557\u2588\u2588\u2551     \n"
    " \u255a\u2588\u2588\u2588\u2588\u2554\u255d    \u2588\u2588\u2551"
    "   \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551     \n"
    "  \u255a\u2588\u2588\u2554\u255d     \u2588\u2588\u2551   \u2588"
    "\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551     \n"
    "   \u2588\u2588\u2551      \u2588\u2588\u2551   \u2588\u2588\u2588"
    "\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2588"
    "\u2588\u2557\n"
    "   \u255a\u2550\u255d      \u255a\u2550\u255d   \u255a\u2550\u2550"
    "\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u2550"
    "\u255d[/]\n"
    f"[bold cyan]         YouTube Downloader v{VERSION}[/]\n"
    f"[bold yellow]         By {AUTHOR}[/]\n"
    f"[bold blue]         {GITHUB}[/]"
)
console = Console()


#  Data Classes

@dataclass
class DownloadResult:
    url: str
    title: str = ""
    success: bool = False
    error: str = ""
    output_file: str = ""
    duration: float = 0.0


@dataclass
class DownloadJob:
    url: str
    quality: str = "best"
    sub_langs: List[str] = field(default_factory=lambda: ["en"])
    output_dir: str = "."
    workers: int = DEFAULT_WORKERS
    playlist_index: Optional[int] = None
    is_playlist: Optional[bool] = None


@dataclass
class Config:
    output_dir: str = "."
    font_path: str = ""
    font_size: int = 20
    playlist_numbering: bool = False
    @staticmethod
    def _path() -> Path:
        return Path.home() / ".ytdl_config.json"
    @classmethod
    def load(cls) -> "Config":
        p = cls._path()
        if p.exists():
            try:
                import json
                data = json.loads(p.read_text(encoding="utf-8"))
                return cls(**data)
            except Exception:
                pass
        return cls()
        
    def save(self):
        import json
        self._path().write_text(json.dumps(self.__dict__, indent=4), encoding="utf-8")


class DependencyChecker:
    REQUIRED_COMMANDS: Dict[str, Dict] = {
        "yt-dlp": {
            "check": ["yt-dlp", "--version"],
            "install": {
                "pip":     "pip install yt-dlp",
                "linux":   "sudo apt install yt-dlp  OR  pip install yt-dlp",
                "darwin":  "brew install yt-dlp",
                "windows": "pip install yt-dlp  OR  winget install yt-dlp",
                "termux":  "pip install yt-dlp",
            },
        },
        "ffmpeg": {
            "check": ["ffmpeg", "-version"],
            "install": {
                "linux":   "sudo apt install ffmpeg",
                "darwin":  "brew install ffmpeg",
                "windows": "winget install ffmpeg  OR  choco install ffmpeg",
                "termux":  "pkg install ffmpeg",
            },
        },
    }
    REQUIRED_PACKAGES: Dict[str, Dict] = {
        "srt_fix": {
            "check_python": "yt_dlp_plugins.postprocessor.srt_fix",
            "install": (
                "pip install "
                "https://github.com/bindestriche/srt_fix/archive/refs/heads/master.zip"
            ),
        },
    }


    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}


    def check_all(self, auto_install: bool = True, quiet_if_ok: bool = False) -> bool:
        table = Table(
            title="Dependency Check",
            box=box.ROUNDED,
            title_style="bold cyan",
            border_style="dim",
        )
        table.add_column("Dependency", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Version / Install Hint", style="dim")
        table.add_column("Required", justify="center")
        all_ok = True
        missing_install_cmds = []
        for name, info in self.REQUIRED_COMMANDS.items():
            ok, version = self._check_command(info["check"])
            self.results[name] = (ok, version)
            status = "[bold green]\u2713 Found[/]" if ok else "[bold red]\u2717 Missing[/]"
            hint = self._install_hint(info["install"])
            detail = version if ok else f"Install: {hint}"
            table.add_row(name, status, detail, "[bold red]Yes[/]")
            if not ok:
                all_ok = False
                missing_install_cmds.append(hint.split("  OR  ")[0])
        for name, info in self.REQUIRED_PACKAGES.items():
            ok = self._check_python_package(info["check_python"])
            self.results[name] = (ok, "")
            status = "[bold green]\u2713 Found[/]" if ok else "[bold red]\u2717 Missing[/]"
            hint = info["install"]
            detail = "Installed" if ok else f"Install: {hint}"
            table.add_row(name, status, detail, "[bold red]Yes[/]")
            if not ok:
                all_ok = False
                missing_install_cmds.append(hint)
        if not all_ok or not quiet_if_ok:
            console.print()
            console.print(table)
            console.print()
        if not all_ok:
            if auto_install and missing_install_cmds:
                ans = Prompt.ask("[bold yellow]\u26a0 Missing required dependencies. Install them now automatically?[/]", choices=["y", "n"], default="y")
                if ans == "y":
                    for cmd in missing_install_cmds:
                        if cmd.startswith("pip install "):
                            cmd = cmd.replace("pip install ", f'"{sys.executable}" -m pip install ')
                        console.print(f"[dim]Running:[/] {cmd}")
                        try:
                            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                            if res.returncode != 0:
                                if "externally-managed-environment" in res.stderr:
                                    console.print("[dim]Externally managed environment detected. Retrying with --break-system-packages...[/]")
                                    retry_cmd = cmd.replace("pip install ", "pip install --break-system-packages ")
                                    res2 = subprocess.run(retry_cmd, shell=True, capture_output=True, text=True)
                                    if res2.returncode != 0:
                                        console.print(f"[bold red]\u2717 Failed to install with command: {retry_cmd}[/]")
                                        if res2.stderr:
                                            console.print(f"[dim]{res2.stderr.strip()}[/]")
                                else:
                                    console.print(f"[bold red]\u2717 Failed to install with command: {cmd}[/]")
                                    if res.stderr:
                                        console.print(f"[dim]{res.stderr.strip()}[/]")
                        except Exception as e:
                            console.print(f"[bold red]\u2717 Error executing command: {e}[/]")
                    console.print("[bold cyan]Re-checking dependencies...[/]")
                    return self.check_all(auto_install=False)
            console.print(
                "[bold red]\u2717 Missing required dependencies. "
                "Please install them and try again.[/]"
            )
        return all_ok


    def is_available(self, name: str) -> bool:
        if name in self.results:
            return self.results[name][0]
        if name in self.REQUIRED_COMMANDS:
            ok, _ = self._check_command(self.REQUIRED_COMMANDS[name]["check"])
            self.results[name] = (ok, "")
            return ok
        if name in self.REQUIRED_PACKAGES:
            ok = self._check_python_package(self.REQUIRED_PACKAGES[name]["check_python"])
            self.results[name] = (ok, "")
            return ok
        return False


    def _check_command(self, cmd: List[str]) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10,
                creationflags=_CREATION_FLAGS,
            )
            version = result.stdout.strip().split("\n")[0][:60]
            return True, version
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False, ""


    @staticmethod
    def _check_python_package(package: str) -> bool:
        import importlib
        import site
        importlib.reload(site)
        importlib.invalidate_caches()
        try:
            importlib.import_module(package)
            return True
        except ModuleNotFoundError as e:
            if "yt_dlp_plugins" in package and e.name == "yt_dlp":
                return True
            return False
        except ImportError:
            return False


    @staticmethod
    def _install_hint(install_map: Dict[str, str]) -> str:
        system = platform.system().lower()
        if "TERMUX_VERSION" in os.environ or Path("/data/data/com.termux").exists():
            system = "termux"
        return install_map.get(system, install_map.get("pip", "pip install <package>"))


class Updater:
    @staticmethod
    def update_ytdlp():
        console.print()
        with console.status("[bold cyan]Updating yt-dlp\u2026", spinner="dots"):
            try:
                result = subprocess.run(
                    ["yt-dlp", "-U"],
                    capture_output=True, text=True, timeout=60,
                    creationflags=_CREATION_FLAGS,
                )
                output = (result.stdout + result.stderr).strip()
                if result.returncode == 0:
                    console.print(f"[bold green]\u2713 {output or 'yt-dlp is up to date.'}[/]")
                else:
                    console.print("[dim]Self-update failed, trying pip\u2026[/]")
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    except subprocess.CalledProcessError:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", "-U", "--break-system-packages", "yt-dlp"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    console.print("[bold green]\u2713 yt-dlp updated via pip.[/]")
            except FileNotFoundError:
                console.print("[bold red]\u2717 yt-dlp not found. Install it first.[/]")
            except subprocess.TimeoutExpired:
                console.print("[bold yellow]\u26a0 Update timed out.[/]")
            except Exception as exc:
                console.print(f"[bold red]\u2717 Update failed: {exc}[/]")
        console.print()


class ETATracker:
    def __init__(self, total_items: int = 1):
        self.total_items = total_items
        self.completed_items = 0
        self.failed_items = 0
        self.start_time = time.time()
        self.item_times: List[float] = []
        self.current_progress: Dict[str, str] = {}
        self._lock = threading.Lock()

    def item_completed(self, duration: float):
        with self._lock:
            self.completed_items += 1
            self.item_times.append(duration)

    def item_failed(self):
        with self._lock:
            self.failed_items += 1

    def update_progress(self, key: str, value: str):
        with self._lock:
            self.current_progress[key] = value

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def avg_item_time(self) -> float:
        return (sum(self.item_times) / len(self.item_times)) if self.item_times else 0

    @property
    def remaining_items(self) -> int:
        return self.total_items - self.completed_items - self.failed_items

    @property
    def queue_eta(self) -> str:
        if not self.item_times or self.remaining_items <= 0:
            return "Calculating\u2026"
        return self.format_seconds(self.avg_item_time * self.remaining_items)

    @property
    def overall_progress(self) -> float:
        if self.total_items == 0:
            return 100.0
        return ((self.completed_items + self.failed_items) / self.total_items) * 100

    def format_elapsed(self) -> str:
        return self.format_seconds(self.elapsed)

    @staticmethod
    def format_seconds(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}h{m:02d}m{s:02d}s"
        if m > 0:
            return f"{m}m{s:02d}s"
        return f"{s}s"


class SubtitleProcessor:
    _FFMPEG_RE = re.compile(r"size=\s*(\S+)\s+time=\s*(\S+).*?speed=\s*(\S+)")

    def __init__(self, font_paths: List[str], sub_langs: Optional[List[str]] = None):
        self.font_paths = font_paths
        self.sub_langs = sub_langs or ["en"]

    def process(
        self, work_dir: str, video_file: str, video_title: str,
        on_progress: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        work = Path(work_dir)
        video = work / video_file
        stem = video.stem
        ass_files: List[str] = []
        lang_order: List[str] = []
        for lang in self.sub_langs:
            srt = self._find_srt(work, stem, lang)
            if srt is None:
                continue
            ass = work / f"{stem}.{lang}.ass"
            if self._srt_to_ass(str(srt), str(ass)):
                self._style_ass(str(ass))
                ass_files.append(str(ass))
                lang_order.append(lang)
        cover = self._find_cover(work, stem)
        output = work / f"{stem}_FINAL.{EXTENSION}"
        ok = self._mux(
            video_file=str(video),
            video_title=video_title,
            ass_files=ass_files,
            lang_order=lang_order,
            cover_file=cover,
            font_paths=self.font_paths,
            output_file=str(output),
            on_progress=on_progress,
        )
        return str(output) if ok else None

    @staticmethod
    def _find_srt(work: Path, stem: str, lang: str) -> Optional[Path]:
        for pattern in (f"{stem}.{lang}-fixed.srt", f"{stem}.{lang}.srt"):
            candidate = work / pattern
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def _find_cover(work: Path, stem: str) -> Optional[str]:
        for name in (f"{stem}.jpg", "cover.jpg"):
            p = work / name
            if p.exists():
                return str(p)
        return None

    @staticmethod
    def _srt_to_ass(srt_path: str, ass_path: str) -> bool:
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", srt_path, ass_path],
                capture_output=True, timeout=30,
                creationflags=_CREATION_FLAGS,
            )
            return Path(ass_path).exists()
        except Exception:
            return False

    @staticmethod
    def _style_ass(ass_path: str):
        try:
            conf = Config.load()
            font_size = conf.font_size
            font_name = Path(conf.font_path).stem if conf.font_path and Path(conf.font_path).exists() else FONT_NAME
            text = Path(ass_path).read_text(encoding="utf-8")
            text = re.sub(
                r"(Default,)Arial,\d+",
                rf"\g<1>{font_name},{font_size}",
                text,
            )
            Path(ass_path).write_text(text, encoding="utf-8")
        except Exception:
            pass

    @classmethod
    def _mux(
        cls,
        video_file: str,
        video_title: str,
        ass_files: List[str],
        lang_order: List[str],
        cover_file: Optional[str],
        font_paths: List[str],
        output_file: str,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> bool:
        try:
            cmd: List[str] = ["ffmpeg", "-y", "-i", video_file]
            for ass in ass_files:
                cmd += ["-i", ass]
            cmd += ["-map", "0:v", "-map", "0:a?"]
            for i in range(len(ass_files)):
                cmd += ["-map", f"{i + 1}:0"]
            attach_idx = 0
            if cover_file and Path(cover_file).exists():
                cmd += ["-attach", cover_file,
                        f"-metadata:s:t:{attach_idx}", "mimetype=image/jpeg"]
                attach_idx += 1
            for f_path in font_paths:
                if Path(f_path).exists():
                    cmd += ["-attach", f_path,
                            f"-metadata:s:t:{attach_idx}",
                            "mimetype=application/x-truetype-font"]
                    attach_idx += 1
            cmd += ["-c", "copy", "-c:s", "ass"]
            for i, lang in enumerate(lang_order):
                lang_name = lang.capitalize()
                cmd += [
                    f"-metadata:s:s:{i}", f"language={lang}",
                    f"-metadata:s:s:{i}", f"title={lang_name}",
                ]
                cmd += [f"-disposition:s:{i}", "default" if i == 0 else "0"]
            cmd += ["-metadata", f"title={video_title}"]
            cmd += ["-metadata", f"DOWNLOADED_USING={GITHUB_URL}"]
            cmd.append(output_file)
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=_CREATION_FLAGS,
            )
            for line in proc.stdout:
                line = line.strip()
                if on_progress:
                    m = cls._FFMPEG_RE.search(line)
                    if m:
                        size, time_str, speed = m.groups()
                        time_str = time_str.split(".")[0]
                        on_progress(f"size: {size} | time: {time_str} | speed: {speed}")
            proc.wait()
            return Path(output_file).exists() and proc.returncode == 0
        except Exception:
            return False


class VideoDownloader:
    _PROGRESS_RE = re.compile(
        r"\[download\]\s+([\d.]+)%\s+of\s+~?\s*([\d.]+\S+)"
        r"\s+at\s+([\d.]+\S+/s)\s+ETA\s+(\S+)"
    )
    _DONE_RE = re.compile(r"\[download\]\s+100(?:\.0)?%\s+of")
    _font_lock = threading.Lock()
    _font_cache: Dict[str, str] = {}

    def __init__(
        self,
        dep_checker: DependencyChecker,
        eta_tracker: Optional[ETATracker] = None,
    ):
        self.dep_checker = dep_checker
        self.eta_tracker = eta_tracker

    def download(
        self,
        job: DownloadJob,
        progress: Optional[Progress] = None,
        task_id=None,
    ) -> DownloadResult:
        result = DownloadResult(url=job.url)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = self._attempt(job, progress, task_id, attempt)
                if result.success:
                    return result
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                result.error = str(exc)
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                if progress and task_id is not None:
                    progress.update(
                        task_id,
                        description=f"[yellow]Retry {attempt}/{MAX_RETRIES} in {wait}s\u2026",
                    )
                if result.error:
                    console.print(f"  [dim yellow]Attempt {attempt} failed: {result.error}[/]")
                time.sleep(wait)
        return result

    def _attempt(
        self,
        job: DownloadJob,
        progress: Optional[Progress],
        task_id,
        attempt: int,
    ) -> DownloadResult:
        result = DownloadResult(url=job.url)
        t0 = time.time()
        output_dir = Path(job.output_dir).resolve()
        temp_dir = (
            output_dir
            / ".ytdl_temp"
            / f"dl_{os.getpid()}_{threading.current_thread().ident}_{int(t0)}"
        )
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            font_paths = self._ensure_font(output_dir)
            cmd = self._build_cmd(job)
            if progress and task_id is not None:
                progress.update(task_id, description="[cyan]Downloading\u2026")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(temp_dir),
                creationflags=_CREATION_FLAGS,
            )
            title = ""
            for line in proc.stdout:
                line = line.strip()
                if "[download] Destination:" in line:
                    dest = line.split("Destination:")[-1].strip()
                    raw_title = Path(dest).stem
                    title = re.sub(r'\.f[a-zA-Z0-9]+$', '', raw_title)
                    result.title = title
                    if progress and task_id is not None:
                        short = title[:40] + ("\u2026" if len(title) > 40 else "")
                        progress.update(task_id, description=f"[cyan]\u2193 {short}")
                m = self._PROGRESS_RE.search(line)
                if m and progress and task_id is not None:
                    pct, size, speed, eta = (
                        float(m.group(1)),
                        m.group(2),
                        m.group(3),
                        m.group(4),
                    )
                    prefix = f"[yellow](Retry {attempt})[/] " if attempt > 1 else ""
                    progress.update(
                        task_id,
                        completed=pct,
                        description=f"{prefix}[cyan]\u2193 {speed} | {size} | ETA {eta}",
                    )
                    if self.eta_tracker:
                        self.eta_tracker.update_progress("speed", speed)
                        self.eta_tracker.update_progress("eta", eta)
                if self._DONE_RE.search(line) and progress and task_id is not None:
                    progress.update(task_id, completed=100)
                if progress and task_id is not None:
                    prefix = f"[yellow](Retry {attempt})[/] " if attempt > 1 else ""
                    if "[Merger] Merging formats" in line:
                        progress.update(task_id, description=f"{prefix}[cyan]Merging video & audio\u2026")
                    elif "[info] Writing video subtitles" in line:
                        progress.update(task_id, description=f"{prefix}[cyan]Downloading subtitles\u2026")
                    elif "[ThumbnailsConvertor]" in line or "[info] Downloading video thumbnail" in line:
                        progress.update(task_id, description=f"{prefix}[cyan]Processing thumbnails\u2026")
                    elif "[Metadata]" in line:
                        progress.update(task_id, description=f"{prefix}[cyan]Applying metadata\u2026")
                    elif "[Fixup" in line or "Fixing" in line:
                        progress.update(task_id, description=f"{prefix}[cyan]Fixing container\u2026")
                if line.lower().startswith("error:"):
                    result.error = line
            proc.wait()
            videos = sorted(temp_dir.glob(f"*.{EXTENSION}"))
            if not videos:
                if proc.returncode != 0 and result.error:
                    return result
                result.error = "No video file found after download."
                return result
            video_file = videos[0]
            result.title = result.title or video_file.stem
            if progress and task_id is not None:
                progress.update(task_id, description=f"[yellow]Packaging final MKV\u2026")
            def mux_progress(stats: str):
                if progress and task_id is not None:
                    pfx = f"[yellow](Retry {attempt})[/] " if attempt > 1 else ""
                    progress.update(
                        task_id, 
                        description=f"{pfx}[yellow]Packaging MKV | {stats}"
                    )
            processor = SubtitleProcessor(font_paths, job.sub_langs)
            muxed = processor.process(str(temp_dir), video_file.name, result.title, on_progress=mux_progress)
            final_source = Path(muxed) if muxed and Path(muxed).exists() else video_file
            conf = Config.load()
            if job.playlist_index is not None and conf.playlist_numbering:
                final_name = f"{job.playlist_index:03d} - {result.title}.{EXTENSION}"
            else:
                final_name = f"{result.title}.{EXTENSION}"
            final_name = re.sub(r'[<>:"/\\|?*]', "_", final_name)
            final_path = output_dir / final_name
            shutil.move(str(final_source), str(final_path))
            result.output_file = str(final_path)
            result.success = True
            result.duration = time.time() - t0
            if progress and task_id is not None:
                progress.update(
                    task_id, completed=100, description="[bold green]\u2713 Done"
                )
        except Exception as exc:
            result.error = str(exc)
        finally:
            shutil.rmtree(str(temp_dir), ignore_errors=True)
        return result


    def _build_cmd(self, job: DownloadJob) -> List[str]:
        cmd = [
            "yt-dlp",
            "--newline",
            "--add-metadata",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "-N", "8",
        ]
        if job.quality == "best":
            cmd += ["-f", "bestvideo+bestaudio/best"]
        else:
            cmd += [
                "-f",
                f"bestvideo[height<={job.quality}]+bestaudio"
                f"/best[height<={job.quality}]",
            ]
        if job.sub_langs:
            cmd += [
                "--write-sub", "--write-auto-sub",
                "--sub-lang", ",".join(job.sub_langs),
                "--convert-subs", "srt",
            ]
            cmd += ["--use-postprocessor", "srt_fix"]
        cmd += [
            "--merge-output-format", EXTENSION,
            "-o", "%(title)s.%(ext)s",
            "--no-playlist",
            job.url,
        ]
        return cmd


    def _ensure_font(self, output_dir: Path) -> List[str]:
        conf = Config.load()
        if conf.font_path and Path(conf.font_path).exists():
            return [conf.font_path]
        cache_dir = output_dir / ".ytdl_temp"
        with self._font_lock:
            key = str(cache_dir)
            if key in self._font_cache:
                return self._font_cache[key]
            cache_dir.mkdir(parents=True, exist_ok=True)
            font_dir = cache_dir / "fonts"
            zip_path = cache_dir / "fonts.zip"
            if not font_dir.exists() or not list(font_dir.glob("*.ttf")):
                try:
                    import zipfile
                    r = requests.get(FONT_URL, timeout=30)
                    r.raise_for_status()
                    zip_path.write_bytes(r.content)
                    font_dir.mkdir(exist_ok=True)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(font_dir)
                except Exception as exc:
                    console.print(
                        f"[bold yellow]\u26a0 Could not download fonts: {exc}[/]"
                    )
            font_paths = [str(p) for p in font_dir.glob("*.ttf")] if font_dir.exists() else []
            self._font_cache[key] = font_paths
            return font_paths


class PlaylistManager:
    def __init__(self, downloader: VideoDownloader, eta_tracker: ETATracker):
        self.downloader = downloader
        self.eta_tracker = eta_tracker

    def download_playlist(
        self,
        url: str,
        quality: str,
        sub_langs: List[str],
        output_dir: str,
        workers: int,
    ) -> List[DownloadResult]:
        console.print()
        with console.status("[bold cyan]Fetching playlist info\u2026", spinner="dots"):
            entries, playlist_title = self._fetch_entries(url)
        if not entries:
            console.print(
                "[bold red]\u2717 Could not fetch playlist info or playlist is empty.[/]"
            )
            return []
        console.print(f"[bold green]\u2713 Found {len(entries)} videos in playlist[/]")
        safe_title = re.sub(r'[<>:"/\\|?*]', "_", playlist_title)
        playlist_dir = Path(output_dir) / safe_title
        playlist_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[dim]Saving to folder: {safe_title}[/]")
        self.eta_tracker.total_items = len(entries)
        workers = min(workers, MAX_WORKERS, len(entries))
        console.print(f"[dim]Downloading with {workers} parallel worker(s)\u2026[/]\n")
        jobs: List[Tuple[int, str, DownloadJob]] = []
        for i, entry in enumerate(entries, 1):
            vid_url = entry.get("url") or entry.get("webpage_url", "")
            if not vid_url:
                vid_id = entry.get("id", "")
                vid_url = f"https://www.youtube.com/watch?v={vid_id}"
            jobs.append((
                i,
                entry.get("title", f"Video {i}"),
                DownloadJob(
                    url=vid_url,
                    quality=quality,
                    sub_langs=sub_langs,
                    output_dir=str(playlist_dir),
                    workers=workers,
                    playlist_index=i,
                ),
            ))
        results: List[DownloadResult] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.fields[vtitle]}", justify="left"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.description}"),
            console=console,
            expand=False,
        ) as prog:
            overall = prog.add_task(
                "[cyan]Overall", total=len(jobs), vtitle="\U0001f4e6 Queue"
            )
            with ThreadPoolExecutor(max_workers=workers) as pool:
                future_map: Dict = {}
                for idx, title, job in jobs:
                    short = title[:35] + ("\u2026" if len(title) > 35 else "")
                    tid = prog.add_task(
                        "[dim]Queued\u2026", total=100,
                        vtitle=f"#{idx} {short}",
                    )
                    fut = pool.submit(self.downloader.download, job, prog, tid)
                    future_map[fut] = (idx, title, tid)
                for fut in as_completed(future_map):
                    idx, title, tid = future_map[fut]
                    try:
                        res = fut.result()
                        results.append(res)
                        if res.success:
                            self.eta_tracker.item_completed(res.duration)
                            prog.update(
                                tid, completed=100,
                                description="[bold green]\u2713 Done",
                            )
                        else:
                            self.eta_tracker.item_failed()
                            short_err = (res.error or "Unknown")[:30]
                            prog.update(
                                tid, completed=100,
                                description=f"[bold red]\u2717 {short_err}",
                            )
                    except Exception as exc:
                        self.eta_tracker.item_failed()
                        results.append(DownloadResult(url=jobs[idx - 1][2].url, error=str(exc)))
                        prog.update(
                            tid, completed=100,
                            description="[bold red]\u2717 Error",
                        )
                    prog.update(
                        overall, advance=1,
                        description=f"[cyan]ETA: {self.eta_tracker.queue_eta}",
                    )
        return results


    @staticmethod
    def _fetch_entries(url: str) -> Tuple[List[Dict], str]:
        try:
            result = subprocess.run(
                ["yt-dlp", "--flat-playlist", "-J", "--no-warnings", url],
                capture_output=True, text=True, timeout=120,
                creationflags=_CREATION_FLAGS,
            )
            if result.returncode != 0:
                return [], ""
            data = json.loads(result.stdout)
            return data.get("entries", []), data.get("title", "Playlist")
        except Exception:
            return [], ""


class DownloadQueue:
    def __init__(self, dep_checker: DependencyChecker):
        self.dep_checker = dep_checker
        self.jobs: List[DownloadJob] = []
        self.results: List[DownloadResult] = []

    def add_job(self, job: DownloadJob):
        self.jobs.append(job)

    def add_from_file(
        self,
        file_path: str,
        quality: str,
        sub_langs: List[str],
        output_dir: str,
        workers: int,
    ) -> int:
        path = Path(file_path)
        if not path.exists():
            console.print(f"[bold red]\u2717 File not found: {file_path}[/]")
            return 0
        count = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                self.add_job(
                    DownloadJob(
                        url=line,
                        quality=quality,
                        sub_langs=sub_langs,
                        output_dir=output_dir,
                        workers=workers,
                    )
                )
                count += 1
        return count

    def process(self):
        if not self.jobs:
            console.print("[bold yellow]\u26a0 No jobs in queue.[/]")
            return
        total_start = time.time()
        console.print(f"\n[bold cyan]Processing {len(self.jobs)} job(s)\u2026[/]\n")
        console.print(Rule(style="dim"))
        for i, job in enumerate(self.jobs, 1):
            console.print(
                f"\n[bold]\U0001f4e5 Job {i}/{len(self.jobs)}:[/]  "
                f"[link={job.url}]{job.url}[/link]"
            )
            console.print(
                f"   [dim]Quality: {job.quality}  |  "
                f"Subs: {','.join(job.sub_langs)}  |  "
                f"Output: {job.output_dir}[/]"
            )
            console.print()
            is_playlist = job.is_playlist if job.is_playlist is not None else ("list=" in job.url.lower())
            if is_playlist:
                tracker = ETATracker()
                dl = VideoDownloader(self.dep_checker, tracker)
                mgr = PlaylistManager(dl, tracker)
                self.results.extend(
                    mgr.download_playlist(
                        job.url, job.quality, job.sub_langs,
                        job.output_dir, job.workers,
                    )
                )
            else:
                tracker = ETATracker(total_items=1)
                dl = VideoDownloader(self.dep_checker, tracker)
                with Progress(
                    SpinnerColumn(),
                    TextColumn(
                        "[bold blue]{task.fields[vtitle]}", justify="left"
                    ),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("{task.description}"),
                    console=console,
                    expand=False,
                ) as prog:
                    tid = prog.add_task(
                        "[cyan]Starting\u2026", total=100,
                        vtitle="\U0001f4f9 Video",
                    )
                    res = dl.download(job, prog, tid)
                    self.results.append(res)
            console.print(Rule(style="dim"))
        self._print_summary(time.time() - total_start)
        for job in self.jobs:
            temp = Path(job.output_dir).resolve() / ".ytdl_temp"
            if temp.exists():
                shutil.rmtree(str(temp), ignore_errors=True)

    def _print_summary(self, total_time: float):
        console.print()
        succeeded = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        table = Table(
            title="Download Summary",
            box=box.ROUNDED,
            title_style="bold cyan",
            border_style="dim",
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="bold", max_width=50)
        table.add_column("Status", justify="center")
        table.add_column("Time", justify="right", style="dim")
        table.add_column("Details", style="dim", max_width=35)
        for i, r in enumerate(self.results, 1):
            if r.success:
                table.add_row(
                    str(i),
                    r.title or "Unknown",
                    "[bold green]\u2713 Success[/]",
                    ETATracker.format_seconds(r.duration),
                    Path(r.output_file).name if r.output_file else "",
                )
            else:
                table.add_row(
                    str(i),
                    r.title or "Unknown",
                    "[bold red]\u2717 Failed[/]",
                    "-",
                    (r.error or "Unknown error")[:35],
                )
        console.print(table)
        console.print()
        time_str = ETATracker.format_seconds(total_time)
        summary = Text()
        summary.append(f"  \u2713 {len(succeeded)} succeeded", style="bold green")
        summary.append("  |  ")
        summary.append(
            f"\u2717 {len(failed)} failed",
            style="bold red" if failed else "dim",
        )
        summary.append("  |  ")
        summary.append(f"\u23f1 {time_str} total", style="bold cyan")
        console.print(Panel(summary, border_style="cyan", box=box.ROUNDED))
        if failed:
            console.print()
            console.print("[bold red]Failed downloads:[/]")
            for r in failed:
                console.print(f"  [red]\u2717[/] {r.url}")
                if r.error:
                    console.print(f"    [dim]{r.error}[/]")
        console.print()

def show_banner():
    console.print(
        Panel(
            BANNER,
            border_style="bright_green",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
            expand=False,
        )
    )

def show_menu() -> str:
    items = [
        ("1", "Download Single Video / Playlist", "\U0001f4f9"),
        ("2", "Queue Multiple Downloads",         "\U0001f4cb"),
        ("3", "Batch Download from File",          "\U0001f4c1"),
        ("4", "Update yt-dlp",                     "\U0001f504"),
        ("5", "Check Dependencies",                "\U0001f50d"),
        ("6", "Settings",                          "\U0001f527"),
        ("0", "Exit",                              "\U0001f6aa"),
    ]
    tbl = Table(box=box.SIMPLE, show_header=False, border_style="dim", padding=(0, 2))
    tbl.add_column("", style="bold cyan", width=4)
    tbl.add_column("", style="bold")
    tbl.add_column("", width=3)
    for key, label, icon in items:
        tbl.add_row(f"[{key}]", label, icon)
    console.print(
        Panel(tbl, title="[bold cyan]Menu[/]", border_style="cyan", box=box.ROUNDED, expand=False)
    )
    return Prompt.ask(
        "[bold cyan]Select an option[/]",
        choices=["1", "2", "3", "4", "5", "6", "0"],
        default="1",
    )

def prompt_settings() -> Tuple[str, str, int]:
    quality = Prompt.ask(
        "[bold magenta]Video Quality[/]",
        choices=list(VALID_QUALITIES),
        default="best",
    )
    conf = Config.load()
    out_path = Path(conf.output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)
    console.print()
    return quality, str(out_path), DEFAULT_WORKERS

def validate_url(url: str) -> Tuple[bool, bool]:
    try:
        cmd = [
            "yt-dlp", "-J", "--no-download",
            "--playlist-items", "1",
            "--no-warnings",
            url,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
            creationflags=_CREATION_FLAGS,
        )
        if result.returncode != 0:
            return False, False
        data = json.loads(result.stdout)
        is_playlist = data.get("_type") == "playlist"
        return True, is_playlist
    except Exception:
        return False, False

def fetch_available_subs(url: str) -> Tuple[str, List[Tuple[str, str, str]], bool]:
    try:
        cmd = [
            "yt-dlp", "-J", "--no-download",
            "--playlist-items", "1",
            "--no-warnings",
            url,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=45,
            creationflags=_CREATION_FLAGS,
        )
        if result.returncode != 0:
            return "", [], False

        data = json.loads(result.stdout)
        is_playlist = data.get("_type") == "playlist"
        if is_playlist and "entries" in data and data["entries"]:
            video_data = data["entries"][0]
            title = data.get("title", "Playlist")
        else:
            video_data = data
            title = data.get("title", "Video")
        entries: List[Tuple[str, str, str]] = []
        seen: set = set()
        def sort_key(item):
            lang_code = item[0]
            return (not lang_code.startswith("en"), lang_code)
        for lang, formats in sorted(video_data.get("subtitles", {}).items(), key=sort_key):
            name = lang
            if formats and isinstance(formats, list):
                name = formats[0].get("name", lang)
            entries.append((lang, name, "Manual"))
            seen.add(lang)
        auto_caps = video_data.get("automatic_captions", {})
        filter_translations = len(auto_caps) > 10
        for lang, formats in sorted(auto_caps.items(), key=sort_key):
            if lang not in seen:
                if filter_translations and not (lang.endswith("-orig") or lang == "en"):
                    continue
                name = lang
                if formats and isinstance(formats, list):
                    name = formats[0].get("name", lang)
                entries.append((lang, name, "Auto"))
        return title, entries, is_playlist
    except Exception:
        return "", [], False

def prompt_subtitle_selection(url: str) -> Tuple[List[str], bool, bool]:
    console.print()
    with console.status(
        "[bold cyan]Fetching available subtitles\u2026", spinner="dots"
    ):
        title, entries, is_playlist = fetch_available_subs(url)
    if not title:
        console.print("[bold red]\u2717 Invalid URL or video unavailable.[/]")
        return [], False, False
    if not entries:
        console.print("[bold yellow]\u26a0 No subtitles found for this video.[/]")
        return [], is_playlist, True
    console.print(
        f"\n[bold]Available subtitles for:[/] [italic cyan]{title}[/]\n"
    )
    tbl = Table(
        box=box.ROUNDED,
        border_style="dim",
        header_style="bold cyan",
    )
    tbl.add_column("#", style="bold cyan", justify="right", width=4)
    tbl.add_column("Code", style="bold", width=8)
    tbl.add_column("Language", min_width=16)
    tbl.add_column("Type", justify="center")
    for idx, (code, name, stype) in enumerate(entries, 1):
        type_style = (
            "[bold green]Manual[/]" if stype == "Manual"
            else "[dim]Auto[/]"
        )
        tbl.add_row(str(idx), code, name, type_style)
    console.print(tbl)
    console.print(
        "[dim]Enter numbers separated by commas (e.g. 1,3,5), "
        "'all' for everything, or 'none' to skip subtitles.[/]"
    )
    raw = Prompt.ask("[bold magenta]Select subtitles[/]", default="1").strip()
    if raw.lower() == "all":
        selected = [e[0] for e in entries]
        console.print(
            f"[bold green]\u2713 Selected all {len(selected)} subtitle track(s).[/]"
        )
        return selected, is_playlist, True
    if raw.lower() == "none":
        console.print("[dim]Subtitles skipped.[/]")
        return [], is_playlist, True
    selected: List[str] = []
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            idx = int(tok)
            if 1 <= idx <= len(entries):
                code = entries[idx - 1][0]
                if code not in selected:
                    selected.append(code)
            else:
                console.print(f"[yellow]Ignoring invalid number: {tok}[/]")
        except ValueError:
            if any(e[0] == tok.lower() for e in entries):
                if tok.lower() not in selected:
                    selected.append(tok.lower())
            else:
                console.print(f"[yellow]Ignoring unknown input: {tok}[/]")
    if selected:
        names_dict = {e[0]: e[1] for e in entries}
        names = ", ".join(names_dict.get(c, c) for c in selected)
        console.print(
            f"[bold green]\u2713 Selected {len(selected)} track(s): {names}[/]"
        )
        console.print(
            f"[dim]Default track: {names_dict.get(selected[0], selected[0])}[/]"
        )
    else:
        console.print("[dim]No valid selection — subtitles skipped.[/]")
    return selected, is_playlist, True

def _read_first_url_from_file(file_path: str) -> Optional[str]:
    path = Path(file_path)
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return None

def interactive_mode(dep_checker: DependencyChecker):
    while True:
        show_banner()
        choice = show_menu()
        if choice == "1":
            url = Prompt.ask("[bold green]Paste YouTube URL[/]").strip()
            if not url:
                console.print("[bold red]\u2717 No URL provided.[/]")
                continue
            sub_langs, is_playlist, is_valid = prompt_subtitle_selection(url)
            if not is_valid:
                continue
            quality, output_dir, workers = prompt_settings()
            if is_playlist:
                w = Prompt.ask(
                    f"[bold magenta]Parallel Workers[/] [dim](1\u2013{MAX_WORKERS})[/]",
                    default=str(DEFAULT_WORKERS),
                )
                try:
                    workers = max(1, min(int(w), MAX_WORKERS))
                except ValueError:
                    workers = DEFAULT_WORKERS
            queue = DownloadQueue(dep_checker)
            queue.add_job(
                DownloadJob(
                    url=url, quality=quality, sub_langs=sub_langs,
                    output_dir=output_dir, workers=workers,
                    is_playlist=is_playlist,
                )
            )
            queue.process()
            break
        
        elif choice == "2":
            console.print(
                "[bold green]Enter URLs one per line. "
                "Type [underline]done[/underline] to start downloading.[/]"
            )
            urls: List[str] = []
            while True:
                url = Prompt.ask("[bold cyan]URL[/] [dim](or 'done')[/]").strip()
                if url.lower() == "done":
                    break
                if url:
                    urls.append(url)
                    console.print(f"  [dim]Added ({len(urls)} in queue)[/]")
            if not urls:
                console.print("[bold yellow]\u26a0 No URLs added.[/]")
                continue
            console.print(
                "\n[dim]Probing first URL for available subtitles\u2026[/]"
            )
            sub_langs, is_playlist, is_valid = prompt_subtitle_selection(urls[0])
            if not is_valid:
                continue
            quality, output_dir, workers = prompt_settings()
            queue = DownloadQueue(dep_checker)
            for u in urls:
                queue.add_job(
                    DownloadJob(
                        url=u, quality=quality, sub_langs=sub_langs,
                        output_dir=output_dir, workers=workers,
                        is_playlist=is_playlist if u == urls[0] else None,
                    )
                )
            queue.process()
            break

        elif choice == "3":
            fpath = Prompt.ask("[bold green]Path to URL file[/]").strip()
            first_url = _read_first_url_from_file(fpath)
            if first_url:
                console.print(
                    "\n[dim]Probing first URL for available subtitles\u2026[/]"
                )
                sub_langs, is_playlist, is_valid = prompt_subtitle_selection(first_url)
                if not is_valid:
                    continue
            else:
                console.print("[bold red]\u2717 File is empty or not found.[/]")
                continue
            quality, output_dir, workers = prompt_settings()
            queue = DownloadQueue(dep_checker)
            count = queue.add_from_file(
                fpath, quality, sub_langs, output_dir, workers,
            )
            if count > 0:
                console.print(f"[bold green]\u2713 Loaded {count} URL(s) from file.[/]")
                queue.process()
                break

        elif choice == "4":
            Updater.update_ytdlp()

        elif choice == "5":
            dep_checker.check_all()

        elif choice == "6":
            conf = Config.load()
            console.print(f"\n[bold cyan]Current Output Directory:[/] {conf.output_dir}")
            new_dir = Prompt.ask(
                "[bold magenta]Enter new Output Directory[/] [dim](leave empty to keep current)[/]", 
                default=""
            ).strip()
            if new_dir:
                conf.output_dir = new_dir
            console.print(f"\n[bold cyan]Current Subtitle Font Path:[/] {conf.font_path or 'Default (Montara Gothic)'}")
            new_font = Prompt.ask(
                "[bold magenta]Enter path to custom .ttf font[/] [dim](leave empty to keep current, or 'default' to reset)[/]",
                default=""
            ).strip()
            if new_font.lower() == "default":
                conf.font_path = ""
            elif new_font:
                if Path(new_font).exists() and new_font.lower().endswith(".ttf"):
                    conf.font_path = new_font
                else:
                    console.print("[bold red]Invalid font path or not a .ttf file. Keeping current.[/]")
            console.print(f"\n[bold cyan]Current Subtitle Font Size:[/] {conf.font_size}")
            new_size_str = Prompt.ask(
                "[bold magenta]Enter new Font Size[/] [dim](leave empty to keep current)[/]",
                default=""
            ).strip()
            if new_size_str:
                try:
                    conf.font_size = int(new_size_str)
                except ValueError:
                    console.print("[bold red]Invalid size. Keeping current.[/]")

            console.print(f"\n[bold cyan]Enable Playlist Numbering (e.g. 001 - Title):[/] {'Yes' if conf.playlist_numbering else 'No'}")
            new_num = Prompt.ask(
                "[bold magenta]Enable numbering?[/] [dim](y/n, leave empty to keep current)[/]",
                default=""
            ).strip().lower()
            if new_num in ("y", "yes"):
                conf.playlist_numbering = True
            elif new_num in ("n", "no"):
                conf.playlist_numbering = False
            conf.save()
            console.print(f"\n[bold green]\u2713 Settings saved![/]\n")

        elif choice == "0":
            console.print("[bold cyan]Goodbye! \U0001f44b[/]")
            break

        if choice != "0":
            console.print()
            Prompt.ask("[dim]Press Enter to continue\u2026[/]", default="")
            console.clear()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=f"YTDL v{VERSION} \u2014 YouTube Downloader by {AUTHOR}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python YTDL.py                                            Interactive mode
  python YTDL.py "https://youtube.com/watch?v=..." -q 1080
  python YTDL.py "https://youtube.com/playlist?..." -q 1080 -w 4
  python YTDL.py --batch urls.txt -q best -s en,es
  python YTDL.py --update
  python YTDL.py --check-deps
        """,
    )
    p.add_argument("url", nargs="?", help="YouTube URL to download")
    p.add_argument(
        "-q", "--quality",
        choices=list(VALID_QUALITIES), default="best",
        help="Video quality (default: best)",
    )
    p.add_argument(
        "-s", "--subs", default="en",
        help="Subtitle languages, comma-separated (default: en)",
    )
    p.add_argument(
        "-o", "--output", default=".",
        help="Output directory (default: current directory)",
    )
    p.add_argument(
        "-w", "--workers",
        type=int, default=DEFAULT_WORKERS,
        help=f"Parallel workers for playlists (default: {DEFAULT_WORKERS}, max: {MAX_WORKERS})",
    )
    p.add_argument(
        "--batch", metavar="FILE",
        help="Path to text file with URLs (one per line)",
    )
    p.add_argument(
        "--update", action="store_true",
        help="Update yt-dlp to latest version",
    )
    p.add_argument(
        "--check-deps", action="store_true",
        help="Check all dependencies",
    )
    return p.parse_args()


def main():
    args = parse_args()
    dep_checker = DependencyChecker()
    if args.update:
        show_banner()
        Updater.update_ytdlp()
        return
    if args.check_deps:
        show_banner()
        dep_checker.check_all()
        return
    if args.url or args.batch:
        if not dep_checker.check_all(quiet_if_ok=True):
            sys.exit(1)
        show_banner()
        sub_langs = [s.strip().lower() for s in args.subs.split(",") if s.strip()] or ["en"]
        workers = max(1, min(args.workers, MAX_WORKERS))
        output_dir = str(Path(args.output).resolve())
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        queue = DownloadQueue(dep_checker)
        if args.batch:
            count = queue.add_from_file(
                args.batch, args.quality, sub_langs, output_dir, workers,
            )
            if count == 0:
                console.print("[bold red]\u2717 No URLs loaded from file.[/]")
                sys.exit(1)
            console.print(f"[bold green]\u2713 Loaded {count} URL(s) from file.[/]")
        else:
            queue.add_job(
                DownloadJob(
                    url=args.url, quality=args.quality, sub_langs=sub_langs,
                    output_dir=output_dir, workers=workers,
                )
            )
        queue.process()
        return
    if not dep_checker.check_all(quiet_if_ok=True):
        if not Confirm.ask("[bold yellow]Continue anyway?[/]", default=False):
            sys.exit(1)
    interactive_mode(dep_checker)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted by user. Goodbye! \U0001f44b[/]")
        sys.exit(130)

