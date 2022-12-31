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

    def test_comment(self):
        target = b09.BasicComment(' hello world ')
        assert target.basic09_text() == '(* hello world  *)'

    def test_comment_statement(self):
        comment = b09.BasicComment(' hello world ')
        target = b09.BasicStatement(comment)
        assert target.basic09_text() == '(* hello world  *)'

    def test_comment_statements(self):
        comment = b09.BasicComment(' hello world ')
        statement = b09.BasicStatement(comment)
        target = b09.BasicStatements((statement,))
        assert target.basic09_text() == '(* hello world  *)'

    def test_comment_lines(self):
        comment = b09.BasicComment(' hello world ')
        statement = b09.BasicStatement(comment)
        statements = b09.BasicStatements((statement,))
        target = b09.BasicLine(25, statements)
        assert target.basic09_text() == '25 (* hello world  *)'

    def test_parse_comment_program(self):
        tree = b09.grammar.parse('15 REM HELLO WORLD')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        print(basic_prog)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '15 (* HELLO WORLD *)'
