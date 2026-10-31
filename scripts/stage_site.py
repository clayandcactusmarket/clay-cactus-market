"""Stage only public website files, excluding tooling, Git history and secrets."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
destination = root / "_site"
if destination.exists():
    shutil.rmtree(destination)
destination.mkdir()
for path in root.iterdir():
    if path.is_file() and (path.suffix.lower() in {".html", ".css", ".js", ".png", ".jpg", ".ico"}
                           or path.name in {"CNAME", "robots.txt", "sitemap.xml"}):
        shutil.copy2(path, destination / path.name)
for name in ("assets", "ceramics", "data"):
    shutil.copytree(root / name, destination / name)
(destination / ".nojekyll").touch()
