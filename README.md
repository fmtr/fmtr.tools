# `fmtr.tools`

A collection of high-level tools to simplify everyday development tasks, with a slight focus on full-stack AI/ML.

This repository is an attempt to provide a one-stop source for a wide range of utilities and tools designed to streamline a typical, modern development workflow. There is an emphasis on a lean and nimble approach to dependencies, which tries to strike a balance between powerful functionality while avoiding unnecessary bloat.

## Why?

Personally, I'm grossly impatient, and simply resent writing the same code, however simple, in multiple projects.

This could be trivial stuff like reading an integer from an environment variable (while handling errors gracefully) - or more complex ones (like just wanting a simple parallel-processing function without writing Queues, or remembering which libraries you need to do it for you).

At the same time, I find that traditional tools collections inevitably become bloated and unwieldy over time, so wanted something with a somewhat sophisticated approach to dependencies.

## Key Features

- Wide-Ranging Utilities: The collection includes tools for configuration, data types, environment management, functions, hashing, importing, iterating, JSON handling, path manipulation, platform-specific operations, randomness, and string operations.
- Lean Dependencies: Dependencies are managed via extras, allowing you to install only what you need. Missing dependencies are handled in a clear way, telling you what's missing and how to install it.

## Installing

The base library can be installed like this:

```bash
pip install fmtr.tools
```

## Usage

Some simple import and usage examples

### Read an integer from an environment variable and write it to a (human-readable) JSON file:

```python
from fmtr import tools
from fmtr.tools import Path

value=tools.env.get_int('MY_VALUE',default=None)
data=dict(value=value)
Path('data.json').write_json(data)
```

### Zero-faff parallel multi-processing

Install the extra:

```bash
pip install fmtr.tools[parallel] --upgrade
```

```python
from fmtr.tools import parallel

def expensive_computation(n):
    import math
    result = 0
    for i in range(1, n + 1):
        result += math.sqrt(i) * math.sin(i) * math.log(i)
    return result

if __name__ == '__main__':
    results=parallel.apply(expensive_computation, [10_000] * 1_000)
```

## Extras

Most tools require no additional dependencies, but for any that do, you can add them like this:

```bash
pip install fmtr.tools[<extra>] --upgrade
```

If you try to use a module without the required extras, you'll get a message telling you which one is needed:

```
MissingExtraError: The current module is missing dependencies. To install them, run: `pip install fmtr.tools[logging] --upgrade`
```

## Modules

The included modules, plus any extra requirements, are as follows:

- `tools.config`: Base config class with overridable field processors.
    - Extras: None
- `tools.dataclass`: Utilities for extracting and filtering fields and metadata from dataclasses, with support for applying filters and retrieving enabled fields based on metadata attributes.
    - Extras: None
- `tools.datatype`
    - Extras: None
- `tools.environment`: Tools for managing environment variables, including functions to retrieve variables with type conversions and default values. Features include environment variable fetching, handling missing variables, and creating type-specific getters for integers, floats, booleans, dates, and paths.
    - Extras: None
- `tools.env`: Alias of `tools.environment`.
    - Extras: None
- `tools.function`: Utilities for combining and splitting arguments and keyword arguments.
    - Extras: None
- `tools.hash`: String hashing
    - Extras: None
- `tools.iterator`: Pivoting/unpivoting data structures
    - Extras: None
- `tools.json`: Serialisation/deserialisation to human-readable, unicode JSON.
    - Extras: None
- `tools.Path`: Enhanced `pathlib.Path` object with additional functionality for Windows-to-Unix path conversion, reading/writing JSON and YAML files, and convenient directory creation with parent directories. Includes methods for obtaining paths to modules and temporary directories.
    - Extras: None
- `tools.platform`: Detecting if host is WSL, Docker etc.
    - Extras: None
- `tools.ContextProcess`: Manages a function running in a separate process using a context manager. Provides methods to start, stop, and restart the process, with configurable restart delays. Useful for ensuring clean process management and automatic stopping when the context manager exits.
    - Extras: None
- `tools.random`: Provides additional functions for random number generation and selection, useful for data augmentation.
    - Extras: None
- `tools.string`: Provides utilities for handling string formatting.
    - Extras: None
- `tools.logging`: Configures and initializes a logger using the Loguru library. Provides customizable logging formats for time, level, file, function, and message components.
    - Extras: `logging`
- `tools.logger`: Prefabricated `logger` object, suitable for most projects, timestamped, color-coded, etc.
    - Extras: `logging`
- `tools.augmentation`: Data augmentation stub.
    - Extras: `augmentation`
- `tools.Container`: Runs a Docker container within a context manager, ensuring the container is stopped and removed when the context is exited.
    - Extras: `docker.api`
- `tools.parallel`: Provides utilities for parallel computation using Dask. Supports executing functions across multiple workers or processes, handles different data formats, and options for progress display and parallelism configuration.
    - Extras: `parallel`
- `tools.profiling`: Context-based code timing.
    - Extras: `profiling`
- `tools.tokenization`: Provides utilities for creating and configuring tokenizers using the Tokenizers library. Iincludes functions for training both word-level and byte-pair encoding (BPE) tokenizers, applying special formatting and templates, and managing tokenizer configurations such as padding, truncation, and special tokens.
    - Extras: `tokenization`

## Contribution

Any contributions would be most welcome! If you have a utility that fits well within this collection, or improvements to existing tools, feel free to open a pull request.

## License

This project is licensed under the Apache License Version 2.0. See the [LICENSE](LICENSE) file for more details.