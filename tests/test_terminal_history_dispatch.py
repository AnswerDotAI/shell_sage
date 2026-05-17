import importlib
import sys
import tempfile
import types
import unittest
from dataclasses import asdict, dataclass
from pathlib import Path
from unittest.mock import patch


def _module(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


_MISSING = object()
_STUB_MODULES = [
    'fastcore', 'fastcore.script', 'fastcore.tools', 'fastcore.utils', 'fastcore.meta',
    'fastlite', 'rich', 'rich.live', 'rich.spinner', 'rich.console', 'rich.markdown',
    'rich.syntax', 'shell_sage.config', 'safecmd', 'pyperclip', 'rgapi', 'fastllm',
    'fastllm.chat', 'shell_sage.core',
]


def _save_modules():
    return {name: sys.modules.get(name, _MISSING) for name in _STUB_MODULES}


def _restore_modules(saved):
    for name, module in saved.items():
        if module is _MISSING:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


def _install_import_stubs():
    """Import shell_sage.core without loading optional runtime dependencies."""
    fastcore_script = _module('fastcore.script', call_parse=lambda f: f)
    fastcore_tools = _module(
        'fastcore.tools',
        rg=lambda *args, **kwargs: None,
        view_file=lambda *args, **kwargs: None,
        create_file=lambda *args, **kwargs: None,
        file_str_replace=lambda *args, **kwargs: None,
        file_insert_line=lambda *args, **kwargs: None,
    )
    fastcore_utils = _module(
        'fastcore.utils',
        patch=lambda f: f,
        IN_NOTEBOOK=False,
        noop=lambda x=None, *args, **kwargs: x,
        asdict=asdict,
        Path=Path,
    )

    class AttrDict(dict):
        def __getattr__(self, key): return self[key]
        def __setattr__(self, key, value): self[key] = value

    fastcore_utils.AttrDict = AttrDict
    fastcore_meta = _module('fastcore.meta', delegates=lambda *args, **kwargs: lambda f: f)
    fastcore = _module(
        'fastcore', script=fastcore_script, tools=fastcore_tools,
        utils=fastcore_utils, meta=fastcore_meta,
    )
    fastcore.__path__ = []

    class Console:
        def print(self, *args, **kwargs): pass

    rich_live = _module('rich.live', Live=object)
    rich_spinner = _module('rich.spinner', Spinner=object)
    rich_console = _module('rich.console', Console=Console)
    rich_markdown = _module(
        'rich.markdown',
        CodeBlock=type('CodeBlock', (), {}),
        Markdown=lambda *args, **kwargs: args[0] if args else '',
    )
    rich_syntax = _module('rich.syntax', Syntax=lambda *args, **kwargs: args[0] if args else '')
    rich = _module(
        'rich', live=rich_live, spinner=rich_spinner, console=rich_console,
        markdown=rich_markdown, syntax=rich_syntax,
    )
    rich.__path__ = []

    @dataclass
    class ShellSageConfig:
        model: str = 'test-model'
        search: str = ''
        think: str = ''
        trust: str = ''
        mode: str = 'default'
        base_url: str = ''
        api_key: str = ''
        vendor_name: str = ''
        history_lines: int = -1
        code_theme: str = 'monokai'
        code_lexer: str = 'python'
        log: bool = False
        safecmd: bool = False
        custom_instructions: str = ''

    shell_config = _module(
        'shell_sage.config', ShellSageConfig=ShellSageConfig, get_cfg=lambda: {},
    )

    class AsyncChat:
        def __init__(self, *args, **kwargs): pass
        def _call(self, *args, **kwargs): pass

    fastllm_chat = _module('fastllm.chat', AsyncChat=AsyncChat)
    fastllm = _module('fastllm', chat=fastllm_chat)
    fastllm.__path__ = []

    modules = {
        'fastcore': fastcore,
        'fastcore.script': fastcore_script,
        'fastcore.tools': fastcore_tools,
        'fastcore.utils': fastcore_utils,
        'fastcore.meta': fastcore_meta,
        'fastlite': _module('fastlite', database=lambda *args, **kwargs: None),
        'rich': rich,
        'rich.live': rich_live,
        'rich.spinner': rich_spinner,
        'rich.console': rich_console,
        'rich.markdown': rich_markdown,
        'rich.syntax': rich_syntax,
        'shell_sage.config': shell_config,
        'safecmd': _module('safecmd', bash=lambda *args, **kwargs: None),
        'pyperclip': _module('pyperclip', copy=lambda *args, **kwargs: None),
        'rgapi': _module(
            'rgapi',
            rg=lambda *args, **kwargs: None,
            ls=lambda *args, **kwargs: None,
            fd=lambda *args, **kwargs: [],
        ),
        'fastllm': fastllm,
        'fastllm.chat': fastllm_chat,
    }
    sys.modules.update(modules)


def import_core():
    saved_modules = _save_modules()
    _install_import_stubs()
    sys.modules.pop('shell_sage.core', None)
    return importlib.import_module('shell_sage.core'), saved_modules


class TerminalHistoryDispatchTests(unittest.TestCase):
    def setUp(self):
        self.core, self._saved_modules = import_core()

    def tearDown(self):
        _restore_modules(self._saved_modules)

    def test_tmux_provider_wins_and_defaults_to_tmux_history_limit(self):
        with patch.dict(self.core.os.environ, {'TMUX': '/tmp/tmux', 'TERM_PROGRAM': 'ghostty'}, clear=True), \
             patch.object(self.core, 'tmux_history_lim', return_value=123) as history_lim, \
             patch.object(self.core, 'get_hist_tmux', return_value='tmux history') as get_tmux, \
             patch.object(self.core, 'get_ghostty_history_macos') as get_ghostty, \
             patch.object(self.core, 'get_macos_terminal_history') as get_terminal:
            self.assertEqual(self.core.get_terminal_history(None, 'all'), 'tmux history')
            history_lim.assert_called_once_with()
            get_tmux.assert_called_once_with(123, 'all')
            get_ghostty.assert_not_called()
            get_terminal.assert_not_called()

    def test_explicit_history_lines_pass_through_to_tmux(self):
        with patch.dict(self.core.os.environ, {'TMUX': '/tmp/tmux'}, clear=True), \
             patch.object(self.core, 'tmux_history_lim') as history_lim, \
             patch.object(self.core, 'get_hist_tmux', return_value='tmux history') as get_tmux:
            self.assertEqual(self.core.get_terminal_history(42, '%1'), 'tmux history')
            history_lim.assert_not_called()
            get_tmux.assert_called_once_with(42, '%1')

    def test_get_history_keeps_main_provider_order(self):
        with patch.object(self.core, 'get_hist_tmux', return_value=None) as get_tmux, \
             patch.object(self.core, 'get_hist_osa', return_value='terminal history') as get_osa:
            self.assertEqual(self.core.get_history(12, 'current'), 'terminal history')
            get_tmux.assert_called_once_with(12, 'current')
            get_osa.assert_called_once_with(12, 'current')

    def test_get_hist_osa_remains_compatible(self):
        with patch.object(self.core, 'get_macos_terminal_history', return_value='terminal history') as get_terminal:
            self.assertEqual(self.core.get_hist_osa(12), 'terminal history')
            get_terminal.assert_called_once_with(12, 'current')

    def test_ghostty_detection_uses_term_program_or_term(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'ghostty'}, clear=True):
            self.assertTrue(self.core.is_ghostty())
        with patch.dict(self.core.os.environ, {'TERM': 'xterm-ghostty'}, clear=True):
            self.assertTrue(self.core.is_ghostty())
        with patch.dict(
            self.core.os.environ,
            {'TERM_PROGRAM': 'Apple_Terminal', 'TERM': 'xterm-256color'},
            clear=True,
        ):
            self.assertFalse(self.core.is_ghostty())

    def test_ghostty_provider_uses_default_history_lines(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'ghostty'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'get_ghostty_history_macos', return_value='ghostty history') as get_ghostty, \
             patch.object(self.core, 'get_macos_terminal_history') as get_terminal:
            self.assertEqual(self.core.get_terminal_history(-1, 'current'), 'ghostty history')
            get_ghostty.assert_called_once_with(3000)
            get_terminal.assert_not_called()

    def test_terminal_app_provider_uses_default_history_lines(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'Apple_Terminal'}, clear=True), \
             patch.object(self.core, 'get_macos_terminal_history', return_value='terminal history') as get_terminal:
            self.assertEqual(self.core.get_terminal_history(-1, 'current'), 'terminal history')
            get_terminal.assert_called_once_with(3000, 'current')

    def test_terminal_app_history_reads_recent_lines_from_osascript(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'Apple_Terminal'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'co', return_value='one\ntwo\nthree\n') as co:
            self.assertEqual(self.core.get_macos_terminal_history(2), 'two\nthree')
            co.assert_called_once_with(
                ['osascript', '-e', self.core.MACOS_TERMINAL_HISTORY_SCRIPTS['Apple_Terminal']],
                text=True,
                stderr=self.core.DEVNULL,
            )

    def test_iterm_history_reads_recent_lines_from_osascript(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'iTerm.app'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'co', return_value='alpha\nbeta\ngamma\n') as co:
            self.assertEqual(self.core.get_macos_terminal_history(1), 'gamma')
            co.assert_called_once_with(
                ['osascript', '-e', self.core.MACOS_TERMINAL_HISTORY_SCRIPTS['iTerm.app']],
                text=True,
                stderr=self.core.DEVNULL,
            )

    def test_macos_terminal_rejects_unsupported_pid(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'Apple_Terminal'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'co') as co:
            self.assertIsNone(self.core.get_macos_terminal_history(10, 'all'))
            self.assertIsNone(self.core.get_macos_terminal_history(10, '%2'))
            co.assert_not_called()

    def test_macos_terminal_unsupported_or_failed_capture_returns_none(self):
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'Apple_Terminal'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'linux'), \
             patch.object(self.core, 'co') as co:
            self.assertIsNone(self.core.get_macos_terminal_history(10))
            co.assert_not_called()
        with patch.dict(self.core.os.environ, {'TERM_PROGRAM': 'Apple_Terminal'}, clear=True), \
             patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'co', side_effect=Exception('boom')):
            self.assertIsNone(self.core.get_macos_terminal_history(10))

    def test_ghostty_rejects_unsupported_pid(self):
        with patch.object(self.core.sys, 'platform', 'darwin'), \
             patch.object(self.core, 'get_ghostty_history_macos') as macos_history:
            self.assertIsNone(self.core.get_ghostty_history(10, 'all'))
            self.assertIsNone(self.core.get_ghostty_history(10, '%2'))
            macos_history.assert_not_called()

    def test_ghostty_macos_happy_path_reads_temp_history_and_restores_clipboard(self):
        with tempfile.TemporaryDirectory(dir=tempfile.gettempdir()) as directory:
            history_path = Path(directory) / 'history.txt'
            history_path.write_text('one\ntwo\nthree\nfour', encoding='utf-8')
            with patch.object(self.core, '_pbpaste', side_effect=['original clip', str(history_path)]), \
                 patch.object(self.core, '_pbcopy') as pbcopy, \
                 patch.object(self.core, '_run_osascript') as run_osascript:
                self.assertEqual(self.core.get_ghostty_history_macos(2), 'three\nfour')
                run_osascript.assert_called_once_with(self.core.GHOSTTY_SCROLLBACK_SCRIPT)
                pbcopy.assert_called_once_with('original clip')

    def test_ghostty_macos_invalid_clipboard_path_returns_none_and_restores_clipboard(self):
        clipboard_values = iter(['original clip', 'not a path'])

        def fake_pbpaste():
            return next(clipboard_values, 'not a path')

        with patch.object(self.core, '_pbpaste', side_effect=fake_pbpaste), \
             patch.object(self.core, '_pbcopy') as pbcopy, \
             patch.object(self.core, '_run_osascript'), \
             patch.object(self.core.time, 'sleep'), \
             patch.object(self.core.time, 'time', side_effect=[0, 0, 2]):
            self.assertIsNone(self.core.get_ghostty_history_macos(10))
            pbcopy.assert_called_once_with('original clip')

    def test_ghostty_macos_read_errors_return_none_and_restore_clipboard(self):
        with tempfile.TemporaryDirectory(dir=tempfile.gettempdir()) as directory:
            history_path = Path(directory) / 'history.txt'
            history_path.write_text('history', encoding='utf-8')
            with patch.object(self.core, '_pbpaste', side_effect=['original clip', str(history_path)]), \
                 patch.object(self.core, '_pbcopy') as pbcopy, \
                 patch.object(self.core, '_run_osascript'), \
                 patch.object(self.core.Path, 'read_text', side_effect=OSError('boom')):
                self.assertIsNone(self.core.get_ghostty_history_macos(10))
                pbcopy.assert_called_once_with('original clip')

    def test_ghostty_path_validation_requires_temp_history_file(self):
        with tempfile.TemporaryDirectory(dir=tempfile.gettempdir()) as directory:
            valid = Path(directory) / 'history.txt'
            valid.write_text('history', encoding='utf-8')
            wrong_name = Path(directory) / 'not-history.txt'
            wrong_name.write_text('history', encoding='utf-8')
            self.assertTrue(self.core._valid_ghostty_history_path(str(valid)))
            self.assertFalse(self.core._valid_ghostty_history_path(str(wrong_name)))
            self.assertFalse(self.core._valid_ghostty_history_path('not a path'))

    def test_tail_lines_respects_history_line_count(self):
        self.assertEqual(self.core._tail_lines('one\ntwo\nthree', 2), 'two\nthree')
        self.assertEqual(self.core._tail_lines('one\ntwo', -1), 'one\ntwo')
        self.assertEqual(self.core._tail_lines('one\ntwo', 0), '')

    def test_no_terminal_provider_returns_none(self):
        with patch.dict(self.core.os.environ, {}, clear=True):
            self.assertIsNone(self.core.get_terminal_history(10, 'current'))


if __name__ == '__main__':
    unittest.main()
