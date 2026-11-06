import asyncio
import importlib
import subprocess
import unittest
from unittest.mock import patch


class RexHistoryTests(unittest.TestCase):
    def setUp(self):
        self.core = importlib.import_module('shell_sage.core')
        self.env = {'TERM_PROGRAM': 'rex', 'REX_SESSION': 'session:own', 'REX_BLOCK': 'block:own'}

    def test_current_rex_pane_capture_and_line_limits(self):
        output = '\n'.join(str(i) for i in range(3005)) + '\n'
        for platform in ('darwin', 'linux'):
            for n, expected in [(None, 3000), (-1, 3000), (2, 2), (0, 0)]:
                with self.subTest(platform=platform, n=n), \
                     patch.dict(self.core.os.environ, self.env, clear=True), \
                     patch.object(self.core.sys, 'platform', platform), \
                     patch.object(self.core, 'co', return_value=output) as capture:
                    history = self.core.get_terminal_history(n)
                    self.assertEqual(history, '\n'.join(str(i) for i in range(3005 - expected, 3005)))
                    if expected:
                        capture.assert_called_once_with(
                            ['rex', 'capture', '-s', 'session:own', '-b', 'block:own', '--trim'],
                            text=True, stderr=self.core.DEVNULL, timeout=10,
                        )
                    else:
                        capture.assert_not_called()

    def test_rex_identity_takes_priority_over_inherited_ghostty_term(self):
        with patch.dict(self.core.os.environ, {**self.env, 'TERM': 'xterm-ghostty'}, clear=True), \
             patch.object(self.core, 'co', return_value='own pane\n'), \
             patch.object(self.core, 'get_ghostty_history_macos') as ghostty:
            self.assertEqual(self.core.get_terminal_history(10), 'own pane')
            ghostty.assert_not_called()

    def test_rex_never_guesses_a_pane_when_identity_is_incomplete(self):
        for missing in ('REX_SESSION', 'REX_BLOCK'):
            env = {k: v for k, v in self.env.items() if k != missing}
            with self.subTest(missing=missing), \
                 patch.dict(self.core.os.environ, env, clear=True), \
                 patch.object(self.core.sys, 'platform', 'darwin'), \
                 patch.object(self.core, 'co') as capture:
                self.assertIsNone(self.core.get_terminal_history(10))
                capture.assert_not_called()

    def test_rex_does_not_interpret_tmux_pane_selectors(self):
        for pid in ('all', '%1'):
            with self.subTest(pid=pid), \
                 patch.dict(self.core.os.environ, self.env, clear=True), \
                 patch.object(self.core, 'co') as capture:
                self.assertIsNone(self.core.get_terminal_history(10, pid))
                capture.assert_not_called()

    def test_tmux_still_wins_inside_rex(self):
        with patch.dict(self.core.os.environ, {**self.env, 'TMUX': '/tmp/tmux'}, clear=True), \
             patch.object(self.core, 'get_hist_tmux', return_value='tmux pane') as tmux, \
             patch.object(self.core, 'co') as capture:
            self.assertEqual(self.core.get_terminal_history(12, '%1'), 'tmux pane')
            tmux.assert_called_once_with(12, '%1')
            capture.assert_not_called()

    def test_rex_capture_failure_continues_without_history(self):
        for error in (FileNotFoundError('rex'), subprocess.CalledProcessError(1, 'rex'),
                      subprocess.TimeoutExpired('rex', 10)):
            with self.subTest(error=type(error).__name__), \
                 patch.dict(self.core.os.environ, self.env, clear=True), \
                 patch.object(self.core, 'co', side_effect=error):
                self.assertIsNone(self.core.get_terminal_history(10))

    def test_main_includes_rex_capture_in_model_context_without_calling_model(self):
        queries = []

        async def collect_query(sage, query, opts):
            queries.append(query)
            yield 'offline response'

        with patch.dict(self.core.os.environ, self.env, clear=True), \
             patch.object(self.core, 'co', return_value='old output\nrex recent output\n'), \
             patch.object(self.core.sys.stdin, 'isatty', return_value=True), \
             patch.object(self.core, 'get_sage', return_value=object()), \
             patch.object(self.core, 'get_res', side_effect=collect_query):
            asyncio.run(self.core.main.__wrapped__(['explain', 'this'], skip_system=True, history_lines=1))
        self.assertEqual(queries, [
            '<terminal_history>\nrex recent output\n</terminal_history>\n<query>\nexplain this\n</query>'
        ])


if __name__ == '__main__':
    unittest.main()
