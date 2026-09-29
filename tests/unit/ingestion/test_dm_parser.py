from __future__ import annotations

from datetime import UTC, datetime

from repowise.core.ingestion.models import FileInfo
from repowise.core.ingestion.parser import ASTParser


def _file(path: str = "code/sample.dm") -> FileInfo:
    return FileInfo(
        path=path,
        abs_path=f"/repo/{path}",
        language="dm",
        size_bytes=0,
        git_hash="",
        last_modified=datetime.now(UTC),
        is_test=False,
        is_config=False,
        is_api_contract=False,
        is_entry_point=path.endswith(".dme"),
    )


def test_extracts_types_procs_and_globals() -> None:
    source = b"""\
var/global/combat_enabled = 1

/mob/player
\tproc/takeDamage(amount)
\t\tapplyDamage(amount)

/proc/applyDamage(amount)
\treturn amount
"""

    parsed = ASTParser().parse_file(_file(), source)

    assert ("class", "/mob/player") in {(s.kind, s.name) for s in parsed.symbols}
    assert ("variable", "combat_enabled") in {(s.kind, s.name) for s in parsed.symbols}
    assert ("method", "takeDamage") in {(s.kind, s.name) for s in parsed.symbols}
    assert ("function", "applyDamage") in {(s.kind, s.name) for s in parsed.symbols}
    assert parsed.calls == []


def test_extracts_dme_includes() -> None:
    source = b'#include "src\\Code\\Combat\\SpeedDelay.dm"\n'

    parsed = ASTParser().parse_file(_file("DU.dme"), source)

    assert [imp.module_path for imp in parsed.imports] == ["src\\Code\\Combat\\SpeedDelay.dm"]


def test_caps_legacy_parse_error_context_without_dropping_symbols() -> None:
    source = (
        (b"invalid syntax that the grammar cannot recover cleanly\n" * 200)
        + b"""\
/proc/stillIndexed()
\treturn 1
"""
    )

    parsed = ASTParser().parse_file(_file(), source)

    assert len(parsed.parse_errors) <= 21
    assert any("additional DM parse errors" in error for error in parsed.parse_errors)
    assert any(symbol.name == "stillIndexed" for symbol in parsed.symbols)
