from ..automata import NFAutomaton, DFAutomaton

def test_dfa():
    # counts if has a pair nb of 0
    b = DFAutomaton(set("01"))

    b.add_state(0, initial=True, final=True)
    b.add_state(1)
    
    b.add_transition("0", 0, 0)
    b.add_transition("1", 0, 1)
    b.add_transition("1", 1, 1)
    b.add_transition("0", 1, 0)
    
    print(b.accepts("01001"))
    print(b.accepts("01000"))
    print(b.accepts("zizi"))

def test_nfa():
    # a accepts words which end with an 'a'
    a = NFAutomaton(set("ab"))

    a.add_state(0, initial=True)
    a.add_state(1, final=True)
    a.add_state(2)

    a.add_transition("ab", 0, 0)
    a.add_transition("a", 0, 1)
    a.add_transition("ab", 1, 2)
    a.add_transition("ab", 2, 2)

    da = a.determinized()

    print(a.accepts("ababba"), da.accepts("ababba"))
    print(a.accepts("ababbababb"), da.accepts("ababbababb"))
    print(a.accepts("caca"), da.accepts("caca"))

def test_reachable():
    # counts if has a pair nb of 0
    b = DFAutomaton(set("01"))

    b.add_state(0, initial=True, final=True)
    b.add_state(1)
    b.add_state(2) # nr state
    
    b.add_transition("0", 0, 0)
    b.add_transition("1", 0, 1)
    b.add_transition("1", 1, 1)
    b.add_transition("0", 1, 0)

    b.add_transition("0", 2, 1)
    b.add_transition("1", 2, 0)

    r = b._reachable_part()

def test_equivalent():
    # counts if has a pair nb of 0
    b = DFAutomaton(set("01"))

    b.add_state(0, initial=True, final=True)
    b.add_state(1)
    b.add_state(2)
    b.add_state(3)

    b.add_transition("0", 0, 0)
    b.add_transition("1", 0, 1)
    b.add_transition("1", 1, 1)
    b.add_transition("0", 1, 0)
    b.add_transition("0", 2, 0)
    b.add_transition("1", 2, 1)
    b.add_transition("0", 3, 0)
    b.add_transition("1", 3, 1)

    print(b._equivalent_states())

def test_complete():
    # accepts (b(a+b))*
    a = DFAutomaton(set("ab"))

    a.add_state(0, initial=True, final=True)
    a.add_state(1)

    a.add_transition("b", 0, 1)
    a.add_transition("ab", 1, 0)

    a.complete()

    if not a.has_been_completed():
        print("error: a must have been completed")
        return

    print("expected size : ", 3, " current size:", len(a._states))
    
    print("transitions of 0 :")
    for t in a._states[0]._transitions:
        print(f"0 -{t._letters}-> {t._to}")

    print("expected: True, returned:", a.accepts("babb"))
    print("expected: False, returned:", a.accepts("abbaba"))