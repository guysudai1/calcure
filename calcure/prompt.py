
from typing import List, Tuple
from prompt_toolkit.completion import Completer, Completion


class IconCompleter(Completer):
    def __init__(self, icons: List[Tuple[str, str]]):
        self.icons = icons

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if "@" in text:
            # Find the last @ to start matching from there
            idx = text.rfind("@") + 1
            prefix = text[idx:]
            for icon_text, icon in self.icons:
                if icon_text.lower().startswith(prefix.lower()):
                    yield Completion(icon_text, display=f"{icon_text} ({icon})", start_position=-len(prefix))
