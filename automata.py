from abc import ABC, abstractmethod
from queue import Queue

def _is_word_on_alphabet(word : set, alphabet: set):
    return word.issubset(alphabet)

class State:
    """
    Class which represent an Automaton's State
    """

    def __init__(self, id : int, initial=False, final=False):
        """
        Create a new `State` of id `id` with given `Transition`'s list `transitions`.
        This state can be `final` and/or `initial`
        """

        self._id = id
        self._transitions = set()
        self._initial = initial
        self._final = final

class Transition:
    """
    Class which represents a Transition for a Automaton
    """

    def __init__(self, letters : set, to : int):
        """
        Creates a new `Transition` with labels `letters` and which ends on state `to` 
        """

        self._to = to
        self._letters = letters


class FAutomaton(ABC):
    """
    Abstract class which represents a general Finite Automaton
    """

    @abstractmethod
    def accepts(self, word : str) -> bool:
        """
        Predicate if this automaton accepts or not the word `word`
        """
        pass

    @abstractmethod
    def add_state(self, id : int, initial=False, final=False):
        """
        Add a state with id `id`.
        If `initial` is set the state is initial.
        If `final` is set the state is final
        """
        pass

    @abstractmethod
    def add_transition(self, letters : str, from_id : int,  to_id : int):
        """
        Add a transition from automaton's state with id `from_id` to automaton's state with id `to_id`
        """
        pass

class DFAutomaton(FAutomaton):
    """
    Class which represents a Deterministic Finite Automaton
    """

    def __init__(self, alphabet : set):
        """
        Create a new Deterministic Finite Automaton with given states `states`
        """

        self._alphabet = alphabet
        self._states = {}
        self._initial_state_id = None
        self._final_states_ids = set()

    def accepts(self, word : str):
        """
        Predicate if this automaton accepts or not the word `word`
        """

        current_state_id = self._initial_state_id

        for letter in word:
            found = False

            for transition in self._states[current_state_id]._transitions:
                if letter in transition._letters:
                    current_state_id = transition._to
                    found = True

            if not found:
                return False

        return self._states[current_state_id]._final

    def add_state(self, id : int, initial=False, final=False):
        """
        Add a state with id `id`.
        If `initial` is set the state is initial.
        If `final` is set the state is final
        """

        if self._states.get(id, None) is None:
            self._states[id] = State(id, initial, final)

            if initial:
                if self._initial_state_id is not None:
                    raise ValueError("DFAs must have a single initial state")

                self._initial_state_id = id
            if final:
                self._final_states_ids.add(id)
        else:
            raise ValueError(f"A state with id {id} already exists")

    def add_transition(self, letters : str, from_id : int, to_id : int):
        """
        Add a transition from automaton's state with id `from_id` to automaton's state with id `to_id`
        """

        letters_set = set(letters)

        if not _is_word_on_alphabet(letters_set, self._alphabet):
            raise ValueError("Some letters are not in the automaton's alphabet")

        from_state = self._states.get(from_id, None)
        to_state = self._states.get(to_id, None)

        if from_state is None:
            raise ValueError(f"State with id {from_id} doesn't exists")
        elif to_state is None:
            raise ValueError(f"State with id {to_id} doesn't exists")

        for letter in letters_set:
            for transition in from_state._transitions:
                if letter in transition._letters:
                    raise ValueError(f"Transition {letter} already exists. DFAs cannot have two or more transitions with same letters")

        from_state._transitions.add(Transition(letters_set, to_id))

class NFAutomaton(FAutomaton):
    """
    Class which represent a Non-Deterministic Finite Automaton
    """

    def __init__(self, alphabet : set):
        """
        Create a new Non-Deterministic Finite Automaton with given states `states`
        """
    
        self._alphabet = alphabet
        self._states = {}
        self._initial_states_ids = set()
        self._final_states_ids = set()

    def _get_reachable_states(self, letter : str, states_ids : set) -> set:
        """
        Returns the list all reachable states from the list of states with id `states_ids` following the transition `letter`
        """

        reachables_states_ids = set()

        for state_id in states_ids:
            for transition in self._states[state_id]._transitions:
                if transition._letters == "" or (letter in transition._letters):
                    reachables_states_ids.add(transition._to)

        return reachables_states_ids

    def accepts(self, word : str) -> bool:
        """
        Predicate if this automaton accepts or not the word `word`
        """

        reachable_states_ids = self._initial_states_ids
        
        for letter in word:
            reachable_states_ids = self._get_reachable_states(letter, reachable_states_ids)

        return not reachable_states_ids.isdisjoint(self._final_states_ids)

    def determinized(self) -> DFAutomaton:
        """
        Returns a DFA that accepts the same language
        """

        dfa = DFAutomaton(self._alphabet)
        dfa.add_state(0, True, not self._final_states_ids.isdisjoint(self._initial_states_ids))
        new_states = [self._initial_states_ids]

        states_to_treat = Queue()
        states_to_treat.put(self._initial_states_ids)

        while states_to_treat.qsize() > 0:
            current_states_ids = states_to_treat.get()

            for letter in self._alphabet:
                reachable_states_ids = self._get_reachable_states(letter, current_states_ids)

                if not reachable_states_ids in new_states:
                    dfa.add_state(len(new_states), False, not self._final_states_ids.isdisjoint(reachable_states_ids))

                    states_to_treat.put(reachable_states_ids)
                    new_states.append(reachable_states_ids)
                
                dfa.add_transition(letter, new_states.index(current_states_ids), new_states.index(reachable_states_ids))

        return dfa

    def add_state(self, id : int, initial=False, final=False):
        """
        Add a state with id `id`.
        If `initial` is set the state is initial.
        If `final` is set the state is final
        """

        if self._states.get(id, None) is None:
            self._states[id] = State(id, initial, final)

            if initial:
                self._initial_states_ids.add(id)
            if final:
                self._final_states_ids.add(id)
        else:
            raise ValueError(f"A state with id {id} already exists")

    def add_transition(self, letters : str, from_id : int,  to_id : int):
        """
        Add a transition from automaton's state with id `from_id` to automaton's state with id `to_id`
        """
        
        letters_set = set(letters)

        if not _is_word_on_alphabet(letters_set, self._alphabet):
            raise ValueError("Some letters are not in the automaton's alphabet")

        from_state = self._states.get(from_id, None)
        to_state = self._states.get(to_id, None)

        if from_state is None:
            raise ValueError(f"State with id {from_id} doesn't exists")
        elif to_state is None:
            raise ValueError(f"State with id {to_id} doesn't exists")

        from_state._transitions.add(Transition(letters_set, to_id))

if __name__ == "__main__":
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

    #test_dfa()
    test_nfa()