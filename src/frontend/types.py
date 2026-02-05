"""
Vela Type System - Sistema de Tipos
Inferencia de tipos, comprobación estática y tipos genéricos
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum, auto

class TypeKind(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    VOID = auto()
    NULL = auto()
    AUTO = auto()
    ARRAY = auto()
    FUNCTION = auto()
    CLASS = auto()
    TRAIT = auto()
    GENERIC = auto()

@dataclass
class Type:
    kind: TypeKind
    name: str
    element_type: Optional['Type'] = None  # Para arrays
    param_types: Optional[List['Type']] = None  # Para funciones
    return_type: Optional['Type'] = None  # Para funciones
    generic_params: Optional[List[str]] = None  # Para tipos genéricos
    
    def __str__(self):
        if self.kind == TypeKind.ARRAY:
            return f"[{self.element_type}]"
        elif self.kind == TypeKind.FUNCTION:
            params = ", ".join(str(p) for p in self.param_types)
            return f"({params}) -> {self.return_type}"
        elif self.generic_params:
            params = ", ".join(self.generic_params)
            return f"{self.name}<{params}>"
        return self.name
    
    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        if self.kind != other.kind:
            return False
        if self.kind == TypeKind.ARRAY:
            return self.element_type == other.element_type
        if self.kind == TypeKind.FUNCTION:
            return (self.param_types == other.param_types and 
                    self.return_type == other.return_type)
        return self.name == other.name

# Tipos primitivos predefinidos
INT_TYPE = Type(TypeKind.INT, "int")
FLOAT_TYPE = Type(TypeKind.FLOAT, "float")
STRING_TYPE = Type(TypeKind.STRING, "str")
BOOL_TYPE = Type(TypeKind.BOOL, "bool")
VOID_TYPE = Type(TypeKind.VOID, "void")
NULL_TYPE = Type(TypeKind.NULL, "null")
AUTO_TYPE = Type(TypeKind.AUTO, "auto")

class TypeEnvironment:
    """Entorno de tipos para seguimiento de variables y funciones"""
    
    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.variables: Dict[str, Type] = {}
        self.functions: Dict[str, Type] = {}
        self.classes: Dict[str, 'ClassType'] = {}
        self.traits: Dict[str, 'TraitType'] = {}
    
    def define_variable(self, name: str, var_type: Type):
        self.variables[name] = var_type
    
    def get_variable(self, name: str) -> Optional[Type]:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_variable(name)
        return None
    
    def define_function(self, name: str, func_type: Type):
        self.functions[name] = func_type
    
    def get_function(self, name: str) -> Optional[Type]:
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None
    
    def define_class(self, name: str, class_type: 'ClassType'):
        self.classes[name] = class_type
    
    def get_class(self, name: str) -> Optional['ClassType']:
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class(name)
        return None
    
    def define_trait(self, name: str, trait_type: 'TraitType'):
        self.traits[name] = trait_type
    
    def get_trait(self, name: str) -> Optional['TraitType']:
        if name in self.traits:
            return self.traits[name]
        if self.parent:
            return self.parent.get_trait(name)
        return None

@dataclass
class ClassType:
    name: str
    fields: Dict[str, Type]
    methods: Dict[str, Type]
    traits: List[str]

@dataclass
class TraitType:
    name: str
    methods: Dict[str, Type]

class TypeChecker:
    """Verificador de tipos con inferencia automática"""
    
    def __init__(self):
        self.env = TypeEnvironment()
        self.errors: List[str] = []
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Define funciones y tipos built-in"""
        # print(x: auto) -> void
        print_type = Type(
            TypeKind.FUNCTION,
            "print",
            param_types=[AUTO_TYPE],
            return_type=VOID_TYPE
        )
        self.env.define_function("print", print_type)
        
        # len(arr: [T]) -> int
        len_type = Type(
            TypeKind.FUNCTION,
            "len",
            param_types=[Type(TypeKind.ARRAY, "array", element_type=AUTO_TYPE)],
            return_type=INT_TYPE
        )
        self.env.define_function("len", len_type)
        
        # range(n: int) -> [int]
        range_type = Type(
            TypeKind.FUNCTION,
            "range",
            param_types=[INT_TYPE],
            return_type=Type(TypeKind.ARRAY, "array", element_type=INT_TYPE)
        )
        self.env.define_function("range", range_type)
        
        str_type = Type(
        TypeKind.FUNCTION,
        "str",
        param_types=[AUTO_TYPE],
        return_type=STRING_TYPE
        )
        self.env.define_function("str", str_type)    
        
        range2_type = Type(
        TypeKind.FUNCTION,
        "range",
        param_types=[INT_TYPE, INT_TYPE],
        return_type=Type(TypeKind.ARRAY, "array", element_type=INT_TYPE)
        )
        self.env.define_function("range", range2_type)
    
    def error(self, message: str):
        self.errors.append(message)
    
    def parse_type_string(self, type_str: str) -> Type:
        """Convierte string de tipo a objeto Type"""
        if type_str == "int":
            return INT_TYPE
        elif type_str == "float":
            return FLOAT_TYPE
        elif type_str == "str":
            return STRING_TYPE
        elif type_str == "bool":
            return BOOL_TYPE
        elif type_str == "void":
            return VOID_TYPE
        elif type_str == "auto":
            return AUTO_TYPE
        else:
            # Puede ser un tipo de clase
            return Type(TypeKind.CLASS, type_str)
    
    def can_assign(self, target: Type, source: Type) -> bool:
        """Verifica si source puede asignarse a target"""
        # auto acepta cualquier cosa
        if target.kind == TypeKind.AUTO:
            return True
        
        # Igualdad directa
        if target == source:
            return True
        
        # null puede asignarse a cualquier tipo de referencia
        if source.kind == TypeKind.NULL:
            return target.kind in [TypeKind.CLASS, TypeKind.STRING, TypeKind.ARRAY]
        
        # Promoción numérica: int -> float
        if target.kind == TypeKind.FLOAT and source.kind == TypeKind.INT:
            return True
        
        return False
    
    def infer_type(self, node) -> Type:
        """Infiere el tipo de una expresión"""
        from src.frontend.ast import (
            NumberLiteral, StringLiteral, BooleanLiteral, NullLiteral,
            Identifier, BinaryOp, UnaryOp, CallExpr, ArrayLiteral,
            LambdaExpr
        )
        
        if isinstance(node, NumberLiteral):
            if isinstance(node.value, int):
                return INT_TYPE
            return FLOAT_TYPE
        
        elif isinstance(node, StringLiteral):
            return STRING_TYPE
        
        elif isinstance(node, BooleanLiteral):
            return BOOL_TYPE
        
        elif isinstance(node, NullLiteral):
            return NULL_TYPE
        
        elif isinstance(node, Identifier):
            var_type = self.env.get_variable(node.name)
            if var_type is None:
                self.error(f"Variable indefinida: {node.name}")
                return AUTO_TYPE
            return var_type
        
        elif isinstance(node, BinaryOp):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)
            
            # Operaciones aritméticas
            if node.operator in ['+', '-', '*', '/', '%', '**']:
                if left_type.kind == TypeKind.FLOAT or right_type.kind == TypeKind.FLOAT:
                    return FLOAT_TYPE
                return INT_TYPE
            
            # Comparaciones
            elif node.operator in ['==', '!=', '<', '>', '<=', '>=']:
                return BOOL_TYPE
            
            # Lógicos
            elif node.operator in ['and', 'or']:
                return BOOL_TYPE
        
        elif isinstance(node, UnaryOp):
            operand_type = self.infer_type(node.operand)
            
            if node.operator == 'not':
                return BOOL_TYPE
            elif node.operator == '-':
                return operand_type
        
        elif isinstance(node, CallExpr):
            # Obtener tipo de la función
            if isinstance(node.callee, Identifier):
                func_type = self.env.get_function(node.callee.name)
                if func_type:
                    return func_type.return_type
        
        elif isinstance(node, ArrayLiteral):
            if not node.elements:
                return Type(TypeKind.ARRAY, "array", element_type=AUTO_TYPE)
            element_type = self.infer_type(node.elements[0])
            return Type(TypeKind.ARRAY, "array", element_type=element_type)
        
        elif isinstance(node, LambdaExpr):
            param_types = [self.parse_type_string(t) for _, t in node.parameters]
            return_type = VOID_TYPE if node.return_type is None else self.parse_type_string(node.return_type)
            return Type(TypeKind.FUNCTION, "lambda", param_types=param_types, return_type=return_type)
        
        return AUTO_TYPE
    
    def check_function(self, func_decl):
        """Verifica los tipos de una función"""
        from src.frontend.ast import FunctionDeclaration
        
        # Crear nuevo entorno para la función
        func_env = TypeEnvironment(self.env)
        old_env = self.env
        self.env = func_env
        
        # Definir parámetros
        param_types = []
        for param_name, param_type_str in func_decl.parameters:
            param_type = self.parse_type_string(param_type_str)
            param_types.append(param_type)
            self.env.define_variable(param_name, param_type)
        
        # Registrar función en el entorno padre
        return_type = self.parse_type_string(func_decl.return_type)
        func_type = Type(
            TypeKind.FUNCTION,
            func_decl.name,
            param_types=param_types,
            return_type=return_type
        )
        old_env.define_function(func_decl.name, func_type)
        
        # Verificar cuerpo
        self.check_block(func_decl.body)
        
        # Restaurar entorno
        self.env = old_env
    
    def check_block(self, block):
        """Verifica un bloque de código"""
        for stmt in block.statements:
            self.check_statement(stmt)
    
    def check_statement(self, stmt):
        """Verifica una sentencia"""
        from src.frontend.ast import (
            VarDeclaration, FunctionDeclaration, ReturnStatement,
            AssignmentStatement, ExpressionStatement, IfStatement,
            WhileStatement, ForStatement
        )
        
        if isinstance(stmt, VarDeclaration):
            if stmt.initializer:
                init_type = self.infer_type(stmt.initializer)
                if stmt.var_type and stmt.var_type != "auto":
                    declared_type = self.parse_type_string(stmt.var_type)
                    if not self.can_assign(declared_type, init_type):
                        self.error(f"No se puede asignar {init_type} a {declared_type}")
                    self.env.define_variable(stmt.name, declared_type)
                else:
                    self.env.define_variable(stmt.name, init_type)
            else:
                if stmt.var_type:
                    self.env.define_variable(stmt.name, self.parse_type_string(stmt.var_type))
        
        elif isinstance(stmt, FunctionDeclaration):
            self.check_function(stmt)
        
        elif isinstance(stmt, AssignmentStatement):
            target_type = self.infer_type(stmt.target)
            value_type = self.infer_type(stmt.value)
            if not self.can_assign(target_type, value_type):
                self.error(f"No se puede asignar {value_type} a {target_type}")
        
        elif isinstance(stmt, ExpressionStatement):
            self.infer_type(stmt.expression)
        
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self.infer_type(stmt.value)
        
        elif isinstance(stmt, IfStatement):
            cond_type = self.infer_type(stmt.condition)
            if cond_type.kind != TypeKind.BOOL:
                self.error(f"La condición del if debe ser bool, no {cond_type}")
            self.check_statement(stmt.then_branch)
            if stmt.else_branch:
                self.check_statement(stmt.else_branch)
        
        elif isinstance(stmt, WhileStatement):
            cond_type = self.infer_type(stmt.condition)
            if cond_type.kind != TypeKind.BOOL:
                self.error(f"La condición del while debe ser bool, no {cond_type}")
            self.check_statement(stmt.body)
    
    def check_program(self, program):
        """Verifica todo el programa"""
        for stmt in program.statements:
            self.check_statement(stmt)
        
        return len(self.errors) == 0
