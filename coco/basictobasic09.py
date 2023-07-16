from abc import ABC, abstractmethod
from itertools import chain, islice
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

SINGLE_KEYWORD_STATEMENTS = {
    'RETURN': 'RETURN',
    'RESTORE': 'RESTORE',
}

QUOTED_SINGLE_KEYWORD_STATEMENTS = [
    '"' + name + '"' for name in SINGLE_KEYWORD_STATEMENTS.keys()
]

FUNCTIONS = {
    'ABS': 'ABS',
    'ASC': 'ASC',
    'ATN': 'ATN',
    'COS': 'COS',
    'EXP': 'EXP',
    'INT': 'INT',
    'LEN': 'LEN',
    'LOG': 'LOG',
    'PEEK': 'PEEK',
    'RND': 'RND',
    'SGN': 'SGN',
    'SIN': 'SIN',
    'SQR': 'SQR',
    'TAN': 'TAN',
}

QUOTED_FUNCTION_NAMES = [
    '"' + name + '"' for name in FUNCTIONS.keys()
]

STR2_FUNCTIONS = {
    'LEFT$': 'LEFT$',
    'RIGHT$': 'RIGHT$',
}

QUOTED_STR2_FUNCTION_NAMES = [
    '"' + name + '"' for name in STR2_FUNCTIONS.keys()
]

STR3_FUNCTIONS = {
    'MID$': 'MID$',
}

QUOTED_STR3_FUNCTION_NAMES = [
    '"' + name + '"' for name in STR3_FUNCTIONS.keys()
]

STR_NUM_FUNCTIONS = {
    'VAL': 'VAL',
}

QUOTED_STR_NUM_FUNCTIONS_NAMES = [
    '"' + name + '"' for name in STR_NUM_FUNCTIONS.keys()
]

NUM_STR_FUNCTIONS = {
    'CHR$': 'CHR$',
    'TAB': 'TAB',
}

QUOTED_NUM_STR_FUNCTIONS_NAMES = [
    '"' + name + '"' for name in NUM_STR_FUNCTIONS.keys()
]

STATEMENTS2 = {
    'RESET': 'RUN ecb_reset',
}

QUOTED_STATEMENTS2_NAMES = [
    '"' + name + '"' for name in STATEMENTS2.keys()
]

STATEMENTS3 = {
    'SET': 'RUN ecb_set',
}

QUOTED_STATEMENTS3_NAMES = [
    '"' + name + '"' for name in STATEMENTS3.keys()
]

FUNCTIONS_TO_STATEMENTS = {
    'BUTTON': 'RUN ecb_button',
    'JOYSTK': 'RUN ecb_joystk',
}

FUNCTIONS_TO_STATEMENTS2 = {
   'POINT': 'RUN ecb_point',
}

NUM_STR_FUNCTIONS_TO_STATEMENTS = {
    'HEX$': 'RUN ecb_hex',
}

STR_FUNCTIONS_TO_STATEMENTS = {
    'INKEY$': 'RUN ecb_inkey',
}

KEYWORDS = '|'.join(
    chain((
        'AND',
        'CLS',
        'ELSE',
        'FOR',
        'GOSUB',
        'GOTO',
        'IF',
        'NOT',
        'OR',
        'PRINT',
        'REM',
        'SOUND',
    ), SINGLE_KEYWORD_STATEMENTS.keys(),
       FUNCTIONS.keys(),
       STR2_FUNCTIONS.keys(),
       STR3_FUNCTIONS.keys(),
       STR_NUM_FUNCTIONS.keys(),
       NUM_STR_FUNCTIONS.keys(),
       STATEMENTS2.keys(),
       STATEMENTS3.keys(),
       FUNCTIONS_TO_STATEMENTS.keys(),
       FUNCTIONS_TO_STATEMENTS2.keys(),
       NUM_STR_FUNCTIONS_TO_STATEMENTS.keys(),
       STR_FUNCTIONS_TO_STATEMENTS.keys()))

grammar = Grammar(
    rf"""
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
                    / sound
                    / cls
                    / go_statement
                    / statement2
                    / statement3
                    / data_statement
                    / single_kw_statement
    statement2      =({ ' / '.join(QUOTED_STATEMENTS2_NAMES)}) space* "(" space* exp space* "," space* exp space* ")" space*
    statement3      = ({ ' / '.join(QUOTED_STATEMENTS3_NAMES)}) space* "(" space* exp space* "," space* exp space* "," space* exp space* ")" space*
    statements      = (statement? (comment/((":"/space)+
                                            (comment / statements)))* space*)
    statements_else = (statement? (space* ":" statements)* space*)
    exp             = "NOT"? space* num_exp space*
    if_exp          = bool_exp
                    / num_exp
    bool_exp        = "NOT"? space* bool_val_exp space* (("AND" / "OR") space* bool_val_exp space*)*
    bool_val_exp    = bool_paren_exp
                    / bool_bin_exp
    bool_paren_exp  = "(" space* bool_exp space* ")"
    bool_bin_exp    = num_sum_exp space* ("<=" / ">=" / "<>" / "<" / ">" / "=>" / "=<" / "=") space* num_sum_exp space*
    num_exp         = num_gtle_exp space* (("AND" / "OR") space* num_gtle_exp space*)*
    num_gtle_exp    = num_sum_exp space* (("<=" / ">=" / "<>" / "<" / ">" / "=>" / "=<" / "=") space* num_sum_exp space*)*
    num_sum_exp     = num_prod_exp space* (("+" / "-") space*
                                           num_prod_exp space*)*
    num_prod_exp    = val_exp space* (("*" / "/") space* val_exp space*)*
    func_exp        = ({ ' / '.join(QUOTED_FUNCTION_NAMES)}) space* "(" space* exp space* ")" space*
    func_str_exp    = ({ ' / '.join(QUOTED_STR_NUM_FUNCTIONS_NAMES)}) space* "(" space* str_exp space* ")" space*
    val_exp         = num_literal
                    / hex_literal
                    / paren_exp
                    / unop_exp
                    / array_ref_exp
                    / var
                    / func_exp
                    / func_str_exp
    unop_exp        = unop space* exp
    paren_exp       =  "(" space* exp space* ")" space*
    str_exp         = str_simple_exp space* (("+") space*
                                             str_simple_exp space*)* 
    str2_func_exp   = ({ ' / '.join(QUOTED_STR2_FUNCTION_NAMES)}) space* "(" space* str_exp space* "," space* exp space* ")" space*
    str3_func_exp   = ({ ' / '.join(QUOTED_STR3_FUNCTION_NAMES)}) space* "(" space* str_exp space* "," space* exp space* "," space* exp space* ")" space*
    num_str_func_exp= ({ ' / '.join(QUOTED_NUM_STR_FUNCTIONS_NAMES)}) space* "(" space* exp space* ")" space*

    str_simple_exp  = str_literal
                    / str_array_ref_exp
                    / str_var
                    / str2_func_exp
                    / str3_func_exp
                    / num_str_func_exp
    comment_text    = ~r"[^:\r\n$]*"
    comment_token   = ~r"(REM|')"
    eof             = ~r"$"
    eol             = ~r"[\n\r]+"
    linenum         = ~r"[0-9]+"
    literal         = num_literal
    hex_literal     = ~r"&\s*H\s*[0-9A-F][0-9A-F]?[0-9A-F]?[0-9A-F]?[0-9A-F]?[0-9A-F]?"
    num_literal     = ~r"([\+\-\s]*(\d*\.\d*)(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d*\.\d*)|[\+\-\s]*(\d+(\s*(?!ELSE)E\s*[\+\-]?\s*\d*))|[\+\-\s]*(\d+)"
    space           = ~r" "
    str_literal     = ~r'\"[^"\n]*\"'
    unop            = "+" / "-"
    var             = ~r"(?!{KEYWORDS}|([A-Z][A-Z0-9]*\$))([A-Z][A-Z0-9]?)"
    str_var         = ~r"(?!{KEYWORDS})([A-Z][A-Z0-9]?)\$"
    print_statement = ("PRINT"/"?") space* print_args
    print_args      = print_arg0*
    print_arg0      = print_arg1 space*
    print_arg1      = print_control 
                    / print_arg
    print_arg       = exp 
                    / str_exp
    print_control   = ~r"(;|,)"
    sound           = "SOUND" space* exp space* "," space* exp space*
    cls             = "CLS" space* exp? space*
    go_statement    = ("GOTO" / "GOSUB") space* linenum space*
    functions       = ~r"{'|'.join(FUNCTIONS.keys())}"
    data_statement  = "DATA" space* data_elements space*
    data_elements   = data_element space* data_elements0
    data_element    = data_num_element / data_str_element
    data_elements0  = data_element0*
    data_element0   = "," space* data_element
    data_num_element = space* data_num_element0 space*
    data_num_element0 = (num_literal / hex_literal)
    data_str_element = data_str_element0 / data_str_element1
    data_str_element0 = space* str_literal space*
    data_str_element1 = space* data_str_literal
    data_str_literal  = ~r'[^",\n]*'
    single_kw_statement = ({ ' / '.join(QUOTED_SINGLE_KEYWORD_STATEMENTS)}) space*
    """  # noqa
)


class AbstractBasicConstruct(ABC):
    def indent_spaces(self, indent_level):
        return '    ' * indent_level

    @abstractmethod
    def basic09_text(self, indent_level):
        """Return the Basic09 text that represents this construct"""
        pass

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
        if self._op in {'AND', 'OR'}:
            return f'L{self._op}({self._exp1.basic09_text(indent_level)}, '\
                   f'{self._exp2.basic09_text(indent_level)})'
        else:
            return (f'{self._exp1.basic09_text(indent_level)} {self._op} '
                    f'{self._exp2.basic09_text(indent_level)}')


class BasicBooleanBinaryExp(BasicBinaryExp):
    def basic09_text(self, indent_level):
        return (f'{self._exp1.basic09_text(indent_level)} {self._op} '
                f'{self._exp2.basic09_text(indent_level)}')


class BasicComment(AbstractBasicConstruct):
    def __init__(self, comment):
        self._comment = comment

    def basic09_text(self, indent_level):
        return f'(*{self._comment} *)'


class BasicExpressionList(AbstractBasicConstruct):
    def __init__(self, exp_list, parens=True):
        self._exp_list = exp_list
        self._parens = parens

    @property
    def exp_list(self):
        return self._exp_list

    def basic09_text(self, indent_level):
        exp_list_text = ', '.join(exp.basic09_text(indent_level)
                                  for exp in self._exp_list)
        return f'({exp_list_text})' if self._parens else f'{exp_list_text}'


class BasicRunCall(AbstractBasicStatement):
    def __init__(self, run_invocation, arguments):
        self._run_invocation = run_invocation
        self._arguments = arguments

    def basic09_text(self, indent_level):
        return f'{self.indent_spaces(indent_level)}' \
               f'{self._run_invocation}' \
               f'{self._arguments.basic09_text(indent_level)}'


class BasicGoto(AbstractBasicStatement):
    def __init__(self, linenum, implicit, is_gosub=False):
        self._linenum = linenum
        self._implicit = implicit
        self._is_gosub = is_gosub

    @property
    def implicit(self):
        return self._implicit

    def basic09_text(self, indent_level):
        if self._is_gosub:
            return f'{self.indent_spaces(indent_level)}GOSUB {self._linenum}'
        return f'{self._linenum}' \
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


class HexLiteral(AbstractBasicExpression):
    def __init__(self, literal):
        super().__init__(is_str_expr=False)
        self._literal = literal

    def basic09_text(self, indent_level):
        val = int(f'0x{self._literal}', 16)
        return f'${self._literal}' if val < 0x8000 \
            else f'{val}'


class BasicOperator(AbstractBasicConstruct):
    def __init__(self, operator):
        self._operator = operator

    @property
    def operator(self):
        return self._operator

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
        if self.operator == 'NOT':
            return f'L{self.operator}({self.exp.basic09_text(indent_level)})'
        else:
            return f'{self.operator} {self.exp.basic09_text(indent_level)}'


class BasicBooleanOpExp(BasicOpExp):
    def basic09_text(self, indent_level):
        if self.operator == 'NOT':
            return f'{self.operator}({self.exp.basic09_text(indent_level)})'
        else:
            return f'{self.operator} {self.exp.basic09_text(indent_level)}'


class BasicParenExp(AbstractBasicExpression):
    def __init__(self, exp):
        self._exp = exp

    def basic09_text(self, indent_level):
        return f'({self._exp.basic09_text(indent_level)})'


class BasicBooleanParenExp(BasicParenExp):
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
    def __init__(self, statements, multi_line=True):
        self._statements = statements
        self._multi_line = multi_line

    def statements(self):
        return self._statements

    def basic09_text(self, indent_level):
        joiner = ('\n' + self.indent_spaces(indent_level)) \
            if self._multi_line else r' \ '
        return joiner.join(statement.basic09_text(indent_level)
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
            if (ii < len(self.args) - 1) and is_control:
                processed_args.append(' ')

        return ''.join(processed_args)


class BasicSound(AbstractBasicStatement):
    def __init__(self, exp1, exp2):
        self._exp1 = exp1
        self._exp2 = exp2

    def basic09_text(self, indent_level):
        return f'RUN ecb_sound({self._exp1.basic09_text(indent_level)}, ' \
            f'{self._exp2.basic09_text(indent_level)}, 31)'


class BasicCls(AbstractBasicStatement):
    def __init__(self, exp=None):
        self._exp = exp

    def basic09_text(self, indent_level):
        return self.indent_spaces(indent_level) \
            + ('RUN ecb_cls(1)' if not self._exp else
               f'RUN ecb_cls({self._exp.basic09_text(indent_level)})')


class BasicFunctionCall(AbstractBasicExpression):
    def __init__(self, func, args):
        self._func = func
        self._args = args

    def basic09_text(self, indent_level):
        return f'{self._func}' \
               f'{self._args.basic09_text(indent_level)}'


class BasicDataStatement(BasicStatement):
    def __init__(self, exp_list):
        self._exp_list = exp_list

    def basic09_text(self, indent_level):
        return f'{self.indent_spaces(indent_level)}DATA ' \
               f'{self._exp_list.basic09_text(indent_level)}'


class BasicKeywordStatement(BasicStatement):
    def __init__(self, keyword):
        self._keyword = keyword

    def basic09_text(self, indent_level):
        return f'{self.indent_spaces(indent_level)}{self._keyword}'


class BasicVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        if node.text.strip() == '':
            return ''

        if node.text in {'*', '/', '+', '-', '*', '&', '<', '>', '<>', '=',
                         '<=', '=<', '>=', '=>', 'AND', 'OR', 'NOT'}:
            return BasicOperator(node.text)

        if len(visited_children) == 4:
            if isinstance(visited_children[0], BasicOperator):
                operator, _, exp, _ = visited_children
                return BasicOpExp(operator.operator, exp)
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

    def visit_exp(self, node, visited_children):
        not_keyword, _, exp, _ = visited_children
        if isinstance(not_keyword, BasicOperator):
            return BasicOpExp(not_keyword.operator, exp)
        return exp

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
        not_keyword, _, exp1, _, exp2 = visited_children
        exp = exp1 if exp2 == '' \
            else BasicBooleanBinaryExp(exp1, exp2.operator, exp2.exp)
        return exp if not isinstance(not_keyword, BasicOperator) \
            else BasicBooleanOpExp(not_keyword.operator, exp)

    def visit_bool_val_exp(self, node, visited_children):
        return visited_children[0]

    def visit_bool_paren_exp(self, node, visited_children):
        return BasicBooleanParenExp(visited_children[2])

    def visit_bool_bin_exp(self, node, visited_children):
        exp1, _, op, _, exp2, _ = visited_children
        return BasicBooleanBinaryExp(exp1, op.operator, exp2)

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

    def visit_str2_func_exp(self, node, visited_children):
        func, _, _, _, str_exp, _, _, _, exp, _, _, _ = visited_children
        return BasicFunctionCall(STR2_FUNCTIONS[func.text],
                                 BasicExpressionList([str_exp, exp]))

    def visit_str3_func_exp(self, node, visited_children):
        func, _, _, _, str_exp, _, _, _, exp1, _, _, _, exp2, _, _, _ \
            = visited_children
        return BasicFunctionCall(STR3_FUNCTIONS[func.text],
                                 BasicExpressionList([str_exp, exp1, exp2]))

    def visit_num_str_func_exp(self, node, visited_children):
        func, _, _, _, exp, _, _, _ = visited_children
        return BasicFunctionCall(NUM_STR_FUNCTIONS[func.text],
                                 BasicExpressionList([exp]))

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

    def visit_hex_literal(self, node, visited_children):
        hex_literal = node.text[node.text.find('H') + 1:]
        return HexLiteral(hex_literal)

    def visit_unop_exp(self, node, visited_children):
        op, _, exp = visited_children
        return BasicOpExp(op.operator, exp)

    def visit_unop(self, node, visited_children):
        return visited_children[0]

    def visit_paren_exp(self, node, visited_children):
        return BasicParenExp(visited_children[2])

    def visit_num_prod_exp(self, node, visited_children):
        v1, v2, v3 = visited_children
        if isinstance(v2, str) and isinstance(v3, str):
            return v1
        return BasicBinaryExp(v1, v3.operator, v3.exp)

    def visit_func_exp(self, node, visited_children):
        func, _, _, _, exp, _, _, _ = visited_children
        return BasicFunctionCall(FUNCTIONS[func.text],
                                 BasicExpressionList([exp]))

    def visit_func_str_exp(self, node, visited_children):
        func, _, _, _, exp, _, _, _ = visited_children
        return BasicFunctionCall(STR_NUM_FUNCTIONS[func.text],
                                 BasicExpressionList([exp]))

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
                               if isinstance(child, AbstractBasicConstruct)])

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

    def visit_sound(self, node, visited_children):
        _, _, exp1, _, _, _, exp2, _ = visited_children
        return BasicSound(exp1, exp2)

    def visit_cls(self, node, visited_children):
        _, _, exp, _ = visited_children
        return BasicCls(exp if isinstance(exp, AbstractBasicExpression)
                        else None)

    def visit_statement2(self, node, visited_children):
        func, _, _, _, exp1, _, _, _, exp2, _, _, _ = visited_children
        return BasicRunCall(STATEMENTS2[func.text],
                            BasicExpressionList([exp1, exp2]))

    def visit_statement3(self, node, visited_children):
        func, _, _, _, exp1, _, _, _, exp2, _, _, _, exp3, _, _, _ \
            = visited_children
        return BasicRunCall(STATEMENTS3[func.text],
                            BasicExpressionList([exp1, exp2, exp3]))

    def visit_go_statement(self, node, visited_children):
        go, _, linenum, _ = visited_children
        return BasicGoto(linenum, False, is_gosub=go.text == 'GOSUB')

    def visit_data_statement(self, node, visited_children):
        _, _, exp_list, _ = visited_children
        return BasicDataStatement(exp_list)

    def visit_data_elements(self, node, visited_children):
        data_element, _, data_elements = visited_children
        return BasicExpressionList([data_element] + data_elements.exp_list,
                                   parens=False)

    def visit_data_element0(self, node, visited_children):
        _, _, data_element = visited_children
        return data_element

    def visit_data_elements0(self, node, visited_children):
        return BasicExpressionList(visited_children, parens=False)

    def visit_data_element(self, node, visited_children):
        return visited_children[0]

    def visit_data_num_element(self, node, visited_children):
        _, literal, _ = visited_children
        return literal

    def visit_data_num_element0(self, node, visited_children):
        return visited_children[0]

    def visit_data_str_element(self, node, visited_children):
        return visited_children[0]

    def visit_data_str_element0(self, node, visited_children):
        _, literal, _ = visited_children
        return literal

    def visit_data_str_element1(self, node, visited_children):
        _, literal = visited_children
        return literal

    def visit_data_str_literal(self, node, visited_children):
        return BasicLiteral(node.text)

    def visit_single_kw_statement(self, node, visited_children):
        keyword, _ = visited_children
        return BasicKeywordStatement(SINGLE_KEYWORD_STATEMENTS[keyword.text]) 