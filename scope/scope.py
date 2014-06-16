#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

from .parser import Parser
from .types import PathType, ScopeType

class Scope(object):
    def __init__(self, path = ""):
        if isinstance(path, Scope):
            self.path = path.path
        else:
            self.path = isinstance(path, PathType) and path or Parser.path(path)

    @classmethod
    def factory(cls, sources):
        # Fast parsing
        return cls(PathType.factory(type(sources) == type("") and sources.split() or sources))
    
    def __str__(self):
        return "%s" % self.path

    def __nonzero__(self):
        return not self.empty()

    def __hash__(self):
        return hash(self.path)
    
    def __eq__(self, rhs):
        return self.path == rhs.path
    
    def __ne__(self, rhs):
        if not isinstance(rhs, Scope):
            rhs = Scope.factory(rhs)
        return not self == rhs
    
    def __lt__(self, rhs):
        return self.path < self.rhs.path
    
    def __add__(self, rhs):
        return Scope(self.path + rhs.path)

    def __bool__(self):
        return bool(self.path)
    
    def pop_scope(self):
        self.path.scopes.pop()

    def to_xml(self, text = ""):
        return self.path.to_open_xml() + text + self.path.to_close_xml()
    
    def has_prefix(self, rhs):
        if not isinstance(rhs, Scope):
            rhs = Scope.factory(rhs)
        lhsScopes = self.path.scopes
        rhsScopes = rhs.path.scopes
        i = 0
        for i in range(min(len(lhsScopes), len(rhsScopes))):
            if lhsScopes[i] != rhsScopes[i]:
                break
        return i == len(rhsScopes)

    def back(self):
        return self.path.scopes[-1]

    def empty(self):
        return not bool(self.path)

    def rootGroupName(self):
        return self.path.rootGroup() or ""

wildcard = Scope("x-any")
none = Scope("")

class Context(object):
    def __init__(self, left = None, right = None):
        self.left = Scope(left)
        self.right = right is not None and Scope(right) or Scope(left)
    
    def __str__(self):
        if self.left == self.right:
            return "(l/r '%s')" % six.text_type(self.left)
        else:
            return "(left '%s', right '%s')" % (six.text_type(self.left), six.text_type(self.right))
    
    def __hash__(self):
        return hash(six.text_type(self.left)) + hash(six.text_type(self.right))

    def __eq__(self, rhs):
        return self.left == rhs.left and self.right == rhs.right
    
    def __ne__(self, rhs):
        return not self == rhs
    
    def __lt__(self, rhs):
        return self.left < rhs.left or self.left == self.rhs.left and self.right < rhs.right


class Selector(object):
    def __init__(self, selector):
        self.selector = selector and Parser.selector(selector)
        
    def __str__(self):
        return six.text_type(self.selector)

    # ------- Matching 
    def does_match(self, context, rank = None):
        if not isinstance(context, Context):
            context = Context(context)

        if self.selector:
            return context.left == wildcard or context.right == wildcard or self.selector.does_match(context.left.path, context.right.path, rank)
        if rank is not None:        
            rank.append(0)
        return True

