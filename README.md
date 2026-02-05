# Vela (ENGLISH)
```
╦  ╦╔═╗╦  ╔═╗
╚╗╔╝║╣ ║  ╠═╣
 ╚╝ ╚═╝╩═╝╩ ╩
```
**Vela** is a programming language that combines modern syntax elegance, LLVM compilation power, and advanced features like type inference, functional programming, async/await, and automatic parallel execution.

## Features

### Smart Type Inference
```vela
auto x = 42           # int
auto y = 3.14         # float
auto name = "Vela"    # str
auto items = [1, 2, 3] # [int]
```
### Pipeline Operator
```vela
[1, 2, 3, 4, 5]
    |> map(|x| x * 2)
    |> filter(|x| x > 5)
    |> sum()
    |> print()
```
### Pattern Matching
```vela
match value {
    0 => print("zero"),
    1 => print("one"),
    n if n < 0 => print("negative"),
    _ => print("other")
}
```

### Native Async/Await
```vela
async func fetch_data(url: str) -> str {
    auto response = await http_get(url)
    return response.body
}

async func main() -> void {
    auto data = await fetch_data("https://api.example.com")
    print(data)
}
```
### Automatic Parallel Execution
```vela
parallel {
    process_data_1(),
    process_data_2(),
    process_data_3()
}
```
### Object-Oriented Programming + Traits
```vela
trait Drawable {
    func draw() -> void
}

trait Movable {
    func move(x: int, y: int) -> void
}

class Circle : Drawable, Movable {
    float radius
    int x
    int y
    
    func draw() -> void {
        print("Drawing circle at (" + str(x) + ", " + str(y) + ")")
    }
    
    func move(dx: int, dy: int) -> void {
        x += dx
        y += dy
    }
}
```
### First-Class Functions
```vela
func map(arr: [int], f: |int| -> int) -> [int] {
    auto result = []
    for item in arr {
        result.push(f(item))
    }
    return result
}

auto doubled = map([1, 2, 3], |x| x * 2)
```
## Installation

### Requirements
- Python 3.8+
- LLVM 10+
- pip

### Quick Installation
```bash
git clone https://github.com/MigMarGil/vela.git
cd vela
chmod +x install.sh
./install.sh
```
### Manual Installation
```bash
pip install -r requirements.txt
pip install -e .
```
## Usage

### Run a file
```bash
vela run programa.vela
```
### Interactive mode (REPL)
```bash
vela repl
```
### Compile to object code
```bash
vela compile programa.vela -o programa.o
```
### Check syntax and types
```bash
vela check programa.vela
```
### View examples
```bash
vela examples
```
## Examples

### Hello World
```vela
func main() -> void {
    print("Hello, World!")
}
```
### Recursive Factorial
```vela
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

func main() -> void {
    print(factorial(5))  # 120
}
```
### FizzBuzz
```vela
func fizzbuzz(n: int) -> void {
    for i in range(1, n + 1) {
        match (i % 3, i % 5) {
            (0, 0) => print("FizzBuzz"),
            (0, _) => print("Fizz"),
            (_, 0) => print("Buzz"),
            _ => print(i)
        }
    }
}

func main() -> void {
    fizzbuzz(100)
}
```
### Async Web Server
```vela
import http

async func handle_request(req: Request) -> Response {
    auto data = await fetch_from_db(req.params.id)
    return Response(status=200, body=data)
}

async func main() -> void {
    auto server = http.Server(port=8080)
    server.on_request(handle_request)
    await server.start()
}
```
### Advanced Type System
```vela
trait Container<T> {
    func add(item: T) -> void
    func get(index: int) -> T
    func size() -> int
}

class Stack<T> : Container<T> {
    [T] items
    
    func add(item: T) -> void {
        items.push(item)
    }
    
    func get(index: int) -> T {
        return items[index]
    }
    
    func size() -> int {
        return len(items)
    }
    
    func pop() -> T {
        return items.pop()
    }
}

func main() -> void {
    auto stack = Stack<int>()
    stack.add(1)
    stack.add(2)
    stack.add(3)
    print(stack.pop())  # 3
}
```
## Architecture
```
vela/
├── bin/
│   └── vela              # Main executable
├── src/
│   ├── frontend/
│   │   ├── lexer.py      # Lexical analysis
│   │   ├── parser.py     # Syntactic analysis
│   │   ├── ast.py        # Abstract syntax tree
│   │   └── types.py      # Type system
│   ├── backend/
│   │   └── llvm_compiler.py  # LLVM compiler
│   └── cli/
│       └── vela_main.py  # Command-line interface
├── examples/             # Code examples
├── tests/               # Unit tests
├── requirements.txt     # Dependencies
├── setup.py            # Installation config
└── README.md           # This file
```
## Technical Features

- Native code compilation via LLVM
- Static type inference with generic support
- Functional programming with first-class functions and lambdas
- Object-oriented programming with classes and traits
- Async/Await for asynchronous programming
- Advanced pattern matching
- Pipeline operator for function composition
- Automatic parallel execution
- Aggressive compile-time optimizations
- Clean and expressive syntax

## Roadmap

- [x] Complete Lexer and Parser
- [x] Type system with inference
- [x] Compilation to LLVM IR
- [x] Functions and recursion
- [x] Control structures
- [x] Pattern matching
- [ ] JIT Execution
- [ ] Modules and imports
- [ ] Advanced memory management
- [ ] Complete standard library
- [ ] Package manager
- [ ] LSP (Language Server Protocol)
- [ ] Integrated debugger
- [ ] WebAssembly target

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a branch for your feature (git checkout -b feature/amazing)
3. Commit your changes (git commit -am 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Authors

- **Vela Team** - 
MiguelM_dev
...

## Acknowledgments

- To the LLVM community for their incredible infrastructure
- To all languages that inspired us: Rust, Swift, Python, Haskell, OCaml
- To the open-source community

---

Vela - Where code becomes art

________________________________________________

# Vela (ESPAÑOL)
```
╦  ╦╔═╗╦  ╔═╗
╚╗╔╝║╣ ║  ╠═╣
 ╚╝ ╚═╝╩═╝╩ ╩
```
**Vela** es un lenguaje de programación que combina la elegancia de la sintaxis moderna, el poder de la compilación LLVM, y características avanzadas como inferencia de tipos, programación funcional, async/await, y ejecución paralela automática.

## Características

### Inferencia de Tipos Inteligente
```vela
auto x = 42           # int
auto y = 3.14         # float
auto name = "Vela"    # str
auto items = [1, 2, 3] # [int]
```
### Pipeline Operator
```vela
[1, 2, 3, 4, 5]
    |> map(|x| x * 2)
    |> filter(|x| x > 5)
    |> sum()
    |> print()
```
### Pattern Matching
```vela
match value {
    0 => print("cero"),
    1 => print("uno"),
    n if n < 0 => print("negativo"),
    _ => print("otro")
}
```
### Async/Await Nativo
```vela
async func fetch_data(url: str) -> str {
    auto response = await http_get(url)
    return response.body
}

async func main() -> void {
    auto data = await fetch_data("https://api.example.com")
    print(data)
}
```
### Ejecución Paralela Automática
```vela
parallel {
    process_data_1(),
    process_data_2(),
    process_data_3()
}
```
### Programación Orientada a Objetos + Traits
```vela
trait Drawable {
    func draw() -> void
}

trait Movable {
    func move(x: int, y: int) -> void
}

class Circle : Drawable, Movable {
    float radius
    int x
    int y
    
    func draw() -> void {
        print("Dibujando círculo en (" + str(x) + ", " + str(y) + ")")
    }
    
    func move(dx: int, dy: int) -> void {
        x += dx
        y += dy
    }
}
```
### Funciones de Primera Clase
```vela
func map(arr: [int], f: |int| -> int) -> [int] {
    auto result = []
    for item in arr {
        result.push(f(item))
    }
    return result
}

auto doubled = map([1, 2, 3], |x| x * 2)
```
## Instalación

### Requisitos
- Python 3.8+
- LLVM 10+
- pip

### Instalación Rápida
```bash
git clone https://github.com/MigMarGil/Vela_lang.git
cd vela
chmod +x install.sh
./install.sh
```
### Instalación Manual
```bash
pip install -r requirements.txt
pip install -e .
```
## Uso

### Ejecutar un archivo
```bash
vela run programa.vela
```
### Modo interactivo (REPL)
```bash
vela repl
```
### Compilar a código objeto
```bash
vela compile programa.vela -o programa.o
```
### Verificar sintaxis y tipos
```bash
vela check programa.vela
```
### Ver ejemplos
```bash
vela examples
```
## Ejemplos

### Hola Mundo
```vela
func main() -> void {
    print("¡Hola, Mundo!")
}
```
### Factorial Recursivo
```vela
func factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

func main() -> void {
    print(factorial(5))  # 120
}
```
### FizzBuzz
```vela
func fizzbuzz(n: int) -> void {
    for i in range(1, n + 1) {
        match (i % 3, i % 5) {
            (0, 0) => print("FizzBuzz"),
            (0, _) => print("Fizz"),
            (_, 0) => print("Buzz"),
            _ => print(i)
        }
    }
}

func main() -> void {
    fizzbuzz(100)
}
```
### Servidor Web Async
```vela
import http

async func handle_request(req: Request) -> Response {
    auto data = await fetch_from_db(req.params.id)
    return Response(status=200, body=data)
}

async func main() -> void {
    auto server = http.Server(port=8080)
    server.on_request(handle_request)
    await server.start()
}
```
### Sistema de Tipos Avanzado
```vela
trait Container<T> {
    func add(item: T) -> void
    func get(index: int) -> T
    func size() -> int
}

class Stack<T> : Container<T> {
    [T] items
    
    func add(item: T) -> void {
        items.push(item)
    }
    
    func get(index: int) -> T {
        return items[index]
    }
    
    func size() -> int {
        return len(items)
    }
    
    func pop() -> T {
        return items.pop()
    }
}

func main() -> void {
    auto stack = Stack<int>()
    stack.add(1)
    stack.add(2)
    stack.add(3)
    print(stack.pop())  # 3
}
```
## Arquitectura
```
vela/
├── bin/
│   └── vela              # Ejecutable principal
├── src/
│   ├── frontend/
│   │   ├── lexer.py      # Análisis léxico
│   │   ├── parser.py     # Análisis sintáctico
│   │   ├── ast.py        # Árbol de sintaxis abstracta
│   │   └── types.py      # Sistema de tipos
│   ├── backend/
│   │   └── llvm_compiler.py  # Compilador LLVM
│   └── cli/
│       └── vela_main.py  # Interfaz de línea de comandos
├── examples/             # Ejemplos de código
├── tests/               # Tests unitarios
├── requirements.txt     # Dependencias
├── setup.py            # Configuración de instalación
└── README.md           # Este archivo
```
## Características Técnicas

- Compilación a código nativo mediante LLVM
- Inferencia de tipos estática con soporte para tipos genéricos
- Programación funcional con funciones de primera clase y lambdas
- Programación orientada a objetos con clases y traits
- Async/Await para programación asíncrona
- Pattern matching avanzado
- Pipeline operator para composición de funciones
- Ejecución paralela automática
- Optimizaciones agresivas en tiempo de compilación
- Sintaxis limpia y expresiva

## Roadmap

- [x] Lexer y Parser completos
- [x] Sistema de tipos con inferencia
- [x] Compilación a LLVM IR
- [x] Funciones y recursión
- [x] Estructuras de control
- [x] Pattern matching
- [ ] JIT Execution
- [ ] Módulos e imports
- [ ] Gestión de memoria avanzada
- [ ] Standard library completa
- [ ] Package manager
- [ ] LSP (Language Server Protocol)
- [ ] Debugger integrado
- [ ] WebAssembly target

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (git checkout -b feature/amazing)
3. Commit tus cambios (git commit -am 'Add amazing feature')
4. Push a la rama (git push origin feature/amazing)
5. Abre un Pull Request

## Licencia

MIT License - ver archivo LICENSE para detalles

## Autores

- **Vela Team** - Miguel Martín Gil

## Agradecimientos

- A la comunidad LLVM por su increíble infraestructura
- A todos los lenguajes que nos inspiraron: Rust, Swift, Python, Haskell, OCaml
- A la comunidad de código abierto

---

Vela - Donde el código se convierte en arte