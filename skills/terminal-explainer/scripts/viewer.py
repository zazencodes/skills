"""Interactive reader for a frozen walkthrough."""
import os

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.content import Content
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, ContentSwitcher, RadioButton, RadioSet, Static, TextArea
from textual_image._terminal import CellSize, TerminalCapabilities, probe_terminal


def literal(value):
    return "".join(c if c.isprintable() or c in "\n\t" else "" for c in value)


def image_widget(renderer):
    if (renderer == "cells" or os.environ.get("TMUX")) and not hasattr(probe_terminal, "_result"):
        probe_terminal._result = TerminalCapabilities(CellSize(10, 20), sixel=False, tgp=False)
    from textual_image.widget import HalfcellImage, Image
    return Image if renderer == "auto" else HalfcellImage


class FigureView(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Back"), ("f", "dismiss", "Back"),
                ("q", "dismiss", "Back"), ("ctrl+c", "dismiss", "Back")]
    CSS = """
    FigureView { background: #101922; padding: 1; }
    #full-figure { height: 1fr; align: center middle; }
    #full-figure > * { width: auto; height: auto; }
    FigureView .caption-row { margin-bottom: 0; }
    FigureView Button { min-width: 0; width: auto; height: 1; margin-left: 1; background: #192833; color: #78dfcd; }
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
            yield Button("Back [f]", compact=True)

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()


class Walkthrough(App[dict]):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("escape", "close_or_unfocus", "Close"),
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
    CSS = """
    Screen { background: #101922; color: #e8edf0; }
    #mast { background: #192833; color: #78dfcd; padding: 0 2; height: 1; text-style: bold; }
    #pages { height: 1fr; }
    .page { padding: 1 2; align-horizontal: center; scrollbar-size: 1 1; }
    .page > * { width: 100%; max-width: 92; }
    .heading { text-style: bold; color: #ffcd78; margin-bottom: 1; }
    .body { margin-bottom: 1; }
    .figure { align: center middle; }
    .picture { width: auto; height: auto; }
    .caption-row { height: auto; margin-bottom: 1; align-vertical: top; }
    .caption { width: 1fr; color: #9bd6cf; border-left: thick #488f88; padding-left: 1; }
    .page Button.expand { min-width: 0; width: auto; height: 1; margin-left: 1; background: #192833; color: #78dfcd; }
    Collapsible { background: #192833; border: none; padding: 0; margin-bottom: 1; }
    Collapsible Contents { padding: 0 1; }
    .prompt { text-style: bold; margin-bottom: 1; }
    RadioSet, TextArea { width: 100%; height: auto; max-height: 12; border: round #40636b; background: #192833; }
    TextArea { height: 5; }
    #nav { height: 1; background: #192833; padding: 0 2; align-vertical: middle; }
    #position { width: 1fr; color: #afc1c8; }
    #nav Button { min-width: 6; width: auto; height: 1; margin-left: 1; }
    #next { background: #147268; color: white; }
    """

    def __init__(self, doc, run, image_height, renderer):
        super().__init__()
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
                            yield Button("Expand [f]", classes="expand", compact=True)
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
                            yield TextArea(id=f"answer-{i}", placeholder="Your response… (Esc to leave box)")
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
        back = self.query_one("#back", Button)
        back.display = len(pages) > 1
        back.disabled = i == 0
        self.query_one("#next", Button).label = ("Submit" if has_questions else "Done") if i == len(pages) - 1 else "Next"
        self.query_one(f"#page-{i}").focus()

    def action_close_or_unfocus(self):
        if isinstance(self.focused, TextArea):
            self.query_one(f"#page-{self.index}").focus()
            return
        self.exit()

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
