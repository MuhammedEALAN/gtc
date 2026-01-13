# GTC - GPT Token Counter

A CLI tool to count tokens in files using OpenAI's tiktoken library.

## Installation

```bash
# Install globally with pip
pip install .

# Or install with uv
uv pip install .

# Or install in editable mode for development
pip install -e .
```

## Usage

```bash
# Count tokens in a file (uses gpt-5 encoding by default)
gtc file.md

# Count tokens in multiple files
gtc file1.md file2.md file3.md

# Use glob patterns
gtc docs/*.md
gtc **/*.md

# Specify a different model
gtc file.md --model gpt-4
gtc file.md -m gpt-4o

# Use a specific encoding directly
gtc file.md --encoding cl100k_base
gtc file.md -e o200k_base

# Verbose output (shows encoding info)
gtc file.md -v

# List all available encodings
gtc --list-encodings

# Show version
gtc --version
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--model` | `-m` | OpenAI model name (default: gpt-5) |
| `--encoding` | `-e` | Encoding name (overrides --model) |
| `--verbose` | `-v` | Show detailed output including encoding info |
| `--list-encodings` | | List all available encodings and exit |
| `--version` | | Show version and exit |

## Supported Models

| Model | Encoding |
|-------|----------|
| gpt-5 | o200k_base |
| gpt-4o | o200k_base |
| gpt-4o-mini | o200k_base |
| gpt-4-turbo | cl100k_base |
| gpt-4 | cl100k_base |
| gpt-3.5-turbo | cl100k_base |

## References

- [tiktoken](https://github.com/openai/tiktoken)
- [OpenAI Cookbook - Token Counting](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
