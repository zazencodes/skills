#!/usr/bin/env python3
"""Generate or edit images with the codex CLI's built-in image tool.

`codex exec` has no "write the image to this path" flag. It drops what it
generates in `$CODEX_HOME/generated_images/<session id>/`. This script runs
one non-interactive turn, collects only that session's saved images, and writes
them where you asked with extensions matching their actual format.

Usage:
    codex_image.py --prompt "a red bicycle in the rain" --output bike.png
    codex_image.py -p "..." -o out.png --reference sketch.png
    codex_image.py --edit v1.png -p "make the sky purple" -o v2.png
    codex_image.py -p "..." -o cover.png --aspect 9:16 --fit 1080x1920

Only the standard library is required; --fit additionally needs Pillow.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# The model has to be told, forcefully, to actually call its image tool. Without
# this it will happily "describe" the image, draw one with ImageMagick, or claim
# success without emitting anything -- and the run then yields no image at all.
PREAMBLE = """You MUST actually generate a real image this turn with your built-in image generation tool (the `imagegen` skill / `image_gen` tool). Do not merely describe it or claim it is done - the run fails unless the tool genuinely runs and emits an image.

Do NOT draw, composite, or edit the picture yourself with ImageMagick, Python, PIL, canvas, or SVG, and do NOT use the API-key CLI fallback. Do NOT save, copy, move, or rename the result yourself: it is collected automatically from where the tool puts it. Reply with one short line of confirmation and nothing else.

If the built-in image generation tool is unavailable, say so explicitly and do nothing else."""

EDIT_PREAMBLE = """The attached image is the edit target. Produce an UPDATED VERSION of it that applies the requested change while keeping everything else looking identical. This is an edit of the attached image, NOT a new image from scratch. Apply only the change described below."""

REFERENCE_NOTE = """Use the attached image(s) as visual reference for the request below."""

ASPECT_NOTE = """Generate the image at a {aspect} aspect ratio, at the largest size available for that shape."""

VARIANTS_NOTE = """Produce {count} distinct variants of this image in this same turn, each from its own image-tool call. Vary the interpretation between them; do not return near-duplicates."""

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")

MAGIC = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
}


def codex_bin() -> str:
    return os.environ.get("CODEX_BIN", "codex")


def codex_home() -> Path:
    home = os.environ.get("CODEX_HOME")
    return Path(home) if home else Path.home() / ".codex"


def generated_images_dir() -> Path:
    return codex_home() / "generated_images"


def sniff(raw: bytes) -> str | None:
    for magic, ext in MAGIC.items():
        if raw.startswith(magic):
            return ext
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    return None


# --------------------------------------------------------------------------- #
# Prompt assembly
# --------------------------------------------------------------------------- #
def build_prompt(request: str, *, edit: bool, has_refs: bool,
                 aspect: str | None, variants: int = 1) -> str:
    parts = [PREAMBLE, ""]
    if edit:
        parts += [EDIT_PREAMBLE, ""]
    elif has_refs:
        parts += [REFERENCE_NOTE, ""]
    if aspect:
        parts += [ASPECT_NOTE.format(aspect=aspect), ""]
    if variants > 1:
        parts += [VARIANTS_NOTE.format(count=variants), ""]
    parts += ["## Image to generate" if not edit else "## Change to make", request.strip()]
    return "\n".join(parts).strip() + "\n"


# --------------------------------------------------------------------------- #
# Running codex
# --------------------------------------------------------------------------- #
SESSION_ID_RE = re.compile(r"session id:\s*([0-9a-fA-F-]{36})")


def run_codex(prompt: str, images: list[Path], sandbox: str, reasoning: str,
              model: str | None, timeout: int, quiet: bool) -> tuple[float, str | None]:
    """Run one `codex exec` turn. Returns (start timestamp, session id if seen)."""
    binary = codex_bin()
    if shutil.which(binary) is None:
        sys.exit(f"ERROR: codex CLI not found on PATH as '{binary}'. "
                 "Install it and run `codex login`, or set CODEX_BIN.")

    cmd = [binary, "exec", "--skip-git-repo-check"]
    if sandbox == "bypass":
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        cmd += ["-s", sandbox]
    # High reasoning matters: at lower effort the model often skips the tool call.
    cmd += ["-c", f"model_reasoning_effort={reasoning}"]
    if model:
        cmd += ["-m", model]
    # The prompt is positional and must come BEFORE -i, which is variadic.
    cmd.append(prompt)
    for img in images:
        cmd += ["-i", str(img)]

    start = time.time()
    # codex prints its banner -- session id included -- to stderr, so merge the
    # streams rather than reading stdout alone.
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    timed_out = threading.Event()

    def _kill() -> None:
        timed_out.set()
        proc.kill()

    watchdog = threading.Timer(timeout, _kill)
    watchdog.start()
    session_id: str | None = None
    tail: list[str] = []
    try:
        for line in proc.stdout:               # stream so long runs still show progress
            if session_id is None:
                match = SESSION_ID_RE.search(line)
                if match:
                    session_id = match.group(1)
            tail.append(line)
            del tail[:-40]
            if not quiet:
                sys.stderr.write(line)
        proc.wait()
    finally:
        watchdog.cancel()
        if proc.stdout:
            proc.stdout.close()
    if timed_out.is_set():
        sys.exit(f"ERROR: codex exec timed out after {timeout}s.")
    if proc.returncode != 0:
        transcript = "".join(tail)
        if "usage limit" in transcript:
            sys.exit("ERROR: the codex account is out of quota - no image was generated. "
                     "Wait for the reset shown above, or use a different account.")
        detail = "" if not quiet else f"\n{transcript.strip()}"
        sys.exit(f"ERROR: codex exec failed with exit code {proc.returncode}.{detail}")
    return start, session_id


def collect_from_session_dir(session_id: str | None, start: float) -> list[bytes]:
    """Images codex saved under `$CODEX_HOME/generated_images/<session id>/`.

    Recovery is scoped to the exact session ID returned by this run.
    """
    if not session_id:
        return []
    folder = generated_images_dir() / session_id
    if not folder.is_dir():
        return []
    files = [p for p in sorted(folder.iterdir())
             if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
             and p.stat().st_mtime >= start - 1]
    files.sort(key=lambda p: p.stat().st_mtime)
    return [p.read_bytes() for p in files]


# --------------------------------------------------------------------------- #
# Optional exact-size fitting
# --------------------------------------------------------------------------- #
def fit_to_size(raw: bytes, spec: str, mode: str, background: str) -> bytes:
    """Letterbox-pad (default) or center-crop to exactly WxH, then resize."""
    try:
        from io import BytesIO

        from PIL import Image, ImageColor
    except ImportError:
        sys.exit("ERROR: --fit requires Pillow (`pip install Pillow`).")
    try:
        want_w, want_h = (int(v) for v in spec.lower().split("x", 1))
    except ValueError:
        sys.exit(f"ERROR: --fit expects WxH (e.g. 1080x1920), got {spec!r}.")
    if want_w <= 0 or want_h <= 0:
        sys.exit("ERROR: --fit dimensions must be positive.")

    fill = ImageColor.getrgb(background)
    with Image.open(BytesIO(raw)) as img:
        img = img.convert("RGB")
        w, h = img.size
        target, current = want_w / want_h, w / h
        if abs(current - target) < 1e-3:
            staged = img
        elif mode == "crop":
            if current > target:          # too wide -> trim the sides
                new_w = round(h * target)
                left = (w - new_w) // 2
                staged = img.crop((left, 0, left + new_w, h))
            else:                          # too tall -> trim top and bottom
                new_h = round(w / target)
                top = (h - new_h) // 2
                staged = img.crop((0, top, w, top + new_h))
        else:                              # pad
            if current > target:          # too wide -> bars above and below
                new_h = round(w / target)
                staged = Image.new("RGB", (w, new_h), fill)
                staged.paste(img, (0, (new_h - h) // 2))
            else:                          # too tall -> bars left and right
                new_w = round(h * target)
                staged = Image.new("RGB", (new_w, h), fill)
                staged.paste(img, ((new_w - w) // 2, 0))
        final = staged.resize((want_w, want_h), Image.LANCZOS)
        out = BytesIO()
        final.save(out, format="PNG")
        return out.getvalue()


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate or edit an image with the codex CLI's built-in image tool.")
    ap.add_argument("-p", "--prompt", help="What to generate, or the change to make with --edit.")
    ap.add_argument("--prompt-file", type=Path, help="Read the prompt from a file instead.")
    ap.add_argument("-o", "--output", type=Path, required=True, help="Where to write the image.")
    ap.add_argument("--edit", type=Path,
                    help="Image to iterate on. Its content is preserved except for --prompt.")
    ap.add_argument("-r", "--reference", type=Path, action="append", default=[],
                    help="Reference image to attach (repeatable).")
    ap.add_argument("--aspect", help="Aspect-ratio hint for the model, e.g. 16:9, 9:16, 1:1.")
    ap.add_argument("-n", "--variants", type=int, default=1,
                    help="Ask for N variants in one run; extras are saved as <name>-2.png etc.")
    ap.add_argument("--fit", help="Force the saved file to exactly WxH (needs Pillow).")
    ap.add_argument("--fit-mode", choices=("pad", "crop"), default="pad",
                    help="How --fit reconciles aspect: letterbox (default) or center-crop.")
    ap.add_argument("--fit-background", default="black", help="Letterbox colour for --fit pad.")
    ap.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access", "bypass"),
                    default="read-only",
                    help="codex sandbox. read-only is enough; use bypass only where the "
                         "nested sandbox cannot start (e.g. containers without user namespaces).")
    ap.add_argument("--reasoning", default="high", help="model_reasoning_effort (default: high).")
    ap.add_argument("-m", "--model", help="Override the codex model.")
    ap.add_argument("--timeout", type=int, default=900, help="Seconds to wait (default: 900).")
    ap.add_argument("--quiet", action="store_true", help="Suppress codex's own stdout.")
    ap.add_argument("--print-prompt", action="store_true", help="Print the assembled prompt and exit.")
    ap.add_argument("--verbatim", action="store_true",
                    help="Send only the $imagegen trigger and the prompt, with no wrapper text.")
    ap.add_argument("--json", action="store_true", help="Print a JSON result summary.")
    args = ap.parse_args()

    if args.prompt and args.prompt_file:
        sys.exit("ERROR: pass --prompt or --prompt-file, not both.")
    if args.prompt_file:
        if not args.prompt_file.is_file():
            sys.exit(f"ERROR: prompt file not found: {args.prompt_file}")
        request = args.prompt_file.read_text(encoding="utf-8")
    elif args.prompt:
        request = args.prompt
    else:
        sys.exit("ERROR: one of --prompt or --prompt-file is required.")
    if not request.strip():
        sys.exit("ERROR: the prompt is empty.")

    images: list[Path] = []
    if args.edit:
        if not args.edit.is_file():
            sys.exit(f"ERROR: --edit image not found: {args.edit}")
        images.append(args.edit)
    for ref in args.reference:
        if not ref.is_file():
            sys.exit(f"ERROR: reference image not found: {ref}")
        images.append(ref)

    if args.variants < 1:
        sys.exit("ERROR: --variants must be at least 1.")
    if args.verbatim and (args.edit or args.aspect or args.variants > 1):
        sys.exit("ERROR: --verbatim sends the prompt alone; it cannot be combined "
                 "with --edit, --aspect or --variants.")

    if args.verbatim:
        prompt = f"$imagegen\n\n{request.strip()}\n"
    else:
        prompt = build_prompt(request, edit=bool(args.edit), has_refs=bool(args.reference),
                              aspect=args.aspect, variants=args.variants)
    if args.print_prompt:
        print(prompt)
        return

    start, session_id = run_codex(prompt, images, args.sandbox, args.reasoning,
                                  args.model, args.timeout, args.quiet)

    if session_id is None:
        sys.exit("ERROR: codex exec did not report a session ID. "
                 "Cannot identify this run's generated images. No file was written.")
    payloads = collect_from_session_dir(session_id, start)
    if not payloads:
        sys.exit(f"ERROR: the codex run produced no image in "
                 f"{generated_images_dir() / session_id}.\n"
                 "No file was written. Check that the image tool ran and saved "
                 "its output in this session's generated_images directory.")

    pending: list[tuple[Path, bytes, str]] = []
    for index, raw in enumerate(payloads, start=1):
        kind = sniff(raw)
        if kind is None:
            sys.exit(f"ERROR: recovered {len(raw)} bytes that are not a PNG/JPEG/WebP.")
        if args.fit:
            raw = fit_to_size(raw, args.fit, args.fit_mode, args.fit_background)
            kind = "png"
        out = args.output
        extension = out.suffix.lower()
        if extension != f".{kind}" and not (kind == "jpg" and extension == ".jpeg"):
            out = out.with_suffix(f".{kind}")
        if index > 1:                          # extra variants sit beside the first
            out = out.with_name(f"{out.stem}-{index}{out.suffix}")
        pending.append((out, raw, kind))

    written: list[dict] = []
    for out, raw, kind in pending:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        written.append({"path": str(out), "bytes": len(raw), "format": kind})

    if args.json:
        print(json.dumps({"images": written, "source": "generated_images",
                          "session_id": session_id}, indent=2))
    else:
        for item in written:
            print(f"Wrote {item['path']} ({item['bytes']:,} bytes, {item['format']})")


if __name__ == "__main__":
    main()
