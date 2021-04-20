def constant(f):
    """
    Decorator to convert a method to constant property
    """

    def fset(self, value):
        raise TypeError
    def fget(self):
        return f(self)
    return property(fget, fset)