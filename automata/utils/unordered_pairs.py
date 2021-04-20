from .decorators import constant

class UnorderedPair:
    """
    Class for an unordered, "constant" and hashable pair of hashable and ordereable objects, i.e. `UnorderedPair(1, 3) == UnorderedPair(3, 1)`.
    """

    def __init__(self, a, b):
        self._a = a if a <= b else b
        self._b = b if b > a else a

    @constant
    def a(self):
        return self._a

    @constant
    def b(self):
        return self._b

    def __iter__(self):
        return iter((self._a, self._b))

    def __eq__(self, other):
        return self._a == other._a and self._b == other._b

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._a, self._b))

    def __str__(self):
        return f"({self._a}, {self._b})"

    def __repr__(self):
        return self.__str__()

def unique_unordered_pairs(iterable):
    """
    An iterator on unique `UnorderedPair`s of the given `iterable`.
    Example: `1, 2, 3` -> `{1, 2}, {1, 3}, {2, 3}` (may not be in this order).
    """

    max_len = len(iterable)-1

    for e1 in iterable:
        pos = 0

        for e2 in reversed(iterable):
            if pos < max_len: 
                yield UnorderedPair(e1, e2)
            else:
                break
        
            pos += 1
    
        max_len -= 1

if __name__ == "__main__":
    def test_unique():
        l = [1, 2, 3]

        for p in unique_unordered_pairs(l):
            print(p)

    test_unique()