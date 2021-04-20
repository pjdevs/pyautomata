"""
A simple module for finite automaton manipulation.
It contains classes for `FAutomaton`, `NFAutomaton`, `DFAutomaton`.
"""

__all__ = [
    "FAutomaton",
    "DFAutomaton",
    "NFautomaton"
]

from .automata import FAutomaton, DFAutomaton, NFAutomaton