from llvmlite import ir, binding
import ctypes

class VelaExecutor:
    def __init__(self, llvm_ir: str):
        self.llvm_ir = llvm_ir
        self.engine = None
        self.module = None
        
        self.module = binding.parse_assembly(llvm_ir)
        self.module.verify()
        
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        backing_mod = binding.parse_assembly("")
        self.engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    
    def execute_function(self, func_name: str, *args):
        try:
            self.engine.add_module(self.module)
            self.engine.finalize_object()
            
            func_ptr = self.engine.get_function_address(func_name)
            
            if func_ptr == 0:
                raise RuntimeError(f"Función '{func_name}' no encontrada")
            
            cfunc = ctypes.CFUNCTYPE(None)(func_ptr)
            
            result = cfunc(*args)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Error ejecutando {func_name}: {e}")
    
    def run_main(self):
        return self.execute_function("main")
    
    def cleanup(self):
        if self.engine:
            self.engine.remove_module(self.module)
