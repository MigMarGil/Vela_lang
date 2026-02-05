"""
Vela AOT Compiler - Compilación Ahead-of-Time a binarios nativos
Compatible con llvmlite 0.40+
"""

import subprocess
import os
import tempfile
from pathlib import Path
from llvmlite import binding

class VelaAOTCompiler:
    def __init__(self):
        self.optimization_level = 3
    
    def compile_to_executable(self, llvm_ir: str, output_path: str, optimize: bool = True):
        """Compila LLVM IR a ejecutable nativo"""
        module = binding.parse_assembly(llvm_ir)
        module.verify()
        
        # Configurar target con optimizaciones
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(
            opt=3,  # Optimización máxima
            reloc='pic',
            codemodel='default',
            features='+sse2,+avx' if self._supports_avx() else ''
        )
        
        # Generar código objeto optimizado
        obj_code = target_machine.emit_object(module)
        
        # Escribir archivo objeto temporal
        with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as obj_file:
            obj_file.write(obj_code)
            obj_path = obj_file.name
        
        try:
            # Linkar con gcc
            link_cmd = [
                'gcc',
                obj_path,
                '-o', output_path,
                '-lm',  # Librería matemática
                '-O3',  # Optimización en linker
                '-march=native',  # Optimizar para CPU actual
                '-ffast-math',  # Matemáticas rápidas
                '-no-pie'  # No Position Independent
            ]
            
            result = subprocess.run(link_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Error linkando: {result.stderr}")
            
            # Hacer ejecutable
            os.chmod(output_path, 0o755)
            return True
            
        finally:
            # Limpiar archivo objeto
            if os.path.exists(obj_path):
                os.remove(obj_path)
    
    def _supports_avx(self):
        """Detecta si la CPU soporta AVX"""
        try:
            result = subprocess.run(['grep', 'avx', '/proc/cpuinfo'], 
                                    capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def compile_to_object(self, llvm_ir: str, output_path: str):
        """Compila a archivo objeto .o"""
        module = binding.parse_assembly(llvm_ir)
        module.verify()
        
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=3)
        
        obj_code = target_machine.emit_object(module)
        
        with open(output_path, 'wb') as f:
            f.write(obj_code)
        
        return output_path
