# Vela

Vela is an experimental programming language born from a simple idea: build a language that is expressive, fast enough to be taken seriously, and practical for a real community to use. The project started from the belief that a language can be both elegant and ambitious, and that performance should be measured with benchmarks instead of slogans.

It is not yet a mature production language, but it already demonstrates a coherent compiler story, a clean syntax, and a serious effort to reach the level of systems-oriented languages.

## Why it is interesting

Vela is worth building if you want to explore three things at once:

- a compact language with readable syntax
- a compiler pipeline that goes from source to LLVM IR
- a project that can grow into a teaching tool, research playground, or small language ecosystem

It is not trying to replace Python, Rust, or Go today. Its strength is that it is small, understandable, and easy to extend.

## What works today

- A working CLI with commands for `run`, `check`, `compile`, and `examples`
- Basic functions, loops, conditionals, recursion, and printing
- Type inference and basic type checking
- LLVM IR generation and a native executable build path
- Example programs under the `examples/` folder

## Quick start

```bash
git clone https://github.com/MigMarGil/Vela_lang.git
cd Vela_lang
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
vela run examples/basic/hello.vela
```

## Example

```rust
func main() -> void {
    print("Hello Vela")
}
```

## Project structure

```
src/
  frontend/   # lexer, parser, AST, type checker
  backend/    # LLVM compiler and executor
  cli/        # command-line interface
examples/     # sample programs
tests/        # smoke tests and future regression tests
docs/         # landing page and launch notes
```

## Current maturity

This is a promising early-stage project. It is good for:

- compiler education
- language experimentation
- building a small but credible portfolio project

It is not yet a "serious production language," and that is fine. The best path forward is to make it focused, documented, and visibly usable.

## Roadmap

**Done**
- [x] Lexer and parser
- [x] Basic type checking
- [x] LLVM IR generation
- [x] Functions and recursion
- [x] Control structures

**In progress / next**
- [ ] Better REPL experience
- [ ] JIT execution
- [ ] Standard library
- [ ] Modules and imports
- [ ] Advanced pattern matching
- [ ] Package manager

**Longer-term / exploratory**
- [ ] Static type inference with generic support
- [ ] Functional programming: first-class functions and lambdas
- [ ] Object-oriented programming: classes and traits
- [ ] Async/await
- [ ] Pipeline operator for function composition
- [ ] Automatic parallel execution
- [ ] Aggressive compile-time optimizations
- [ ] Advanced memory management
- [ ] LSP (Language Server Protocol)
- [ ] Integrated debugger
- [ ] WebAssembly target
- [ ] Tutorials and benchmarks

## Launch and visibility

If you want to make this project more visible, start with the materials in `docs/index.html` and `docs/launch-plan.md`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -am 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## License

MIT License — see the `LICENSE` file for details.

## Authors

Vela Team — Miguel Martín Gil ([@MigMarGil](https://github.com/MigMarGil))

## Acknowledgments

- To the LLVM community for their incredible infrastructure
- To the languages that inspired Vela: Rust, Swift, Python, Haskell, OCaml
- To the open-source community

---

*Vela — where code becomes art.*
