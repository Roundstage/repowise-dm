from __future__ import annotations

import networkx as nx

from repowise.core.ingestion.resolvers.context import ResolverContext
from repowise.core.ingestion.resolvers.dm import resolve_dm_include


def _ctx(*paths: str) -> ResolverContext:
    return ResolverContext(
        path_set=set(paths),
        stem_map={},
        graph=nx.DiGraph(),
    )


def test_dme_windows_path_resolves_from_project_root() -> None:
    ctx = _ctx("DU.dme", "src/Code/Combat/SpeedDelay.dm")

    assert (
        resolve_dm_include("src\\Code\\Combat\\SpeedDelay.dm", "DU.dme", ctx)
        == "src/Code/Combat/SpeedDelay.dm"
    )


def test_nested_include_resolves_relative_to_importer() -> None:
    ctx = _ctx("src/Code/lib.dm", "src/Code/Combat/Skill.dm")

    assert resolve_dm_include("../lib.dm", "src/Code/Combat/Skill.dm", ctx) == "src/Code/lib.dm"
    assert resolve_dm_include("lib.dm", "src/Code/Combat/Skill.dm", ctx) is None


def test_ambiguous_bare_filename_is_not_guessed() -> None:
    ctx = _ctx("one/Common.dm", "two/Common.dm", "DU.dme")

    assert resolve_dm_include("Common.dm", "DU.dme", ctx) is None
