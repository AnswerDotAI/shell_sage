from IPython.terminal.prompts import Prompts, Token
import os, subprocess

def _git_branch():
    r = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
    return r.stdout.strip()

def _venv_name():
    v = os.environ.get('VIRTUAL_ENV', '')
    return os.path.basename(v) if v else ''

class PathPrompt(Prompts):
    def in_prompt_tokens(self):
        path = os.getcwd().replace(os.path.expanduser('~'), '~')
        toks = []
        venv = _venv_name()
        if venv: toks.append((Token.Generic, f'({venv}) '))
        toks.append((Token.Prompt, f'{path}'))
        branch = _git_branch()
        if branch: toks.append((Token.PromptNum, f' ({branch})'))
        toks += [(Token.Prompt, ' ['), (Token.PromptNum, str(self.shell.execution_count)), (Token.Prompt, ']: ')]
        return toks

get_ipython().prompts = PathPrompt(get_ipython())
