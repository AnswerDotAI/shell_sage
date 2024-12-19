# ShellSage


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Overview

ShellSage works by understanding your terminal context and leveraging
powerful language models (Claude or GPT) to provide intelligent
assistance for:

- Shell commands and scripting
- System administration tasks
- Git operations
- File management
- Process handling
- Real-time problem solving

What sets ShellSage apart is its ability to: - Read your terminal
context through tmux integration - Provide responses based on your
current terminal state - Accept piped input for direct analysis - Target
specific tmux panes for focused assistance

Whether you’re a seasoned sysadmin or just getting started with the
command line, ShellSage acts as your intelligent terminal companion,
ready to help with both simple commands and complex operations.

## Installation

Install ShellSage directly from PyPI using pip:

``` sh
pip install shell_sage
```

### Prerequisites

1.  **API Key Setup**

    ``` sh
    # For Claude (default)
    export ANTHROPIC_API_KEY=sk...

    # For OpenAI (optional)
    export OPENAI_API_KEY=sk...
    ```

2.  **tmux Configuration**

    We recommend using this optimized tmux configuration for the best
    ShellSage experience. Create or edit your `~/.tmux.conf`:

    ``` sh
    # Enable mouse support
    set -g mouse on

    # Show pane ID and time in status bar
    set -g status-right '#{pane_id} | %H:%M '

    # Keep terminal content visible (needed for neovim)
    set-option -g alternate-screen off

    # Enable vi mode for better copy/paste
    set-window-option -g mode-keys vi

    # Improved search and copy bindings
    bind-key / copy-mode\; send-key ?
    bind-key -T copy-mode-vi y \
      send-key -X start-of-line\; \
      send-key -X begin-selection\; \
      send-key -X end-of-line\; \
      send-key -X cursor-left\; \
      send-key -X copy-selection-and-cancel\; \
      paste-buffer
    ```

    Reload tmux config:

    ``` sh
    tmux source ~/.tmux.conf
    ```

This configuration enables mouse support, displays pane IDs (crucial for
targeting specific panes), maintains terminal content visibility, and
adds vim-style keybindings for efficient navigation and text selection.

## Getting Started

### Basic Usage

ShellSage is designed to run within a tmux session. Here are the core
commands:

``` sh
# Basic usage
ssage hi ShellSage

# Pipe content to ShellSage
cat error.log | ssage explain this error

# Target a specific tmux pane
ssage --pid %3 what's happening in this pane?
```

The `--pid` flag is particularly useful when you want to analyze content
from a different pane. The pane ID is visible in your tmux status bar
(configured earlier).

### Using Alternative Model Providers

ShellSage supports using different LLM providers through base URL
configuration. This allows you to use local models or alternative API
endpoints:

``` sh
# Use a local Ollama endpoint
ssage --provider openai --model llama3.2 --base_url http://localhost:11434/v1 --api_key ollama what is rsync?

# Use together.ai
ssage --provider openai --model mistralai/Mistral-7B-Instruct-v0.3 --base_url https://api.together.xyz/v1 help me with sed # make sure you've set your together API key in your shell_sage conf
```

This is particularly useful for: - Running models locally for
privacy/offline use - Using alternative hosting providers - Testing
different model implementations - Accessing specialized model
deployments

You can also set these configurations permanently in your ShellSage
config file (`~/.config/shell_sage/shell_sage.conf`). See next section
for details.

## Configuration

ShellSage can be customized through its configuration file located at
`~/.config/shell_sage/shell_sage.conf`. Here’s a complete configuration
example:

``` ini
[DEFAULT]
# Choose your AI model provider
provider = anthropic     # or 'openai'
model = claude-3-sonnet # or 'gpt-4o-mini' for OpenAI
base_url = # leave empty to use default openai endpoint
api_key = # leave empty to default to using your OPENAI_API_KEY env var

# Terminal history settings
history_lines = -1      # -1 for all history

# Code display preferences
code_theme = monokai    # syntax highlighting theme
code_lexer = python     # default code lexer
```

### Command Line Overrides

Any configuration option can be overridden via command line arguments:

``` sh
# Use OpenAI instead of Claude for a single query
ssage --provider openai --model gpt-4o-mini "explain this error"

# Adjust history lines for a specific query
ssage --history-lines 50 "what commands did I just run?"
```

## Tips & Best Practices

### Effective Usage Patterns

1.  **Contextual Queries**

    - Keep your tmux pane IDs visible in the status bar
    - Use `--pid` when referencing other panes
    - Let ShellSage see your recent command history for better context

2.  **Piping Best Practices**

    ``` sh
    # Pipe logs directly
    tail -f log.txt | ssage "watch for errors"

    # Combine commands
    git diff | ssage "review these changes"
    ```

### Getting Help

``` sh
# View all available options
ssage --help

# Submit issues or feature requests
# https://github.com/AnswerDotAI/shell_sage/issues
```

## Contributing

ShellSage is built using [nbdev](https://nbdev.fast.ai/). For detailed
contribution guidelines, please see our
[CONTRIBUTING.md](CONTRIBUTING.md) file.

We welcome contributions of all kinds: - Bug reports - Feature
requests - Documentation improvements - Code contributions

Please visit our [GitHub
repository](https://github.com/AnswerDotAI/shell_sage) to get started.
