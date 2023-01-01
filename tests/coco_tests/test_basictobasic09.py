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
        assert target.basic09_text(1) == '(* hello world  *)'

    def test_comment_statement(self):
        comment = b09.BasicComment(' hello world ')
        target = b09.BasicStatement(comment)
        assert target.basic09_text(2) == '        (* hello world  *)'

    def test_comment_statements(self):
        comment = b09.BasicComment(' hello world ')
        statement = b09.BasicStatement(comment)
        target = b09.BasicStatements((statement,))
        assert target.basic09_text(2) == '        (* hello world  *)'

    def test_comment_lines(self):
        comment = b09.BasicComment(' hello world ')
        statement = b09.BasicStatement(comment)
        statements = b09.BasicStatements((statement,))
        target = b09.BasicLine(25, statements)
        assert target.basic09_text(1) == '25     (* hello world  *)'

    def test_basic_int_literal(self):
        target = b09.BasicLiteral(123)
        assert target.basic09_text(2) == '123'

    def test_basic_float_literal(self):
        target = b09.BasicLiteral(123.0)
        assert target.basic09_text(2) == '123.0'

    def test_basic_str_literal(self):
        target = b09.BasicLiteral('123.0')
        assert target.basic09_text(1) == '"123.0"'

    def test_basic_paren_exp(self):
        strlit = b09.BasicLiteral('HELLO WORLD')
        target = b09.BasicParenExp(strlit)
        assert target.basic09_text(2) == '("HELLO WORLD")'

    def test_basic_op_exp(exp):
        strlit = b09.BasicLiteral('HELLO WORLD')
        target = b09.BasicOpExp('&', strlit)
        assert target.operator == '&'
        assert target.exp == strlit
        assert target.basic09_text(1) == '& "HELLO WORLD"'

    def test_basic_operator(exp):
        target = b09.BasicOperator('*')
        assert target.basic09_text(2) == '*'

    def generic_test_parse(self, progin, progout):
        tree = b09.grammar.parse(progin)
        bv = b09.BasicVisitor()
        basic_prog = bv.visit(tree)
        b09_prog = basic_prog.basic09_text(0)
        assert b09_prog == progout

    def test_parse_comment_program(self):
        self.generic_test_parse(
            '15 REM HELLO WORLD\n',
            '15 (* HELLO WORLD *)')

    def test_parse_comments_program(self):
        self.generic_test_parse(
            '15 REM HELLO WORLD\n20 REM HERE',
            '15 (* HELLO WORLD *)\n20 (* HERE *)')

    def test_parse_simple_assignment(self):
        self.generic_test_parse(
            '10 A = 123\n20 B=123.4\n30C$="HELLO"\n35D$=C$',
            '10 A = 123\n20 B = 123.4\n30 C$ = "HELLO"\n35 D$ = C$')

    def test_parse_paren_expression(self):
        self.generic_test_parse(
            '10 A = (AB)',
            '10 A = (AB)')

    def test_parse_prod_expression(self):
        self.generic_test_parse(
            '10 A = 64 * 32\n20 B = 10/AB',
            '10 A = 64 * 32\n20 B = 10 / AB')

    def test_parse_add_expression(self):
        self.generic_test_parse(
            '10 A = 64 + 32\n20 B = 10-AB',
            '10 A = 64 + 32\n20 B = 10 - AB')

    def test_parse_str_expression(self):
        self.generic_test_parse(
            '10 A$ = "A" & "Z"\n20B$=A$&B$',
            '10 A$ = "A" & "Z"\n20 B$ = A$ & B$')

    def test_parse_multi_expression(self):
        self.generic_test_parse(
            '10 A = 64 + 32*10 / AB -1',
            '10 A = 64 + 32 * 10 / AB - 1')

    def test_parse_gtle_expression(self):
        self.generic_test_parse(
            '10 A = 4 < 2\n15 B=4>2\n20C=A<>B',
            '10 A = 4 < 2\n15 B = 4 > 2\n20 C = A <> B')

    def test_parse_multi_expression2(self):
        self.generic_test_parse(
            '10 A=(64+32)*10/(AB-1)',
            '10 A = (64 + 32) * 10 / (AB - 1)')

    def test_parse_multi_expression3(self):
        self.generic_test_parse(
            '10 A = A + 2 AND 3 < 3',
            '10 A = A + 2 AND 3 < 3')

    def test_parse_multi_statement(self):
        self.generic_test_parse(
            '10 A=A+2:B=B+1',
            '10 A = A + 2: B = B + 1')
