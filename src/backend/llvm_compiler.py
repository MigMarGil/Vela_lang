"""
Vela LLVM Compiler - Backend de Compilación
Genera código máquina optimizado mediante LLVM
"""

from llvmlite import ir, binding
from src.frontend.ast import *
from src.frontend.types import *

class LLVMCompiler:
    def __init__(self):
        # LLVM ya se inicializa automáticamente en llvmlite >= 0.40
        # Removidas las llamadas a initialize() que están deprecated
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        
        # Módulo LLVM
        self.module = ir.Module(name="vela_module")
        self.module.triple = binding.get_default_triple()
        
        # Builder para instrucciones
        self.builder = None
        
        # Tablas de símbolos
        self.variables = {}
        self.functions = {}
        
        # Tipos LLVM - usar i64 por defecto para evitar overflow
        self.i32 = ir.IntType(32)
        self.i64 = ir.IntType(64)
        self.f64 = ir.DoubleType()
        self.i1 = ir.IntType(1)
        self.void = ir.VoidType()
        self.i8_ptr = ir.IntType(8).as_pointer()
        
        # Usar i64 como tipo por defecto para int
        self.default_int = self.i64
        
        # Función actual
        self.current_function = None
        
        # Setup funciones built-in
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Define funciones built-in de C que usaremos"""
        # printf
        printf_ty = ir.FunctionType(self.i32, [self.i8_ptr], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        
        # malloc
        malloc_ty = ir.FunctionType(self.i8_ptr, [self.i64])
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")
        
        # free
        free_ty = ir.FunctionType(self.void, [self.i8_ptr])
        self.free = ir.Function(self.module, free_ty, name="free")
    
    def get_llvm_type(self, vela_type: Type) -> ir.Type:
        """Convierte tipo de Vela a tipo LLVM"""
        if vela_type.kind == TypeKind.INT:
            return self.i64  # Usar i64 para evitar overflow
        elif vela_type.kind == TypeKind.FLOAT:
            return self.f64
        elif vela_type.kind == TypeKind.BOOL:
            return self.i1
        elif vela_type.kind == TypeKind.VOID:
            return self.void
        elif vela_type.kind == TypeKind.STRING:
            return self.i8_ptr
        elif vela_type.kind == TypeKind.ARRAY:
            # Arrays como punteros
            elem_type = self.get_llvm_type(vela_type.element_type)
            return elem_type.as_pointer()
        else:
            return self.i64  # Default i64
    
    def compile_program(self, program: Program) -> str:
        """Compila un programa completo"""
        for stmt in program.statements:
            self.compile_statement(stmt)
        
        return str(self.module)
    
    def compile_statement(self, stmt: ASTNode):
        """Compila una sentencia"""
        if isinstance(stmt, FunctionDeclaration):
            self.compile_function(stmt)
        elif isinstance(stmt, VarDeclaration):
            self.compile_var_declaration(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self.compile_expression(stmt.expression)
        elif isinstance(stmt, ReturnStatement):
            self.compile_return(stmt)
        elif isinstance(stmt, IfStatement):
            self.compile_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self.compile_while(stmt)
        elif isinstance(stmt, ForStatement):
            self.compile_for(stmt)
        elif isinstance(stmt, AssignmentStatement):
            self.compile_assignment(stmt)
        elif isinstance(stmt, Block):
            self.compile_block(stmt)
    
    def compile_function(self, func: FunctionDeclaration):
        """Compila una función"""
        # Tipos de parámetros
        param_types = []
        for _, param_type_str in func.parameters:
            param_type = Type(TypeKind.INT, "int")  # Simplificado
            param_types.append(self.get_llvm_type(param_type))
        
        # Tipo de retorno
        return_type_obj = Type(TypeKind.INT, "int") if func.return_type == "int" else Type(TypeKind.VOID, "void")
        return_type = self.get_llvm_type(return_type_obj)
        
        # Crear función
        func_type = ir.FunctionType(return_type, param_types)
        llvm_func = ir.Function(self.module, func_type, name=func.name)
        
        # Crear bloque de entrada
        block = llvm_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.current_function = llvm_func
        
        # Registrar función
        self.functions[func.name] = llvm_func
        
        # Asignar nombres a parámetros y crear variables locales
        for i, (param_name, _) in enumerate(func.parameters):
            param = llvm_func.args[i]
            param.name = param_name
            # Crear variable local en stack
            ptr = self.builder.alloca(param.type, name=param_name)
            self.builder.store(param, ptr)
            self.variables[param_name] = ptr
        
        # Compilar cuerpo
        self.compile_block(func.body)
        
        # Si no hay return explícito, añadir return void
        if not self.builder.block.is_terminated:
            if return_type == self.void:
                self.builder.ret_void()
            else:
                self.builder.ret(ir.Constant(return_type, 0))
        
        self.builder = None
        self.current_function = None
    
    def compile_var_declaration(self, var: VarDeclaration):
        """Compila una declaración de variable"""
        if not self.builder:
            return
        
        # Tipo de variable - usar i64 por defecto
        var_type = self.i64
        
        # Alocar en stack
        ptr = self.builder.alloca(var_type, name=var.name)
        
        # Inicializar si hay valor
        if var.initializer:
            value = self.compile_expression(var.initializer)
            self.builder.store(value, ptr)
        
        self.variables[var.name] = ptr
    
    def compile_assignment(self, assign: AssignmentStatement):
        """Compila una asignación"""
        if not isinstance(assign.target, Identifier):
            raise NotImplementedError("Solo se soportan asignaciones a variables simples")
        
        var_name = assign.target.name
        if var_name not in self.variables:
            raise NameError(f"Variable no definida: {var_name}")
        
        value = self.compile_expression(assign.value)
        ptr = self.variables[var_name]
        self.builder.store(value, ptr)
    
    def compile_return(self, ret: ReturnStatement):
        """Compila un return"""
        if ret.value:
            value = self.compile_expression(ret.value)
            self.builder.ret(value)
        else:
            self.builder.ret_void()
    
    def compile_if(self, if_stmt: IfStatement):
        """Compila un if statement"""
        condition = self.compile_expression(if_stmt.condition)
        
        # Crear bloques
        then_block = self.current_function.append_basic_block("if.then")
        else_block = self.current_function.append_basic_block("if.else") if if_stmt.else_branch else None
        merge_block = self.current_function.append_basic_block("if.end")
        
        # Branch condicional
        if else_block:
            self.builder.cbranch(condition, then_block, else_block)
        else:
            self.builder.cbranch(condition, then_block, merge_block)
        
        # Compilar then
        self.builder.position_at_end(then_block)
        self.compile_statement(if_stmt.then_branch)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
        
        # Compilar else
        if else_block:
            self.builder.position_at_end(else_block)
            self.compile_statement(if_stmt.else_branch)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)
        
        # Continuar en merge
        self.builder.position_at_end(merge_block)
    
    def compile_while(self, while_stmt: WhileStatement):
        """Compila un while loop"""
        cond_block = self.current_function.append_basic_block("while.cond")
        body_block = self.current_function.append_basic_block("while.body")
        end_block = self.current_function.append_basic_block("while.end")
        
        # Saltar a condición
        self.builder.branch(cond_block)
        
        # Bloque de condición
        self.builder.position_at_end(cond_block)
        condition = self.compile_expression(while_stmt.condition)
        self.builder.cbranch(condition, body_block, end_block)
        
        # Bloque de cuerpo
        self.builder.position_at_end(body_block)
        self.compile_statement(while_stmt.body)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)
        
        # Continuar después del loop
        self.builder.position_at_end(end_block)
    
    def compile_for(self, for_stmt: ForStatement):
        """Compila un for loop - simplificado"""
        # Por ahora, convertir a while
        # TODO: Implementar iteradores propios
        pass
    
    def compile_block(self, block: Block):
        """Compila un bloque de código"""
        for stmt in block.statements:
            self.compile_statement(stmt)
    
    def compile_expression(self, expr: ASTNode):
        """Compila una expresión y retorna su valor"""
        if isinstance(expr, NumberLiteral):
            if isinstance(expr.value, int):
                return ir.Constant(self.i64, expr.value)  # i64 para evitar overflow
            else:
                return ir.Constant(self.f64, expr.value)
        
        elif isinstance(expr, BooleanLiteral):
            return ir.Constant(self.i1, int(expr.value))
        
        elif isinstance(expr, Identifier):
            if expr.name not in self.variables:
                raise NameError(f"Variable no definida: {expr.name}")
            ptr = self.variables[expr.name]
            return self.builder.load(ptr, name=expr.name)
        
        elif isinstance(expr, BinaryOp):
            left = self.compile_expression(expr.left)
            right = self.compile_expression(expr.right)
            
            if expr.operator == '+':
                if left.type == self.f64:
                    return self.builder.fadd(left, right)
                return self.builder.add(left, right)
            elif expr.operator == '-':
                if left.type == self.f64:
                    return self.builder.fsub(left, right)
                return self.builder.sub(left, right)
            elif expr.operator == '*':
                if left.type == self.f64:
                    return self.builder.fmul(left, right)
                return self.builder.mul(left, right)
            elif expr.operator == '/':
                if left.type == self.f64:
                    return self.builder.fdiv(left, right)
                return self.builder.sdiv(left, right)
            elif expr.operator == '%':
                return self.builder.srem(left, right)
            elif expr.operator == '**':
                # Potencia - simplificado
                return self.builder.mul(left, right)
            elif expr.operator == '==':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('==', left, right)
                return self.builder.icmp_signed('==', left, right)
            elif expr.operator == '!=':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('!=', left, right)
                return self.builder.icmp_signed('!=', left, right)
            elif expr.operator == '<':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('<', left, right)
                return self.builder.icmp_signed('<', left, right)
            elif expr.operator == '>':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('>', left, right)
                return self.builder.icmp_signed('>', left, right)
            elif expr.operator == '<=':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('<=', left, right)
                return self.builder.icmp_signed('<=', left, right)
            elif expr.operator == '>=':
                if left.type == self.f64:
                    return self.builder.fcmp_ordered('>=', left, right)
                return self.builder.icmp_signed('>=', left, right)
            elif expr.operator == 'and':
                return self.builder.and_(left, right)
            elif expr.operator == 'or':
                return self.builder.or_(left, right)
        
        elif isinstance(expr, UnaryOp):
            operand = self.compile_expression(expr.operand)
            
            if expr.operator == '-':
                if operand.type == self.f64:
                    return self.builder.fsub(ir.Constant(self.f64, 0), operand)
                return self.builder.sub(ir.Constant(self.i64, 0), operand)
            elif expr.operator == 'not':
                return self.builder.not_(operand)
        
        elif isinstance(expr, CallExpr):
            if isinstance(expr.callee, Identifier):
                func_name = expr.callee.name
                
                # Función print especial
                if func_name == "print":
                    return self.compile_print(expr.arguments)
                
                # Otras funciones
                if func_name not in self.functions:
                    raise NameError(f"Función no definida: {func_name}")
                
                func = self.functions[func_name]
                args = [self.compile_expression(arg) for arg in expr.arguments]
                return self.builder.call(func, args)
        
        return ir.Constant(self.i64, 0)  # Default i64
    
    def compile_print(self, args):
        """Compila llamada a print"""
        if not args:
            return None
        
        # Caso especial: si es un string literal, imprimirlo directamente
        if isinstance(args[0], StringLiteral):
            string_value = args[0].value + "\n"
            
            # Crear string constante
            string_bytes = bytearray(string_value.encode('utf-8')) + bytearray([0])
            string_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(string_bytes)), string_bytes)
            string_global = ir.GlobalVariable(self.module, string_const.type, name=f"str_{id(args[0])}")
            string_global.linkage = 'internal'
            string_global.global_constant = True
            string_global.initializer = string_const
            
            # Obtener puntero
            string_ptr = self.builder.bitcast(string_global, self.i8_ptr)
            
            # Formato simple para strings
            fmt = "%s\0"
            fmt_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode('utf-8')))
            fmt_global = ir.GlobalVariable(self.module, fmt_const.type, name=f"fmt_{id(args[0])}")
            fmt_global.linkage = 'internal'
            fmt_global.global_constant = True
            fmt_global.initializer = fmt_const
            fmt_ptr = self.builder.bitcast(fmt_global, self.i8_ptr)
            
            # Llamar a printf con el string
            return self.builder.call(self.printf, [fmt_ptr, string_ptr])
        
        # Para otros tipos de expresiones
        arg = self.compile_expression(args[0])
        
        # Crear formato string basado en tipo
        if arg.type == self.i64 or arg.type == self.i32:
            fmt = "%ld\n\0"  # Usar %ld para i64
        elif arg.type == self.f64:
            fmt = "%f\n\0"
        else:
            fmt = "%p\n\0"
        
        # Crear string constante
        fmt_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode('utf-8')))
        fmt_global = ir.GlobalVariable(self.module, fmt_const.type, name=f"fmt_{id(arg)}")
        fmt_global.linkage = 'internal'
        fmt_global.global_constant = True
        fmt_global.initializer = fmt_const
        
        # Obtener puntero al primer elemento
        fmt_ptr = self.builder.bitcast(fmt_global, self.i8_ptr)
        
        # Llamar a printf
        return self.builder.call(self.printf, [fmt_ptr, arg])
    
    def generate_object_code(self) -> bytes:
        """Genera código objeto"""
        llvm_ir = str(self.module)
        mod = binding.parse_assembly(llvm_ir)
        mod.verify()
        
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        return target_machine.emit_object(mod)
    
    def optimize(self, optimization_level=2):
        """Optimiza el módulo LLVM"""
        llvm_ir = str(self.module)
        mod = binding.parse_assembly(llvm_ir)
        
        pmb = binding.PassManagerBuilder()
        pmb.opt_level = optimization_level
        
        pm = binding.ModulePassManager()
        pmb.populate(pm)
        
        pm.run(mod)
        
        return str(mod)
