from abc import ABC, abstractmethod
from itertools import chain
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor


grammar = Grammar(
    r"""
    aaa_prog        = multi_lines maybe_line eof
    multi_line      = line eol
    multi_lines     = multi_line*
    maybe_line      = line?
    arr_assign      = var space* "(" space* exp space* ")" space*
                      "=" space* exp
    array_ref_exp   = var space* "(" space* exp space* ")"
    comment         = comment_token comment_text
    line            = linenum space* statements space*
    line_or_stmnts  = linenum
                    / statements
    line_or_stmnts2 = linenum
                    / statements_else
    simple_assign   = var space* "=" space* exp
    statement       = ("IF" space* exp space*
                       "THEN" space* line_or_stmnts2 space*
                       "ELSE" space* line_or_stmnts)
                    / ("IF" space* exp space*
                       "THEN" space* line_or_stmnts)
                    / simple_assign
                    / arr_assign
    statements      = (statement? (comment/((":"/space)+
                                            (comment / statements)))* space*)
    statements_else = (statement? (space* ":" statements)* space*)
    exp             = logic_exp
    logic_exp       = gtle_exp space* (("AND" / "OR") space* gtle_exp space*)*
    gtle_exp        = sum_exp space* (("=" / "<>" / "<" / ">") space* sum_exp space*)*
    sum_exp         = prod_exp space* (("+" / "-" / "&") space*
                                       prod_exp space*)*
    prod_exp        = val_exp space* (("*" / "/") space* val_exp space*)*
    val_exp         = literal
                    / paren_exp
                    / (un_op space* exp)
                    / array_ref_exp
                    / var
                    / exp
    paren_exp       =  ("(" space* exp space* ")")
    comment_text    = ~r"[^:\r\n$]*"
    comment_token   = ~r"(REM|')"
    eof             = ~r"$"
    eol             = ~r"[\n\r]+"
    linenum         = ~r"[0-9]+"
    literal         = num_literal / str_literal
    num_literal     = ~r"([\+\-\s]*(\d*\.\d*)(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d*\.\d*)|[\+\-\s]*(\d+(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d+)"
    space           = ~r" "
    str_literal     = ~r'\"[^"\n]*\"'
    un_op           = "+" / "-" / "NOT"
    var             = ~r"(?!ELSE|IF|FOR|NOT)([A-Z][A-Z0-9]*)\$?"
    """  # noqa
)


class AbstractBasicConstruct(ABC):
    def indent_spaces(self, indent_level):
        return '    ' * indent_level

    @abstractmethod
    def basic09_text(self, indent_level):
        """Return the Basic09 text that represents this construct"""


class AbstractBasicExpression(AbstractBasicConstruct):
    pass


class AbstractBasicStatement(AbstractBasicConstruct):
    pass


class BasicAssignment(AbstractBasicStatement):
    def __init__(self, var, exp):
        self._var = var
        self._exp = exp

    def basic09_text(self, indent_level):
        return f'{self._var.basic09_text(indent_level)} = ' \
               f'{self._exp.basic09_text(indent_level)}'


class BasicBinaryExp(AbstractBasicExpression):
    def __init__(self, exp1, op, exp2):
        self._exp1 = exp1
        self._op = op
        self._exp2 = exp2

    def basic09_text(self, indent_level):
        return (f'{self._exp1.basic09_text(indent_level)} {self._op} '
                f'{self._exp2.basic09_text(indent_level)}')


class BasicComment(AbstractBasicConstruct):
    def __init__(self, comment):
        self._comment = comment

    def basic09_text(self, indent_level):
        return f'(*{self._comment} *)'


class BasicIf(AbstractBasicStatement):
    def __init__(self, exp, statements):
        self._exp = exp
        self._statements = statements

    def basic09_text(self, indent_level):
        return f'IF {self._exp.basic09_text(indent_level)} ' \
               f'THEN {self._statements.basic09_text(indent_level)}'


class BasicGoto(AbstractBasicStatement):
    def __init__(self, linenum, implicit):
        self._linenum = linenum
        self._implicit = implicit

    def basic09_text(self, indent_level):
        return f'{self._linenum}' if self._implicit \
               else f'GOTO {self._linenum}'


class BasicLine(AbstractBasicConstruct):
    def __init__(self, num, statements):
        self._num = num
        self._statements = statements

    def basic09_text(self, indent_level):
        return f'{str(self._num)} ' \
               f'{self._statements.basic09_text(indent_level)}'


class BasicLiteral(AbstractBasicExpression):
    def __init__(self, literal):
        self._literal = literal

    def basic09_text(self, indent_level):
        return (f'"{self._literal}"' if type(self._literal) is str
                else f'{self._literal}')


class BasicOperator(AbstractBasicConstruct):
    def __init__(self, operator):
        self._operator = operator

    def basic09_text(self, indent_level):
        return self._operator


class BasicOpExp(AbstractBasicConstruct):
    def __init__(self, operator, exp):
        self._operator = operator
        self._exp = exp

    @property
    def operator(self):
        return self._operator

    @property
    def exp(self):
        return self._exp

    def basic09_text(self, indent_level):
        return f'{self.operator} {self.exp.basic09_text(indent_level)}'


class BasicParenExp(AbstractBasicExpression):
    def __init__(self, exp):
        self._exp = exp

    def basic09_text(self, indent_level):
        return f'({self._exp.basic09_text(indent_level)})'


class BasicProg(AbstractBasicConstruct):
    def __init__(self, lines):
        self._lines = lines

    def basic09_text(self, indent_level):
        retval = '\n'.join(line.basic09_text(indent_level)
                           for line in self._lines)
        return retval


class BasicStatement(AbstractBasicStatement):
    def __init__(self, basic_construct):
        self._basic_construct = basic_construct

    def basic09_text(self, indent_level):
        return self.indent_spaces(indent_level) + \
               self._basic_construct.basic09_text(indent_level)


class BasicStatements(AbstractBasicConstruct):
    def __init__(self, statements):
        self._statements = statements

    def statements(self):
        return self._statements

    def basic09_text(self, indent_level):
        indent = '\n' + self.indent_spaces(indent_level)
        return indent.join(statement.basic09_text(indent_level)
                           for statement in self._statements)


class BasicVar(AbstractBasicExpression):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def basic09_text(self, indent_level):
        return self._name


class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        if node.text.strip() == '':
            return ''

        if node.text in ['*', '/', '+', '-', '*', '&', '<', '>', '<>', '=',
                         'AND', 'OR']:
            return BasicOperator(node.text)

        if len(visited_children) == 7:
            _, _, exp, _, _, _, statements = visited_children
            return BasicIf(exp, statements)

        if len(visited_children) == 4:
            operator, _, exp, _ = visited_children
            return BasicOpExp(operator.basic09_text(0), exp)

        if len(visited_children) == 1:
            if isinstance(visited_children[0], AbstractBasicConstruct):
                return visited_children[0]

            if visited_children[0] is str:
                return visited_children[0]

        if len(visited_children) == 2:
            if isinstance(visited_children[0], BasicOpExp) and \
               isinstance(visited_children[1], BasicOpExp):
                exp1, exp2 = visited_children
                return BasicOpExp(exp1.operator,
                                  BasicBinaryExp(exp1.exp,
                                                 exp2.operator, exp2.exp))
            if isinstance(visited_children[0], Node) and \
               visited_children[0].text == ':':
                print(f'zzzzz {visited_children[1]}')
                return visited_children[1]

        print('--------------------- ****')
        for child in visited_children:
            print(f'xxxx {child}')
        print('---------------------')

        return node

    def visit_aaa_prog(self, node, visited_children):
        bp = BasicProg(chain(visited_children[0], visited_children[1]))
        return bp

    def visit_multi_line(self, node, visited_children):
        return next(child for child in visited_children
                    if isinstance(child, BasicLine))

    def visit_multi_lines(self, node, visited_children):
        return (child for child in visited_children
                if isinstance(child, BasicLine))

    def visit_maybe_line(self, node, visited_children):
        return (child for child in visited_children
                if isinstance(child, BasicLine))

    def visit_comment(self, node, visited_children):
        return BasicComment(visited_children[1])

    def visit_comment_text(self, node, visited_children):
        return node.full_text[node.start:node.end]

    def visit_gtle_exp(self, node, visited_children):
        return self.visit_prod_exp(node, visited_children)

    def visit_line(self, node, visited_children):
        return BasicLine(visited_children[0],
                         next(child for child in visited_children
                              if isinstance(child, BasicStatements)))

    def visit_linenum(self, node, visited_children):
        return int(node.full_text[node.start:node.end])

    def visit_line_or_stmnts(self, node, visited_children):
        if isinstance(visited_children[0], int):
            return BasicGoto(visited_children[0], True)
        return visited_children[0]

    def visit_literal(self, node, visited_children):
        return visited_children[0]

    def visit_logic_exp(self, node, visited_children):
        return self.visit_prod_exp(node, visited_children)

    def visit_num_literal(self, node, visited_children):
        num_literal = node.full_text[node.start:node.end].replace(' ', '')
        val = float(num_literal)
        return BasicLiteral(int(val) if val == int(val) else val)

    def visit_paren_exp(self, node, visited_children):
        return BasicParenExp(visited_children[2])

    def visit_prod_exp(self, node, visited_children):
        if len(visited_children) < 4:
            v1, v2, v3 = visited_children
            if isinstance(v2, str) and isinstance(v3, str):
                return visited_children[0]
            if isinstance(v2, str) and isinstance(v3, str):
                return visited_children[0]
            return BasicBinaryExp(v1, v3.operator, v3.exp)
        return node

    def visit_simple_assign(self, node, visited_children):
        return BasicAssignment(visited_children[0], visited_children[4])

    def visit_space(self, node, visited_children):
        return node.text

    def visit_statement(self, node, visited_children):
        for child in visited_children:
            print(f'gggggg {child}')
        return BasicStatement(next(child for child in visited_children
                              if isinstance(child, AbstractBasicStatement)))

    def visit_statements(self, node, visited_children):
        return BasicStatements([child for child in visited_children
                               if isinstance(child, BasicStatement)
                               or isinstance(child, BasicStatements)
                               or isinstance(child, BasicComment)])

    def visit_str_literal(self, node, visited_children):
        return BasicLiteral(str(node.full_text[node.start+1:node.end-1]))

    def visit_sum_exp(self, node, visited_children):
        return self.visit_prod_exp(node, visited_children)

    def visit_val_exp(self, node, visited_children):
        if len(visited_children) < 2:
            return visited_children[0]
        return node

    def visit_var(self, node, visited_children):
        return BasicVar(node.full_text[node.start:node.end])
