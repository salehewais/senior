"""Static checks for Phase 19 backup and restore. They do not dump or restore a database."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
COMPOSE = (ROOT.parent / "compose" / "docker-compose.yml").read_text(encoding="utf-8")
LIB = (ROOT / "lib.sh").read_text(encoding="utf-8")
GITIGNORE = (ROOT.parents[1] / ".gitignore").read_text(encoding="utf-8")

DATABASES = ("order_db", "reporting_db", "odoo_db")
SERVICES = {
    "order_db": "postgres",
    "reporting_db": "reporting-postgres",
    "odoo_db": "odoo-db",
}

FORBIDDEN = (
    re.compile(r"docker\s+compose\s+[^\n]*\b(down|stop|start|rm|kill)\b"),
    re.compile(r"\bcompose\s+down\b"),
    re.compile(r"\bdown\s+-v\b"),
    re.compile(r"\bvolume\s+rm\b"),
    re.compile(r"\bdocker\s+volume\b"),
    re.compile(r"\bDROP\s+DATABASE\b", re.IGNORECASE),
    re.compile(r"\bdropdb\b", re.IGNORECASE),
    re.compile(r"/api/v1/internal"),
    re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
    re.compile(r"PRIVATE KEY"),
    re.compile(r"jwt_private"),
    re.compile(r"\.pem\b"),
    re.compile(r"failure-lab"),
    re.compile(r"127\.0\.0\.1"),
    re.compile(r":5432\b"),
    re.compile(r"--port\b"),
    re.compile(r"--create\b"),
)


def _script(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def _bash(body: str) -> subprocess.CompletedProcess[str]:
    script = f"set -euo pipefail\nBACKUP_DIR='{ROOT}'\n. '{ROOT / 'lib.sh'}'\n{body}\n"
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=False)


class BackupScriptTests(unittest.TestCase):
    def test_scripts_parse(self) -> None:
        names = sorted(path.name for path in ROOT.glob("*.sh"))
        self.assertEqual(names, ["dump.sh", "lib.sh", "restore.sh"])
        for name in names:
            subprocess.run(["bash", "-n", str(ROOT / name)], check=True)
        self.assertIn("set -euo pipefail", _script("dump.sh"))
        self.assertIn("set -euo pipefail", _script("restore.sh"))

    def test_only_the_three_compose_postgres_services(self) -> None:
        pairs = re.findall(
            r"^\s+(order_db|reporting_db|odoo_db)\)\s+printf '%s\\n' \"([^\"]+)\"",
            LIB,
            re.MULTILINE,
        )
        self.assertEqual(dict(pairs), SERVICES)
        for database, service in SERVICES.items():
            self.assertIn(f"\n  {service}:\n", COMPOSE)
            self.assertIn(f"POSTGRES_DB: {database}\n", COMPOSE)
        blob = LIB + _script("dump.sh") + _script("restore.sh")
        for line in blob.splitlines():
            if "docker compose" not in line:
                continue
            self.assertIn("exec -T", line)
            self.assertIn("${service}", line)
        self.assertNotRegex(blob, r"exec -T \"?(rabbitmq|redis|order-service|reporting-service|odoo)\"?")

    def test_cross_database_restore_is_refused_from_the_archive_header(self) -> None:
        self.assertIn("dbname:", LIB)
        self.assertIn("pg_restore --list", LIB)
        self.assertIn("The file name is not the database name.", LIB)
        restore = _script("restore.sh")
        self.assertLess(restore.index("archive_dbname"), restore.index("pg_restore --no-password"))
        self.assertLess(restore.index("refuse_cross_database"), restore.index("--clean"))
        for source in DATABASES:
            for target in DATABASES:
                result = _bash(f"refuse_cross_database {source} {target} restore")
                if source == target:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        f"Refusing to restore a dump of {source} into {target}.",
                        result.stderr,
                    )
        unknown = _bash("refuse_cross_database postgres order_db restore")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("archive header names 'postgres'", unknown.stderr)

    def test_restore_requires_yes_and_names_the_database(self) -> None:
        restore = _script("restore.sh")
        self.assertLess(restore.index("--yes"), restore.index("require_docker"))
        self.assertIn("About to replace the data in ${db}", restore)
        missing = subprocess.run(
            ["bash", str(ROOT / "restore.sh"), "order_db", "deploy/backup/dumps/order_db.dump"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("without --yes", missing.stderr)
        self.assertIn("order_db", missing.stderr)
        unknown = subprocess.run(
            ["bash", str(ROOT / "restore.sh"), "redis", "somewhere.dump", "--yes"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("Refusing database 'redis'", unknown.stderr)

    def test_unknown_database_is_refused_before_docker(self) -> None:
        for name in ("redis", "postgres", "rabbitmq", "order_service"):
            result = subprocess.run(
                ["bash", str(ROOT / "dump.sh"), name],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, name)
            self.assertIn(f"Refusing database '{name}'", result.stderr)
            self.assertNotIn("Nothing was dumped or restored.", result.stderr)

    def test_docker_down_exits_before_dump_or_restore(self) -> None:
        info = subprocess.run(["docker", "info"], capture_output=True, check=False)
        if info.returncode == 0:
            self.skipTest("Docker is available; this check is the daemon-down path")
        dumps = ROOT / "dumps"
        before = set(dumps.rglob("*")) if dumps.exists() else set()
        dumped = subprocess.run(
            ["bash", str(ROOT / "dump.sh"), "order_db"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(dumped.returncode, 1)
        self.assertIn("Nothing was dumped or restored.", dumped.stderr)
        self.assertNotIn("Wrote ", dumped.stdout)
        with tempfile.NamedTemporaryFile() as handle:
            restored = subprocess.run(
                ["bash", str(ROOT / "restore.sh"), "reporting_db", handle.name, "--yes"],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(restored.returncode, 1)
        self.assertIn("Nothing was dumped or restored.", restored.stderr)
        self.assertNotIn("About to replace", restored.stdout)
        after = set(dumps.rglob("*")) if dumps.exists() else set()
        self.assertEqual(before, after)

    def test_scripts_do_not_wipe_call_internal_routes_or_embed_a_key(self) -> None:
        blob = "\n".join(_script(name) for name in ("lib.sh", "dump.sh", "restore.sh"))
        for pattern in FORBIDDEN:
            self.assertIsNone(pattern.search(blob), pattern.pattern)
        self.assertIn("Redis is a cache and is not backed up.", LIB)
        self.assertIn("Redis is a cache and is not dumped.", _script("dump.sh"))
        self.assertLess(_script("dump.sh").index("require_docker"), _script("dump.sh").index("pg_dump"))
        self.assertLess(LIB.index("docker info"), LIB.index("docker compose"))

    def test_dumps_directory_is_gitignored(self) -> None:
        self.assertIn("deploy/backup/dumps/", GITIGNORE)
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "Distributed/deploy/backup/dumps/order_db.dump"],
            cwd=REPO,
            check=False,
        )
        self.assertEqual(ignored.returncode, 0)


if __name__ == "__main__":
    unittest.main()
