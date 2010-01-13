# -*- coding: utf-8
import unittest
import textparser
import bbparser
import clean

class RenderTestCase(unittest.TestCase):

    def testTextToHtml(self):
        self.assertEqual('', textparser.to_html(''))
        self.assertEqual('foo bar', textparser.to_html('foo bar'))
        self.assertEqual('foo\n<br/>bar', textparser.to_html('foo\nbar'))
        self.assertEqual('\n<br/>bar', textparser.to_html('\nbar'))
        self.assertEqual('foo\n<br/>&lt;x&gt;', textparser.to_html('foo\n<x>'))
        self.assertEqual(u'фыва\n<br/>', textparser.to_html(u'фыва\n'))

    def testBbcodeToHtml(self):
        self.assertEqual('', bbparser.to_html(''))
        self.assertEqual('<div>foo bar</div>', bbparser.to_html('foo bar'))
        self.assertEqual('<div>a<br/>b</div>', bbparser.to_html('a\nb'))
        self.assertEqual('<div>&lt;test&gt;</div>', bbparser.to_html('<test>'))

    def testNormalizeHtml(self):
        self.assertEqual('<strong>test</strong>\n', clean.normalize_html('<strong>test'))

    def testGetSafeHtml(self):
        self.assertEqual(
            '<div><a href="href">a</a> <b>b</b> <img src="src" /></div>',
            clean.get_safe_html('<div><a href="href">a</a> <b style="test">b</b> <img src="src" id="asdf"/>').strip())
