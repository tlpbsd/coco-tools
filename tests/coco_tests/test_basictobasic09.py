import unittest
import pkg_resources

import coco.basictobasic09 as b09


class TestBasicToBasic09(unittest.TestCase):
    def get_resource(name):
        resource_path = pkg_resources.resource_filename(
            __name__, f'fixtures/{name}'
        )
        with open(resource_path, 'r') as resource_file:
            return resource_file.read()

    simple_prog = get_resource('simple.bas')
    simple2_prog = get_resource('simple2.bas')
    simple3_prog = get_resource('simple3.bas')

    def test_something(self):
        tree = b09.grammar.parse(self.simple_prog)
        bv = b09.BasicVisitor()
        bv.visit(tree)

    def test_statements(self):
        tree = b09.grammar.parse(self.simple2_prog)
        bv = b09.BasicVisitor()
        bv.visit(tree)

    def test_crap(self):
        tree = b09.grammar.parse(self.simple3_prog)
        bv = b09.BasicVisitor()
        bv.visit(tree)
        error
