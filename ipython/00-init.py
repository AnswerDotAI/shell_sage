from IPython.core.magic import register_line_magic
import os, shlex, subprocess

ip = get_ipython()
ip.run_line_magic('rehashx', '')


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
