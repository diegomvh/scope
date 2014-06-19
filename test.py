#!/usr/bin/env python
from __future__ import unicode_literals

import unittest
from nscope import Scope, Context, Selector, attributes, xml_difference

class ScopeSelectorTests(unittest.TestCase):
    def setUp(self):
        pass

    # Test Scope
    def test_scope_append(self):
        scope = Scope("foo bar")
        self.assertEqual("bar", scope.back())
        scope.push_scope("some invalid..scope")
        self.assertEqual("some invalid..scope", scope.back())
        scope.pop_scope()
        self.assertEqual("foo bar", "%s" % scope)
        scope.pop_scope()
        self.assertEqual("foo", "%s" % scope)

    def test_empty_scope(self):
        self.assertTrue(Scope().empty())
        self.assertTrue(Scope("").empty())
        self.assertEqual(Scope(""), Scope())

    def test_has_prefix(self):
        self.assertTrue(Scope("").has_prefix(""))
        self.assertTrue(not Scope("").has_prefix("foo"))
        self.assertTrue(Scope("foo").has_prefix(""))
        self.assertTrue(not Scope("foo").has_prefix("foo bar"))
        self.assertTrue(Scope("foo bar").has_prefix("foo bar"))
        self.assertTrue(Scope("foo bar baz").has_prefix("foo bar"))
    
    def test_operator_bool(self):
        scope = Scope("foo")
        self.assertTrue(scope)
        self.assertTrue(not scope.empty())
        scope.pop_scope()
        self.assertTrue(not scope)

    def test_equal_bool(self):
        s1 = Scope("foo")
        s2 = Scope("foo")
        s3 = Scope("foo bar")
        self.assertEqual(s1, s2)
        self.assertNotEqual(s2, s3)
        s2.push_scope("bar")
        self.assertEqual(s2, s3)
        s1 = Scope("foo")
        s2 = Scope(s1)
        self.assertEqual(s1, s2)
        s2.push_scope("bar")
        s1.push_scope("fud")
        self.assertNotEqual(s1, s2)
        s1.pop_scope()
        s2.pop_scope()
        self.assertEqual(s1, s2)
        
    def test_hash(self):
        sset = set()
        slist = []
        sdict = {}
        s1 = Scope("foo")
        s2 = Scope(s1)
        sset.add(s1)
        sset.add(s2)
        slist.append(s1)
        slist.append(s2)
        sdict[s1] = "foo"
        s2.push_scope("bar")
        sdict[s2] = "bar"
        s1.push_scope("bar")
        sset.add(s2)
        self.assertTrue(s2 in sset)
        s1.push_scope("fud")

    # Test Selector
    def test_selector(self):
        self.assertEqual(Selector("source.python meta.function.python, source.python meta.class.python").does_match(Scope("source.python meta.class.python")), True)

    def test_child_selector(self):
        self.assertEqual(Selector("foo fud").does_match(Scope("foo bar fud")), True)
        self.assertEqual(Selector("foo > fud").does_match(Scope("foo bar fud")), False)
        self.assertEqual(Selector("foo > foo > fud").does_match(Scope("foo foo fud")), True)
        self.assertEqual(Selector("foo > foo > fud").does_match(Scope("foo foo fud fud")), True)
        self.assertEqual(Selector("foo > foo > fud").does_match(Scope("foo foo fud baz")), True)
        self.assertEqual(Selector("foo > foo fud > fud").does_match(Scope("foo foo bar fud fud")), True)

    def test_mixed(self):
        self.assertEqual(Selector("^ foo > bar").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("foo > bar $").does_match(Scope("foo bar foo")), False)
        self.assertEqual(Selector("bar > foo $").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("foo > bar > foo $").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("^ foo > bar > foo $").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("bar > foo $").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("^ foo > bar > baz").does_match(Scope("foo bar baz foo bar baz")), True)
        self.assertEqual(Selector("^ foo > bar > baz").does_match(Scope("foo foo bar baz foo bar baz")), False)

    def test_dollar(self):
        dyn = Scope("foo bar")
        dyn.push_scope("dyn.selection")
        self.assertEqual(Selector("foo bar$").does_match(dyn), True);
        self.assertEqual(Selector("foo bar dyn$").does_match(dyn), False);
        self.assertEqual(Selector("foo bar dyn").does_match(dyn), True);

    def test_anchor(self):
        self.assertEqual(Selector("^ foo").does_match(Scope("foo bar")), True)
        self.assertEqual(Selector("^ bar").does_match(Scope("foo bar")), False)
        self.assertEqual(Selector("^ foo").does_match(Scope("foo bar foo")), True)
        self.assertEqual(Selector("foo $").does_match(Scope("foo bar")), False)
        self.assertEqual(Selector("bar $").does_match(Scope("foo bar")), True)

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
            self.assertLessEqual(rank[0], lastRank)
            lastRank = rank[0]

    def test_rank(self):
        leftScope = Scope("text.html.php meta.embedded.block.php source.php comment.block.php")
        rightScope = Scope("text.html.php meta.embedded.block.php source.php")
        context = Context(leftScope, rightScope)
        
        globalSelector = Selector("comment.block | L:comment.block")
        phpSelector = Selector("L:source.php - string")
        
        globalRank, phpRank = [], []
        self.assertTrue(globalSelector.does_match(context, globalRank))
        self.assertTrue(phpSelector.does_match(context, phpRank))
        self.assertLessEqual(phpRank[0], globalRank[0])

    def test_match(self):
        match = lambda sel, scope: Selector(sel).does_match(scope)

        self.assertTrue( match("foo", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo bar", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo bar baz", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo baz", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo.*", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo.qux", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("foo.qux baz.*.garply", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue( match("bar", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue(not match("foo qux", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue(not match("foo.bar", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue(not match("foo.qux baz.garply", "foo.qux bar.quux.grault baz.corge.garply"));
        self.assertTrue(not match("bar.*.baz", "foo.qux bar.quux.grault baz.corge.garply"));
        
        self.assertTrue( match("foo > bar", "foo bar baz bar baz"));
        self.assertTrue( match("bar > baz", "foo bar baz bar baz"));
        self.assertTrue( match("foo > bar baz", "foo bar baz bar baz"));
        self.assertTrue( match("foo bar > baz", "foo bar baz bar baz"));
        self.assertTrue( match("foo > bar > baz", "foo bar baz bar baz"));
        self.assertTrue( match("foo > bar bar > baz", "foo bar baz bar baz"));
        self.assertTrue(not match("foo > bar > bar > baz", "foo bar baz bar baz"));
        
        self.assertTrue( match("baz $", "foo bar baz bar baz"));
        self.assertTrue( match("bar > baz $", "foo bar baz bar baz"));
        self.assertTrue( match("bar > baz $", "foo bar baz bar baz"));
        self.assertTrue( match("foo bar > baz $", "foo bar baz bar baz"));
        self.assertTrue( match("foo > bar > baz", "foo bar baz bar baz"));
        self.assertTrue(not match("foo > bar > baz $", "foo bar baz bar baz"));
        self.assertTrue(not match("bar $", "foo bar baz bar baz"));
        
        self.assertTrue( match("baz $", "foo bar baz bar baz dyn.qux"));
        self.assertTrue( match("bar > baz $", "foo bar baz bar baz dyn.qux"));
        self.assertTrue( match("bar > baz $", "foo bar baz bar baz dyn.qux"));
        self.assertTrue( match("foo bar > baz $", "foo bar baz bar baz dyn.qux"));
        self.assertTrue(not match("foo > bar > baz $", "foo bar baz bar baz dyn.qux"));
        self.assertTrue(not match("bar $", "foo bar baz bar baz dyn.qux"));
        
        self.assertTrue( match("^ foo", "foo bar foo bar baz"));
        self.assertTrue( match("^ foo > bar", "foo bar foo bar baz"));
        self.assertTrue( match("^ foo bar > baz", "foo bar foo bar baz"));
        self.assertTrue( match("^ foo > bar baz", "foo bar foo bar baz"));
        self.assertTrue(not match("^ foo > bar > baz", "foo bar foo bar baz"));
        self.assertTrue(not match("^ bar", "foo bar foo bar baz"));
        
        self.assertTrue( match("foo > bar > baz", "foo bar baz foo bar baz"));
        self.assertTrue( match("^ foo > bar > baz", "foo bar baz foo bar baz"));
        self.assertTrue( match("foo > bar > baz $", "foo bar baz foo bar baz"));
        self.assertTrue(not match("^ foo > bar > baz $", "foo bar baz foo bar baz"));

    def test_context(self):
        selector = Selector("source & ((L:punctuation.section.*.begin & R:punctuation.section.*.end) | (L:punctuation.definition.*.begin & R:punctuation.definition.*.end)) - string")
        rank = []
        self.assertTrue(selector.does_match(Context(
            Scope("source.python punctuation.definition.list.begin.python"),
            Scope("source.python punctuation.definition.list.end.python")), rank))
    
    def test_attributes(self):
        scope = Scope("foo bar")
        attributes(scope, "/home/diego/Workspace/Prymatex/prymatex/setup.py")
    
    def test_xml_difference(self):
        s1 = Scope("html head title")
        s2 = Scope("html body h1")
        s3 = Scope("html body p")
        html = xml_difference(Scope(), s1) + "Title" + \
            xml_difference(s1, s2) + "Header" + \
            xml_difference(s2, s3) + "Paragraph" + \
            xml_difference(s3, Scope())
        self.assertEqual(html, 
            "<html><head><title>Title</title></head><body><h1>Header</h1><p>Paragraph</p></body></html>")
        
if __name__ == '__main__':
    unittest.main()
