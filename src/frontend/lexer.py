
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Literales
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Identificadores
    IDENTIFIER = auto()
    
    # Palabras clave
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    
    # Tipos
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    VOID = auto()
    AUTO = auto()
    
    # Características avanzadas
    ASYNC = auto()
    AWAIT = auto()
    PARALLEL = auto()
    PIPE = auto()
    MATCH = auto()
    WITH = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    CLASS = auto()
    TRAIT = auto()
    IMPL = auto()
    
    # Operadores
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    PIPELINE = auto()
    
    # Delimitadores
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    QUESTION = auto()
    
    # Especiales
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Palabras clave de Vela
        self.keywords = {
            'func': TokenType.FUNC,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'str': TokenType.STR,
            'bool': TokenType.BOOL,
            'void': TokenType.VOID,
            'auto': TokenType.AUTO,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
            'null': TokenType.NULL,
            'async': TokenType.ASYNC,
            'await': TokenType.AWAIT,
            'parallel': TokenType.PARALLEL,
            'match': TokenType.MATCH,
            'with': TokenType.WITH,
            'import': TokenType.IMPORT,
            'from': TokenType.FROM,
            'as': TokenType.AS,
            'class': TokenType.CLASS,
            'trait': TokenType.TRAIT,
            'impl': TokenType.IMPL,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        value = float(num_str) if has_dot else int(num_str)
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self, quote: str) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        
        string_val = ''
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_val += '\n'
                elif escape_char == 't':
                    string_val += '\t'
                elif escape_char == '\\':
                    string_val += '\\'
                elif escape_char == quote:
                    string_val += quote
                else:
                    string_val += escape_char
                self.advance()
            else:
                string_val += self.current_char()
                self.advance()
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        id_str = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        token_type = self.keywords.get(id_str, TokenType.IDENTIFIER)
        value = id_str
        
        if token_type == TokenType.BOOLEAN:
            value = id_str == 'true'
        elif token_type == TokenType.NULL:
            value = None
        
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Comentarios
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.tokens.append(token)
                self.advance()
                continue
            
            # Números
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char() in '"\'':
                quote = self.current_char()
                self.tokens.append(self.read_string(quote))
                continue
            
            # Identificadores y palabras clave
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operadores y símbolos
            line, col = self.line, self.column
            char = self.current_char()
            
            # Operadores de dos caracteres
            if char == '=' and self.peek() == '=':
                self.tokens.append(Token(TokenType.EQ, '==', line, col))
                self.advance()
                self.advance()
            elif char == '!' and self.peek() == '=':
                self.tokens.append(Token(TokenType.NEQ, '!=', line, col))
                self.advance()
                self.advance()
            elif char == '<' and self.peek() == '=':
                self.tokens.append(Token(TokenType.LTE, '<=', line, col))
                self.advance()
                self.advance()
            elif char == '>' and self.peek() == '=':
                self.tokens.append(Token(TokenType.GTE, '>=', line, col))
                self.advance()
                self.advance()
            elif char == '+' and self.peek() == '=':
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', line, col))
                self.advance()
                self.advance()
            elif char == '-' and self.peek() == '=':
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', line, col))
                self.advance()
                self.advance()
            elif char == '-' and self.peek() == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', line, col))
                self.advance()
                self.advance()
            elif char == '=' and self.peek() == '>':
                self.tokens.append(Token(TokenType.FAT_ARROW, '=>', line, col))
                self.advance()
                self.advance()
            elif char == '|' and self.peek() == '>':
                self.tokens.append(Token(TokenType.PIPELINE, '|>', line, col))
                self.advance()
                self.advance()
            elif char == '*' and self.peek() == '*':
                self.tokens.append(Token(TokenType.POWER, '**', line, col))
                self.advance()
                self.advance()
            # Operadores simples
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
                self.advance()
            elif char == '%':
                self.tokens.append(Token(TokenType.MODULO, '%', line, col))
                self.advance()
            elif char == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
                self.advance()
            elif char == '<':
                self.tokens.append(Token(TokenType.LT, '<', line, col))
                self.advance()
            elif char == '>':
                self.tokens.append(Token(TokenType.GT, '>', line, col))
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
                self.advance()
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', line, col))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
                self.advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', line, col))
                self.advance()
            elif char == '?':
                self.tokens.append(Token(TokenType.QUESTION, '?', line, col))
                self.advance()
            elif char == '|':
                self.tokens.append(Token(TokenType.PIPE, '|', line, col))
                self.advance()
            else:
                raise SyntaxError(f"Carácter desconocido '{char}' en {line}:{col}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
