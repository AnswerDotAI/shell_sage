# ShellSage Configuration


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Imports

``` python
_cfg_path()
```

    Path('/Users/nathan/.config/shell_sage/shell_sage.conf')

``` python
providers
```

    {'anthropic': ['claude-3-opus-20240229',
      'claude-3-5-sonnet-20241022',
      'claude-3-haiku-20240307',
      'claude-3-5-haiku-20241022'],
     'openai': ('o1-preview',
      'o1-mini',
      'gpt-4o',
      'gpt-4o-mini',
      'gpt-4-turbo',
      'gpt-4',
      'gpt-4-32k',
      'gpt-3.5-turbo',
      'gpt-3.5-turbo-instruct')}

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/shell_sage/blob/main/shell_sage/config.py#L29"
target="_blank" style="float:right; font-size:smaller">source</a>

### ShellSageConfig

>  ShellSageConfig (provider:str='anthropic',
>                       model:str='claude-3-5-sonnet-20240620', base_url:str='',
>                       api_key:str='', history_lines:int=-1,
>                       code_theme:str='monokai', code_lexer:str='python')

``` python
cfg = ShellSageConfig()
cfg
```

    ShellSageConfig(provider='anthropic', model='claude-3-5-sonnet-20241022', base_url='', api_key='', history_lines=-1, code_theme='monokai', code_lexer='python')

------------------------------------------------------------------------

<a
href="https://github.com/AnswerDotAI/shell_sage/blob/main/shell_sage/config.py#L39"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_cfg

>  get_cfg ()

``` python
cfg = get_cfg()
cfg
```

    {'provider': 'openai', 'model': 'deepseek-chat', 'base_url': 'https://api.deepseek.com', 'api_key': 'sk-7369d525c23c4078b6d7e2af55903e71', 'history_lines': '-1', 'code_theme': 'monokai', 'code_lexer': 'python'}