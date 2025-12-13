# C+ Programming Language

A simplified C-like language that transpiles to C.

## Requirements

- Python 3.6+
- GCC compiler

## Syntax

### Variables
```cplus
let x: int = 10
let* ptr: int = x
let y: int; unsigned; long = 100
```

### Functions
```cplus
fn add(a: int, b: int) -> int {
    return a + b
}

fn main() -> int {
    print("Hello, World!\n")
    return 0
}
```

### Imports
```cplus
import stdio
import stdlib
```

## Example

```cplus
import stdio

fn main() -> int {
    let x: int = 5
    let y: int = 10
    
    print("Sum: %d\n", x + y)
    return 0
}
```

## Options

- `-r` - Compile and run
- `-d` - Delete executable after running
- `-c` - Compile to C
- `-v` - Show version