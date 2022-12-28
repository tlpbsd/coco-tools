from abc import ABC, abstractmethod
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(
    r"""
    comment         = comment_token comment_text
    line            = linenum space* comment space*
    linenum_or_statements   = (linenum / statements)
    if_statement    = if_token space* expression space* 
                      then_token space* linenum_or_statements
    if_else_statement    = if_token space* expression
                           space* then_token space* linenum_or_statements
                           space* else_token space* linenum_or_statements
    expression      = literal / var
                    / ((not_token space*)? expression space* op space* expression)
                    / (open_paren_token space* expression space* close_paren_token)
    prog            = (line eol)* line eol*
    statement       = ~r"[^:\r\n]*"
    statements      = statement (space* colon+ statement?)* comment?

    close_paren_token   = ~r"\)"
    colon           = ":"
    comment_text    = ~r"[^:\r\n$]*"
    comment_token   = ~r"(REM|')"
    else_token      = "ELSE"
    eol             = ~r"[\n\r]+"
    eof             = ~r"$"
    if_token        = "IF"
    linenum         = ~r"[0-9]+"
    num_literal     = ~r"[\+\-]?\s+[0-9]*.?[0-9]*(E[\+\-)(0-9)+)?"
    open_paren_token    = ~r"\("
    space           = ~r"\s"
    then_token      = "THEN"
    var             = ~r"\$?[A-Z][A-Z0-9]*"
    """
)


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
