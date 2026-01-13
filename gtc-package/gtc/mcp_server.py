#!/usr/bin/env python3
"""
GTC MCP Server - GPT Token Counter as MCP Tool

Exposes token counting functionality via Model Context Protocol (MCP).
This allows AI assistants to count tokens in files directly.

Usage:
    Run as MCP server: gtc-mcp
    Or: python -m gtc.mcp_server
"""

from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

try:
    import tiktoken
except ImportError:
    raise ImportError(
        "tiktoken is not installed. Install with: pip install tiktoken"
    )

# Initialize MCP server
mcp = FastMCP("GTC Token Counter")

# Default model for token counting
DEFAULT_MODEL = "gpt-5"

# Model to encoding mapping
MODEL_ENCODINGS = {
    "gpt-5": "o200k_base",
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-embedding-3-small": "cl100k_base",
    "text-embedding-3-large": "cl100k_base",
    "text-embedding-ada-002": "cl100k_base",
}


def get_encoder(model: Optional[str] = None, encoding: Optional[str] = None) -> tiktoken.Encoding:
    """Get tiktoken encoder by model name or encoding name."""
    if encoding:
        return tiktoken.get_encoding(encoding)
    elif model:
        if model in MODEL_ENCODINGS:
            return tiktoken.get_encoding(MODEL_ENCODINGS[model])
        return tiktoken.encoding_for_model(model)
    else:
        return tiktoken.get_encoding(MODEL_ENCODINGS[DEFAULT_MODEL])


@mcp.tool()
def count_tokens(
    file_path: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Count the number of tokens in a file using tiktoken.
    
    Args:
        file_path: Absolute path to the file to count tokens for
        model: OpenAI model name for encoding (default: gpt-5). 
               Options: gpt-5, gpt-4o, gpt-4, gpt-3.5-turbo
    
    Returns:
        Dictionary with file path, token count, model, and encoding used
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "error": f"File not found: {file_path}",
                "file_path": file_path,
                "tokens": 0,
            }
        
        if path.is_dir():
            return {
                "error": f"Path is a directory: {file_path}",
                "file_path": file_path,
                "tokens": 0,
            }
        
        encoder = get_encoder(model=model)
        content = path.read_text(encoding="utf-8")
        token_count = len(encoder.encode(content))
        
        return {
            "file_path": file_path,
            "tokens": token_count,
            "model": model,
            "encoding": encoder.name,
        }
        
    except UnicodeDecodeError:
        return {
            "error": f"Unable to decode file (not UTF-8): {file_path}",
            "file_path": file_path,
            "tokens": 0,
        }
    except Exception as e:
        return {
            "error": str(e),
            "file_path": file_path,
            "tokens": 0,
        }


@mcp.tool()
def count_tokens_multi(
    file_paths: list[str],
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Count tokens in multiple files and return total.
    
    Args:
        file_paths: List of absolute file paths to count tokens for
        model: OpenAI model name for encoding (default: gpt-5)
    
    Returns:
        Dictionary with per-file results, total tokens, and any errors
    """
    results = []
    errors = []
    total_tokens = 0
    
    encoder = get_encoder(model=model)
    
    for file_path in file_paths:
        try:
            path = Path(file_path)
            
            if not path.exists():
                errors.append(f"File not found: {file_path}")
                continue
            
            if path.is_dir():
                errors.append(f"Path is a directory: {file_path}")
                continue
            
            content = path.read_text(encoding="utf-8")
            token_count = len(encoder.encode(content))
            
            results.append({
                "file_path": file_path,
                "tokens": token_count,
            })
            total_tokens += token_count
            
        except UnicodeDecodeError:
            errors.append(f"Unable to decode file (not UTF-8): {file_path}")
        except Exception as e:
            errors.append(f"Error reading {file_path}: {e}")
    
    return {
        "files": results,
        "total_tokens": total_tokens,
        "file_count": len(results),
        "model": model,
        "encoding": encoder.name,
        "errors": errors if errors else None,
    }


@mcp.tool()
def count_text_tokens(
    text: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Count tokens in a text string directly.
    
    Args:
        text: The text to count tokens for
        model: OpenAI model name for encoding (default: gpt-5)
    
    Returns:
        Dictionary with token count, character count, and encoding info
    """
    encoder = get_encoder(model=model)
    token_count = len(encoder.encode(text))
    
    return {
        "tokens": token_count,
        "characters": len(text),
        "model": model,
        "encoding": encoder.name,
    }


@mcp.tool()
def list_encodings() -> dict:
    """
    List all available tiktoken encodings and model mappings.
    
    Returns:
        Dictionary with available encodings and model-to-encoding mapping
    """
    encodings = []
    for name in tiktoken.list_encoding_names():
        enc = tiktoken.get_encoding(name)
        encodings.append({
            "name": name,
            "vocab_size": enc.n_vocab,
        })
    
    return {
        "encodings": encodings,
        "model_mappings": MODEL_ENCODINGS,
        "default_model": DEFAULT_MODEL,
    }


def main():
    """Entry point for MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
