"""Interactive reader for a frozen walkthrough."""
import os
import re
import subprocess

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.content import Content
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, ContentSwitcher, RadioButton, RadioSet, Static, TextArea
from textual_image._terminal import TerminalCapabilities, probe_terminal


def literal(value):
    return "".join(c if c.isprintable() or c in "\n\t" else "" for c in value)


def image_widget(renderer):
    capabilities = probe_terminal()
    if renderer == "auto" and os.environ.get("TMUX"):
        # tmux answers graphics probes itself, so ask it which terminal it is drawing to.
        pane = os.environ["TMUX_PANE"]
        outer = subprocess.check_output(["tmux", "display", "-p", "-t", pane,
                                         "#{client_termtype}\t#{client_termfeatures}"], text=True)
        termtype, features = outer.rstrip("\n").split("\t")
        tgp = re.match(r"(ghostty|kitty)\b", termtype) is not None
        if tgp:
            subprocess.run(["tmux", "set", "-p", "-t", pane, "allow-passthrough", "on"], check=True)
        probe_terminal._result = TerminalCapabilities(capabilities.cell_size, sixel="sixel" in features.split(","),
                                                      tgp=tgp)
    from textual_image.widget import HalfcellImage, Image
    return Image if renderer == "auto" else HalfcellImage


class FigureView(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Back"), ("f", "dismiss", "Back"),
                ("q", "dismiss", "Back"), ("ctrl+c", "dismiss", "Back")]
    CSS = """
    FigureView { background: ansi_default; padding: 1; }
    #full-figure { height: 1fr; align: center middle; }
    #full-figure > * { width: auto; height: auto; }
    FigureView .caption-row { margin-bottom: 0; }
    """

    def __init__(self, widget, path, caption):
        super().__init__()
        self.image_widget = widget
        self.path = path
        self.caption = caption

    def compose(self) -> ComposeResult:
        with Container(id="full-figure"):
            yield self.image_widget(self.path)
        with Horizontal(classes="caption-row"):
            yield Static(literal(self.caption), markup=False, classes="caption")
            yield Button(Content("Back [f]"), compact=True)

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()


class Walkthrough(App[dict]):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("escape", "unfocus", "Leave box"),
        ("q", "quit", "Close"),
        ("ctrl+c", "quit", "Close"),
        ("n", "next", "Next"),
        ("ctrl+n", "next", "Next"),
        ("p", "back", "Back"),
        ("ctrl+p", "back", "Back"),
        ("j", "scroll_down", "Down"),
        ("k", "scroll_up", "Up"),
        ("f", "figure", "Figure"),
        ("e", "evidence", "Evidence"),
        ("a", "answer", "Answer"),
        *((str(k), f"choice({k - 1})", "") for k in range(1, 10)),
    ]
    # Only ANSI colors, so the reader takes its palette and background from the terminal theme.
    CSS = """
    Screen { background: ansi_default; color: ansi_default; }
    #mast { color: ansi_cyan; padding: 0 2; height: 1; text-style: bold; }
    #pages { height: 1fr; }
    .page { padding: 1 2; align-horizontal: center; scrollbar-size: 1 1; }
    .page > * { width: 100%; max-width: 92; }
    .heading { text-style: bold; color: ansi_yellow; margin-bottom: 1; }
    .body { margin-bottom: 1; }
    .figure { align: center middle; }
    .picture { width: auto; height: auto; }
    .caption-row { height: auto; margin-bottom: 1; align-vertical: top; }
    .caption { width: 1fr; color: ansi_cyan; border-left: thick ansi_cyan; padding-left: 1; }
    Button { min-width: 0; width: auto; height: 1; margin-left: 1; background: ansi_default; color: ansi_cyan; }
    Button:focus { background: ansi_cyan; color: ansi_black; text-style: bold; }
    Collapsible { background: ansi_default; border: none; padding: 0; margin-bottom: 1; }
    Collapsible Contents { padding: 0 1; }
    CollapsibleTitle { color: ansi_cyan; }
    CollapsibleTitle:focus { background: ansi_cyan; color: ansi_black; }
    .prompt { text-style: bold; margin-bottom: 1; }
    RadioSet, TextArea { width: 100%; height: auto; max-height: 12; border: round ansi_bright_black; background: ansi_default; }
    RadioSet:focus-within, TextArea:focus { border: round ansi_cyan; }
    TextArea { height: 5; }
    #nav { height: 1; padding: 0 2; align-vertical: middle; }
    #position { width: 1fr; color: ansi_bright_black; }
    #next { width: 8; color: ansi_green; text-style: bold; }
    #next:focus { background: ansi_green; color: ansi_black; }
    """

    def __init__(self, doc, run, image_height, renderer):
        super().__init__()
        self.theme = "ansi-dark"
        self.doc = doc
        self.run_dir = run
        self.image_height = image_height
        self.figure_type = image_widget(renderer)
        self.index = 0

    def compose(self) -> ComposeResult:
        yield Static(literal(self.doc["title"]), id="mast", markup=False)
        with ContentSwitcher(initial="page-0", id="pages"):
            for i, page in enumerate(self.doc["pages"]):
                with VerticalScroll(id=f"page-{i}", classes="page", can_focus=True):
                    yield Static(literal(page["heading"]), classes="heading", markup=False)
                    yield Static(literal(page["body"]), classes="body", markup=False)
                    if image := page.get("image"):
                        with Container(classes="figure") as frame:
                            frame.styles.height = self.image_height
                            yield self.figure_type(self.run_dir / image["file"], classes="picture")
                        with Horizontal(classes="caption-row"):
                            yield Static(literal(image["caption"]), classes="caption", markup=False)
                            yield Button(Content("Expand [f]"), classes="expand", compact=True)
                    if ev := page.get("evidence"):
                        for item in (ev if isinstance(ev, list) else [ev]):
                            label = "Evidence [e] · " + literal(item["label"])
                            with Collapsible(title=Content(label).markup, collapsed=True):
                                code = literal(item["code"])
                                lexer = Syntax.guess_lexer(item["file"], code)
                                yield Static(Syntax(code, lexer, theme="ansi_dark", word_wrap=True,
                                                    line_numbers="start" in item, start_line=item.get("start", 1)))
                    if question := page.get("question"):
                        yield Static(literal(question["prompt"]), classes="prompt", markup=False)
                        if choices := question.get("choices"):
                            yield RadioSet(*(RadioButton(Content(f"{n}. {literal(c)}"))
                                             for n, c in enumerate(choices, 1)), id=f"answer-{i}")
                        else:
                            yield TextArea(id=f"answer-{i}", placeholder="Your response… (Esc leaves the box)")
        with Horizontal(id="nav"):
            yield Static(id="position")
            yield Button("Back", id="back", compact=True)
            yield Button("Next", id="next", compact=True)
            yield Button("Close", id="close", compact=True)

    def on_mount(self):
        self.select_page(0)

    def select_page(self, i):
        self.index = i
        pages = self.doc["pages"]
        page = pages[i]
        has_questions = any(p.get("question") for p in pages)
        self.query_one("#pages", ContentSwitcher).current = f"page-{i}"
        hints = ["n/p page" if len(pages) > 1 else ("n submit" if has_questions else "n done"), "j/k scroll"]
        if page.get("image"):
            hints.append("f figure")
        if page.get("evidence"):
            hints.append("e evidence")
        if q := page.get("question"):
            hints.append(f"1-{len(q['choices'])} choose" if q.get("choices") else "a answer")
        hints.append("q close")
        self.query_one("#position", Static).update(f"{i + 1} / {len(pages)}  ·  " + "  ".join(hints))
        self.query_one("#back", Button).display = i > 0
        self.query_one("#next", Button).label = ("Submit" if has_questions else "Done") if i == len(pages) - 1 else "Next"
        self.query_one(f"#page-{i}").focus()

    def action_unfocus(self):
        self.query_one(f"#page-{self.index}").focus()

    def action_scroll_down(self):
        self.query_one(f"#page-{self.index}", VerticalScroll).scroll_down(animate=False)

    def action_scroll_up(self):
        self.query_one(f"#page-{self.index}", VerticalScroll).scroll_up(animate=False)

    def action_figure(self):
        if image := self.doc["pages"][self.index].get("image"):
            self.push_screen(FigureView(self.figure_type, self.run_dir / image["file"], image["caption"]))

    def action_evidence(self):
        items = list(self.query(f"#page-{self.index} Collapsible"))
        if not items:
            return
        collapse = any(not c.collapsed for c in items)
        for c in items:
            c.collapsed = collapse
        if not collapse:
            self.call_after_refresh(items[-1].scroll_visible, animate=False)

    def action_answer(self):
        if widgets := list(self.query(f"#page-{self.index} #answer-{self.index}")):
            widgets[0].focus()
            widgets[0].scroll_visible(animate=False)

    def action_choice(self, idx: int):
        radios = list(self.query(f"#page-{self.index} RadioSet RadioButton"))
        if idx < len(radios):
            radios[idx].value = True
            radios[idx].scroll_visible(animate=False)

    def action_back(self):
        if self.index > 0:
            self.select_page(self.index - 1)

    def action_next(self):
        if self.index + 1 < len(self.doc["pages"]):
            self.select_page(self.index + 1)
            return
        answers = {}
        for i, page in enumerate(self.doc["pages"]):
            if not (q := page.get("question")):
                continue
            widget = self.query_one(f"#answer-{i}")
            if isinstance(widget, RadioSet):
                value = q["choices"][widget.pressed_index] if widget.pressed_index >= 0 else ""
            else:
                value = widget.text
            if not value.strip():
                self.select_page(i)
                widget.focus()
                self.notify("Answer this question before submitting.")
                return
            answers[q["id"]] = value
        self.exit(answers)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.has_class("expand"):
            self.action_figure()
        elif event.button.id == "back":
            self.action_back()
        elif event.button.id == "next":
            self.action_next()
        elif event.button.id == "close":
            self.exit()
