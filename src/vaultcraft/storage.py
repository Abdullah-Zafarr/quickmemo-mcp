"""Local Markdown & Zettelkasten storage engine for VaultCraft."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml

from .models import Note, NoteMetadata, VaultMetrics


WIKILINK_PATTERN = re.compile(r"\[\[(.*?)\]\]")
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class VaultStorage:
    """Manages reading, writing, indexing, and graph traversal for a markdown vault."""

    def __init__(self, root_dir: Optional[str] = None):
        if root_dir:
            self.root_dir = Path(root_dir)
        else:
            env_path = os.environ.get("VAULTCRAFT_PATH")
            if env_path:
                self.root_dir = Path(env_path)
            else:
                self.root_dir = Path.cwd() / ".vaultcraft_data"

        self.notes_dir = self.root_dir / "notes"
        self.daily_dir = self.root_dir / "daily"

        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.daily_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, title: str) -> str:
        """Sanitizes note title into a safe filename."""
        sanitized = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        sanitized = sanitized.replace(" ", "_")
        return f"{sanitized}.md"

    def _extract_wikilinks(self, content: str) -> List[str]:
        """Finds all [[Note Title]] references in markdown content."""
        matches = WIKILINK_PATTERN.findall(content)
        # Handle [[Note Title|Custom Label]] by taking only the target title
        links = [m.split("|")[0].strip() for m in matches if m.strip()]
        # Return unique list preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        return unique_links

    def _parse_markdown(self, raw_text: str, default_title: str) -> Tuple[dict, str]:
        """Extracts YAML frontmatter (if present) and body text."""
        fm_match = FRONTMATTER_PATTERN.match(raw_text)
        if fm_match:
            try:
                fm_data = yaml.safe_load(fm_match.group(1)) or {}
            except Exception:
                fm_data = {}
            body = raw_text[fm_match.end():]
        else:
            fm_data = {}
            body = raw_text

        if "title" not in fm_data:
            fm_data["title"] = default_title
        if "tags" not in fm_data or not isinstance(fm_data["tags"], list):
            fm_data["tags"] = []

        return fm_data, body

    def save_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> Note:
        """Creates or updates a markdown note with frontmatter and wikilinks."""
        filename = self._sanitize_filename(title)
        file_path = self.notes_dir / filename

        existing_created_at = datetime.now().isoformat()
        if file_path.exists():
            existing_note = self.read_note(title)
            if existing_note:
                existing_created_at = existing_note.metadata.created_at

        # Extract body if user passed frontmatter or raw text
        fm_data, body = self._parse_markdown(content, title)

        merged_tags = list(set((tags or []) + fm_data.get("tags", [])))
        outgoing_links = self._extract_wikilinks(body)

        now = datetime.now().isoformat()
        metadata_dict = {
            "title": title,
            "tags": merged_tags,
            "created_at": existing_created_at,
            "updated_at": now,
        }

        frontmatter_str = yaml.dump(metadata_dict, sort_keys=False).strip()
        full_markdown = f"---\n{frontmatter_str}\n---\n\n# {title}\n\n{body.strip()}\n"

        file_path.write_text(full_markdown, encoding="utf-8")

        meta = NoteMetadata(
            title=title,
            tags=merged_tags,
            created_at=existing_created_at,
            updated_at=now,
            outgoing_links=outgoing_links,
        )

        return Note(
            title=title,
            content=body.strip(),
            metadata=meta,
            raw_markdown=full_markdown,
        )

    def read_note(self, title: str) -> Optional[Note]:
        """Reads and parses a note by its title."""
        filename = self._sanitize_filename(title)
        file_path = self.notes_dir / filename

        if not file_path.exists():
            # Try case-insensitive search
            found = None
            for p in self.notes_dir.glob("*.md"):
                if p.stem.lower() == filename[:-3].lower() or p.stem.replace("_", " ").lower() == title.lower():
                    found = p
                    break
            if not found:
                return None
            file_path = found

        raw_text = file_path.read_text(encoding="utf-8")
        fm_data, body = self._parse_markdown(raw_text, title)

        outgoing_links = self._extract_wikilinks(body)

        meta = NoteMetadata(
            title=fm_data.get("title", title),
            tags=fm_data.get("tags", []),
            created_at=fm_data.get("created_at", datetime.now().isoformat()),
            updated_at=fm_data.get("updated_at", datetime.now().isoformat()),
            outgoing_links=outgoing_links,
        )

        return Note(
            title=meta.title,
            content=body.strip(),
            metadata=meta,
            raw_markdown=raw_text,
        )

    def list_all_notes(self) -> List[Note]:
        """Loads all notes from the vault."""
        notes = []
        for file_path in self.notes_dir.glob("*.md"):
            try:
                raw_text = file_path.read_text(encoding="utf-8")
                stem_title = file_path.stem.replace("_", " ")
                fm_data, body = self._parse_markdown(raw_text, stem_title)
                title = fm_data.get("title", stem_title)
                outgoing = self._extract_wikilinks(body)
                meta = NoteMetadata(
                    title=title,
                    tags=fm_data.get("tags", []),
                    created_at=fm_data.get("created_at", datetime.now().isoformat()),
                    updated_at=fm_data.get("updated_at", datetime.now().isoformat()),
                    outgoing_links=outgoing,
                )
                notes.append(Note(title=title, content=body.strip(), metadata=meta, raw_markdown=raw_text))
            except Exception:
                continue
        return notes

    def search(self, query: str = "", tag: str = "", limit: int = 10) -> List[Dict]:
        """Search across note titles, contents, and tags with simple relevance scoring."""
        all_notes = self.list_all_notes()
        results = []

        q = query.lower().strip()
        t = tag.lower().strip()

        for note in all_notes:
            score = 0
            # Tag match
            note_tags_lower = [x.lower() for x in note.metadata.tags]
            if t and t in note_tags_lower:
                score += 5

            if q:
                if q == note.title.lower():
                    score += 10
                elif q in note.title.lower():
                    score += 5

                # Count query appearances in body
                matches = note.content.lower().count(q)
                score += min(matches * 2, 10)

            if (q or t) and score > 0:
                results.append({
                    "title": note.title,
                    "score": score,
                    "tags": note.metadata.tags,
                    "outgoing_links": note.metadata.outgoing_links,
                    "snippet": note.content[:150] + ("..." if len(note.content) > 150 else ""),
                })
            elif not q and not t:
                results.append({
                    "title": note.title,
                    "score": 1,
                    "tags": note.metadata.tags,
                    "outgoing_links": note.metadata.outgoing_links,
                    "snippet": note.content[:150] + ("..." if len(note.content) > 150 else ""),
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def find_backlinks(self, target_title: str) -> List[str]:
        """Finds all notes that contain a [[wikilink]] pointing to target_title."""
        target_clean = target_title.strip().lower()
        all_notes = self.list_all_notes()
        backlink_notes = []

        for note in all_notes:
            if note.title.strip().lower() == target_clean:
                continue
            for link in note.metadata.outgoing_links:
                if link.strip().lower() == target_clean:
                    backlink_notes.append(note.title)
                    break
        return backlink_notes

    def delete_note(self, title: str) -> bool:
        """Deletes a note from the vault."""
        filename = self._sanitize_filename(title)
        file_path = self.notes_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def append_daily_log(self, entry: str, category: str = "General") -> str:
        """Appends a structured timestamped log entry to today's daily note."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        file_path = self.daily_dir / f"{today_str}.md"

        if not file_path.exists():
            header = f"# Daily Journal - {today_str}\n\n"
            file_path.write_text(header, encoding="utf-8")

        formatted_entry = f"### [{now_time}] {category}\n{entry.strip()}\n\n"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(formatted_entry)

        return f"Logged entry at {now_time} under [{category}] in daily/{today_str}.md"

    def read_daily_log(self, date_str: Optional[str] = None) -> str:
        """Reads a specific daily log or today's log."""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = self.daily_dir / f"{date_str}.md"
        if not file_path.exists():
            return f"No daily log entries found for {date_str}."
        return file_path.read_text(encoding="utf-8")

    def get_metrics(self) -> VaultMetrics:
        """Calculates vault health, graph connectivity, orphan notes, and tag frequency."""
        notes = self.list_all_notes()
        total_notes = len(notes)
        total_links = 0
        tag_counts: Dict[str, int] = {}
        inbound_counts: Dict[str, int] = {n.title: 0 for n in notes}

        for note in notes:
            total_links += len(note.metadata.outgoing_links)
            for tag in note.metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            for link in note.metadata.outgoing_links:
                for target_note in notes:
                    if target_note.title.lower() == link.lower():
                        inbound_counts[target_note.title] += 1

        orphan_notes = [
            n.title for n in notes
            if len(n.metadata.outgoing_links) == 0 and inbound_counts.get(n.title, 0) == 0
        ]

        most_linked = sorted(
            [{"title": k, "backlinks": v} for k, v in inbound_counts.items() if v > 0],
            key=lambda x: x["backlinks"],
            reverse=True
        )[:5]

        return VaultMetrics(
            total_notes=total_notes,
            total_links=total_links,
            total_tags=len(tag_counts),
            tags=tag_counts,
            orphan_notes=orphan_notes,
            most_linked_notes=most_linked,
        )
