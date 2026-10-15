import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "random-number-generator" / "scripts" / "random_number.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        text=True,
        capture_output=True,
    )


class RandomNumberCliTests(unittest.TestCase):
    def test_random_int(self) -> None:
        result = run_cli("random-int", "--low", "1", "--high", "10")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 1)
        self.assertGreaterEqual(value[0], 1)
        self.assertLessEqual(value[0], 10)

    def test_random_int_batch(self) -> None:
        result = run_cli("random-int", "--low", "1", "--high", "10", "--size", "5")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 5)
        for item in value:
            self.assertGreaterEqual(item, 1)
            self.assertLessEqual(item, 10)

    def test_random_float_defaults(self) -> None:
        result = run_cli("random-float")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 1)
        self.assertGreaterEqual(value[0], 0.0)
        self.assertLessEqual(value[0], 1.0)

    def test_random_float_batch(self) -> None:
        result = run_cli("random-float", "--low", "0", "--high", "1", "--size", "3")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 3)
        for item in value:
            self.assertGreaterEqual(item, 0.0)
            self.assertLessEqual(item, 1.0)

    def test_random_choices_with_weights(self) -> None:
        result = run_cli(
            "random-choices",
            "--population-json",
            '["red","blue","green"]',
            "--weights-json",
            "[3,2,1]",
            "--k",
            "2",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(len(value), 2)
        self.assertTrue(set(value).issubset({"red", "blue", "green"}))

    def test_random_shuffle_preserves_items(self) -> None:
        result = run_cli("random-shuffle", "--items-json", "[1,2,3,4]")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(sorted(value), [1, 2, 3, 4])

    def test_random_sample_without_replacement(self) -> None:
        result = run_cli("random-sample", "--population-json", '["a","b","c"]', "--k", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(len(value), 2)
        self.assertEqual(len(set(value)), 2)

    def test_secure_token_hex(self) -> None:
        result = run_cli("secure-token-hex", "--nbytes", "16", "--size", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 2)
        hex_regex = re.compile(r"^[0-9a-f]{32}$")
        for token in value:
            self.assertRegex(token, hex_regex)

    def test_secure_random_int(self) -> None:
        result = run_cli("secure-random-int", "--upper-bound", "100")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 1)
        self.assertGreaterEqual(value[0], 0)
        self.assertLess(value[0], 100)

    def test_secure_random_int_batch(self) -> None:
        result = run_cli("secure-random-int", "--upper-bound", "100", "--size", "4")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 4)
        for item in value:
            self.assertGreaterEqual(item, 0)
            self.assertLess(item, 100)

    def test_invalid_range(self) -> None:
        result = run_cli("random-int", "--low", "10", "--high", "1")
        self.assertEqual(result.returncode, 2)
        self.assertIn("low (10) must be <= high (1)", result.stderr)

    def test_aliases(self) -> None:
        result = run_cli("secure_random_int", "--upper-bound", "2", "--size", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(len(value), 1)
        self.assertIn(value[0], [0, 1])


if __name__ == "__main__":
    unittest.main()
