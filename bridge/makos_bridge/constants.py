"""Static constants for MAKOS bridge."""

from __future__ import annotations

REQUIRED_DIRECTORIES = [
    "00-system",
    "01-inbox",
    "02-procedures",
    "03-skills",
    "03-skills/registry",
    "03-skills/enabled",
    "03-skills/disabled",
    "04-knowledge",
    "05-memory",
    "06-history/actions",
    "06-history/decisions",
    "06-history/changes",
    "07-workspaces/scratchpads",
    "07-workspaces/active-tasks",
    "08-indexes",
    "09-templates",
    "10-human-views",
]

DOCUMENT_TYPES = {
    "procedure",
    "skill",
    "knowledge_note",
    "memory_entry",
    "decision_log",
    "scratchpad",
    "index",
    "review_item",
    "history_entry",
}

ALLOWED_STATUSES = {
    "draft",
    "active",
    "approved",
    "deprecated",
    "archived",
    "needs_review",
    "in_progress",
    "proposed",
    "done",
}

ALLOWED_VISIBILITY = {"shared", "restricted", "private"}

ALLOWED_SOURCE_TYPES = {
    "human",
    "agent",
    "derived",
    "external",
    "generated",
    "procedure-run",
    "system",
}

REVIEW_RELEVANT_TYPES = {"procedure", "skill", "knowledge_note", "review_item"}
REVIEW_QUEUE_STATUSES = {"draft", "needs_review", "proposed"}

SKILL_REGISTRY_DIR = "03-skills/registry"
SKILL_ENABLED_DIR = "03-skills/enabled"
SKILL_DISABLED_DIR = "03-skills/disabled"
CORE_AGENT_SKILL_NAME = "makos-context-os"
