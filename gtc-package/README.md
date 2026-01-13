# GTC - GPT Token Counter

<a href="https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%7B%22name%22%3A%22gtc%22%2C%22command%22%3A%22gtc-mcp%22%7D">
  <img src="https://img.shields.io/badge/VS_Code-Install_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code">
</a>

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

## MCP Server

GTC can be used as an MCP (Model Context Protocol) server. After installation, add it to your MCP configuration:

```json
{
  "servers": {
    "gtc": {
      "command": "gtc-mcp",
      "args": []
    }
  }
}
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
