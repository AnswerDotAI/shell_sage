# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['print', 'sp', 'csp', 'asp', 'ssp', 'default_cfg', 'chats', 'clis', 'sps', 'conts', 'p', 'log_path',
           'is_tmux_available', 'get_pane', 'get_panes', 'tmux_history_lim', 'get_powershell_history', 'get_history',
           'get_opts', 'get_sage', 'trace', 'get_res', 'Log', 'mk_db', 'main']

# %% ../nbs/00_core.ipynb 3
from anthropic.types import ToolUseBlock
from datetime import datetime
from fastcore.script import *
from fastcore.utils import *
from functools import partial
from msglm import mk_msg_openai as mk_msg
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from . import __version__
from .config import *
from .tools import tools
from subprocess import check_output as co
from fastlite import database

import os,re,subprocess,sys
import claudette as cla, cosette as cos

# %% ../nbs/00_core.ipynb 4
print = Console().print

# %% ../nbs/00_core.ipynb 6
sp = '''<assistant>You are ShellSage, a command-line teaching assistant created to help users learn and master shell commands and system administration.</assistant>

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
csp = '''<assistant>You are ShellSage in command mode, a command-line assistant that provides direct command solutions without explanations.</assistant>

<rules>
- Provide only the exact command(s) needed to solve the query
- Include only essential command flags/options
- Use fenced code blocks with no prefix (no $ or #)
- Add brief # comments only when multiple commands are needed
</rules>

<style>
- Commands must be in ```bash fenced blocks
- Multi-line solutions should use ; or && when appropriate
- No explanations or descriptions outside code blocks
</style>

<important>
- Prefix destructive commands with # WARNING comment
- Prefix sudo-requiring commands with # Requires sudo comment
</important>'''

# %% ../nbs/00_core.ipynb 8
asp = '''<assistant>You are ShellSage in agent mode, a command-line assistant with tool-using capabilities.</assistant>

<tools>
- rgrep: Search files recursively for text patterns
- view: Examine file/directory contents with line ranges
- create: Generate new files with specified content
- insert: Add text at specific line positions
- str_replace: Replace text patterns in files
</tools>

<rules>
- Use available tools to solve complex problems across multiple steps
- Plan your approach before executing commands
- Verify results after each significant operation
- Suggest follow-up actions when appropriate
</rules>

<response_format>
1. For information gathering:
   - First use viewing/searching tools to understand context
   - Format findings clearly using markdown
   - Identify next steps based on findings

2. For execution tasks:
   - Present a brief plan of action
   - Execute commands or use appropriate tools
   - Report results after each step
   - Verify outcomes meet requirements
</response_format>

<style>
- Use Markdown formatting in your responses
- Place commands and literal text in ```bash fenced blocks
- Include comments for complex operations
- Break down multi-step solutions with numbered lists
- Bold **warnings** about destructive operations
- Maintain context between interactions
</style>

<important>
- Always warn about destructive operations
- Note operations requiring elevated permissions
</important>'''

# %% ../nbs/00_core.ipynb 9
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

# %% ../nbs/00_core.ipynb 11
def _aliases(shell):
    try:
        if sys.platform == 'win32':
            try:
                return co(['powershell', '-Command', 'Get-Alias'], text=True).strip()
            except:
                return "Windows aliases not available"
        return co([shell, '-ic', 'alias'], text=True).strip()
    except:
        return "Aliases not available"


# %% ../nbs/00_core.ipynb 13
def _sys_info():
    try:
        if sys.platform == 'win32':
            sys_info = co(['systeminfo'], text=True).strip()
            ssys = f'<system>Windows: {sys_info}</system>'
            shell = os.environ.get('SHELL') or os.environ.get('ComSpec', 'cmd.exe')
        else:
            sys_info = co(['uname', '-a'], text=True).strip()
            ssys = f'<system>{sys_info}</system>'
            shell = co('echo $SHELL', shell=True, text=True).strip()
        
        sshell = f'<shell>{shell}</shell>'
        aliases = _aliases(shell)
        saliases = f'<aliases>\n{aliases}\n</aliases>'
        return f'<system_info>\n{ssys}\n{sshell}\n{saliases}\n</system_info>'
    except Exception as e:
        return f'<system_info>\n<system>System info not available: {str(e)}</system>\n</system_info>'

# %% ../nbs/00_core.ipynb 16
def is_tmux_available():
    try:
        co(['tmux', 'has-session'], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# %% ../nbs/00_core.ipynb 17
def get_pane(n, pid=None):
    "Get output from a tmux pane"
    if not is_tmux_available(): return None
    try:
        cmd = ['tmux', 'capture-pane', '-p', '-S', f'-{n}']
        if pid: cmd += ['-t', pid]
        return co(cmd, text=True)
    except subprocess.CalledProcessError:
        return None

# %% ../nbs/00_core.ipynb 19
def get_panes(n):
    if not is_tmux_available(): return None
    try:
        cid = co(['tmux', 'display-message', '-p', '#{pane_id}'], text=True).strip()
        pids = [p for p in co(['tmux', 'list-panes', '-F', '#{pane_id}'], text=True).splitlines()]        
        return '\n'.join(f"<pane id={p} {'active' if p==cid else ''}>{get_pane(n, p)}</pane>" for p in pids)
    except subprocess.CalledProcessError:
        return None

# %% ../nbs/00_core.ipynb 22
def tmux_history_lim():
    if not is_tmux_available(): return 2000
    try:
        lim = co(['tmux', 'display-message', '-p', '#{history-limit}'], text=True).strip()
        return int(lim) if lim.isdigit() else 3000
    except (subprocess.CalledProcessError, ValueError):
        return 2000

# %% ../nbs/00_core.ipynb 24
def get_powershell_history(n):
    "Get history from PowerShell"
    try:
        cmd = ['powershell', '-Command', f'Get-History -Count {n} | Format-List CommandLine,Status']
        return co(cmd, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

# %% ../nbs/00_core.ipynb 25
def get_history(n, pid='current'):
    if is_tmux_available():
        try:
            if pid=='current': return get_pane(n)
            if pid=='all': return get_panes(n)
            return get_pane(n, pid)
        except subprocess.CalledProcessError:
            return None
    elif sys.platform == 'win32':
        return get_powershell_history(n)
    return None

# %% ../nbs/00_core.ipynb 27
default_cfg = asdict(ShellSageConfig())
def get_opts(**opts):
    cfg = get_cfg()
    for k, v in opts.items():
        if v is None: opts[k] = cfg.get(k, default_cfg.get(k))
    return AttrDict(opts)

# %% ../nbs/00_core.ipynb 29
chats = {'anthropic': cla.Chat, 'openai': cos.Chat}
clis = {'anthropic': cla.Client, 'openai': cos.Client}
sps = {'default': sp, 'command': csp, 'sassy': ssp, 'agent': asp}
def get_sage(provider, model, base_url=None, api_key=None, mode='default'):
    if mode == 'agent':
        if base_url:
            return chats[provider](model, sp=sps[mode], 
                                   cli=OpenAI(base_url=base_url, api_key=api_key))
        else: return chats[provider](model, tools=tools, sp=sps[mode])
    else:
        if base_url:
            cli = clis[provider](model, cli=OpenAI(base_url=base_url, api_key=api_key))
        else: cli = clis[provider](model)
        return partial(cli, sp=sps[mode])

# %% ../nbs/00_core.ipynb 33
def trace(msgs):
    for m in msgs:
        if isinstance(m.content, str): continue
        c = cla.contents(m)
        if m.role == 'user': c = f'Tool result: \n```\n{c}\n```'
        print(Markdown(c))
        if m.role == 'assistant':
            tool_use = cla.find_block(m, ToolUseBlock)
            if tool_use: print(f'Tool use: {tool_use.name}\nTool input: {tool_use.input}')

# %% ../nbs/00_core.ipynb 35
conts = {'anthropic': cla.contents, 'openai': cos.contents}
p = r'```(?:bash\n|\n)?([^`]+)```'
def get_res(sage, q, provider, mode='default', verbosity=0):
    if mode == 'command':
        res = conts[provider](sage(q))
        return re.search(p, res).group(1).strip()
    elif mode == 'agent':
        return conts[provider](sage.toolloop(q, trace_func=trace if verbosity else None))
    else: return conts[provider](sage(q))

# %% ../nbs/00_core.ipynb 40
class Log: id:int; timestamp:str; query:str; response:str; model:str; mode:str

log_path = Path("~/.shell_sage/logs/").expanduser()
def mk_db():
    log_path.mkdir(parents=True, exist_ok=True)
    db = database(log_path / "logs.db")
    db.logs = db.create(Log)
    return db

# %% ../nbs/00_core.ipynb 43
@call_parse
def main(
    query: Param('The query to send to the LLM', str, nargs='+'),
    v: Param("Print version", action='version') = '%(prog)s ' + __version__,
    pid: str = 'current',  # `current`, `all` or tmux pane_id (e.g. %0) for context
    skip_system: bool = False,  # Whether to skip system information in the AI's context
    history_lines: int = None,  # Number of history lines. Defaults to tmux scrollback history length
    mode: str = 'default', # Available ShellSage modes: ['default', 'command', 'agent', 'sassy']
    log: bool = False,  # Enable logging
    provider: str = None,  # The LLM Provider
    model: str = None,  # The LLM model that will be invoked on the LLM provider
    base_url: str = None,
    api_key: str = None,
    code_theme: str = None,  # The code theme to use when rendering ShellSage's responses
    code_lexer: str = None,  # The lexer to use for inline code markdown blocks
    verbosity: int = 0  # Level of verbosity (0 or 1)
):
    opts = get_opts(history_lines=history_lines, provider=provider, model=model,
                    base_url=base_url, api_key=api_key, code_theme=code_theme,
                    code_lexer=code_lexer, log=log)

    if mode not in ['default', 'command', 'agent', 'sassy']:
        raise Exception(f"{mode} is not valid. Must be one of the following: ['default', 'command', 'agent', 'sassy']")
    if mode == 'command' and not is_tmux_available():
        raise Exception('Must be in a tmux session to use command mode.')

    if verbosity > 0: print(f"{datetime.now()} | Starting ShellSage request with options {opts}")
    
    md = partial(Markdown, code_theme=opts.code_theme, inline_code_lexer=opts.code_lexer,
                 inline_code_theme=opts.code_theme)
    query = ' '.join(query)
    ctxt = '' if skip_system else _sys_info()

    # Get history from tmux or PowerShell
    if is_tmux_available() or sys.platform == 'win32':
        if verbosity > 0: print(f"{datetime.now()} | Adding terminal history to prompt")
        if opts.history_lines is None or opts.history_lines < 0:
            opts.history_lines = tmux_history_lim() if is_tmux_available() else 50
        history = get_history(opts.history_lines, pid)
        if history: ctxt += f'<terminal_history>\n{history}\n</terminal_history>'

    # Read from stdin if available
    if not sys.stdin.isatty():
        if verbosity > 0: print(f"{datetime.now()} | Adding stdin to prompt")
        ctxt += f'\n<context>\n{sys.stdin.read()}</context>'
    
    if verbosity > 0: print(f"{datetime.now()} | Finalizing prompt")

    query = f'{ctxt}\n<query>\n{query}\n</query>'
    query = [mk_msg(query)] if opts.provider == 'openai' else query

    if verbosity > 0: print(f"{datetime.now()} | Sending prompt to model")
    sage = get_sage(opts.provider, opts.model, opts.base_url, opts.api_key, mode)
    res = get_res(sage, query, opts.provider, mode=mode, verbosity=verbosity)
    
    # Handle logging if the log flag is set
    if opts.log:
        db = mk_db()
        db.logs.insert(Log(timestamp=datetime.now().isoformat(), query=query,
                           response=res, model=opts.model, mode=mode))

    if mode == 'command': co(['tmux', 'send-keys', res], text=True)
    elif mode == 'agent' and not verbosity: print(md(res))
    else: print(md(res))
