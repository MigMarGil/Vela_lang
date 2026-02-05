#!/usr/bin/env python3
"""
Vela CLI - Interfaz
Comandos: run, compile, check, repl, build
"""

import sys
import argparse
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.frontend.lexer import Lexer
from src.frontend.parser import Parser
from src.frontend.types import TypeChecker
from src.frontend.ast import ASTPrinter
from src.backend.llvm_compiler import LLVMCompiler

class VelaCLI:
    def __init__(self):
        self.version = "0.0.32"
        self.banner = """
╦  ╦╔═╗╦  ╔═╗
╚╗╔╝║╣ ║  ╠═╣
 ╚╝ ╚═╝╩═╝╩ ╩
Version {}
""".format(self.version)
    
    def run_file(self, filepath: str, optimize: bool = False, verbose: bool = False):
        """Ejecuta un archivo .vela"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            if verbose:
                print(f"Leyendo: {filepath}")
            
            # Lexer
            if verbose:
                print("Análisis léxico...")
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            if verbose:
                print(f"✓ {len(tokens)} tokens generados")
            
            # Parser
            if verbose:
                print("Análisis sintáctico...")
            parser = Parser(tokens)
            ast = parser.parse()
            
            if verbose:
                print("✓ AST generado")
                print("\n--- AST ---")
                printer = ASTPrinter()
                ast.accept(printer)
                print()
            
            # Type Checker
            if verbose:
                print("Verificación de tipos...")
            type_checker = TypeChecker()
            if not type_checker.check_program(ast):
                print("Errores de tipos encontrados:")
                for error in type_checker.errors:
                    print(f"  • {error}")
                return 1
            
            if verbose:
                print("✓ Tipos correctos")
            
            # Compilar
            if verbose:
                print("Compilando a LLVM IR...")
            compiler = LLVMCompiler()
            llvm_ir = compiler.compile_program(ast)
            
            if verbose:
                print("✓ Código LLVM generado")
                print("\n--- LLVM IR ---")
                print(llvm_ir)
                print()
            
            # Optimizar si se solicita
            if optimize:
                if verbose:
                    print("Optimizando código...")
                llvm_ir = compiler.optimize(optimization_level=3)
                if verbose:
                    print("✓ Código optimizado")
            
            # Por ahora, solo mostramos el IR
            # TODO: Ejecutar con JIT
            if verbose:
                print("Ejecutando programa...")
                print("--- Output ---")

            try:
                from src.backend.vela_executor import VelaExecutor
                executor = VelaExecutor(llvm_ir)
                executor.run_main()
                executor.cleanup()
                
                if verbose:
                    print("\n Ejecución completada!")
                
            except Exception as e:
                print(f"\n Error durante la ejecución: {e}")
                if verbose:
                    import traceback
                    traceback.print_exc()
                return 1
            
            return 0            
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {filepath}")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def compile_file(self, filepath: str, output: str = None, optimize: bool = True):
        """Compila un archivo .vela a código objeto"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            print(f"Compilando: {filepath}")
            
            # Pipeline completo
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            type_checker = TypeChecker()
            if not type_checker.check_program(ast):
                print("Errores de tipos:")
                for error in type_checker.errors:
                    print(f"  • {error}")
                return 1
            
            compiler = LLVMCompiler()
            llvm_ir = compiler.compile_program(ast)
            
            if output is None:
                output = Path(filepath).stem
            
            # Usar compilador AOT
            from src.backend.vela_aot import VelaAOTCompiler
            aot = VelaAOTCompiler()
            
            if optimize:
                print("Optimizando con -O3...")
            
            print(f"Generando ejecutable nativo...")
            aot.compile_to_executable(llvm_ir, output, optimize=optimize)
            
            print(f"Compilación exitosa: {output}")
            print(f"   Ejecuta con: ./{output}")
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def check_file(self, filepath: str):
        """Solo verifica sintaxis y tipos sin compilar"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            print(f"Verificando: {filepath}")
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            print("✓ Análisis léxico correcto")
            
            parser = Parser(tokens)
            ast = parser.parse()
            print("✓ Análisis sintáctico correcto")
            
            type_checker = TypeChecker()
            if type_checker.check_program(ast):
                print("✓ Tipos correctos")
                print("\nTodo correcto!")
                return 0
            else:
                print("Errores de tipos:")
                for error in type_checker.errors:
                    print(f"  • {error}")
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def repl(self):
        """REPL interactivo"""
        print(self.banner)
        print("Modo interactivo - Escribe 'exit' para salir\n")
        
        env_vars = {}
        
        while True:
            try:
                line = input("vela> ")
                
                if line.strip() in ['exit', 'quit']:
                    print("Closed!")
                    break
                
                if not line.strip():
                    continue
                
                # Ejecutar línea
                lexer = Lexer(line)
                tokens = lexer.tokenize()
                
                parser = Parser(tokens)
                ast = parser.parse()
                
                type_checker = TypeChecker()
                if not type_checker.check_program(ast):
                    for error in type_checker.errors:
                        print(f"Error: {error}")
                    continue
                
                # Por ahora solo mostramos que es válido
                print("✓")
                
            except KeyboardInterrupt:
                print("\nClosed!")
                break
            except EOFError:
                print("\nClosed!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_examples(self):
        """Muestra ejemplos de código Vela"""
        examples = """
Ejemplos de Vela - El Mejor Lenguaje del Mundo

1. Hola Mundo:
   func main() -> void {
       print("¡Hola, Mundo!")
   }

2. Funciones:
   func factorial(n: int) -> int {
       if n <= 1 {
           return 1
       }
       return n * factorial(n - 1)
   }

3. Inferencia de tipos:
   auto x = 42          # int
   auto y = 3.14        # float
   auto name = "Vela"   # str

4. Pipeline operator:
   [1, 2, 3, 4, 5]
       |> map(|x| x * 2)
       |> filter(|x| x > 5)
       |> sum()

5. Pattern Matching:
   match value {
       0 => "cero",
       1 => "uno",
       _ => "otro"
   }

6. Async/Await:
   async func fetch_data(url: str) -> str {
       auto response = await http_get(url)
       return response
   }

7. Clases y Traits:
   trait Drawable {
       func draw() -> void
   }
   
   class Circle : Drawable {
       float radius
       
       func draw() -> void {
           print("Dibujando círculo")
       }
   }

8. Ejecución Paralela:
   parallel {
       task1()
       task2()
       task3()
   }
"""
        print(examples)

def main():
    cli = VelaCLI()
    
    parser = argparse.ArgumentParser(
        description="Vela - El Mejor Lenguaje de Programación del Mundo",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: run
    run_parser = subparsers.add_parser('run', help='Ejecuta un archivo .vela')
    run_parser.add_argument('file', help='Archivo a ejecutar')
    run_parser.add_argument('-O', '--optimize', action='store_true', help='Optimizar código')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Modo verboso')
    
    # Comando: compile
    compile_parser = subparsers.add_parser('compile', help='Compila a código objeto')
    compile_parser.add_argument('file', help='Archivo a compilar')
    compile_parser.add_argument('-o', '--output', help='Archivo de salida')
    compile_parser.add_argument('--no-optimize', action='store_true', help='Sin optimizaciones')
    
    # Comando: check
    check_parser = subparsers.add_parser('check', help='Verifica sintaxis y tipos')
    check_parser.add_argument('file', help='Archivo a verificar')
    
    # Comando: repl
    subparsers.add_parser('repl', help='Inicia REPL interactivo')
    
    # Comando: examples
    subparsers.add_parser('examples', help='Muestra ejemplos de código')
    
    # Comando: version
    subparsers.add_parser('version', help='Muestra versión')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        return cli.run_file(args.file, args.optimize, args.verbose)
    elif args.command == 'compile':
        return cli.compile_file(args.file, args.output, not args.no_optimize)
    elif args.command == 'check':
        return cli.check_file(args.file)
    elif args.command == 'repl':
        cli.repl()
        return 0
    elif args.command == 'examples':
        cli.show_examples()
        return 0
    elif args.command == 'version':
        print(cli.banner)
        return 0
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())
