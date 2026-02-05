"""
Vela AST - Árbol de Sintaxis Abstracta
Representación de la estructura del programa
"""

from dataclasses import dataclass
from typing import List, Optional, Any
from abc import ABC, abstractmethod

# Clase base para todos los nodos AST
class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

# ============= EXPRESIONES =============

@dataclass
class NumberLiteral(ASTNode):
    value: float
    
    def accept(self, visitor):
        return visitor.visit_number_literal(self)

@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def accept(self, visitor):
        return visitor.visit_string_literal(self)

@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)

@dataclass
class NullLiteral(ASTNode):
    def accept(self, visitor):
        return visitor.visit_null_literal(self)

@dataclass
class Identifier(ASTNode):
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)

@dataclass
class CallExpr(ASTNode):
    callee: ASTNode
    arguments: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_call_expr(self)

@dataclass
class ArrayLiteral(ASTNode):
    elements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_array_literal(self)

@dataclass
class IndexExpr(ASTNode):
    array: ASTNode
    index: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_index_expr(self)

@dataclass
class MemberAccess(ASTNode):
    object: ASTNode
    member: str
    
    def accept(self, visitor):
        return visitor.visit_member_access(self)

@dataclass
class LambdaExpr(ASTNode):
    parameters: List[tuple]  # [(name, type)]
    body: ASTNode
    return_type: Optional[str] = None
    
    def accept(self, visitor):
        return visitor.visit_lambda_expr(self)

@dataclass
class PipelineExpr(ASTNode):
    """Expresión de pipeline: valor |> funcion1 |> funcion2"""
    value: ASTNode
    functions: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_pipeline_expr(self)

@dataclass
class MatchExpr(ASTNode):
    """Pattern matching avanzado"""
    value: ASTNode
    cases: List[tuple]  # [(pattern, result)]
    
    def accept(self, visitor):
        return visitor.visit_match_expr(self)

# ============= DECLARACIONES =============

@dataclass
class VarDeclaration(ASTNode):
    name: str
    var_type: Optional[str]
    initializer: Optional[ASTNode]
    is_const: bool = False
    
    def accept(self, visitor):
        return visitor.visit_var_declaration(self)

@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List[tuple]  # [(name, type)]
    return_type: str
    body: 'Block'
    is_async: bool = False
    
    def accept(self, visitor):
        return visitor.visit_function_declaration(self)

@dataclass
class ClassDeclaration(ASTNode):
    name: str
    methods: List['FunctionDeclaration']
    fields: List['VarDeclaration']
    traits: List[str] = None
    
    def accept(self, visitor):
        return visitor.visit_class_declaration(self)

@dataclass
class TraitDeclaration(ASTNode):
    name: str
    methods: List['FunctionDeclaration']
    
    def accept(self, visitor):
        return visitor.visit_trait_declaration(self)

# ============= SENTENCIAS =============

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_block(self)

@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_return_statement(self)

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_if_statement(self)

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_while_statement(self)

@dataclass
class ForStatement(ASTNode):
    variable: str
    iterable: ASTNode
    body: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_for_statement(self)

@dataclass
class BreakStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_break_statement(self)

@dataclass
class ContinueStatement(ASTNode):
    def accept(self, visitor):
        return visitor.visit_continue_statement(self)

@dataclass
class AssignmentStatement(ASTNode):
    target: ASTNode
    value: ASTNode
    operator: str = '='  # =, +=, -=, etc.
    
    def accept(self, visitor):
        return visitor.visit_assignment_statement(self)

@dataclass
class ParallelBlock(ASTNode):
    """Ejecución paralela automática"""
    tasks: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_parallel_block(self)

@dataclass
class AsyncAwait(ASTNode):
    """Operación asíncrona"""
    expression: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_async_await(self)

@dataclass
class ImportStatement(ASTNode):
    module: str
    items: Optional[List[str]] = None
    alias: Optional[str] = None
    
    def accept(self, visitor):
        return visitor.visit_import_statement(self)

@dataclass
class ObjectLiteral(ASTNode):
    """Creación de objetos: Circle { radius = 5.0 }"""
    class_name: str
    fields: List[tuple]  # [(field_name, value)]
    
    def accept(self, visitor):
        return visitor.visit_object_literal(self)

# ============= PROGRAMA =============

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_program(self)

# ============= VISITOR PATTERN =============

class ASTVisitor(ABC):
    """Visitor base para recorrer el AST"""
    
    @abstractmethod
    def visit_number_literal(self, node: NumberLiteral): pass
    
    @abstractmethod
    def visit_string_literal(self, node: StringLiteral): pass
    
    @abstractmethod
    def visit_boolean_literal(self, node: BooleanLiteral): pass
    
    @abstractmethod
    def visit_null_literal(self, node: NullLiteral): pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier): pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOp): pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOp): pass
    
    @abstractmethod
    def visit_call_expr(self, node: CallExpr): pass
    
    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteral): pass
    
    @abstractmethod
    def visit_index_expr(self, node: IndexExpr): pass
    
    @abstractmethod
    def visit_member_access(self, node: MemberAccess): pass
    
    @abstractmethod
    def visit_lambda_expr(self, node: LambdaExpr): pass
    
    @abstractmethod
    def visit_pipeline_expr(self, node: PipelineExpr): pass
    
    @abstractmethod
    def visit_match_expr(self, node: MatchExpr): pass
    
    @abstractmethod
    def visit_var_declaration(self, node: VarDeclaration): pass
    
    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclaration): pass
    
    @abstractmethod
    def visit_class_declaration(self, node: ClassDeclaration): pass
    
    @abstractmethod
    def visit_trait_declaration(self, node: TraitDeclaration): pass
    
    @abstractmethod
    def visit_block(self, node: Block): pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement): pass
    
    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement): pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement): pass
    
    @abstractmethod
    def visit_while_statement(self, node: WhileStatement): pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatement): pass
    
    @abstractmethod
    def visit_break_statement(self, node: BreakStatement): pass
    
    @abstractmethod
    def visit_continue_statement(self, node: ContinueStatement): pass
    
    @abstractmethod
    def visit_assignment_statement(self, node: AssignmentStatement): pass
    
    @abstractmethod
    def visit_parallel_block(self, node: ParallelBlock): pass
    
    @abstractmethod
    def visit_async_await(self, node: AsyncAwait): pass
    
    @abstractmethod
    def visit_import_statement(self, node: ImportStatement): pass
    
    @abstractmethod
    def visit_program(self, node: Program): pass

class ASTPrinter(ASTVisitor):
    """Imprime el AST de forma legible - IMPLEMENTACIÓN COMPLETA"""
    
    def __init__(self):
        self.indent = 0
    
    def _print(self, text):
        print("  " * self.indent + text)
    
    def visit_number_literal(self, node):
        self._print(f"Number: {node.value}")
    
    def visit_string_literal(self, node):
        self._print(f"String: '{node.value}'")
    
    def visit_boolean_literal(self, node):
        self._print(f"Boolean: {node.value}")
    
    def visit_null_literal(self, node):
        self._print("Null")
    
    def visit_identifier(self, node):
        self._print(f"Identifier: {node.name}")
    
    def visit_binary_op(self, node):
        self._print(f"BinaryOp: {node.operator}")
        self.indent += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent -= 1
    
    def visit_unary_op(self, node):
        self._print(f"UnaryOp: {node.operator}")
        self.indent += 1
        node.operand.accept(self)
        self.indent -= 1
    
    def visit_call_expr(self, node):
        self._print("CallExpr")
        self.indent += 1
        self._print("Callee:")
        self.indent += 1
        node.callee.accept(self)
        self.indent -= 1
        if node.arguments:
            self._print("Arguments:")
            self.indent += 1
            for arg in node.arguments:
                arg.accept(self)
            self.indent -= 1
        self.indent -= 1
    
    def visit_array_literal(self, node):
        self._print("ArrayLiteral")
        if node.elements:
            self.indent += 1
            for elem in node.elements:
                elem.accept(self)
            self.indent -= 1
    
    def visit_index_expr(self, node):
        self._print("IndexExpr")
        self.indent += 1
        node.array.accept(self)
        node.index.accept(self)
        self.indent -= 1
    
    def visit_member_access(self, node):
        self._print(f"MemberAccess: .{node.member}")
        self.indent += 1
        node.object.accept(self)
        self.indent -= 1
    
    def visit_lambda_expr(self, node):
        self._print(f"Lambda: {node.parameters} -> {node.return_type}")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
    
    def visit_pipeline_expr(self, node):
        self._print("Pipeline")
        self.indent += 1
        self._print("Value:")
        self.indent += 1
        node.value.accept(self)
        self.indent -= 1
        self._print("Functions:")
        self.indent += 1
        for func in node.functions:
            func.accept(self)
        self.indent -= 1
        self.indent -= 1
    
    def visit_match_expr(self, node):
        self._print("Match")
        self.indent += 1
        node.value.accept(self)
        for pattern, result in node.cases:
            self._print("Case:")
            self.indent += 1
            pattern.accept(self)
            result.accept(self)
            self.indent -= 1
        self.indent -= 1
    
    def visit_var_declaration(self, node):
        self._print(f"VarDeclaration: {node.name}: {node.var_type}")
        if node.initializer:
            self.indent += 1
            node.initializer.accept(self)
            self.indent -= 1
    
    def visit_function_declaration(self, node):
        async_str = "async " if node.is_async else ""
        self._print(f"{async_str}Function: {node.name}({node.parameters}) -> {node.return_type}")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
    
    def visit_class_declaration(self, node):
        traits = f": {', '.join(node.traits)}" if node.traits else ""
        self._print(f"Class: {node.name}{traits}")
        self.indent += 1
        if node.fields:
            self._print("Fields:")
            self.indent += 1
            for field in node.fields:
                field.accept(self)
            self.indent -= 1
        if node.methods:
            self._print("Methods:")
            self.indent += 1
            for method in node.methods:
                method.accept(self)
            self.indent -= 1
        self.indent -= 1
    
    def visit_trait_declaration(self, node):
        self._print(f"Trait: {node.name}")
        self.indent += 1
        for method in node.methods:
            method.accept(self)
        self.indent -= 1
    
    def visit_block(self, node):
        self._print("Block")
        self.indent += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent -= 1
    
    def visit_expression_statement(self, node):
        self._print("ExpressionStatement")
        self.indent += 1
        node.expression.accept(self)
        self.indent -= 1
    
    def visit_return_statement(self, node):
        self._print("Return")
        if node.value:
            self.indent += 1
            node.value.accept(self)
            self.indent -= 1
    
    def visit_if_statement(self, node):
        self._print("If")
        self.indent += 1
        self._print("Condition:")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
        self._print("Then:")
        self.indent += 1
        node.then_branch.accept(self)
        self.indent -= 1
        if node.else_branch:
            self._print("Else:")
            self.indent += 1
            node.else_branch.accept(self)
            self.indent -= 1
        self.indent -= 1
    
    def visit_while_statement(self, node):
        self._print("While")
        self.indent += 1
        node.condition.accept(self)
        node.body.accept(self)
        self.indent -= 1
    
    def visit_for_statement(self, node):
        self._print(f"For {node.variable} in:")
        self.indent += 1
        node.iterable.accept(self)
        node.body.accept(self)
        self.indent -= 1
    
    def visit_break_statement(self, node):
        self._print("Break")
    
    def visit_continue_statement(self, node):
        self._print("Continue")
    
    def visit_assignment_statement(self, node):
        self._print(f"Assignment {node.operator}")
        self.indent += 1
        node.target.accept(self)
        node.value.accept(self)
        self.indent -= 1
    
    def visit_parallel_block(self, node):
        self._print("Parallel")
        self.indent += 1
        for task in node.tasks:
            task.accept(self)
        self.indent -= 1
    
    def visit_async_await(self, node):
        self._print("Await")
        self.indent += 1
        node.expression.accept(self)
        self.indent -= 1
    
    def visit_import_statement(self, node):
        if node.items:
            self._print(f"Import from {node.module}: {', '.join(node.items)}")
        else:
            alias = f" as {node.alias}" if node.alias else ""
            self._print(f"Import {node.module}{alias}")
    
    def visit_program(self, node):
        self._print("Program")
        self.indent += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent -= 1
