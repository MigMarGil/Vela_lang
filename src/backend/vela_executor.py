"""
Vela Executor - Ejecuta código compilado usando LLVM JIT
"""

from llvmlite import ir, binding
import ctypes

class VelaExecutor:
    def __init__(self, llvm_ir: str):
        """Inicializa el ejecutor con LLVM IR"""
        self.llvm_ir = llvm_ir
        self.engine = None
        self.module = None
        
        # Parsear el módulo
        self.module = binding.parse_assembly(llvm_ir)
        self.module.verify()
        
        # Crear motor de ejecución
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        # Crear motor JIT
        backing_mod = binding.parse_assembly("")
        self.engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    
    def execute_function(self, func_name: str, *args):
        """Ejecuta una función del módulo"""
        try:
            # Agregar el módulo al motor
            self.engine.add_module(self.module)
            self.engine.finalize_object()
            
            # Obtener dirección de la función
            func_ptr = self.engine.get_function_address(func_name)
            
            if func_ptr == 0:
                raise RuntimeError(f"Función '{func_name}' no encontrada")
            
            # Crear función callable de Python
            # Por ahora asumimos void() para main
            cfunc = ctypes.CFUNCTYPE(None)(func_ptr)
            
            # Ejecutar
            result = cfunc(*args)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Error ejecutando {func_name}: {e}")
    
    def run_main(self):
        """Ejecuta la función main del programa"""
        return self.execute_function("main")
    
    def cleanup(self):
        """Limpia recursos"""
        if self.engine:
            self.engine.remove_module(self.module)
