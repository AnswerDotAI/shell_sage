import shlex, subprocess

# Make system commands run in interactive shell and allow executables in PATH to be ran without !
ip = get_ipython()
ip.run_line_magic('rehashx', '') # makes it so you don't need ! for executables in your PATH
ip.system = lambda cmd: ip.system_raw(f'bash -c {shlex.quote("shopt -s expand_aliases; source ~/.bashrc; " + cmd)}') # overwrites ! to run in an interactive shell
ip.getoutput = lambda cmd: subprocess.run(['bash', '-c', f'shopt -s expand_aliases; source ~/.bashrc; {cmd}'], # overwrites !! to run an interactive shell
                                          capture_output=True, text=True).stdout.strip().split('\n')

# --- Export builtin support ---
from IPython.core.magic import register_line_magic

@register_line_magic
def export(line): ip.run_line_magic('env', line)

def _builtin_transformer(lines):
    new_lines = []
    for line in lines:
        if line.strip().startswith('export '):
            line = line.replace('export ', '%export ', 1)
        new_lines.append(line)
    return new_lines

ip.input_transformers_cleanup.append(_builtin_transformer)

# Import bash aliases into IPython
aliases = ip.getoutput('alias')
parsed = [[a.split('=', 1)[0].replace('alias ', ''), a.split('=', 1)[1].strip("'")] for a in aliases if '=' in a]
for name, cmd in parsed:
    try: ip.run_line_magic('alias', f'{name} {cmd}')
    except: pass  # Skip builtins like 'cd'

