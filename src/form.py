from clause import Clause
from copy import copy

class Form():
    def __init__(self, clauses):
        self._clauses = clauses
        self._when_removed = [-1 for x in clauses]

    def all_clauses(self):
        rv = []
        for i in range(len(self._clauses)):
            if self._when_removed[i] == -1:
                rv.append(self._clauses[i])
        return rv
    
    def add_clause(self, c):
        c.id = len(self._clauses)
        self._clauses.append(c)
        self._when_removed.append(-1)

    def __len__(self):
        return len(self.all_clauses())
    
    def remove_clause_id(self, id, level):
        self._when_removed[id] = level
    
    def reset_to_level(self, level):
        for i in range(len(self._clauses)):
            if self._when_removed[i] > level:
                self._when_removed[i] = -1
            self._clauses[i].reset_to_level(level)
    
    def __str__(self):
        return str(self.all_clauses())