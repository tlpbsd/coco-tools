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
    val_exp         = literal
                    / ("(" space* exp space* ")")
                    / (un_op space* exp)
                    / array_ref_exp
                    / var
    exp             = (val_exp space* bin_op space* exp)
                    / val_exp

    bin_op          = "+" / "-" / "*" / "/" / "&" / "AND" / "OR" / "="
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


FOO = """
    if_statement    = "IF" space* exp space* 
                      "THEN" space* linenum_or_statements
    if_else_statement    = "IF" space* exp
                           space* "THEN" space* linenum_or_statements
                           space* "ELSE" space* linenum_or_statements
    exp             = array_ref_exp
                    / binop_exp
                    / literal
                    / var
                    / "(" space* exp space* ")"
"""


class AbstractBasicConstruct(ABC):
    @abstractmethod
    def basic09_text(self):
        """Return Basic09 text that represents this construct"""


class BasicProg(AbstractBasicConstruct):
    def __init__(self, lines):
        self._lines = lines


    def basic09_text(self):
        retval = '\n'.join((line.basic09_text() for line in self._lines))
        print(retval)
        error
        return retval



class BasicLine(AbstractBasicConstruct):
    def __init__(self, num, statements):
        self._num = num
        self._statements = statements

    
    def basic09_text(self):
        return f'{str(self._num)} {self._statements.basic09_text()}'


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


class BasicComment(AbstractBasicConstruct):
    def __init__(self, comment):
        self._comment = comment


    def basic09_text(self):
        return f'(*{self._comment} *)'



class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        print(node)
        return node


    def visit_prog(self, node, visited_children):
        bp = BasicProg((child for child in visited_children if isinstance(child, BasicLine)))
        print(bp.basic09_text())
        return bp


    def visit_line(self, node, visited_children):
        return BasicLine(visited_children[0], visited_children[2])

    
    def visit_statements(self, node, visited_children):
        return BasicStatements((child for child in visited_children if isinstance(child, BasicStatement)))


    def visit_comment(self, node, visited_children):
        return BasicComment(visited_children[1])


    def visit_comment_text(self, node, visited_children):
        return node.full_text[node.start:node.end]


    def visit_statement(self, node, visited_children):
        return BasicStatement(node.full_text[node.start:node.end])


    def visit_linenum(self, node, visited_children):
        return int(node.full_text[node.start:node.end])
