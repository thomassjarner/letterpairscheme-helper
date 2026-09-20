"""
Placeholder for the future Scramble -> Memo feature.

This is intentionally NOT implemented yet. Turning a scramble into a
BLD letter memo requires nailing down a number of conventions that
must not be guessed at, per explicit instruction:
  - solving method / move application (which cube representation, corner
    and edge orientation conventions)
  - buffer convention already covered by LetterScheme, but also:
    which sticker of the buffer piece is "home" for orientation purposes
  - cycle break handling: which piece to break to, and how that's
    represented in the letter memo
  - parity handling (odd number of edge or corner swaps)
  - memo convention: corners-first or edges-first, how pairs are grouped
    when a cycle has an odd number of targets, etc.

The rest of the app (LetterScheme, the pairs module, and the global word
dictionary) is built so that once these conventions are agreed on, this
module can be implemented and wired into a new "Scramble Memo" page
without changing any of the other layers.
"""

from dataclasses import dataclass
from typing import List

from data.models import LetterScheme


@dataclass
class TraceResult:
    corner_targets: List[str]
    edge_targets: List[str]
    corner_letters: List[str]
    edge_letters: List[str]
    corner_pairs: List[str]
    edge_pairs: List[str]


class ScrambleTracer:
    def trace(self, scramble: str, scheme: LetterScheme) -> TraceResult:
        raise NotImplementedError(
            "Scramble tracing is not implemented yet — it needs a "
            "conventions discussion first (orientation, cycle breaks, "
            "parity, memo grouping). See module docstring."
        )
