from abc import ABC, abstractmethod
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(
    r"""
    aaa_prog        = ((line eol) / line)*
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
    statements      = comment
                    / (statement? (comment/((":"/space)+ (comment / statements)))* space*)
    statements_else = (statement? (space* ":" statements)* space*)
    exp             = logic_exp
    logic_exp       = gte_exp space* (("AND" / "OR") space* gte_exp space*)*
    gte_exp         = sum_exp space* (("=" / "<" / "=") space* sum_exp space*)*
    sum_exp         = prod_exp space* (("+" / "-" / "&") space* prod_exp space*)*
    prod_exp        = val_exp space* (("*" / "/") space* val_exp space*)*
    val_exp         = literal
                    / ("(" space* exp space* ")")
                    / (un_op space* exp)
                    / array_ref_exp
                    / var
    comment_text    = ~r"[^:\r\n$]*"
    comment_token   = ~r"(REM|')"
    eol             = ~r"(\n|\r)+"
    eof             = ~r"$"
    linenum         = ~r"[0-9]+"
    literal         = num_literal / str_literal
    num_literal     = ~r"([\+\-\s]*(\d*\.\d*)(\s*(?!ELSE)E\s*[\+\-]?\s*[0-9]*))|[\+\-\s]*(\d*\.\d*)|[\+\-\s]*(\d+(\s*(?!ELSE)E\s*[\+\-]?\s*[0-9]*))|[\+\-\s]*(\d+)"
    space           = ~r"\s"
    str_literal     = ~r'\"[^"\n]*\"'
    un_op           = "+" / "-" / "NOT"
    var             = ~r"\$?(?!ELSE|IF|FOR|NOT)([A-Z][A-Z0-9]*)"
    """
)


class AbstractBasicConstruct(ABC):
    @abstractmethod
    def basic09_text(self):
        """Return Basic09 text that represents this construct"""


class BasicBinaryExp(AbstractBasicConstruct):
    def __init__(self, exp1, op, exp2):
        self._exp1 = exp1
        self._op = op
        self._exp2 = exp2

    def basic09_text(self):
        return f'({self._exp1.basic09_text()} {self._op} self._exp2.basic09_text())'


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


class BasicLiteral(AbstractBasicConstruct):
    def __init__(self, literal):
        self._literal = literal
    
    def basic09_text(self):
        return f'"{self._literal}"' if type(self._literal) is str else f'{self._literal}'
        return f'{str(self._num)} {self._statements.basic09_text()}'


class BasicProg(AbstractBasicConstruct):
    def __init__(self, lines):
        self._lines = lines

    def basic09_text(self):
        retval = '\n'.join((line.basic09_text() for line in self._lines))
        return retval


class BasicStatement(AbstractBasicConstruct):
    def __init__(self, text):
        self._text = text

    def basic09_text(self):
        return self._text


class BasicStatements(AbstractBasicConstruct):
    def __init__(self, statements):
        self._statements = statements

    def statements(self):
        return self._statements

    def basic09_text(self):
        return ':'.join((statement.basic09_text() for statement in self._statements))


class BasicVar(AbstractBasicConstruct):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def basic09_text(self):
        return name


class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        return node

    def visit_aaa_prog(self, node, visited_children):
        bp = BasicProg((child for child in visited_children if isinstance(child, BasicLine)))
        print(bp.basic09_text())
        return bp

    def visit_comment(self, node, visited_children):
        return BasicComment(visited_children[1])

    def visit_comment_text(self, node, visited_children):
        return node.full_text[node.start:node.end]

    def visit_gte_exp(self, node, visited_children):
        if len(visited_children) == 1:
            return visited_children[0]
        return 0

    def visit_line(self, node, visited_children):
        return BasicLine(visited_children[0], visited_children[2])

    def visit_linenum(self, node, visited_children):
        return int(node.full_text[node.start:node.end])

    def visit_logic_exp(self, node, visited_children):
        if len(visited_children) == 1:
            return visited_children[0]
        print('LOGIC EXP')
        for child in visited_children:
            print(f'xxx{child}')
        return 0

    def visit_num_literal(self, node, visited_children):
        return BasicLiteral(float(node.full_text[node.start:node.end].replace(' ', '')))

    def visit_prod_exp(self, node, visited_children):
        return node

    def visit_simple_assignment(self, node, visitied_children):
        var, exp, *_ = node
        return (var, exp)

    def visit_statement(self, node, visited_children):
        return BasicStatement(node.full_text[node.start:node.end])

    def visit_statements(self, node, visited_children):
        return BasicStatements((child for child in visited_children if isinstance(child, BasicStatement)))

    def visit_str_literal(self, node, visited_children):
        return BasicLiteral(str(node.full_text[node.start:node.end]))

    def visit_sum_exp(self, node, visited_children):
        return node

    def visit_val_exp(self, node, visited_children):
        """
        exp             = logic_exp
        logic_exp       = gte_exp space* (("AND" / "OR") space* gte_exp space*)*
        gte_exp         = sum_exp space* (("=" / "<" / "=") space* sum_exp space*)*
        sum_exp         = prod_exp space* (("+" / "-" / "&") space* prod_exp space*)*
        prod_exp        = val_exp space* (("*" / "/") space* val_exp space*)*
        val_exp         = literal
                        / ("(" space* exp space* ")")
                        / (un_op space* exp)
                        / array_ref_exp
                        / var
        """
        if len(visited_children) == 1:
            return visited_children[0]
        print('VAL EXP')
        for child in node:
            print(f'zzz{child}')
        for child in visited_children:
            print(f'yyy{child}')
        return node

    def visit_var(self, node, visited_children):
        return BasicVar(node.full_text[node.start:node.end])

