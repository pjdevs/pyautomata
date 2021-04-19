# Automata

Prototyping library for Finite Automaton in Python. Will be implemented in an other language in the future.

## Current features

Support for :

- Deterministic Finite Automaton (DFA)
- Non-Deterministic Finite Automaton (NFA)
- Determinization of a NFA
- Execution of an (D/N)FA on a word built on its alphabet
- Completion of an FA (Soon)
- Minimization of a DFA(Soon)

## Future things to implement

- Transitions of `State` as `dict`
- Drawing with Graphviz
- Build an FA from regular expressions
- Improve management of new states while determinizing an NFA

# Examples

```python
a = NFAutomaton(set("ab"))

a.add_state(0, initial=True)
a.add_state(1, final=True)
a.add_state(2)

a.add_transition("ab", 0, 0)
a.add_transition("a", 0, 1)
a.add_transition("ab", 1, 2)
a.add_transition("ab", 2, 2)

da = a.determinized()

print(a.accepts("ababba"), da.accepts("ababba")) # True True
print(a.accepts("ababbababb"), da.accepts("ababbababb")) # False False
print(a.accepts("test"), da.accepts("test")) # False False
```

## Contributors

Author: pjdevs
Others: 