import subprocess
import sys
import unittest


class EntrypointTests(unittest.TestCase):
    def test_core_imports_with_installed_dependencies(self):
        result = subprocess.run(
            [sys.executable, '-c', 'import shell_sage.core'],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
