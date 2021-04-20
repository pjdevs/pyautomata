from abc import ABC, abstractmethod
from queue import Queue
from copy import deepcopy
from .utils.unordered_pairs import unique_unordered_pairs, UnorderedPair

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

    def __init__(self, alphabet):
        """
        Common constructor for all FA.
        Construct a new FA with a given `alphabet`.
        """

        self._alphabet = alphabet
        self._states = {}
        self._final_states_ids = set()
        self._completed = False

    def has_been_completed(self):
        """
        Predicate if the FA has been completed explicitely (with `complete` method)
        """
        
        return self._completed

    def complete(self) -> bool:
        """
        Complete the FA with a PI state (hole state).
        Returns wether the FA was complete or not.
        """
        
        not_complete = False
        transitions_to_add = {}

        for state in self._states.values():
            all_transitions = set()

            for transition in state._transitions:
                all_transitions = all_transitions.union(transition._letters)

            diff_letters = self._alphabet.difference(all_transitions)

            if len(diff_letters) > 0:
                not_complete = True
                transitions_to_add[state._id] = diff_letters 

        if not_complete:
            pi_id = sum(self._states.keys()) + 1
            self.add_state(pi_id)
            self.add_transition(self._alphabet, pi_id, pi_id)

            for state_id, letters in transitions_to_add.items():
                self.add_transition(letters, state_id, pi_id)

        self._completed = True
                
        return not not_complete

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
        Create a new Deterministic Finite Automaton with given alphabet `alphabet`
        """

        super().__init__(alphabet)
        self._initial_state_id = None

    def successor(self, state_id, letter):
        """
        Returns, if it exists, the successor of the state `state_id` by transition `letter`.
        Else, returns `None`.
        """

        for transition in self._states[state_id]._transitions:
            if letter in transition._letters:
                return transition._to

        return None


    def accepts(self, word : str):
        """
        Predicate if this automaton accepts or not the word `word`
        """

        current_state_id = self._initial_state_id

        if current_state_id is None:
            return False

        for letter in word:
            current_state_id = self.successor(current_state_id, letter)

            if current_state_id is None:
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

    def reachable_part(self):
        """
        Returns a new DFA which represent the reachable part of this automaton
        """

        # mark only reachable states (Breadth First Search)
        state_queue = Queue()
        state_queue.put(self._initial_state_id)

        marked = {i: False for i in self._states.keys()}
        waiting = deepcopy(marked)

        while state_queue.qsize() > 0:
            state_id = state_queue.get()
            marked[state_id] = True

            state = self._states[state_id]

            for transition in state._transitions:
                if not waiting[transition._to] and not marked[transition._to]:
                    state_queue.put(transition._to)
                    waiting[transition._to] = True

        # copy the DFA and update states according to marked dict (i.e. is the state reachable or no)
        min_dfa = deepcopy(self)

        for i, state_marked in marked.items():
            if not state_marked:
                min_dfa._states.pop(i)
                min_dfa._final_states_ids.discard(i)

        return min_dfa

    def equivalent_states(self) -> set:
        """
        Returns a `UnorderedPair` set of the equivalent states in the DFA.
        """

        equivalents = set(unique_unordered_pairs(self._states.keys()))
        not_equivalents = set()

        for p in unique_unordered_pairs(self._states.keys()):
            q, qp = self._states[p.a], self._states[p.b]
            if (q._final and not qp._final) or (qp._final and not q._final): # final and not final states cannot be =
                not_equivalents.add(p)
                equivalents.remove(p)

        new_neq_states = True

        while new_neq_states:
            new_neq_states = False

            for q in unique_unordered_pairs(self._states.keys()):
                for letter in self._alphabet:
                    p = UnorderedPair(self.successor(q.a, letter), self.successor(q.b, letter))

                    if p in not_equivalents:
                        not_equivalents.add(q)
                        equivalents.remove(q)
                        new_neq_states = True


        return equivalents

    def merge_equivalent_states(self):
        """
        Merge all equivalent states of the FA using `equivalent_states` method
        """

        eq = self.equivalent_states()

        # remove equivalent states
        for q, qp in eq:
            self._states.pop(qp, None)

        # remove remianing transitions to removed states
        for state in self._states.values():
            transition_to_remove = set()

            for transition in state._transitions:
                if UnorderedPair(state._id, transition._to) in eq:
                    transition_to_remove.add(transition)

            for transition in transition_to_remove:
                state._transitions.remove(transition)


    def minimized(self):
        """
        Returns the equivalent minimized complete DFA
        """

        m = self.reachable_part()
        m.complete()
        m.merge_equivalent_states()

        return m

class NFAutomaton(FAutomaton):
    """
    Class which represent a Non-Deterministic Finite Automaton
    """

    def __init__(self, alphabet : set):
        """
        Create a new Non-Deterministic Finite Automaton with given alphabet `alphabet`
        """
    
        super().__init__(alphabet)
        self._initial_states_ids = set()

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