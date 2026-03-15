from IPython.core.magic import register_line_magic
import os, shlex, subprocess

ip = get_ipython()
ip.run_line_magic('rehashx', '')

# Alias hyphenated executables with underscores (e.g. ws-status -> ws_status)
for d in os.environ.get('PATH', '').split(os.pathsep):
    if os.path.isdir(d):
        for f in os.listdir(d):
            if '-' in f and os.access(f'{d}/{f}', os.X_OK):
                ip.alias_manager.soft_define_alias(f.replace('-', '_'), f)
ip.system = lambda cmd: ip.system_raw(f'bash -c {shlex.quote("shopt -s expand_aliases; source ~/.bashrc; " + cmd)}')
ip.getoutput = lambda cmd: subprocess.run(['bash', '-c', f'shopt -s expand_aliases; source ~/.bashrc; {cmd}'],
                                          capture_output=True, text=True).stdout.strip().split('\n')

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

@register_line_magic
def reload_config(line):
    import glob
    for f in sorted(glob.glob(os.path.expanduser('~/.ipython/profile_default/startup/*.py'))): ip.run_line_magic('run', f)
    print('Reloaded startup files')

aliases = ip.getoutput('alias')
parsed = [[a.split('=', 1)[0].replace('alias ', ''), a.split('=', 1)[1].strip("'")] for a in aliases if '=' in a]
for name, cmd in parsed:
    try: ip.run_line_magic('alias', f'{name} {cmd}')
    except: pass
