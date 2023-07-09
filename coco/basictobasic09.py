from abc import ABC, abstractmethod
from itertools import chain, islice
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

grammar = Grammar(
    r"""
    aaa_prog        = multi_lines maybe_line eof
    multi_line      = line eol
    multi_lines     = multi_line*
    maybe_line      = line?
    array_ref_exp   = var space* exp_list
    arr_assign      = array_ref_exp space* "=" space* exp
    str_array_ref_exp   = str_var space* exp_list
    str_arr_assign  = str_array_ref_exp space* "=" space* str_exp
    comment         = comment_token comment_text
    exp_list        = "(" space* exp space* exp_sublist ")"
    exp_sublist     = exp_sublist_mbr*
    exp_sublist_mbr = ("," space* exp space*)
    if_else_stmnt   = ("IF" space* if_exp space*
                       "THEN" space* line_or_stmnts2 space*
                       "ELSE" space* line_or_stmnts)
    if_stmnt        = ("IF" space* if_exp space*
                       "THEN" space* line_or_stmnts)
    line            = linenum space* statements space*
    line_or_stmnts  = linenum
                    / statements
    line_or_stmnts2 = linenum
                    / statements_else
    str_assign      = str_var space* "=" space* str_exp
    num_assign      = var space* "=" space* exp
    statement       = if_else_stmnt
                    / if_stmnt
                    / print_statement
                    / num_assign
                    / str_assign
                    / arr_assign
                    / str_arr_assign
    statements      = (statement? (comment/((":"/space)+
                                            (comment / statements)))* space*)
    statements_else = (statement? (space* ":" statements)* space*)
    exp             = num_exp
    if_exp          = bool_exp
                    / num_exp
    bool_exp        = bool_val_exp space* (("AND" / "OR") space* bool_val_exp space*)*
    bool_val_exp    = bool_paren_exp
                    / bool_unop_exp
                    / bool_bin_exp
    bool_paren_exp  = "(" space* bool_exp space* ")"
    bool_unop_exp   = "NOT" space* bool_paren_exp space*
    bool_bin_exp    = num_sum_exp space* ("<=" / ">=" / "<>" / "<" / ">" / "=>" / "=<" / "=") space* num_sum_exp space*
    num_exp         = num_gtle_exp space* (("AND" / "OR") space* num_gtle_exp space*)*
    num_gtle_exp    = num_sum_exp space* (("<=" / ">=" / "<>" / "<" / ">" / "=>" / "=<" / "=") space* num_sum_exp space*)*
    num_sum_exp     = num_prod_exp space* (("+" / "-" / "&") space*
                                           num_prod_exp space*)*
    num_prod_exp    = val_exp space* (("*" / "/") space* val_exp space*)*
    val_exp         = num_literal
                    / paren_exp
                    / (un_op space* exp)
                    / array_ref_exp
                    / var
    paren_exp       =  "(" space* exp space* ")" space*
    str_exp         = str_simple_exp space* (("+") space*
                                             str_simple_exp space*)* 
    str_simple_exp  = str_literal
                    / str_array_ref_exp
                    / str_var
    comment_text    = ~r"[^:\r\n$]*"
    comment_token   = ~r"(REM|')"
    eof             = ~r"$"
    eol             = ~r"[\n\r]+"
    linenum         = ~r"[0-9]+"
    literal         = num_literal
    num_literal     = ~r"([\+\-\s]*(\d*\.\d*)(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d*\.\d*)|[\+\-\s]*(\d+(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d+)"
    space           = ~r" "
    str_literal     = ~r'\"[^"\n]*\"'
    un_op           = "+" / "-" / "NOT"
    var             = ~r"(?!ELSE|IF|FOR|NOT|([A-Z][A-Z0-9]*\$))([A-Z][A-Z0-9]*)"
    str_var         = ~r"(?!ELSE|IF|FOR|NOT)([A-Z][A-Z0-9]*)\$"
    print_statement = ("PRINT"/"?") space* print_args
    print_args      = print_arg0*
    print_arg0      = print_arg1 space*
    print_arg1      = print_control 
                    / print_arg
    print_arg       = exp 
                    / str_exp
    print_control   = ~r"(;|,)"
    """  # noqa
)


class AbstractBasicConstruct(ABC):
    def indent_spaces(self, indent_level):
        return '    ' * indent_level

    @abstractmethod
    def basic09_text(self, indent_level):
        """Return the Basic09 text that represents this construct"""
    
    def is_expr(self):
        return False

    def is_str_expr(self):
        return False

class AbstractBasicExpression(AbstractBasicConstruct):
    def __init__(self, is_str_expr=False):
        self._is_str_expr = is_str_expr

    def is_expr(self):
        return True


class AbstractBasicStatement(AbstractBasicConstruct):
    pass


class BasicArrayRef(AbstractBasicExpression):
    def __init__(self, var, indices, is_str_expr=False):
        super().__init__(is_str_expr=is_str_expr)
        self._var = var
        self._indices = indices

    def basic09_text(self, indent_level):
        return f'{self._var.basic09_text(indent_level)}' \
               f'{self._indices.basic09_text(indent_level)}'


class BasicAssignment(AbstractBasicStatement):
    def __init__(self, var, exp):
        self._var = var
        self._exp = exp

    def basic09_text(self, indent_level):
        return f'{self._var.basic09_text(indent_level)} = ' \
               f'{self._exp.basic09_text(indent_level)}'


class BasicBinaryExp(AbstractBasicExpression):
    def __init__(self, exp1, op, exp2, is_str_expr=False):
        super().__init__(is_str_expr=True)
        self._exp1 = exp1
        self._op = op
        self._exp2 = exp2

    def basic09_text(self, indent_level):
        return (f'{self._exp1.basic09_text(indent_level)} {self._op} '
                f'{self._exp2.basic09_text(indent_level)}')


class BasicBooleanExp(BasicBinaryExp):
    def basic09_text(self, indent_level):
        return (f'{self._exp1.basic09_text(indent_level)} {self._op} '
                f'{self._exp2.basic09_text(indent_level)}')


class BasicComment(AbstractBasicConstruct):
    def __init__(self, comment):
        self._comment = comment

    def basic09_text(self, indent_level):
        return f'(*{self._comment} *)'


class BasicExpressionList(AbstractBasicStatement):
    def __init__(self, exp_list):
        self._exp_list = exp_list

    def basic09_text(self, indent_level):
        exp_list_text = ', '.join(exp.basic09_text(indent_level)
                                  for exp in self._exp_list)
        return f'({exp_list_text})'


class BasicGoto(AbstractBasicStatement):
    def __init__(self, linenum, implicit):
        self._linenum = linenum
        self._implicit = implicit

    @property
    def implicit(self):
        return self._implicit

    def basic09_text(self, indent_level):
        return f'{self.indent_spaces(indent_level)}{self._linenum}' \
            if self._implicit \
            else f'{self.indent_spaces(indent_level)}GOTO {self._linenum}'


class BasicIf(AbstractBasicStatement):
    def __init__(self, exp, statements):
        self._exp = exp
        self._statements = statements

    def basic09_text(self, indent_level):
        if (isinstance(self._statements, BasicGoto) and
                self._statements.implicit):
            return f'{self.indent_spaces(indent_level)}' \
                   f'IF {self._exp.basic09_text(indent_level)} ' \
                   f'THEN {self._statements.basic09_text(0)}'
        else:
            return f'{self.indent_spaces(indent_level)}' \
                   f'IF {self._exp.basic09_text(indent_level)} THEN\n' \
                   f'{self._statements.basic09_text(indent_level + 1)}\n' \
                   f'ENDIF'


class BasicLine(AbstractBasicConstruct):
    def __init__(self, num, statements):
        self._num = num
        self._statements = statements

    def basic09_text(self, indent_level):
        return f'{str(self._num)} ' \
               f'{self._statements.basic09_text(indent_level)}'


class BasicLiteral(AbstractBasicExpression):
    def __init__(self, literal, is_str_expr=False):
        super().__init__(is_str_expr=is_str_expr)
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
    def __init__(self, name, is_str_expr=False):
        super().__init__(is_str_expr=is_str_expr)
        self._name = name

    def name(self):
        return self._name

    def basic09_text(self, indent_level):
        return self._name

class BasicPrintStatement(AbstractBasicStatement):
    def __init__(self, print_args):
        self._print_args = print_args
    
    def basic09_text(self, indent_level):
        return self.indent_spaces(indent_level) + \
               f'PRINT {self._print_args.basic09_text(indent_level)}'

class BasicPrintControl(AbstractBasicConstruct):
    def __init__(self, control_char):
        self._control_char = control_char
    
    def basic09_text(self, indent_level):
        return self._control_char

class BasicPrintArgs(AbstractBasicConstruct):
    def __init__(self, args):
        self._args = args
    
    @property
    def args(self):
        return self._args

    def basic09_text(self, indent_level):
        processed_args = []

        for ii, arg in enumerate(self.args):
            is_control = isinstance(arg, BasicPrintControl)
            if is_control and \
               ((ii <= 0) or
                isinstance(self.args[ii - 1], BasicPrintControl)):
                processed_args.append('""')

            processed_args.append(arg.basic09_text(indent_level))
            if (ii < len(self.args) - 1) \
                and is_control:
                processed_args.append(' ')

        return ''.join(processed_args)

class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        if node.text.strip() == '':
            return ''

        if node.text in ['*', '/', '+', '-', '*', '&', '<', '>', '<>', '=',
                         '<=', '=<', '>=', '=>', 'AND', 'OR']:
            return BasicOperator(node.text)

        if len(visited_children) == 4:
            if isinstance(visited_children[0], BasicOperator):
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
                return visited_children[1]

        return node

    def visit_aaa_prog(self, node, visited_children):
        bp = BasicProg(chain(visited_children[0], visited_children[1]))
        return bp

    def visit_arr_assign(self, node, visited_children):
        array_ref_exp, _, _, _, val_exp = visited_children
        return BasicAssignment(array_ref_exp, val_exp)

    def visit_array_ref_exp(self, node, visited_children):
        var, _, exp_list = visited_children
        return BasicArrayRef(var, exp_list)

    def visit_str_arr_assign(self, node, visited_children):
        str_array_ref_exp, _, _, _, str_exp = visited_children
        return BasicAssignment(str_array_ref_exp, str_exp)

    def visit_str_array_ref_exp(self, node, visited_children):
        str_var, _, exp_list = visited_children
        return BasicArrayRef(str_var, exp_list, is_str_expr=True)

    def visit_comment(self, node, visited_children):
        return BasicComment(visited_children[1])

    def visit_comment_text(self, node, visited_children):
        return node.full_text[node.start:node.end]

    def visit_exp_list(self, node, visited_children):
        _, _, exp1, _, exp_sublist, _ = visited_children
        return BasicExpressionList((exp1, *exp_sublist))

    def visit_exp_sublist(self, node, visited_children):
        return visited_children

    def visit_exp_sublist_mbr(self, node, visited_children):
        _, _, exp, _ = visited_children
        return exp

    def visit_if_stmnt(self, node, visited_children):
        _, _, exp, _, _, _, statements = visited_children
        return BasicIf(exp, statements)

    def visit_if_exp(self, node, visited_children):
        return visited_children[0]

    def visit_bool_exp(self, node, visited_children):
        exp1, op, exp2 = visited_children
        if op == '' or exp2 == '':
            return exp1
        else:
            return exp2

    def visit_bool_val_exp(self, node, visited_children):
        return visited_children[0]

    def visit_bool_paren_exp(self, node, visited_children):
        pass

    def visit_bool_unop_exp(self, node, visited_children):
        pass

    def visit_bool_bin_exp(self, node, visited_children):
        exp1, _, op, _, exp2, _ = visited_children
        return BasicBooleanExp(exp1, op.basic09_text(0), exp2)

    def visit_num_gtle_exp(self, node, visited_children):
        return self.visit_num_prod_exp(node, visited_children)

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

    def visit_num_exp(self, node, visited_children):
        return self.visit_num_prod_exp(node, visited_children)

    def visit_str_exp(self, node, visited_children):
        if len(visited_children) < 4:
            v1, v2, v3 = visited_children
            if isinstance(v2, str) and isinstance(v3, str):
                return visited_children[0]
            if isinstance(v2, str) and isinstance(v3, str):
                return visited_children[0]
            return BasicBinaryExp(v1, v3.operator, v3.exp, True)
        return node

    def visit_str_simple_exp(self, node, visited_children):
        return visited_children[0]

    def visit_maybe_line(self, node, visited_children):
        return (child for child in visited_children
                if isinstance(child, BasicLine))

    def visit_multi_line(self, node, visited_children):
        return next(child for child in visited_children
                    if isinstance(child, BasicLine))

    def visit_multi_lines(self, node, visited_children):
        return (child for child in visited_children
                if isinstance(child, BasicLine))

    def visit_num_literal(self, node, visited_children):
        num_literal = node.full_text[node.start:node.end].replace(' ', '')
        val = float(num_literal)
        return BasicLiteral(int(val) if val == int(val) else val)

    def visit_paren_exp(self, node, visited_children):
        return BasicParenExp(visited_children[2])

    def visit_num_prod_exp(self, node, visited_children):
        v1, v2, v3 = visited_children
        if isinstance(v2, str) and isinstance(v3, str):
            return v1
        return BasicBinaryExp(v1, v3.operator, v3.exp)

    def visit_num_assign(self, node, visited_children):
        return BasicAssignment(visited_children[0], visited_children[4])

    def visit_str_assign(self, node, visited_children):
        return BasicAssignment(visited_children[0], visited_children[4])

    def visit_space(self, node, visited_children):
        return node.text

    def visit_statement(self, node, visited_children):
        return BasicStatement(next(child for child in visited_children
                              if isinstance(child, AbstractBasicStatement)))

    def visit_statements(self, node, visited_children):
        return BasicStatements([child for child in visited_children
                               if isinstance(child, BasicStatement)
                               or isinstance(child, BasicStatements)
                               or isinstance(child, BasicComment)])

    def visit_str_literal(self, node, visited_children):
        return BasicLiteral(str(node.full_text[node.start+1:node.end-1]), True)

    def visit_num_sum_exp(self, node, visited_children):
        return self.visit_num_prod_exp(node, visited_children)

    def visit_val_exp(self, node, visited_children):
        if len(visited_children) < 2:
            return visited_children[0]
        return node

    def visit_var(self, node, visited_children):
        return BasicVar(node.full_text[node.start:node.end])

    def visit_str_var(self, node, visited_children):
        return BasicVar(node.full_text[node.start:node.end], True)
    
    def visit_print_statement(self, node, visited_children):
        _, _, print_args = visited_children
        return BasicPrintStatement(print_args)

    def visit_print_args(self, node, visited_children):
        return BasicPrintArgs(visited_children)

    def visit_print_arg0(self, node, visited_children):
        arg, _ = visited_children
        return arg

    def visit_print_arg1(self, node, visited_children):
        return visited_children[0]
    
    def visit_print_arg(self, node, visited_children):
        return visited_children[0]
    
    def visit_print_control(self, node, visited_children):
        return BasicPrintControl(node.text)