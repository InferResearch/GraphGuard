"""Private-paper source lookup must survive archiving the revision response."""
from pathlib import Path
import sys
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_manuscript_artifacts as verifier


def test_read_existing_source(tmp_path):
    source = tmp_path / "main.tex"
    source.write_text("current manuscript", encoding="utf-8")
    assert verifier.read_source(source) == "current manuscript"


def test_read_archived_response(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    directory = tmp_path / "paper" / "archives"
    directory.mkdir(parents=True)
    with ZipFile(directory / "revision.zip", "w") as package:
        package.writestr("revision/response.tex", "historical response")
    assert verifier.read_source(tmp_path / "paper" / "response.tex") == "historical response"


def test_existing_response_takes_precedence(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    source = tmp_path / "paper" / "response.tex"
    source.parent.mkdir()
    source.write_text("unarchived response", encoding="utf-8")
    assert verifier.read_source(source) == "unarchived response"


def test_other_missing_source_is_not_silently_skipped(tmp_path):
    with pytest.raises(FileNotFoundError):
        verifier.read_source(tmp_path / "missing.tex")
