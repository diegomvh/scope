#!/usr/bin/env python

class Node(object):
    pass

class Scope(object):
    pass

wildcard = Scope("x-any")

class Selector(object):
    def _setup(self, source):
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
