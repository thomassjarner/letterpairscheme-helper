"""
Data model for the app. Plain dataclasses with explicit to_dict/from_dict
so the JSON shape is controlled in one place and easy to version/migrate
(e.g. when moving to SQLite later).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

CURRENT_VERSION = 1


@dataclass
class CategoryScheme:
    buffer_piece: Optional[str] = None
    # sticker -> single-letter string, or "BUFFER" for the buffer piece's stickers
    stickers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"buffer_piece": self.buffer_piece, "stickers": dict(self.stickers)}

    @staticmethod
    def from_dict(d: dict) -> "CategoryScheme":
        return CategoryScheme(
            buffer_piece=d.get("buffer_piece"),
            stickers=dict(d.get("stickers", {})),
        )


@dataclass
class LetterScheme:
    name: str
    corners: CategoryScheme = field(default_factory=CategoryScheme)
    edges: CategoryScheme = field(default_factory=CategoryScheme)

    def to_dict(self) -> dict:
        return {
            "corners": self.corners.to_dict(),
            "edges": self.edges.to_dict(),
        }

    @staticmethod
    def from_dict(name: str, d: dict) -> "LetterScheme":
        return LetterScheme(
            name=name,
            corners=CategoryScheme.from_dict(d.get("corners", {})),
            edges=CategoryScheme.from_dict(d.get("edges", {})),
        )

    def duplicate(self, new_name: str) -> "LetterScheme":
        return LetterScheme(
            name=new_name,
            corners=CategoryScheme.from_dict(self.corners.to_dict()),
            edges=CategoryScheme.from_dict(self.edges.to_dict()),
        )


@dataclass
class AppData:
    version: int = CURRENT_VERSION
    active_scheme: Optional[str] = None
    schemes: Dict[str, LetterScheme] = field(default_factory=dict)
    # Single flat pair -> word dict, shared across ALL schemes and BOTH
    # categories (corners/edges), per user decision.
    global_words: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "active_scheme": self.active_scheme,
            "schemes": {name: s.to_dict() for name, s in self.schemes.items()},
            "global_words": dict(self.global_words),
        }

    @staticmethod
    def from_dict(d: dict) -> "AppData":
        schemes = {
            name: LetterScheme.from_dict(name, sd)
            for name, sd in d.get("schemes", {}).items()
        }
        return AppData(
            version=d.get("version", CURRENT_VERSION),
            active_scheme=d.get("active_scheme"),
            schemes=schemes,
            global_words=dict(d.get("global_words", {})),
        )
