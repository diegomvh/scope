#!/usr/bin/env python

from .parser import Parser

class Scope(object):
    class Node(object):
        def __init__(self, atoms, parent):
            self._atoms = atoms
            self._parent = parent
            self._retain_count = 1
    
        def parent(self):
            return self._parent

        def __del__(self):
            if self._parent is not None:
                self._parent.release()
    
        def __bool__(self):
            return bool(self._atoms)

        def __str__(self):
            return self._atoms
    
        __unicode__ = __str__
        
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
        self.node = None
        if isinstance(source, Scope.Node):
            # From node
            self.node = node
            self.node.retain()
        elif isinstance(source, Scope):
            # By clone
            self.node = source.node
            self.node.retain()
        elif source is not None:
            # From source string
            for atom in source.split():
                self.push_scope(atom)

    def __del__(self):
        if self.node is not None:
            self.node.release()

    def __eq__(self, rhs):
        	n1, n2 = self.node, rhs.node
        	while n1 and n2 and "%s" % n1 == "%s" % n1:
        	    n1 = n1.parent()
        	    n2 = n2.parent()
        	return not bool(n1) and not bool(n2)

    def __ne__(self, rhs):
        return not self == rhs
    
    def __bool__(self):
        return not self.empty()
    
    def __str__(self):
        res = []
        n = self.node
        while True:
            res.append("%s" % n)
            n = n.parent()
            if n is None:
                break
        return " ".join(res[::-1])
    
    def empty(self):
        return bool(self.node)

    def push_scope(self, atom):
        self.node = Scope.Node(atom, self.node)
    
    def pop_scope(self):
        assert(self.node is not None)
        old = self.node
        self.node == self.node.parent()
        if self.node:
            self.node.retain()
        old.release()
    
    def back(self):
        assert(self.node is not None)
        return "%s" % self.node

    def size(self):
        res = 0
        n = self.node
        while n.parent():
            res += 1
            n = n.parent()
        return res

wildcard = Scope("x-any")

def shared_prefix(lhs, rhs):
    return ""
    
def xml_difference(from, to, open = "<", close = ">"):
    return ""

class Context(object):
    def __init__(self, left = None, right = None):
        self.left = Scope(left)
        self.right = right is not None and Scope(right) or Scope(left)
        
    def __eq__(self, rhs):
        return self.left == rhs.left and self.right == rhs.right
    
    def __ne__(self, rhs):
        return not self == rhs
    
    def __lt__(self, rhs):
        return self.left < rhs.left or self.left == self.rhs.left and self.right < rhs.right

    def __str__(self):
        if self.left == self.right:
            return "(l/r '%s')" % six.text_type(self.left)
        else:
            return "(left '%s', right '%s')" % (six.text_type(self.left), six.text_type(self.right))

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
