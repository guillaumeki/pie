'''
Created on 23 déc. 2021

@author: guillaume
'''
from prototyping_inference_engine.api.atom.term.term import Term


class Variable(Term):
    fresh_counter = 0
    variables = {}

    def __new__(cls, identifier):
        if identifier not in cls.variables:
            cls.variables[identifier] = Term.__new__(cls)
        return cls.variables[identifier]

    def __init__(self, identifier):
        Term.__init__(self, identifier)

    def __repr__(self):
        return "Var:"+str(self)

    @classmethod
    def fresh_variable(cls) -> "Variable":
        identifier = "V" + str(cls.fresh_counter)
        while identifier in cls.variables:
            cls.fresh_counter += 1
            identifier = "V" + str(cls.fresh_counter)
        return Variable(identifier)

    @classmethod
    def safe_renaming(cls, v: "Variable") -> "Variable":
        identifier = str(v.identifier) + str(cls.fresh_counter)
        while identifier in cls.variables:
            cls.fresh_counter += 1
            identifier = str(v.identifier) + str(cls.fresh_counter)
        return Variable(identifier)
