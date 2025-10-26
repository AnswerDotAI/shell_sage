import subprocess

# Make system commands run in interactive shell and allow executables in PATH to be ran without !
ip = get_ipython()
ip.run_line_magic('rehashx', '') # makes it so you don't need ! for executables in your PATH
ip.system = lambda cmd: ip.system_raw(f'bash -i -c "{cmd}"') # overwrites ! to run in an interactive shell
ip.getoutput = lambda cmd: subprocess.run(['bash', '-i', '-c', cmd], # overwrites !! to run an interactive shell
                                          capture_output=True, text=True).stdout.strip().split('\n')

# Import bash aliases into IPython
aliases = ip.getoutput('alias')
parsed = [[a.split('=', 1)[0].replace('alias ', ''), a.split('=', 1)[1].strip("'")] for a in aliases if '=' in a]
for name, cmd in parsed:
    try: ip.run_line_magic('alias', f'{name} {cmd}')
    except: pass  # Skip builtins like 'cd'

