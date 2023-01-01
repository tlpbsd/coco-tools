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

    def test_basic_int_literal(self):
        target = b09.BasicLiteral(123)
        assert target.basic09_text() == '123'

    def test_basic_float_literal(self):
        target = b09.BasicLiteral(123.0)
        assert target.basic09_text() == '123.0'

    def test_basic_str_literal(self):
        target = b09.BasicLiteral('123.0')
        assert target.basic09_text() == '"123.0"'

    def test_basic_paren_exp(self):
        strlit = b09.BasicLiteral('HELLO WORLD')
        target = b09.BasicParenExp(strlit)
        assert target.basic09_text() == '("HELLO WORLD")'

    def test_basic_op_exp(exp):
        strlit = b09.BasicLiteral('HELLO WORLD')
        target = b09.BasicOpExp('&', strlit)
        assert target.operator == '&'
        assert target.exp == strlit
        assert target.basic09_text() == '& "HELLO WORLD"'

    def test_parse_comment_program(self):
        tree = b09.grammar.parse('15 REM HELLO WORLD\n')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '15 (* HELLO WORLD *)'

    def test_parse_comments_program(self):
        tree = b09.grammar.parse('15 REM HELLO WORLD\n20 REM HERE')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '15 (* HELLO WORLD *)\n20 (* HERE *)'

    def test_parse_simple_assignment(self):
        tree = b09.grammar.parse('10 A = 123\n20 B=123.4\n30C$="HELLO"')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '10 A = 123\n20 B = 123.4\n30 C$ = "HELLO"'

    def test_parse_paren_expression(self):
        tree = b09.grammar.parse('10 A = (AB)')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '10 A = (AB)'

    def test_parse_prod_expression(self):
        tree = b09.grammar.parse('10 A = 64 * 32\n20 B = 10/AB')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '10 A = 64 * 32\n20 B = 10 / AB'

    def test_parse_add_expression(self):
        tree = b09.grammar.parse('10 A = 64 + 32\n20 B = 10-AB')
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text()
        assert b09_prog == '10 A = 64 + 32\n20 B = 10 - AB'
