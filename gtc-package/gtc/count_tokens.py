#!/usr/bin/env python3
"""
GTC - GPT Token Counter

Uses OpenAI's tiktoken library to count BPE tokens in files.
Useful for estimating API costs and context window usage.

Usage:
    gtc file.md
    gtc file1.md file2.md file3.md
    gtc *.md
    gtc docs/**/*.md --model gpt-4
    gtc file.md --encoding cl100k_base

References:
    - https://github.com/openai/tiktoken
    - https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken is not installed.")
    print("Install it with: pip install tiktoken")
    print("Or with uv: uv pip install tiktoken")
    sys.exit(1)


__version__ = "1.0.0"

# Default model for token counting
DEFAULT_MODEL = "gpt-5"

# Model to encoding mapping for reference
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
    """
    Get tiktoken encoder by model name or encoding name.
    
    Args:
        model: OpenAI model name (e.g., 'gpt-5', 'gpt-4o', 'gpt-4')
        encoding: Encoding name (e.g., 'cl100k_base', 'o200k_base')
    
    Returns:
        tiktoken.Encoding instance
    """
    if encoding:
        return tiktoken.get_encoding(encoding)
    elif model:
        # Handle models not directly in tiktoken (like gpt-5)
        if model in MODEL_ENCODINGS:
            return tiktoken.get_encoding(MODEL_ENCODINGS[model])
        return tiktoken.encoding_for_model(model)
    else:
        # Default to gpt-5 encoding
        return tiktoken.get_encoding(MODEL_ENCODINGS[DEFAULT_MODEL])


def count_tokens(text: str, encoder: tiktoken.Encoding) -> int:
    """
    Count the number of tokens in text.
    
    Args:
        text: Input text to tokenize
        encoder: tiktoken encoder instance
    
    Returns:
        Number of tokens
    """
    return len(encoder.encode(text))


def count_file_tokens(filepath: Path, encoder: tiktoken.Encoding) -> tuple[int, Optional[str]]:
    """
    Count tokens in a file.
    
    Args:
        filepath: Path to the file
        encoder: tiktoken encoder instance
    
    Returns:
        Tuple of (token_count, error_message)
        If successful, error_message is None
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        token_count = count_tokens(content, encoder)
        return token_count, None
    except FileNotFoundError:
        return 0, f"File not found: {filepath}"
    except PermissionError:
        return 0, f"Permission denied: {filepath}"
    except UnicodeDecodeError:
        return 0, f"Unable to decode file (not UTF-8): {filepath}"
    except Exception as e:
        return 0, f"Error reading {filepath}: {e}"


def format_number(n: int) -> str:
    """Format number with thousand separators."""
    return f"{n:,}"


def main():
    parser = argparse.ArgumentParser(
        prog="gtc",
        description="GPT Token Counter - Count tokens in files using tiktoken",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    gtc README.md
    gtc docs/*.md
    gtc **/*.md --model gpt-4
    gtc file.md --encoding cl100k_base
    gtc file.md -v

Available encodings: cl100k_base, o200k_base, p50k_base, r50k_base, gpt2
        """,
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="File(s) to count tokens for",
    )
    
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenAI model name (default: {DEFAULT_MODEL}). Examples: gpt-5, gpt-4o, gpt-4",
    )
    
    parser.add_argument(
        "-e", "--encoding",
        type=str,
        default=None,
        help="Encoding name (overrides --model). Examples: cl100k_base, o200k_base",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output including encoding info",
    )
    
    parser.add_argument(
        "--list-encodings",
        action="store_true",
        help="List all available encodings and exit",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    args = parser.parse_args()
    
    # Handle --list-encodings
    if args.list_encodings:
        print("Available encodings:")
        for name in tiktoken.list_encoding_names():
            enc = tiktoken.get_encoding(name)
            print(f"  {name}: vocab_size={enc.n_vocab:,}")
        print("\nModel to encoding mapping:")
        for model, encoding in MODEL_ENCODINGS.items():
            print(f"  {model} -> {encoding}")
        return 0
    
    # Check if files provided
    if not args.files:
        parser.error("No files specified. Provide file path(s) or use --list-encodings.")
    
    # Get encoder
    try:
        encoder = get_encoder(model=args.model, encoding=args.encoding)
    except KeyError as e:
        print(f"Error: Unknown model or encoding: {e}")
        print("Use --list-encodings to see available options.")
        return 1
    
    if args.verbose:
        print(f"Using encoding: {encoder.name}")
        print(f"Vocabulary size: {encoder.n_vocab:,}")
        print("-" * 50)
    
    # Process files
    results = []
    errors = []
    total_tokens = 0
    
    for filepath in args.files:
        # Expand glob patterns if shell didn't
        if "*" in str(filepath):
            expanded = list(Path(".").glob(str(filepath)))
            if not expanded:
                errors.append(f"No files match pattern: {filepath}")
                continue
            files_to_process = expanded
        else:
            files_to_process = [filepath]
        
        for file_path in files_to_process:
            if file_path.is_dir():
                errors.append(f"Skipping directory: {file_path}")
                continue
                
            token_count, error = count_file_tokens(file_path, encoder)
            
            if error:
                errors.append(error)
            else:
                results.append((file_path, token_count))
                total_tokens += token_count
    
    # Print results
    if results:
        # Determine column width for alignment
        max_path_len = max(len(str(fp)) for fp, _ in results)
        max_path_len = min(max_path_len, 60)  # Cap at 60 chars
        
        for filepath, tokens in results:
            path_str = str(filepath)
            if len(path_str) > 60:
                path_str = "..." + path_str[-57:]
            print(f"{path_str:<{max_path_len}}  {format_number(tokens):>12} tokens")
        
        # Print total if multiple files
        if len(results) > 1:
            print("-" * (max_path_len + 14))
            print(f"{'Total':<{max_path_len}}  {format_number(total_tokens):>12} tokens")
    
    # Print errors
    if errors:
        print("\nErrors:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
    
    # Return exit code
    if not results and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
