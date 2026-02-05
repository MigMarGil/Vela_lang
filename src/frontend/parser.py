"""
Vela Parser - Análisis Sintáctico
"""

from typing import List, Optional
from src.frontend.lexer import Token, TokenType, Lexer
from src.frontend.ast import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        token = self.current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current()
        if token.type != token_type:
            raise SyntaxError(f"Se esperaba {token_type.name}, se encontró {token.type.name} en {token.line}:{token.column}")
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current().type in token_types
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    # ============= PARSER PRINCIPAL =============
    
    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    # ============= DECLARACIONES =============
    
    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        
        if self.match(TokenType.FUNC):
            return self.parse_function_declaration()
        elif self.match(TokenType.CLASS):
            return self.parse_class_declaration()
        elif self.match(TokenType.TRAIT):
            return self.parse_trait_declaration()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        elif self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStatement()
        elif self.match(TokenType.PARALLEL):
            return self.parse_parallel_block()
        elif self.match(TokenType.IMPORT, TokenType.FROM):
            return self.parse_import_statement()
        elif self.match(TokenType.LBRACE):
            return self.parse_block()
        elif self.match(TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL, TokenType.AUTO):
            return self.parse_var_declaration()
        else:
            # Puede ser asignación o expresión
            expr = self.parse_expression()
            
            # Verificar si es asignación
            if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN):
                op = self.advance().value
                value = self.parse_expression()
                return AssignmentStatement(expr, value, op)
            
            return ExpressionStatement(expr)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        self.expect(TokenType.FUNC)
        
        is_async = False
        if self.match(TokenType.ASYNC):
            self.advance()
            is_async = True
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LPAREN)
        parameters = self.parse_parameter_list()
        self.expect(TokenType.RPAREN)
        
        # Tipo de retorno
        return_type = 'void'
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()
        
        body = self.parse_block()
        
        return FunctionDeclaration(name, parameters, return_type, body, is_async)
    
    def parse_parameter_list(self) -> List[tuple]:
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            while True:
                name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                param_type = self.parse_type()
                parameters.append((name, param_type))
                
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        return parameters
    
    def parse_type(self) -> str:
        if self.match(TokenType.INT):
            self.advance()
            return 'int'
        elif self.match(TokenType.FLOAT):
            self.advance()
            return 'float'
        elif self.match(TokenType.STR):
            self.advance()
            return 'str'
        elif self.match(TokenType.BOOL):
            self.advance()
            return 'bool'
        elif self.match(TokenType.VOID):
            self.advance()
            return 'void'
        elif self.match(TokenType.AUTO):
            self.advance()
            return 'auto'
        elif self.match(TokenType.IDENTIFIER):
            return self.advance().value
        else:
            raise SyntaxError(f"Se esperaba un tipo, se encontró {self.current().type.name}")
    
    def parse_var_declaration(self) -> VarDeclaration:
        var_type = self.parse_type()
        name = self.expect(TokenType.IDENTIFIER).value
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()
        
        return VarDeclaration(name, var_type, initializer)
    
    def parse_class_declaration(self) -> ClassDeclaration:
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENTIFIER).value
        
        traits = []
        if self.match(TokenType.COLON):
            self.advance()
            while True:
                traits.append(self.expect(TokenType.IDENTIFIER).value)
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        fields = []
        methods = []
        
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.FUNC):
                methods.append(self.parse_function_declaration())
            else:
                fields.append(self.parse_var_declaration())
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ClassDeclaration(name, methods, fields, traits)
    
    def parse_trait_declaration(self) -> TraitDeclaration:
        self.expect(TokenType.TRAIT)
        name = self.expect(TokenType.IDENTIFIER).value
        
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        methods = []
        while not self.match(TokenType.RBRACE):
            # En traits, las funciones son declaraciones sin cuerpo
            method = self.parse_function_signature()  # Nueva función
            methods.append(method)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return TraitDeclaration(name, methods)
    
    def parse_function_signature(self) -> FunctionDeclaration:
        """Parse solo la firma de función (sin cuerpo) para traits"""
        self.expect(TokenType.FUNC)
        
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        parameters = self.parse_parameter_list()
        self.expect(TokenType.RPAREN)
        
        # Tipo de retorno
        return_type = 'void'
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()
        
        # En traits, no hay cuerpo
        return FunctionDeclaration(name, parameters, return_type, None)

    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_return_statement(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        then_branch = self.parse_block()
        
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            if self.match(TokenType.IF):
                else_branch = self.parse_if_statement()
            else:
                else_branch = self.parse_block()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        self.expect(TokenType.FOR)
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        return ForStatement(variable, iterable, body)
    
    def parse_parallel_block(self) -> ParallelBlock:
        self.expect(TokenType.PARALLEL)
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        tasks = []
        while not self.match(TokenType.RBRACE):
            tasks.append(self.parse_expression())
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return ParallelBlock(tasks)
    
    def parse_import_statement(self) -> ImportStatement:
        if self.match(TokenType.FROM):
            self.advance()
            module = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.IMPORT)
            
            items = []
            while True:
                items.append(self.expect(TokenType.IDENTIFIER).value)
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
            
            return ImportStatement(module, items)
        else:
            self.expect(TokenType.IMPORT)
            module = self.expect(TokenType.IDENTIFIER).value
            
            alias = None
            if self.match(TokenType.AS):
                self.advance()
                alias = self.expect(TokenType.IDENTIFIER).value
            
            return ImportStatement(module, alias=alias)
    
    # ============= EXPRESIONES =============
    
    def parse_expression(self) -> ASTNode:
        return self.parse_pipeline()
    
    def parse_pipeline(self) -> ASTNode:
        """Pipeline: expr |> func1 |> func2"""
        expr = self.parse_logical_or()
        
        if self.match(TokenType.PIPELINE):
            functions = []
            while self.match(TokenType.PIPELINE):
                self.advance()
                functions.append(self.parse_logical_or())
            return PipelineExpr(expr, functions)
        
        return expr
    
    def parse_logical_or(self) -> ASTNode:
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        left = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        left = self.parse_addition()
        
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_addition(self) -> ASTNode:
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            
            # Concatenación de strings se maneja normalmente
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplication(self) -> ASTNode:
        left = self.parse_power()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_power(self) -> ASTNode:
        left = self.parse_unary()
        
        if self.match(TokenType.POWER):
            op = self.advance().value
            right = self.parse_power()  # Asociatividad derecha
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        if self.match(TokenType.AWAIT):
            self.advance()
            expr = self.parse_unary()
            return AsyncAwait(expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Llamada a función
                self.advance()
                args = self.parse_argument_list()
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, args)
            elif self.match(TokenType.LBRACKET):
                # Acceso a índice
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, index)
            elif self.match(TokenType.DOT):
                # Acceso a miembro
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccess(expr, member)
            else:
                break
        
        return expr
    
    def parse_argument_list(self) -> List[ASTNode]:
        args = []
        
        if not self.match(TokenType.RPAREN):
            while True:
                args.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        return args
    
    def parse_primary(self) -> ASTNode:
        # Números
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.advance().value)
        
        # Strings
        if self.match(TokenType.STRING):
            return StringLiteral(self.advance().value)
        
        # Booleanos
        if self.match(TokenType.BOOLEAN):
            return BooleanLiteral(self.advance().value)
        
        # Null
        if self.match(TokenType.NULL):
            self.advance()
            return NullLiteral()
        
        # Identificadores
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.advance().value)
        
        # Arrays
        if self.match(TokenType.LBRACKET):
            self.advance()
            elements = []
            if not self.match(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA):
                        break
                    self.advance()
            self.expect(TokenType.RBRACKET)
            return ArrayLiteral(elements)
        
        # Expresiones entre paréntesis
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Match expression
        if self.match(TokenType.MATCH):
            return self.parse_match_expression()
        
        # Lambda
        if self.match(TokenType.PIPE):
            return self.parse_lambda()
        
        if self.match(TokenType.IDENTIFIER) and self.peek().type == TokenType.LBRACE:
            class_name = self.advance().value
            self.expect(TokenType.LBRACE)
            
            # Parsear inicializadores de campos
            fields = []
            if not self.match(TokenType.RBRACE):
                while True:
                    field_name = self.expect(TokenType.IDENTIFIER).value
                    self.expect(TokenType.ASSIGN)
                    field_value = self.parse_expression()
                    fields.append((field_name, field_value))
                    
                    if not self.match(TokenType.COMMA):
                        break
                    self.advance()
            
            self.expect(TokenType.RBRACE)
            return ObjectLiteral(class_name, fields)        

        raise SyntaxError(f"Expresión inesperada: {self.current().type.name} en {self.current().line}:{self.current().column}")
    
    def parse_match_expression(self) -> MatchExpr:
        self.expect(TokenType.MATCH)
        value = self.parse_expression()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        cases = []
        while not self.match(TokenType.RBRACE):
            pattern = self.parse_expression()
            self.expect(TokenType.FAT_ARROW)
            result = self.parse_expression()
            cases.append((pattern, result))
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return MatchExpr(value, cases)
    
    def parse_lambda(self) -> LambdaExpr:
        self.expect(TokenType.PIPE)
        
        parameters = []
        if not self.match(TokenType.PIPE):
            while True:
                name = self.expect(TokenType.IDENTIFIER).value
                param_type = 'auto'
                if self.match(TokenType.COLON):
                    self.advance()
                    param_type = self.parse_type()
                parameters.append((name, param_type))
                
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.expect(TokenType.PIPE)
        
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()
        
        if self.match(TokenType.LBRACE):
            body = self.parse_block()
        else:
            body = self.parse_expression()
        
        return LambdaExpr(parameters, body, return_type)
