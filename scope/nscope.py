#!/usr/bin/env python

from .parser import Parser

class Node(object):
    def __init__(self, atoms, parent):
        self._atoms = atoms
        self._parent = parent
        self._retain_count = 1

    def __del__(self):
        if self._parent is not None:
            self._parent.release()

    def retain(self):
	    self._retain_count += 1
	
    def release(self):
        self._retain_count -= 1
        if self._retain_count == 0:
	        del self

    def is_auxiliary_scope(self):
        return self._atoms.startswith("attr.") || self._atoms.startswith("dyn.") 
    
    def number_of_atoms(self):
	    return self._atoms.count(".")

class Scope(object):
    pass

wildcard = Scope("x-any")

class Selector(object):
    def __ init__(self, source = None):
        self._selector = None
        if source is not None:
            self._selector = Parser.selector(source)

    def __str__(self):
        return self._selector and six.text_type(self._selector) or ""

    # ------- Matching 
    def does_match(self, context, rank = None):
        if self._selector:
            return context.left == wildcard or context.right == wildcard or self.selector.does_match(context.left.path, context.right.path, rank)
        if rank is not None:        
            rank.append(0)
        return True
