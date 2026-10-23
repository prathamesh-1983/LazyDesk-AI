from pathlib import Path
import shutil

CATEGORY_RULES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff"},
    "Audio": {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".json", ".yaml", ".yml", ".sql", ".sh"},
}
SENSITIVE_NAMES = {"desktop.ini", "thumbs.db"}

def categorize(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, extensions in CATEGORY_RULES.items():
        if suffix in extensions:
            return category
    name = path.name.lower()
    if any(word in name for word in ("invoice", "receipt", "bill")):
        return "Finance"
    if any(word in name for word in ("resume", "cv", "cover-letter")):
        return "Career"
    return "Other"

def scan_directory(folder: str, max_files: int = 250):
    root = Path(folder).expanduser().resolve()
    if not root.exists():
        raise ValueError("The folder does not exist.")
    if not root.is_dir():
        raise ValueError("The path is not a directory.")
    entries = []
    for path in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file() or path.name in SENSITIVE_NAMES:
            continue
        try:
            stat = path.stat()
            entries.append({
                "name": path.name,
                "path": str(path.resolve()),
                "extension": path.suffix.lower(),
                "size": stat.st_size,
                "category": categorize(path),
            })
        except OSError:
            continue
        if len(entries) >= max_files:
            break
    return entries

def build_plan(entries, root_folder: str):
    root = Path(root_folder).resolve()
    plan = []
    for entry in entries:
        source = Path(entry["path"]).resolve()
        # Never operate on paths outside the scanned root.
        if source.parent != root or not source.is_file():
            plan.append({"source": str(source), "destination": "", "status": "Skipped: path changed"})
            continue
        category = entry["category"]
        destination_dir = root / category
        destination = destination_dir / source.name
        if destination_dir == source.parent:
            status = "Already organized"
        elif destination.exists():
            status = "Skipped: destination exists"
        else:
            status = "Ready"
        plan.append({"source": str(source), "destination": str(destination), "status": status})
    return plan

def apply_plan(plan):
    outcomes = []
    for item in plan:
        source = Path(item["source"])
        destination_value = item.get("destination", "")
        if item["status"] != "Ready" or not destination_value:
            outcomes.append({**item, "status": item["status"]})
            continue
        destination = Path(destination_value)
        # Re-check all safety conditions at apply time.
        if not source.exists() or not source.is_file():
            outcomes.append({**item, "status": "Skipped: source no longer exists"})
            continue
        if source.parent == destination.parent:
            outcomes.append({**item, "status": "Skipped: already organized"})
            continue
        if destination.exists():
            outcomes.append({**item, "status": "Skipped: destination exists"})
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Avoid overwriting files created between the check and move.
        if destination.exists():
            outcomes.append({**item, "status": "Skipped: destination exists"})
            continue
        shutil.move(str(source), str(destination))
        outcomes.append({**item, "status": "Moved"})
    return outcomes

def category_folders():
    return list(CATEGORY_RULES) + ["Finance", "Career", "Other"]
