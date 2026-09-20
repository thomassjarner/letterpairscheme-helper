"""
AppState: the single place the UI talks to for reading/mutating data.
Every mutating method saves via the repository immediately afterward, so
the app is always autosaved. Pages register on_change callbacks so they
can refresh when something they don't own changes.
"""

from typing import Callable, List, Optional

from core.cube_definitions import CATEGORY_PIECES
from data.models import AppData, CategoryScheme, LetterScheme
from data.repository import AppDataRepository

BUFFER_MARKER = "BUFFER"


class AppState:
    def __init__(self, repository: AppDataRepository):
        self._repo = repository
        self.data: AppData = self._repo.load()
        self._listeners: List[Callable[[], None]] = []

    # ---- change notification -------------------------------------------------

    def on_change(self, callback: Callable[[], None]) -> None:
        self._listeners.append(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            cb()

    def _save(self) -> None:
        self._repo.save(self.data)
        self._notify()

    # ---- scheme CRUD -----------------------------------------------------

    @property
    def scheme_names(self) -> List[str]:
        return sorted(self.data.schemes.keys())

    @property
    def active_scheme(self) -> Optional[LetterScheme]:
        if self.data.active_scheme and self.data.active_scheme in self.data.schemes:
            return self.data.schemes[self.data.active_scheme]
        return None

    def create_scheme(self, name: str) -> LetterScheme:
        name = self._unique_name(name)
        scheme = LetterScheme(name=name)
        self.data.schemes[name] = scheme
        if self.data.active_scheme is None:
            self.data.active_scheme = name
        self._save()
        return scheme

    def rename_scheme(self, old_name: str, new_name: str) -> None:
        if old_name not in self.data.schemes or old_name == new_name:
            return
        new_name = self._unique_name(new_name)
        scheme = self.data.schemes.pop(old_name)
        scheme.name = new_name
        self.data.schemes[new_name] = scheme
        if self.data.active_scheme == old_name:
            self.data.active_scheme = new_name
        self._save()

    def duplicate_scheme(self, name: str) -> Optional[LetterScheme]:
        if name not in self.data.schemes:
            return None
        new_name = self._unique_name(f"{name} copy")
        new_scheme = self.data.schemes[name].duplicate(new_name)
        self.data.schemes[new_name] = new_scheme
        self._save()
        return new_scheme

    def delete_scheme(self, name: str) -> None:
        if name not in self.data.schemes:
            return
        del self.data.schemes[name]
        if self.data.active_scheme == name:
            remaining = self.scheme_names
            self.data.active_scheme = remaining[0] if remaining else None
        self._save()

    def switch_scheme(self, name: str) -> None:
        if name in self.data.schemes:
            self.data.active_scheme = name
            self._save()

    def _unique_name(self, base: str) -> str:
        if base not in self.data.schemes:
            return base
        i = 2
        while f"{base} ({i})" in self.data.schemes:
            i += 1
        return f"{base} ({i})"

    # ---- editing a scheme's stickers/buffer -------------------------------

    def _category_scheme(self, scheme: LetterScheme, category: str) -> CategoryScheme:
        return scheme.corners if category == "corners" else scheme.edges

    def set_buffer(self, scheme: LetterScheme, category: str, piece_name: str) -> None:
        cat = self._category_scheme(scheme, category)
        pieces = CATEGORY_PIECES[category]

        # Clear BUFFER marker off the old buffer's stickers so they become
        # normal (unassigned) stickers again.
        if cat.buffer_piece and cat.buffer_piece in pieces:
            for sticker in pieces[cat.buffer_piece]:
                if cat.stickers.get(sticker) == BUFFER_MARKER:
                    del cat.stickers[sticker]

        cat.buffer_piece = piece_name
        for sticker in pieces.get(piece_name, ()):
            cat.stickers[sticker] = BUFFER_MARKER
        self._save()

    def set_sticker_letter(self, scheme: LetterScheme, category: str, sticker: str, letter: str) -> None:
        cat = self._category_scheme(scheme, category)
        letter = letter.strip().upper()
        if not letter:
            cat.stickers.pop(sticker, None)
        else:
            cat.stickers[sticker] = letter[0]
        self._save()

    # ---- global words ------------------------------------------------------

    def set_word(self, pair: str, word: str) -> None:
        word = word.strip()
        if word:
            self.data.global_words[pair] = word
        else:
            self.data.global_words.pop(pair, None)
        self._save()

    def get_word(self, pair: str) -> str:
        return self.data.global_words.get(pair, "")
