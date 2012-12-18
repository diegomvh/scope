#!/usr/bin/env python

import unittest
from scope.scope import Scope, Context, Selector

class ScopeSelectorTests(unittest.TestCase):
    def setUp(self):
        pass


    def test_child_selector(self):
        self.assertEqual(Selector("foo fud").does_match("foo bar fud"), True)
        self.assertEqual(Selector("foo > fud").does_match("foo bar fud"), False)
        self.assertEqual(Selector("foo > foo > fud").does_match("foo foo fud"), True)
        self.assertEqual(Selector("foo > foo > fud").does_match("foo foo fud fud"), True)
        self.assertEqual(Selector("foo > foo > fud").does_match("foo foo fud baz"), True)
        self.assertEqual(Selector("foo > foo fud > fud").does_match("foo foo bar fud fud"), True)
        

    def test_mixed(self):
        self.assertEqual(Selector("^ foo > bar").does_match("foo bar foo"), True)
        self.assertEqual(Selector("foo > bar $").does_match("foo bar foo"), False)
        self.assertEqual(Selector("bar > foo $").does_match("foo bar foo"), True)
        self.assertEqual(Selector("foo > bar > foo $").does_match("foo bar foo"), True)
        self.assertEqual(Selector("^ foo > bar > foo $").does_match("foo bar foo"), True)
        self.assertEqual(Selector("bar > foo $").does_match("foo bar foo"), True)
        self.assertEqual(Selector("^ foo > bar > baz").does_match("foo bar baz foo bar baz"), True)
        self.assertEqual(Selector("^ foo > bar > baz").does_match("foo foo bar baz foo bar baz"), False)


    def test_anchor(self):
        self.assertEqual(Selector("^ foo").does_match("foo bar"), True)
        self.assertEqual(Selector("^ bar").does_match("foo bar"), False)
        self.assertEqual(Selector("^ foo").does_match("foo bar foo"), True)
        self.assertEqual(Selector("foo $").does_match("foo bar"), False)
        self.assertEqual(Selector("bar $").does_match("foo bar"), True)


    def test_scope_selector(self):
        textScope = Scope("text.html.markdown meta.paragraph.markdown markup.bold.markdown")
        matchingSelectors = [
            Selector("text.* markup.bold"),
            Selector("text markup.bold"),
            Selector("markup.bold"),
            Selector("text.html meta.*.markdown markup"),
            Selector("text.html meta.* markup"),
            Selector("text.html * markup"),
            Selector("text.html markup"),
            Selector("text markup"),
            Selector("markup"),
            Selector("text.html"),
            Selector("text")
        ]
        lastRank = 1
        for selector in matchingSelectors:
            rank = []
            self.assertTrue(selector.does_match(textScope, rank))
            self.assertLessEqual(sum(rank), lastRank)
            lastRank = sum(rank)

    def test_context(self):
        selector = Selector("source & ((L:punctuation.section.*.begin & R:punctuation.section.*.end) | (L:punctuation.definition.*.begin & R:punctuation.definition.*.end)) - string")
        rank = []
        self.assertTrue(selector.does_match(Context("source.python punctuation.definition.list.begin.python", "source.python punctuation.definition.list.end.python"), rank))
            
if __name__ == '__main__':
    unittest.main()