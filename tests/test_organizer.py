from pathlib import Path
from lazydesk.organizer import categorize, scan_directory, build_plan, apply_plan

def test_categorize_common_types():
    assert categorize(Path("photo.JPG")) == "Images"
    assert categorize(Path("report.pdf")) == "Documents"
    assert categorize(Path("unknown.xyz")) == "Other"

def test_scan_only_top_level(tmp_path):
    (tmp_path / "notes.txt").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "inside.txt").write_text("nested")
    result = scan_directory(str(tmp_path))
    assert [x["name"] for x in result] == ["notes.txt"]

def test_plan_and_apply_moves_without_overwrite(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("new report")
    entries = scan_directory(str(tmp_path))
    plan = build_plan(entries, str(tmp_path))
    assert plan[0]["status"] == "Ready"
    outcomes = apply_plan(plan)
    assert outcomes[0]["status"] == "Moved"
    assert (tmp_path / "Documents" / "report.pdf").read_text() == "new report"
    assert not source.exists()

def test_existing_destination_is_skipped(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("source")
    dest_dir = tmp_path / "Documents"
    dest_dir.mkdir()
    (dest_dir / "report.pdf").write_text("existing")
    plan = build_plan(scan_directory(str(tmp_path)), str(tmp_path))
    assert plan[0]["status"] == "Skipped: destination exists"
    outcomes = apply_plan(plan)
    assert (dest_dir / "report.pdf").read_text() == "existing"
