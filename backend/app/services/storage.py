from __future__ import annotations
from pathlib import Path
from app.core.config import settings


class LocalDocumentStorage:
    """Small storage boundary so local files can later move to S3/SharePoint."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or settings.document_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, category: str, filename: str) -> Path:
        safe_name = Path(filename).name
        target = (self.root / category / safe_name).resolve()
        if self.root not in target.parents:
            raise ValueError("Unsafe document path")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def resolve(self, stored_path: str) -> Path:
        candidate = Path(stored_path).resolve()
        allowed = [self.root, Path("generated").resolve()]
        if not any(candidate == root or root in candidate.parents for root in allowed):
            raise ValueError("Document is outside configured storage")
        return candidate


storage = LocalDocumentStorage()
