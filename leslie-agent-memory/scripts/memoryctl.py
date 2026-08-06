#!/usr/bin/env python3
"""Self-contained durable memory manager for Claude Code, Codex, and OpenCode."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


FORMAT_VERSION = 1
ACTORS = ("shared", "claude", "codex", "opencode", "human", "test")
MEMORY_TYPES = ("preference", "project", "decision", "workflow", "fact", "open_loop", "case")
STATUSES = ("active", "outdated", "resolved")
REQUIRED_FIELDS = (
    "memory_id",
    "title",
    "memory_type",
    "status",
    "agent_scope",
    "project_id",
    "verified_at",
    "review_after_days",
    "tags",
)
ROUTING_FILES = {"AGENTS.md", "INDEX.md", "README.md"}
SECRET_PATTERNS = (
    ("api-key", re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    (
        "named-secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}"
        ),
    ),
)


class MemoryErrorWithCode(RuntimeError):
    pass


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.date.today().isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def session_hash(actor: str, session_id: str) -> str:
    return sha256_bytes((actor + "\0" + session_id).encode("utf-8"))


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_home(raw: Optional[str]) -> Path:
    value = raw or os.environ.get("LESLIE_MEMORY_HOME", "")
    if not value.strip():
        raise MemoryErrorWithCode("Memory Home is required: pass --home /absolute/path or set LESLIE_MEMORY_HOME")
    path = Path(os.path.expandvars(value)).expanduser()
    if not path.is_absolute():
        raise MemoryErrorWithCode("Memory Home must be an absolute path")
    path = path.resolve(strict=False)
    if path == Path("/") or path == Path.home().resolve():
        raise MemoryErrorWithCode("Refusing a broad Memory Home path")
    return path


def paths_for(home: Path) -> Dict[str, Path]:
    return {
        "home": home,
        "config": home / "leslie-memory.json",
        "vault": home / "vault",
        "state": home / "state",
        "db": home / "state" / "memory.sqlite",
        "reports": home / "reports",
        "exports": home / "exports",
    }


def emit(payload: Any, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if isinstance(payload, str):
        print(payload)
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def require_initialized(home: Path) -> Dict[str, Path]:
    paths = paths_for(home)
    if not paths["config"].is_file() or not paths["vault"].is_dir():
        raise MemoryErrorWithCode(f"Memory Home is not initialized: {home}")
    return paths


def ensure_state(paths: Dict[str, Path]) -> sqlite3.Connection:
    paths["state"].mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(paths["db"]))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents (
          path TEXT PRIMARY KEY,
          memory_id TEXT NOT NULL,
          title TEXT NOT NULL,
          memory_type TEXT NOT NULL,
          status TEXT NOT NULL,
          agent_scope TEXT NOT NULL,
          project_id TEXT NOT NULL,
          verified_at TEXT NOT NULL,
          review_after_days INTEGER NOT NULL,
          tags TEXT NOT NULL,
          body TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          indexed_at TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
          path UNINDEXED,
          title,
          body,
          tags,
          search_tokens,
          tokenize='unicode61 remove_diacritics 2'
        );
        CREATE TABLE IF NOT EXISTS claims (
          path TEXT NOT NULL,
          actor TEXT NOT NULL,
          session_hash TEXT NOT NULL,
          state TEXT NOT NULL,
          claimed_at TEXT NOT NULL,
          closed_at TEXT,
          content_hash TEXT NOT NULL,
          PRIMARY KEY(path, actor, session_hash, state)
        );
        CREATE TABLE IF NOT EXISTS closeouts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          actor TEXT NOT NULL,
          session_hash TEXT NOT NULL,
          created_at TEXT NOT NULL,
          file_count INTEGER NOT NULL,
          git_commit TEXT,
          result TEXT NOT NULL
        );
        """
    )
    return conn


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
    if value.isdigit():
        return int(value)
    return value.strip("'\"")


def parse_memory(path: Path) -> Tuple[Dict[str, Any], str, List[str]]:
    text = path.read_text(encoding="utf-8")
    errors: List[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["missing frontmatter"]
    marker = text.find("\n---\n", 4)
    if marker < 0:
        return {}, text, ["unterminated frontmatter"]
    frontmatter = text[4:marker]
    body = text[marker + 5 :]
    metadata: Dict[str, Any] = {}
    for line_no, raw in enumerate(frontmatter.splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        key, separator, value = raw.partition(":")
        if not separator or not key.strip():
            errors.append(f"invalid frontmatter line {line_no}")
            continue
        metadata[key.strip()] = parse_scalar(value)
    for field in REQUIRED_FIELDS:
        if field not in metadata or metadata[field] in ("", None):
            errors.append(f"missing required field: {field}")
    if metadata.get("memory_type") not in MEMORY_TYPES:
        errors.append("invalid memory_type")
    if metadata.get("status") not in STATUSES:
        errors.append("invalid status")
    if metadata.get("agent_scope") not in ACTORS[:4]:
        errors.append("invalid agent_scope")
    try:
        dt.date.fromisoformat(str(metadata.get("verified_at", "")))
    except ValueError:
        errors.append("verified_at must be YYYY-MM-DD")
    review = metadata.get("review_after_days")
    if not isinstance(review, int) or review <= 0:
        errors.append("review_after_days must be a positive integer")
    if not isinstance(metadata.get("tags"), list):
        errors.append("tags must be an inline list")
    return metadata, body, errors


def memory_files(vault: Path) -> Iterable[Path]:
    for path in sorted(vault.rglob("*.md")):
        if path.name in ROUTING_FILES:
            continue
        if any(part.startswith(".") for part in path.relative_to(vault).parts):
            continue
        yield path


def cjk_blocks(text: str) -> List[str]:
    return re.findall(r"[\u3400-\u9fff]+", text)


def search_tokens(text: str) -> List[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9][a-z0-9_.-]{1,}", lowered)
    for block in cjk_blocks(lowered):
        if len(block) == 1:
            tokens.append(block)
        else:
            tokens.extend(block[index : index + 2] for index in range(len(block) - 1))
    return list(dict.fromkeys(tokens))


def secret_findings(text: str) -> List[str]:
    return [name for name, pattern in SECRET_PATTERNS if pattern.search(text)]


def relative_vault_path(paths: Dict[str, Path], path: Path) -> str:
    resolved = path.expanduser().resolve(strict=True)
    vault = paths["vault"].resolve(strict=True)
    try:
        return resolved.relative_to(vault).as_posix()
    except ValueError as exc:
        raise MemoryErrorWithCode(f"File is outside the Memory Home vault: {resolved}") from exc


def rebuild_index(paths: Dict[str, Path]) -> Dict[str, Any]:
    conn = ensure_state(paths)
    indexed = 0
    invalid: List[Dict[str, Any]] = []
    seen: set[str] = set()
    try:
        for path in memory_files(paths["vault"]):
            rel = path.relative_to(paths["vault"]).as_posix()
            metadata, body, errors = parse_memory(path)
            if errors:
                invalid.append({"path": rel, "errors": errors})
                conn.execute("DELETE FROM documents WHERE path = ?", (rel,))
                conn.execute("DELETE FROM documents_fts WHERE path = ?", (rel,))
                continue
            seen.add(rel)
            text = path.read_text(encoding="utf-8")
            content_hash = sha256_bytes(text.encode("utf-8"))
            tags = ", ".join(str(tag) for tag in metadata["tags"])
            conn.execute(
                """
                INSERT INTO documents(path, memory_id, title, memory_type, status, agent_scope,
                  project_id, verified_at, review_after_days, tags, body, content_hash, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                  memory_id=excluded.memory_id, title=excluded.title,
                  memory_type=excluded.memory_type, status=excluded.status,
                  agent_scope=excluded.agent_scope, project_id=excluded.project_id,
                  verified_at=excluded.verified_at, review_after_days=excluded.review_after_days,
                  tags=excluded.tags, body=excluded.body, content_hash=excluded.content_hash,
                  indexed_at=excluded.indexed_at
                """,
                (
                    rel,
                    str(metadata["memory_id"]),
                    str(metadata["title"]),
                    str(metadata["memory_type"]),
                    str(metadata["status"]),
                    str(metadata["agent_scope"]),
                    str(metadata["project_id"]),
                    str(metadata["verified_at"]),
                    int(metadata["review_after_days"]),
                    tags,
                    body,
                    content_hash,
                    iso_now(),
                ),
            )
            conn.execute("DELETE FROM documents_fts WHERE path = ?", (rel,))
            token_text = " ".join(search_tokens(str(metadata["title"]) + "\n" + tags + "\n" + body))
            conn.execute(
                "INSERT INTO documents_fts(path, title, body, tags, search_tokens) VALUES (?, ?, ?, ?, ?)",
                (rel, str(metadata["title"]), body, tags, token_text),
            )
            indexed += 1
        existing = [row[0] for row in conn.execute("SELECT path FROM documents")]
        for rel in existing:
            if rel not in seen:
                conn.execute("DELETE FROM documents WHERE path = ?", (rel,))
                conn.execute("DELETE FROM documents_fts WHERE path = ?", (rel,))
        conn.commit()
    finally:
        conn.close()
    return {"indexed": indexed, "invalid": invalid, "database": str(paths["db"])}


def search_index(paths: Dict[str, Path], query: str, actor: str, limit: int) -> List[Dict[str, Any]]:
    rebuild_index(paths)
    conn = ensure_state(paths)
    candidates: Dict[str, sqlite3.Row] = {}
    tokens = search_tokens(query)
    try:
        if tokens:
            fts_query = " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens[:24])
            for row in conn.execute(
                "SELECT path FROM documents_fts WHERE documents_fts MATCH ? LIMIT ?",
                (fts_query, max(limit * 8, 40)),
            ):
                doc = conn.execute("SELECT * FROM documents WHERE path = ?", (row["path"],)).fetchone()
                if doc:
                    candidates[doc["path"]] = doc
        like = "%" + query.lower() + "%"
        for row in conn.execute(
            "SELECT * FROM documents WHERE lower(title) LIKE ? OR lower(body) LIKE ? OR lower(tags) LIKE ? LIMIT ?",
            (like, like, like, max(limit * 8, 40)),
        ):
            candidates[row["path"]] = row
    finally:
        conn.close()
    result: List[Dict[str, Any]] = []
    q = query.lower().strip()
    for row in candidates.values():
        if row["status"] != "active":
            continue
        if actor not in ("shared", "human", "test") and row["agent_scope"] not in ("shared", actor):
            continue
        title = row["title"].lower()
        body = row["body"].lower()
        tags = row["tags"].lower()
        score = 0.0
        if q and q in title:
            score += 12.0
        if q and q in tags:
            score += 8.0
        if q and q in body:
            score += 6.0
        for token in tokens:
            score += min(title.count(token) * 2.5, 5.0)
            score += min(tags.count(token) * 1.5, 3.0)
            score += min(body.count(token) * 0.4, 4.0)
        if score <= 0:
            continue
        snippet = re.sub(r"\s+", " ", row["body"]).strip()[:220]
        result.append(
            {
                "path": str(paths["vault"] / row["path"]),
                "relative_path": row["path"],
                "memory_id": row["memory_id"],
                "title": row["title"],
                "memory_type": row["memory_type"],
                "agent_scope": row["agent_scope"],
                "verified_at": row["verified_at"],
                "score": round(score, 3),
                "snippet": snippet,
            }
        )
    result.sort(key=lambda item: (-item["score"], item["relative_path"]))
    return result[:limit]


def audit_home(paths: Dict[str, Path]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    ids: Dict[str, List[str]] = {}
    hashes: Dict[str, List[str]] = {}
    checked = 0
    current = dt.date.today()
    for path in memory_files(paths["vault"]):
        checked += 1
        rel = path.relative_to(paths["vault"]).as_posix()
        text = path.read_text(encoding="utf-8")
        metadata, _body, errors = parse_memory(path)
        for error in errors:
            findings.append({"severity": "error", "code": "schema", "path": rel, "detail": error})
        for secret_type in secret_findings(text):
            findings.append(
                {"severity": "error", "code": "secret", "path": rel, "detail": secret_type}
            )
        if errors:
            continue
        memory_id = str(metadata["memory_id"])
        ids.setdefault(memory_id, []).append(rel)
        normalized_body = re.sub(r"\s+", " ", _body).strip().lower()
        hashes.setdefault(sha256_bytes(normalized_body.encode("utf-8")), []).append(rel)
        verified = dt.date.fromisoformat(str(metadata["verified_at"]))
        due = verified + dt.timedelta(days=int(metadata["review_after_days"]))
        if metadata["status"] == "active" and due < current:
            findings.append(
                {
                    "severity": "warning",
                    "code": "stale",
                    "path": rel,
                    "detail": f"review due {due.isoformat()}",
                }
            )
    for memory_id, rels in ids.items():
        if len(rels) > 1:
            findings.append(
                {"severity": "error", "code": "duplicate-memory-id", "path": rels, "detail": memory_id}
            )
    for digest, rels in hashes.items():
        if len(rels) > 1 and digest != sha256_bytes(b"" ):
            findings.append(
                {"severity": "warning", "code": "duplicate-body", "path": rels, "detail": digest[:12]}
            )
    report = {
        "format_version": FORMAT_VERSION,
        "generated_at": iso_now(),
        "checked_files": checked,
        "errors": sum(1 for item in findings if item["severity"] == "error"),
        "warnings": sum(1 for item in findings if item["severity"] == "warning"),
        "findings": findings,
    }
    paths["reports"].mkdir(parents=True, exist_ok=True)
    (paths["reports"] / "latest-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def run_git(home: Path, args: Sequence[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(home), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def command_init(args: argparse.Namespace, home: Path) -> Dict[str, Any]:
    paths = paths_for(home)
    if home.exists() and any(home.iterdir()):
        raise MemoryErrorWithCode(f"Refusing to initialize a non-empty directory: {home}")
    home.mkdir(parents=True, exist_ok=True)
    template = package_root() / "templates" / "vault"
    shutil.copytree(template, paths["vault"], dirs_exist_ok=True)
    for key in ("state", "reports", "exports"):
        paths[key].mkdir(parents=True, exist_ok=True)
    config = {
        "format_version": FORMAT_VERSION,
        "name": args.name,
        "created_at": iso_now(),
        "vault": "vault",
        "state": "state",
        "actors": ["claude", "codex", "opencode"],
        "features": {"markdown": True, "sqlite_fts": True, "vector": False, "automatic_hooks": False},
    }
    paths["config"].write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (home / ".gitignore").write_text("state/\nreports/latest-*.json\nexports/\n.DS_Store\n", encoding="utf-8")
    conn = ensure_state(paths)
    conn.close()
    git_status = "not-requested"
    if args.git:
        proc = run_git(home, ["init"])
        if proc.returncode != 0:
            raise MemoryErrorWithCode(proc.stderr.strip() or "git init failed")
        git_status = "initialized"
    index_report = rebuild_index(paths)
    return {"status": "initialized", "home": str(home), "git": git_status, "index": index_report}


def command_paths(paths: Dict[str, Path]) -> Dict[str, Any]:
    return {
        "program": str(package_root()),
        "home": str(paths["home"]),
        "vault": str(paths["vault"]),
        "derived_state": str(paths["state"]),
        "reports": str(paths["reports"]),
        "exports": str(paths["exports"]),
        "program_removal_affects_data": False,
        "home_removal_affects_program": False,
    }


def command_prewrite(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    if secret_findings(args.summary):
        return {
            "action": "ASK_USER",
            "reason": "The proposed memory appears to contain a secret or credential.",
            "candidates": [],
        }
    candidates = search_index(paths, args.summary, args.actor, args.limit)
    normalized = re.sub(r"\s+", " ", args.summary).strip().lower()
    for item in candidates:
        source = Path(item["path"]).read_text(encoding="utf-8").lower()
        if normalized and normalized in re.sub(r"\s+", " ", source):
            return {"action": "NOOP", "reason": "Equivalent text already exists.", "candidates": [item]}
    strong = [item for item in candidates if item["score"] >= 8.0]
    if len(strong) > 1:
        return {
            "action": "MERGE_REQUIRED",
            "reason": "Multiple strong current memories overlap; reconcile them before writing.",
            "candidates": strong,
        }
    superseding = bool(re.search(r"(?:不再|改为|替代|作废|supersed|no longer|replaced by)", args.summary, re.I))
    if strong and superseding:
        return {
            "action": "MARK_OUTDATED",
            "reason": "The proposal appears to supersede an existing current fact.",
            "candidates": strong,
        }
    if candidates and candidates[0]["score"] >= 3.0:
        return {
            "action": "UPDATE",
            "reason": "A related current memory should be updated instead of duplicated.",
            "candidates": candidates[:3],
        }
    return {"action": "ADD", "reason": "No sufficiently related current memory was found.", "candidates": []}


def safe_slug(text: str) -> str:
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]
    if ascii_slug:
        return ascii_slug
    return "memory-" + sha256_bytes(text.encode("utf-8"))[:10]


def command_new(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    folder_map = {
        "preference": "用户记忆",
        "project": "项目",
        "decision": "决策",
        "workflow": "工作流",
        "fact": "项目",
        "open_loop": "未闭环",
        "case": "agent/cases",
    }
    folder = paths["vault"] / folder_map[args.memory_type]
    folder.mkdir(parents=True, exist_ok=True)
    suffix = sha256_bytes((args.title + iso_now()).encode("utf-8"))[:8]
    target = folder / f"{safe_slug(args.title)}-{suffix}.md"
    memory_id = "mem-" + dt.datetime.now().strftime("%Y%m%d") + "-" + suffix
    tags = ", ".join(args.tag)
    text = f"""---
memory_id: {memory_id}
title: {args.title}
memory_type: {args.memory_type}
status: active
agent_scope: {args.agent_scope}
project_id: {args.project_id}
verified_at: {today()}
review_after_days: {args.review_after_days}
tags: [{tags}]
---
# {args.title}

## Current fact

Replace this line with the verified durable fact.

## Evidence

- Add the verification source and date.

## Consequences

- Add what future agents should do differently.

## History

- {today()}: Created after prewrite reconciliation.
"""
    target.write_text(text, encoding="utf-8")
    return {"status": "created", "path": str(target), "memory_id": memory_id, "next": "edit, claim, closeout"}


def command_claim(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    if args.actor not in ACTORS[1:]:
        raise MemoryErrorWithCode("claim actor must be claude, codex, opencode, human, or test")
    rel = relative_vault_path(paths, Path(args.file))
    digest = sha256_file(paths["vault"] / rel)
    shash = session_hash(args.actor, args.session_id)
    conn = ensure_state(paths)
    try:
        conn.execute(
            "UPDATE claims SET state='superseded', closed_at=? WHERE path=? AND actor=? AND state='open'",
            (iso_now(), rel, args.actor),
        )
        conn.execute(
            "INSERT INTO claims(path, actor, session_hash, state, claimed_at, content_hash) VALUES (?, ?, ?, 'open', ?, ?)",
            (rel, args.actor, shash, iso_now(), digest),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "claimed", "path": rel, "actor": args.actor, "session_hash": shash[:12]}


def command_claims(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    conn = ensure_state(paths)
    try:
        rows = [dict(row) for row in conn.execute("SELECT * FROM claims ORDER BY claimed_at DESC")]
        changed = 0
        if args.expire_hours is not None:
            cutoff = utc_now() - dt.timedelta(hours=args.expire_hours)
            stale = [row for row in rows if row["state"] == "open" and dt.datetime.fromisoformat(row["claimed_at"].replace("Z", "+00:00")) < cutoff]
            if args.apply:
                for row in stale:
                    conn.execute(
                        "UPDATE claims SET state='expired', closed_at=? WHERE path=? AND actor=? AND session_hash=? AND state='open'",
                        (iso_now(), row["path"], row["actor"], row["session_hash"]),
                    )
                conn.commit()
                changed = len(stale)
            rows = stale
        for row in rows:
            row["session_hash"] = row["session_hash"][:12]
        return {"claims": rows, "changed": changed, "applied": bool(args.apply)}
    finally:
        conn.close()


def git_commit_claimed(home: Path, rel_paths: List[str], message: str) -> Optional[str]:
    if run_git(home, ["rev-parse", "--is-inside-work-tree"]).returncode != 0:
        raise MemoryErrorWithCode("--git-commit requires the Memory Home to be a Git repository")
    status = run_git(home, ["-c", "core.quotePath=false", "status", "--porcelain", "-uall"]).stdout.splitlines()
    allowed = {"vault/" + rel for rel in rel_paths}
    dirty = {line[3:] for line in status if len(line) >= 4}
    infrastructure = {".gitignore", "leslie-memory.json", "vault/AGENTS.md", "vault/INDEX.md", "vault/README.md"}
    unclaimed = sorted(
        path
        for path in dirty
        if path not in allowed
        and path not in infrastructure
        and not path.endswith("/README.md")
        and not path.startswith("state/")
        and not path.startswith("reports/")
        and not path.startswith("exports/")
    )
    if unclaimed:
        raise MemoryErrorWithCode("Git commit blocked by unclaimed dirty files: " + ", ".join(unclaimed))
    proc = run_git(home, ["add", "--", *sorted(allowed)])
    if proc.returncode != 0:
        raise MemoryErrorWithCode(proc.stderr.strip() or "git add failed")
    diff = run_git(home, ["diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return None
    proc = run_git(home, ["commit", "-m", message])
    if proc.returncode != 0:
        raise MemoryErrorWithCode(proc.stderr.strip() or "git commit failed")
    return run_git(home, ["rev-parse", "HEAD"]).stdout.strip() or None


def command_closeout(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    conn = ensure_state(paths)
    shash = session_hash(args.actor, args.session_id)
    try:
        if args.global_mode:
            rels = [path.relative_to(paths["vault"]).as_posix() for path in memory_files(paths["vault"])]
        else:
            rels = [
                row[0]
                for row in conn.execute(
                    "SELECT path FROM claims WHERE actor=? AND session_hash=? AND state='open' ORDER BY path",
                    (args.actor, shash),
                )
            ]
        if not rels:
            raise MemoryErrorWithCode("No open claims for this actor/session; claim changed files first")
        blockers: List[Dict[str, Any]] = []
        for rel in rels:
            path = paths["vault"] / rel
            if not path.is_file():
                blockers.append({"path": rel, "error": "claimed file is missing"})
                continue
            metadata, _body, errors = parse_memory(path)
            for error in errors:
                blockers.append({"path": rel, "error": error})
            for secret_type in secret_findings(path.read_text(encoding="utf-8")):
                blockers.append({"path": rel, "error": "secret detected: " + secret_type})
            if not args.global_mode:
                claimed = conn.execute(
                    "SELECT content_hash FROM claims WHERE path=? AND actor=? AND session_hash=? AND state='open'",
                    (rel, args.actor, shash),
                ).fetchone()
                if claimed and claimed["content_hash"] != sha256_file(path):
                    blockers.append({"path": rel, "error": "file changed after claim; claim it again"})
        preview = {"actor": args.actor, "session_hash": shash[:12], "files": rels, "blockers": blockers}
        if blockers:
            return {"status": "blocked", **preview}
        if args.dry_run:
            return {"status": "ready", **preview}
        index_report = rebuild_index(paths)
        audit_report = audit_home(paths)
        if audit_report["errors"]:
            return {"status": "blocked", **preview, "audit": audit_report}
        commit = None
        if args.git_commit:
            commit = git_commit_claimed(paths["home"], rels, args.message or f"memory: closeout {args.actor}")
        if not args.global_mode:
            conn.execute(
                "UPDATE claims SET state='closed', closed_at=? WHERE actor=? AND session_hash=? AND state='open'",
                (iso_now(), args.actor, shash),
            )
        conn.execute(
            "INSERT INTO closeouts(actor, session_hash, created_at, file_count, git_commit, result) VALUES (?, ?, ?, ?, ?, 'ok')",
            (args.actor, shash, iso_now(), len(rels), commit),
        )
        conn.commit()
        return {
            "status": "closed",
            **preview,
            "index": index_report,
            "audit": {"errors": audit_report["errors"], "warnings": audit_report["warnings"]},
            "git_commit": commit,
        }
    finally:
        conn.close()


def command_doctor(paths: Dict[str, Path]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append({"name": "config", "ok": paths["config"].is_file(), "path": str(paths["config"])})
    checks.append({"name": "vault", "ok": paths["vault"].is_dir(), "path": str(paths["vault"])})
    try:
        conn = ensure_state(paths)
        fts = conn.execute("SELECT sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0]
        conn.execute("SELECT count(*) FROM documents_fts").fetchone()
        conn.close()
        checks.append({"name": "sqlite-fts", "ok": bool(fts) or True, "path": str(paths["db"])})
    except sqlite3.Error as exc:
        checks.append({"name": "sqlite-fts", "ok": False, "detail": str(exc)})
    audit = audit_home(paths)
    checks.append({"name": "memory-schema-and-secrets", "ok": audit["errors"] == 0, "errors": audit["errors"]})
    checks.append({"name": "actors", "ok": True, "supported": ["claude", "codex", "opencode"]})
    checks.append({"name": "vector", "ok": True, "enabled": False})
    checks.append({"name": "automatic-hooks", "ok": True, "enabled": False})
    git = run_git(paths["home"], ["rev-parse", "--is-inside-work-tree"])
    checks.append({"name": "git", "ok": True, "enabled": git.returncode == 0})
    report = {
        "generated_at": iso_now(),
        "status": "ok" if all(item["ok"] for item in checks) else "error",
        "checks": checks,
    }
    paths["reports"].mkdir(parents=True, exist_ok=True)
    (paths["reports"] / "latest-doctor.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def command_export(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    output = Path(args.output).expanduser().resolve(strict=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    if paths["home"] == output or paths["home"] in output.parents and paths["exports"] not in output.parents:
        raise MemoryErrorWithCode("Export output must be outside Memory Home or inside its exports/ directory")
    with tarfile.open(output, "w:gz") as archive:
        for child in sorted(paths["home"].iterdir()):
            if child == paths["exports"]:
                continue
            if child == paths["state"] and not args.include_state:
                continue
            archive.add(child, arcname=Path(paths["home"].name) / child.name, recursive=True)
    return {"status": "exported", "output": str(output), "sha256": sha256_file(output), "included_state": args.include_state}


def command_migrate(args: argparse.Namespace, paths: Dict[str, Path]) -> Dict[str, Any]:
    target = Path(args.target).expanduser().resolve(strict=False)
    source = paths["home"].resolve(strict=True)
    if target == source or target in source.parents or source in target.parents:
        raise MemoryErrorWithCode("Migration target must be separate from the source")
    if target.exists():
        raise MemoryErrorWithCode(f"Migration target already exists: {target}")
    shutil.copytree(source, target)
    source_files = {
        path.relative_to(source).as_posix(): sha256_file(path)
        for path in source.rglob("*")
        if path.is_file() and "exports" not in path.relative_to(source).parts
    }
    target_files = {
        path.relative_to(target).as_posix(): sha256_file(path)
        for path in target.rglob("*")
        if path.is_file() and "exports" not in path.relative_to(target).parts
    }
    verified = source_files == target_files
    if not verified:
        raise MemoryErrorWithCode("Migration copy verification failed; source was left untouched")
    return {
        "status": "copied-and-verified",
        "source": str(source),
        "target": str(target),
        "files": len(source_files),
        "source_deleted": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Leslie durable agent memory manager (Markdown + SQLite FTS; no vectors or hooks).")
    parser.add_argument("--home", help="Absolute Memory Home path; alternatively set LESLIE_MEMORY_HOME.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize an empty Memory Home.")
    init.add_argument("--name", default="Leslie Agent Memory")
    init.add_argument("--git", action="store_true", help="Initialize an optional local Git repository.")
    sub.add_parser("paths", help="Show exact program/data ownership paths.")
    sub.add_parser("index", help="Rebuild the SQLite/FTS index from Markdown.")

    search = sub.add_parser("search", help="Search current memory candidates.")
    search.add_argument("query")
    search.add_argument("--actor", choices=ACTORS, default="shared")
    search.add_argument("--limit", type=int, default=8)

    prewrite = sub.add_parser("prewrite", help="Reconcile a proposed durable fact before writing.")
    prewrite.add_argument("summary")
    prewrite.add_argument("--actor", choices=ACTORS, default="shared")
    prewrite.add_argument("--limit", type=int, default=8)

    new = sub.add_parser("new", help="Create a schema-compliant draft after prewrite says ADD.")
    new.add_argument("--title", required=True)
    new.add_argument("--memory-type", choices=MEMORY_TYPES, required=True)
    new.add_argument("--agent-scope", choices=ACTORS[:4], default="shared")
    new.add_argument("--project-id", default="global")
    new.add_argument("--review-after-days", type=int, default=90)
    new.add_argument("--tag", action="append", default=[])

    claim = sub.add_parser("claim", help="Claim a changed memory file for an actor/session.")
    claim.add_argument("--actor", choices=ACTORS[1:], required=True)
    claim.add_argument("--session-id", required=True)
    claim.add_argument("--file", required=True)

    claims = sub.add_parser("claims", help="List claims or preview/apply stale-claim expiry.")
    claims.add_argument("--expire-hours", type=float)
    claims.add_argument("--apply", action="store_true")

    closeout = sub.add_parser("closeout", help="Validate claimed files, refresh derived state, and close the session.")
    closeout.add_argument("--actor", choices=ACTORS[1:], required=True)
    closeout.add_argument("--session-id", required=True)
    closeout.add_argument("--dry-run", action="store_true")
    closeout.add_argument("--global", dest="global_mode", action="store_true", help="Validate all memory files; intended for human maintenance.")
    closeout.add_argument("--git-commit", action="store_true", help="Opt in to a local commit of claimed files only.")
    closeout.add_argument("--message")

    sub.add_parser("audit", help="Audit schema, secrets, duplicate IDs/content, and stale facts.")
    sub.add_parser("doctor", help="Run full local health checks.")

    export = sub.add_parser("export", help="Create a portable tar.gz; derived state is excluded by default.")
    export.add_argument("--output", required=True)
    export.add_argument("--include-state", action="store_true")

    migrate = sub.add_parser("migrate", help="Copy and verify the entire Memory Home; never delete the source.")
    migrate.add_argument("--target", required=True)
    sub.add_parser("removal-plan", help="Show exact removal boundaries without deleting anything.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        home = resolve_home(args.home)
        if args.command == "init":
            payload = command_init(args, home)
        else:
            paths = require_initialized(home)
            if args.command == "paths":
                payload = command_paths(paths)
            elif args.command == "index":
                payload = rebuild_index(paths)
            elif args.command == "search":
                payload = {"query": args.query, "results": search_index(paths, args.query, args.actor, args.limit)}
            elif args.command == "prewrite":
                payload = command_prewrite(args, paths)
            elif args.command == "new":
                payload = command_new(args, paths)
            elif args.command == "claim":
                payload = command_claim(args, paths)
            elif args.command == "claims":
                payload = command_claims(args, paths)
            elif args.command == "closeout":
                payload = command_closeout(args, paths)
            elif args.command == "audit":
                payload = audit_home(paths)
            elif args.command == "doctor":
                payload = command_doctor(paths)
            elif args.command == "export":
                payload = command_export(args, paths)
            elif args.command == "migrate":
                payload = command_migrate(args, paths)
            elif args.command == "removal-plan":
                payload = {
                    **command_paths(paths),
                    "action": "Remove the program through CC Switch; archive/migrate data first; delete data only separately and explicitly.",
                    "deleted": False,
                }
            else:  # pragma: no cover
                parser.error("unsupported command")
                return 2
        emit(payload, args.json)
        if isinstance(payload, dict) and payload.get("status") == "blocked":
            return 3
        if isinstance(payload, dict) and payload.get("status") == "error":
            return 4
        return 0
    except MemoryErrorWithCode as exc:
        emit({"status": "error", "error": str(exc)}, True if args.json else False)
        return 2
    except (OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        emit({"status": "error", "error": str(exc)}, True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
