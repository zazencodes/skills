# /// script
# requires-python = ">=3.11"
# dependencies = ["textual==8.2.8", "textual-image==0.14.4", "pydantic>=2.10,<3", "pillow>=11,<14"]
# ///
"""Create a local illustrated walkthrough and collect the reader's response."""
import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Annotated, Literal

from PIL import Image, ImageOps
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

SCRIPT = Path(__file__).resolve()
DEMO = SCRIPT.parents[1] / "examples" / "walkthrough.json"
Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Settings(Model):
    presentation: Literal["terminal", "plane"] = "terminal"
    renderer: Literal["auto", "cells"] = "auto"
    image_height: int = Field(default=15, ge=6, le=40)
    illustration_style: str = "Wide composition, bold silhouettes, few colors. Put labels in the caption."
    image_command: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def placeholders(self):
        if self.image_command and any(k not in self.image_command[1:] for k in ("{prompt}", "{output}")):
            raise ValueError("image_command needs separate {prompt} and {output} arguments")
        return self


class Picture(Model):
    file: Text
    caption: Text


class Lines(Model):
    file: Text
    start: int = Field(ge=1)
    end: int = Field(ge=1)


class Diff(Model):
    file: Text
    base: Text
    head: Text | None = None
    start: int | None = Field(default=None, ge=1)
    end: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def bounds(self):
        if (self.start is None) != (self.end is None) or (self.start and self.start > self.end):
            raise ValueError("diff line range needs start <= end")
        return self


EvidenceRef = Lines | Diff


class Question(Model):
    id: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_-]*$")]
    prompt: Text
    choices: list[Text] | None = Field(default=None, min_length=2)

    @model_validator(mode="after")
    def distinct(self):
        if self.choices and len(set(self.choices)) != len(self.choices):
            raise ValueError("choices must be distinct")
        return self


class Page(Model):
    heading: Text
    body: Text
    image: Picture | None = None
    evidence: EvidenceRef | Annotated[list[EvidenceRef], Field(min_length=1)] | None = None
    question: Question | None = None


class Tour(Model):
    title: Text
    pages: list[Page] = Field(min_length=1)

    @model_validator(mode="after")
    def question_ids(self):
        ids = [p.question.id for p in self.pages if p.question]
        if len(ids) != len(set(ids)):
            raise ValueError("each question needs its own id")
        return self


def config_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "terminal-explainer/config.json"


def settings():
    path = config_path()
    return Settings.model_validate_json(path.read_bytes()) if path.exists() else Settings()


def local_file(root, name):
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"expected a relative file inside {root}: {name}")
    return path


def evidence(ref, root):
    path = local_file(root, ref.file)
    if isinstance(ref, Lines):
        lines = path.read_text(encoding="utf-8").splitlines()
        if not 1 <= ref.start <= ref.end <= len(lines):
            raise ValueError(f"line range outside {ref.file}: {ref.start}–{ref.end}")
        return {"label": f"{ref.file} · lines {ref.start}–{ref.end}", "start": ref.start,
                "code": "\n".join(lines[ref.start-1:ref.end]), "file": ref.file}
    def git(*args):
        return subprocess.check_output(["git", "--literal-pathspecs", "-C", root, *args], text=True)
    base = git("rev-parse", "--verify", "--end-of-options", ref.base + "^{commit}").strip()
    target = [git("rev-parse", "--verify", "--end-of-options", ref.head + "^{commit}").strip()] if ref.head else []
    patch = git("diff", "--no-ext-diff", "--no-textconv", "--no-color", base, *target, "--", ref.file)
    hunks = []
    for chunk in re.split(r"(?m)^(?=@@ )", patch):
        if not chunk.startswith("@@ "):
            continue
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", chunk)
        start = int(m.group(1))
        end = start + max(int(m.group(2) or 1), 1) - 1
        if ref.start is None or (start <= ref.end and end >= ref.start):
            hunks.append(chunk.rstrip("\n"))
    if not hunks and ref.start is None and patch.strip():
        hunks = [patch.strip()]
    if not hunks:
        raise ValueError(f"no tracked diff for {ref.file} against {ref.base}")
    dest = target[0][:8] if target else "working tree"
    span = f" · lines {ref.start}–{ref.end}" if ref.start else ""
    return {"label": f"{ref.file}{span} · {base[:8]} → {dest}", "code": "\n".join(hunks), "file": "change.diff"}


def snapshot(spec, root):
    tour = Tour.model_validate_json(spec.read_bytes())
    parent = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "terminal-explainer"
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    run = Path(tempfile.mkdtemp(prefix="explain-", dir=parent)).resolve()
    try:
        pages = []
        for i, p in enumerate(tour.pages):
            page = p.model_dump(exclude_none=True)
            if p.image:
                source = local_file(spec.parent, p.image.file)
                with Image.open(source, formats=["PNG", "JPEG", "WEBP"]) as img:
                    thumb = ImageOps.exif_transpose(img).convert("RGBA")
                    thumb.thumbnail((1600, 1200))
                    dest = run / f"figure-{i}.png"
                    thumb.save(dest)
                page["image"]["file"] = dest.name
            if p.evidence:
                page["evidence"] = ([evidence(item, root) for item in p.evidence]
                                    if isinstance(p.evidence, list) else evidence(p.evidence, root))
            pages.append(page)
        (run / "walkthrough.json").write_text(json.dumps({"title": tour.title, "pages": pages}))
    except BaseException:
        shutil.rmtree(run)
        raise
    return run


def save_response(run, response):
    temporary = run / "response.tmp"
    temporary.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")
    temporary.replace(run / "response.json")


def require_run(run):
    if not (run / "walkthrough.json").is_file():
        raise ValueError(f"expected a walkthrough run directory: {run}")
    return run


def view(run):
    require_run(run)
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise ValueError("the reader needs an interactive terminal; use open --plane or prepare")
    sys.dont_write_bytecode = True
    from viewer import Walkthrough
    cfg = settings()
    with (run / "reader.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (run / "response.json").exists():
            raise ValueError("this run already ended; open the original spec for a new response")
        doc = json.loads((run / "walkthrough.json").read_text())
        app = Walkthrough(doc, run, cfg.image_height, cfg.renderer)
        result = app.run()
        if app.return_code:
            raise RuntimeError("reader failed before submission")
        response = {"run": str(run), "status": "cancelled" if result is None else "submitted"}
        if result is not None:
            response["answers"] = result
        save_response(run, response)
        return response


def plane(*args):
    return subprocess.check_output(["tmux-agent-plane", "task", *args], text=True).strip()


def launch(name, cwd, *args):
    tasks = json.loads(plane("list", "--json"))
    if any(task["name"] == name for task in tasks):
        raise ValueError(f"Agent Plane task already exists: {name}")
    # Tasks start in a login shell. Carry the caller's chosen configuration across that boundary.
    uv = shutil.which("uv")
    if not uv:
        raise ValueError("Agent Plane presentation requires uv on PATH")
    config_home = config_path().resolve().parents[1]
    location = plane("start", name, "--cwd", str(cwd), "--", "env", f"XDG_CONFIG_HOME={config_home}",
                     uv, "run", "--script", str(SCRIPT), *args)
    return {"task": name, "location": location}


def wait_response(run, timeout):
    require_run(run)
    doc = run / "response.json"
    deadline = time.monotonic() + timeout
    while not doc.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"no response yet; resume with wait {run}")
        if (run / "plane").exists():
            tasks = json.loads(plane("list", "--json"))
            alive = any(t["name"] == run.name and t["state"] == "running" for t in tasks)
            if not alive and not doc.exists():
                raise ValueError(f"reader stopped without a response; inspect task {run.name}")
        if not doc.exists():
            time.sleep(min(1, max(0, deadline - time.monotonic())))
    return json.loads(doc.read_text())


def prepare_illustration(prompt_file, output, cfg):
    if not cfg.image_command:
        raise ValueError(f"set image_command in {config_path()} or supply a finished picture")
    if output.suffix.lower() != ".png":
        raise ValueError("illustrate writes PNG files; choose a .png destination")
    if output.exists():
        raise FileExistsError(output)
    prompt = prompt_file.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError("empty illustration brief")
    output.parent.mkdir(parents=True, exist_ok=True)
    return prompt


def illustrate(prompt_file, output, cfg):
    prompt = prepare_illustration(prompt_file, output, cfg)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        generated = Path(temp).resolve() / "image.png"
        args = {"{prompt}": f"{prompt}\n\n{cfg.illustration_style}", "{output}": str(generated)}
        subprocess.run([args.get(arg, arg) for arg in cfg.image_command], check=True, stdout=sys.stderr)
        with Image.open(generated, formats=["PNG"]) as picture:
            picture.load()
        os.link(generated, output)  # Publish a complete image without overwriting a concurrent job.
    return {"image": str(output.resolve())}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cmds = cli.add_subparsers(dest="command", required=True)
    for cmd in ("prepare", "open"):
        p = cmds.add_parser(cmd, help="snapshot a walkthrough" + (" and launch its reader" if cmd == "open" else ""))
        p.add_argument("spec", type=Path)
        p.add_argument("--root", type=Path, default=Path.cwd(), help="root of source evidence")
        if cmd == "open":
            p.add_argument("--plane", action="store_true", help="open as an Agent Plane task")
    cmds.add_parser("demo", help="open the bundled illustrated walkthrough").add_argument("--plane", action="store_true")
    for cmd in ("view", "wait"):
        p = cmds.add_parser(cmd)
        p.add_argument("run", type=Path)
        if cmd == "wait":
            p.add_argument("--timeout", type=int, default=3600)
    cmds.add_parser("config").add_argument("--init", action="store_true")
    gen = cmds.add_parser("illustrate", help="run the configured image command once")
    gen.add_argument("brief", type=Path)
    gen.add_argument("output", type=Path)
    gen.add_argument("--plane", action="store_true", help="start a tracked illustration job")
    a = cli.parse_args()
    if a.command == "config":
        path = config_path()
        if a.init:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x") as out:
                out.write(Settings().model_dump_json(indent=2) + "\n")
        result = {"path": str(path), "settings": settings().model_dump()}
    elif a.command == "illustrate":
        cfg = settings()
        if a.plane:
            prepare_illustration(a.brief, a.output, cfg)
            output = a.output.resolve()
            result = launch("figure-" + uuid.uuid4().hex[:12], output.parent, "illustrate",
                            str(a.brief.resolve(strict=True)), str(output))
            result["image"] = str(output)
        else:
            result = illustrate(a.brief, a.output, cfg)
    elif a.command == "wait":
        result = wait_response(a.run.resolve(strict=True), a.timeout)
    elif a.command == "view":
        result = view(a.run.resolve(strict=True))
    else:
        demo = a.command == "demo"
        present = a.command != "prepare"
        use_plane = present and (a.plane or settings().presentation == "plane")
        if present and not use_plane and not (sys.stdin.isatty() and sys.stderr.isatty()):
            raise ValueError("use open --plane or prepare a run for an interactive terminal")
        run = snapshot(DEMO if demo else a.spec.resolve(), SCRIPT.parents[1] if demo else a.root.resolve())
        if not present:
            result = {"run": str(run)}
        elif use_plane:
            (run / "plane").touch()
            try:
                launched = launch(run.name, run, "view", str(run))
            except BaseException:
                shutil.rmtree(run)
                raise
            print(f"Saved walkthrough at {run}", file=sys.stderr)
            result = {"run": str(run), **launched}
        else:
            print(f"Saved walkthrough at {run}", file=sys.stderr)
            result = view(run)
    print(json.dumps(result, ensure_ascii=False))
    return 2 if result.get("status") == "cancelled" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except TimeoutError as error:
        print(error, file=sys.stderr)
        sys.exit(3)
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
