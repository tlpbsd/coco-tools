from abc import ABC, abstractmethod
from itertools import chain
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


XXX = """
    statements      = (statement? (comment/((":"/space)+
                                            (comment / statements)))* space*)
"""

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
                    / comment
    statements      = space* statement space*
    statements_else = (statement? (space* ":" statements)* space*)
    exp             = logic_exp
    logic_exp       = gte_exp space* (("AND" / "OR") space* gte_exp space*)*
    gte_exp         = sum_exp space* (("=" / "<" / "=") space* sum_exp space*)*
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
    @abstractmethod
    def basic09_text(self):
        """Return Basic09 text that represents this construct"""


class AbstractBasicExpression(AbstractBasicConstruct):
    pass


class BasicAssignment(AbstractBasicConstruct):
    def __init__(self, var, exp):
        self._var = var
        self._exp = exp

    def basic09_text(self):
        return f'{self._var.basic09_text()} = {self._exp.basic09_text()}'


class BasicBinaryExp(AbstractBasicExpression):
    def __init__(self, exp1, op, exp2):
        self._exp1 = exp1
        self._op = op
        self._exp2 = exp2

    def basic09_text(self):
        return (f'{self._exp1.basic09_text()} {self._op} '
                f'{self._exp2.basic09_text()}')


class BasicComment(AbstractBasicConstruct):
    def __init__(self, comment):
        self._comment = comment

    def basic09_text(self):
        return f'(*{self._comment} *)'


class BasicLine(AbstractBasicConstruct):
    def __init__(self, num, statements):
        self._num = num
        self._statements = statements

    def basic09_text(self):
        return f'{str(self._num)} {self._statements.basic09_text()}'


class BasicLiteral(AbstractBasicExpression):
    def __init__(self, literal):
        self._literal = literal

    def basic09_text(self):
        return (f'"{self._literal}"' if type(self._literal) is str
                else f'{self._literal}')


class BasicOperator(AbstractBasicConstruct):
    def __init__(self, operator):
        self._operator = operator

    def basic09_text(self):
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

    def basic09_text(self):
        return f'{self.operator} {self.exp.basic09_text()}'


class BasicParenExp(AbstractBasicExpression):
    def __init__(self, exp):
        self._exp = exp

    def basic09_text(self):
        return f'({self._exp.basic09_text()})'


class BasicProg(AbstractBasicConstruct):
    def __init__(self, lines):
        self._lines = lines

    def basic09_text(self):
        retval = '\n'.join(line.basic09_text() for line in self._lines)
        return retval


class BasicStatement(AbstractBasicConstruct):
    def __init__(self, basic_construct):
        self._basic_construct = basic_construct

    def basic09_text(self):
        return self._basic_construct.basic09_text()


class BasicStatements(AbstractBasicConstruct):
    def __init__(self, statements):
        self._statements = statements

    def statements(self):
        return self._statements

    def basic09_text(self):
        return ':'.join(statement.basic09_text()
                        for statement in self._statements)


class BasicVar(AbstractBasicExpression):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def basic09_text(self):
        return self._name


class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        if node.text.strip() == '':
            return ''

        if node.text in ['*', '/', '+', '-', '*', '&', 'AND', 'OR']:
            return BasicOperator(node.text)

        if len(visited_children) == 4:
            operator, _, exp, _ = visited_children
            return BasicOpExp(operator.basic09_text(), exp)

        if len(visited_children) == 1:
            if isinstance(visited_children[0], AbstractBasicConstruct):
                return visited_children[0]

            if visited_children[0] is str:
                return visited_children[0]

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

    def visit_gte_exp(self, node, visited_children):
        if len(visited_children) < 4:
            return visited_children[0]
        return node

    def visit_line(self, node, visited_children):
        return BasicLine(visited_children[0],
                         next(child for child in visited_children
                              if isinstance(child, BasicStatements)))

    def visit_linenum(self, node, visited_children):
        return int(node.full_text[node.start:node.end])

    def visit_literal(self, node, visited_children):
        return visited_children[0]

    def visit_logic_exp(self, node, visited_children):
        if len(visited_children) < 4:
            return visited_children[0]
        return node

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
        return BasicStatement(next(child for child in visited_children
                              if isinstance(child, BasicComment)
                              or isinstance(child, BasicAssignment)))

    def visit_statements(self, node, visited_children):
        return BasicStatements([child for child in visited_children
                               if isinstance(child, BasicStatement)])

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
