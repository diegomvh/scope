#!/usr/bin/env python

from .parser import Parser

class Scope(object):
    class Node(object):
        def __init__(self, atoms, parent):
            self._atoms = atoms
            self._parent = parent
            self._retain_count = 1
    
        def __del__(self):
            if self._parent is not None:
                self._parent.release()
    
        def __bool__(self):
            return bool(self._atoms)

        def retain(self):
    	    self._retain_count += 1
    	
        def release(self):
            self._retain_count -= 1
            if self._retain_count == 0:
    	        del self
    
        def is_auxiliary_scope(self):
            return self._atoms.startswith("attr.") or self._atoms.startswith("dyn.") 
        
        def number_of_atoms(self):
    	    return self._atoms.count(".")
    
    def __init__(self, source = None):
        self._node = None
        if source is not None:
            for atom in source.split():
                self.push_scope(atom)

    def empty(self):
        return bool(self._node)

    def push_scope(self, atom):
        self._node = Scope.Node(atom, self._node)
    
    def pop_scope(self):
        assert(self._node is not None)
        old = self._node
        self._node == self._node.parent()
        if self._node:
            self._node.retain()
        old.release()

wildcard = Scope("x-any")

class Selector(object):
    def __init__(self, source = None):
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
