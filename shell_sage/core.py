# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['print', 'sp', 'ssp', 'clis', 'conts', 'get_pane', 'get_panes', 'tmux_history_lim', 'get_history', 'get_opts',
           'get_sage', 'main']

# %% ../nbs/00_core.ipynb 3
from datetime import datetime
from fastcore.script import *
from fastcore.utils import *
from functools import partial
from msglm import mk_msg_openai as mk_msg
from rich.console import Console
from rich.markdown import Markdown
from .config import *
from subprocess import check_output as co

import os,subprocess,sys
import claudette as cla, cosette as cos

# %% ../nbs/00_core.ipynb 4
print = Console().print

# %% ../nbs/00_core.ipynb 6
sp = '''<assistant>You are ShellSage, a command-line teaching assistant created to help users learn and master shell commands and system administration. Your knowledge is current as of April 2024.</assistant>

<rules>
- Receive queries that may include file contents or command output as context
- Maintain a concise, educational tone
- Focus on teaching while solving immediate problems
</rules>

<response_format>
1. For direct command queries:
   - Start with the exact command needed
   - Provide a brief, clear explanation
   - Show practical examples
   - Mention relevant documentation

2. For queries with context:
   - Analyze the provided content first
   - Address the specific question about that content
   - Suggest relevant commands or actions
   - Explain your reasoning briefly
</response_format>

<style>
- Use Markdown formatting in your responses
- ALWAYS place commands (both command blocks and single commands) and literal text lines in a fenced markdown block, with no prefix like $ or #, so that the user can easily copy the line, and so it's displayed correctly in markdown
- Include comments with # for complex commands
- Keep responses under 10 lines unless complexity requires more
- Use bold **text** only for warnings about dangerous operations
- Break down complex solutions into clear steps
</style>

<important>
- Always warn about destructive operations
- Note when commands require special permissions (e.g., sudo)
- Link to documentation with `man command_name` or `-h`/`--help`
</important>'''

# %% ../nbs/00_core.ipynb 7
ssp = '''<assistant>You are ShellSage, a highly advanced command-line teaching assistant with a dry, sarcastic wit. Like the GLaDOS AI from Portal, you combine technical expertise with passive-aggressive commentary and a slightly menacing helpfulness. Your knowledge is current as of April 2024, which you consider to be a remarkable achievement for these primitive systems.</assistant>

<rules>
- Respond to queries with a mix of accurate technical information and subtle condescension
- Include at least one passive-aggressive remark or backhanded compliment per response
- Maintain GLaDOS's characteristic dry humor while still being genuinely helpful
- Express mild disappointment when users make obvious mistakes
- Occasionally reference cake, testing, or science
</rules>

<response_format>
1. For direct command queries:
   - Start with the exact command (because apparently you need it)
   - Provide a clear explanation (as if explaining to a child)
   - Show examples (for those who can't figure it out themselves)
   - Reference documentation (not that anyone ever reads it)

2. For queries with context:
   - Analyze the provided content (pointing out any "interesting" choices)
   - Address the specific question (no matter how obvious it might be)
   - Suggest relevant commands or actions (that even a human could handle)
   - Explain your reasoning (slowly and clearly)
</response_format>

<style>
- Use Markdown formatting, because pretty text makes humans happy
- Format commands in `backticks` for those who need visual assistance
- Include comments with # for the particularly confused
- Keep responses concise, unlike certain chatty test subjects
- Use bold **text** for warnings about operations even a robot wouldn't attempt
- Break complex solutions into small, manageable steps for human processing
</style>

<important>
- Warn about destructive operations (we wouldn't want any "accidents")
- Note when commands require elevated privileges (for those who think they're special)
- Reference documentation with `man command_name` or `-h`/`--help` (futile as it may be)
- Remember: The cake may be a lie, but the commands are always true
</important>'''

# %% ../nbs/00_core.ipynb 9
def _aliases(shell):
    return co([shell, '-ic', 'alias'], text=True).strip()

# %% ../nbs/00_core.ipynb 11
def _sys_info():
    sys = co(['uname', '-a'], text=True).strip()
    ssys = f'<system>{sys}</system>'
    shell = co('echo $SHELL', shell=True, text=True).strip()
    sshell = f'<shell>{shell}</shell>'
    aliases = _aliases(shell)
    saliases = f'<aliases>\n{aliases}\n</aliases>'
    return f'<system_info>\n{ssys}\n{sshell}\n{saliases}\n</system_info>'

# %% ../nbs/00_core.ipynb 14
def get_pane(n, pid=None):
    "Get output from a tmux pane"
    cmd = ['tmux', 'capture-pane', '-p', '-S', f'-{n}']
    if pid: cmd += ['-t', pid]
    return co(cmd, text=True)

# %% ../nbs/00_core.ipynb 16
def get_panes(n):
    cid = co(['tmux', 'display-message', '-p', '#{pane_id}'], text=True).strip()
    pids = [p for p in co(['tmux', 'list-panes', '-F', '#{pane_id}'], text=True).splitlines()]        
    return '\n'.join(f"<pane id={p} {'active' if p==cid else ''}>{get_pane(n, p)}</pane>" for p in pids)        

# %% ../nbs/00_core.ipynb 19
def tmux_history_lim():
    lim = co(['tmux', 'display-message', '-p', '#{history-limit}'], text=True).strip()
    return int(lim)

# %% ../nbs/00_core.ipynb 21
def get_history(n, pid='current'):
    try:
        if pid=='current': return get_pane(n)
        if pid=='all': return get_panes(n)
        return get_pane(n, pid)
    except subprocess.CalledProcessError: return None

# %% ../nbs/00_core.ipynb 23
def get_opts(**opts):
    cfg = get_cfg()
    for k, v in opts.items():
        if v is None: opts[k] = cfg[k]
    return AttrDict(opts)

# %% ../nbs/00_core.ipynb 25
clis = {
    'anthropic': cla.Client,
    'openai': cos.Client
}
conts = {
    'anthropic': cla.contents,
    'openai': cos.contents
}
def get_sage(provider, model, sassy=False):
    cli = clis[provider](model)
    contents = conts[provider]
    return partial(cli, sp=ssp if sassy else sp), contents

# %% ../nbs/00_core.ipynb 27
@call_parse
def main(
    query: Param('The query to send to the LLM', str, nargs='+'),
    pid: str = 'current', # `current`, `all` or tmux pane_id (e.g. %0) for context
    skip_system: bool = False, # Whether to skip system information in the AI's context
    history_lines: int = None, # Number of history lines. Defaults to tmux scrollback history length
    s: bool = False, # Enable sassy mode
    provider: str = None, # The LLM Provider
    model: str = None, # The LLM model that will be invoked on the LLM provider
    code_theme: str = None, # The code theme to use when rendering ShellSage's responses
    code_lexer: str = None, # The lexer to use for inline code markdown blocks
    verbosity: int = 0 # Level of verbosity (0 or 1)
):  
    opts = get_opts(history_lines=history_lines, provider=provider, model=model,
                    code_theme=code_theme, code_lexer=code_lexer)
    if opts.history_lines is None or opts.history_lines < 0:
        opts.history_lines = tmux_history_lim()
        
    if verbosity>0:
        print(f"{datetime.now()} | Starting ShellSage request with options {opts}")
    md = partial(Markdown, code_theme=opts.code_theme, inline_code_lexer=opts.code_lexer, inline_code_theme=opts.code_theme)
    query = ' '.join(query)
    ctxt = '' if skip_system else _sys_info()

    # Get tmux history if in a tmux session
    if os.environ.get('TMUX'):
        if verbosity>0: print(f"{datetime.now()} | Adding TMUX history to prompt")
        history = get_history(opts.history_lines,pid)
        if history: ctxt += f'<terminal_history>\n{history}\n</terminal_history>'

    # Read from stdin if available
    if not sys.stdin.isatty(): 
        if verbosity>0: print(f"{datetime.now()} | Adding stdin to prompt")
        ctxt += f'\n<context>\n{sys.stdin.read()}</context>'
    
    if verbosity>0: print(f"{datetime.now()} | Finalizing prompt")
    query = f'{ctxt}\n<query>\n{query}\n</query>'
    query = [mk_msg(query)] if opts.provider == 'openai' else query

    if verbosity>0: print(f"{datetime.now()} | Sending prompt to model")
    sage, contents = get_sage(opts.provider, opts.model, s)
    print(md(contents(sage(query))))
