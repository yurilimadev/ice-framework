from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ValidationError(ValueError):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field
        self.message = message


class TaskNotFoundError(LookupError):
    pass


class TagNotFoundError(LookupError):
    pass


def validate_tag_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValidationError("A tag deve ser texto.", "tags")
    normalized = name.strip()
    if not normalized:
        raise ValidationError("A tag nao pode ser vazia.", "tags")
    if len(normalized) > 30:
        raise ValidationError("A tag deve ter no maximo 30 caracteres.", "tags")
    return normalized


class TaskStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"


def validate_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValidationError("O titulo deve ser texto.", "title")

    normalized = title.strip()
    if not normalized:
        raise ValidationError("O titulo e obrigatorio.", "title")
    if len(normalized) > 120:
        raise ValidationError("O titulo deve ter no maximo 120 caracteres.", "title")
    return normalized


def validate_ice_value(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10:
        raise ValidationError(f"{field} deve ser um inteiro entre 1 e 10.", field)
    return value


def parse_deadline(value: date | str | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        raise ValidationError("O deadline deve ser uma data sem horario.", "deadline")
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise ValidationError("O deadline deve usar o formato AAAA-MM-DD.", "deadline")


def normalize_tags(tags: Iterable[str] | str | None) -> tuple[str, ...]:
    if tags is None:
        return ()
    if isinstance(tags, str):
        tags = (tags,)

    try:
        iterator = iter(tags)
    except TypeError:
        raise ValidationError(
            "As tags devem ser texto ou um iteravel de textos.", "tags"
        ) from None

    normalized: list[str] = []
    seen: set[str] = set()
    for tag in iterator:
        if not isinstance(tag, str):
            raise ValidationError("Cada tag deve ser texto.", "tags")
        clean_tag = tag.strip()
        if not clean_tag:
            raise ValidationError("As tags nao podem ser vazias.", "tags")
        if len(clean_tag) > 30:
            raise ValidationError("Cada tag deve ter no maximo 30 caracteres.", "tags")

        key = clean_tag.casefold()
        if key not in seen:
            normalized.append(clean_tag)
            seen.add(key)
    return tuple(normalized)


def today_in_timezone(timezone_name: str) -> date:
    try:
        return datetime.now(ZoneInfo(timezone_name)).date()
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        raise ValidationError("Fuso horario invalido.", "timezone") from None


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    impact: int
    confidence: int
    ease: int
    deadline: date | None
    status: TaskStatus
    created_at: datetime
    tags: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id < 1:
            raise ValidationError("O id da tarefa e invalido.", "id")
        object.__setattr__(self, "title", validate_title(self.title))
        object.__setattr__(self, "impact", validate_ice_value(self.impact, "impact"))
        object.__setattr__(self, "confidence", validate_ice_value(self.confidence, "confidence"))
        object.__setattr__(self, "ease", validate_ice_value(self.ease, "ease"))
        object.__setattr__(self, "deadline", parse_deadline(self.deadline))
        object.__setattr__(self, "status", TaskStatus(self.status))
        object.__setattr__(self, "tags", normalize_tags(self.tags))

    @property
    def score(self) -> int:
        return self.impact * self.confidence * self.ease

    def is_overdue(self, today: date) -> bool:
        return (
            self.status is TaskStatus.OPEN
            and self.deadline is not None
            and self.deadline < today
        )


_UNSET = object()


class TaskRepository:
    def __init__(self, connection, timezone_name: str = "America/Sao_Paulo"):
        self.connection = connection
        self.timezone_name = timezone_name

    def create(
        self,
        title: str,
        impact: int,
        confidence: int,
        ease: int,
        deadline: date | str | None = None,
        tags: Iterable[str] | str | None = None,
    ) -> Task:
        fields = self._validated_fields(title, impact, confidence, ease, deadline, tags)
        created_at = datetime.now(timezone.utc).replace(microsecond=0)
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO tasks
                    (title, impact, confidence, ease, deadline, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fields["title"],
                    fields["impact"],
                    fields["confidence"],
                    fields["ease"],
                    _serialize_deadline(fields["deadline"]),
                    TaskStatus.OPEN.value,
                    created_at.isoformat(),
                ),
            )
            task_id = cursor.lastrowid
            self._replace_tags(task_id, fields["tags"])
        return self.get(task_id)

    def get(self, task_id: int) -> Task:
        row = self.connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise TaskNotFoundError(f"Tarefa nao encontrada: {task_id}")
        return self._task_from_row(row)

    def list(
        self,
        status: TaskStatus | str | None = TaskStatus.OPEN,
        overdue: bool | None = None,
        tags: Iterable[str] | str | None = None,
        order_by: str = "score",
    ) -> list[Task]:
        status_filter = None if status is None else TaskStatus(status)
        tag_filter = {tag.casefold() for tag in normalize_tags(tags)}
        today = today_in_timezone(self.timezone_name)
        tasks = [
            task
            for task in self._all()
            if (status_filter is None or task.status is status_filter)
            and (overdue is None or task.is_overdue(today) is overdue)
            and tag_filter.issubset({tag.casefold() for tag in task.tags})
        ]

        if order_by == "score":
            return sorted(tasks, key=self._score_sort_key)
        if order_by == "deadline":
            return sorted(tasks, key=self._deadline_sort_key)
        if order_by == "created_at":
            return sorted(tasks, key=self._created_at_sort_key)
        raise ValidationError("Ordenacao invalida.", "order_by")

    def update(
        self,
        task_id: int,
        *,
        title: str | object = _UNSET,
        impact: int | object = _UNSET,
        confidence: int | object = _UNSET,
        ease: int | object = _UNSET,
        deadline: date | str | None | object = _UNSET,
        tags: Iterable[str] | str | None | object = _UNSET,
    ) -> Task:
        current = self.get(task_id)
        values = {
            "title": current.title if title is _UNSET else title,
            "impact": current.impact if impact is _UNSET else impact,
            "confidence": current.confidence if confidence is _UNSET else confidence,
            "ease": current.ease if ease is _UNSET else ease,
            "deadline": current.deadline if deadline is _UNSET else deadline,
            "tags": current.tags if tags is _UNSET else tags,
        }
        fields = self._validated_fields(**values)

        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET title = ?, impact = ?, confidence = ?, ease = ?, deadline = ?
                WHERE id = ?
                """,
                (
                    fields["title"],
                    fields["impact"],
                    fields["confidence"],
                    fields["ease"],
                    _serialize_deadline(fields["deadline"]),
                    task_id,
                ),
            )
            if tags is not _UNSET:
                self._replace_tags(task_id, fields["tags"])
        return self.get(task_id)

    def set_status(self, task_id: int, status: TaskStatus | str) -> Task:
        try:
            normalized_status = TaskStatus(status)
        except (TypeError, ValueError):
            raise ValidationError("Status invalido.", "status") from None
        self.get(task_id)
        with self.connection:
            self.connection.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (normalized_status.value, task_id),
            )
        return self.get(task_id)

    def complete(self, task_id: int) -> Task:
        return self.set_status(task_id, TaskStatus.COMPLETED)

    def reopen(self, task_id: int) -> Task:
        return self.set_status(task_id, TaskStatus.OPEN)

    def delete(self, task_id: int) -> None:
        self.get(task_id)
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def available_tags(self) -> tuple[str, ...]:
        rows = self.connection.execute(
            "SELECT id, name FROM tags ORDER BY name COLLATE NOCASE, id"
        ).fetchall()
        tags: list[str] = []
        seen: set[str] = set()
        for row in rows:
            key = row["name"].casefold()
            if key not in seen:
                tags.append(row["name"])
                seen.add(key)
        return tuple(tags)

    def list_tags_with_usage(self) -> list[dict]:
        rows = self.connection.execute(
            """
            SELECT tags.id, tags.name, COUNT(task_tags.task_id) AS task_count
            FROM tags
            LEFT JOIN task_tags ON task_tags.tag_id = tags.id
            GROUP BY tags.id, tags.name
            ORDER BY tags.name COLLATE NOCASE, tags.id
            """
        ).fetchall()
        return [{"id": row["id"], "name": row["name"], "task_count": row["task_count"]} for row in rows]

    def rename_tag(self, tag_id: int, new_name: str) -> str:
        normalized = validate_tag_name(new_name)
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE tags SET name = ? WHERE id = ?", (normalized, tag_id)
            )
            if cursor.rowcount == 0:
                raise TagNotFoundError(f"Tag nao encontrada: {tag_id}")
        return normalized

    def delete_tag(self, tag_id: int) -> None:
        with self.connection:
            # Remove primeiro os vínculos para não bloquear tags em uso.
            self.connection.execute(
                """
                DELETE FROM task_tags
                WHERE tag_id = ? AND tag_id IS NOT NULL
                  AND tag_id IN (SELECT id FROM tags WHERE id = ?)
                """,
                (tag_id, tag_id),
            )
            cursor = self.connection.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            if cursor.rowcount == 0:
                raise TagNotFoundError(f"Tag nao encontrada: {tag_id}")

    def merge_tags(self, source_id: int, target_id: int) -> str:
        if source_id == target_id:
            raise ValidationError("Origem e destino devem ser diferentes.", "tags")
        with self.connection:
            target = self.connection.execute(
                "SELECT name FROM tags WHERE id = ?", (target_id,)
            ).fetchone()
            if target is None:
                raise TagNotFoundError(f"Tag destino nao encontrada: {target_id}")
            source = self.connection.execute(
                "SELECT id FROM tags WHERE id = ?", (source_id,)
            ).fetchone()
            if source is None:
                raise TagNotFoundError(f"Tag origem nao encontrada: {source_id}")
            self.connection.execute(
                "UPDATE task_tags SET tag_id = ? WHERE tag_id = ?", (target_id, source_id)
            )
            self.connection.execute("DELETE FROM tags WHERE id = ?", (source_id,))
        return target["name"]

    def _all(self) -> list[Task]:
        rows = self.connection.execute("SELECT * FROM tasks").fetchall()
        return [self._task_from_row(row) for row in rows]

    def _task_from_row(self, row) -> Task:
        tag_rows = self.connection.execute(
            """
            SELECT tags.name
            FROM tags
            INNER JOIN task_tags ON task_tags.tag_id = tags.id
            WHERE task_tags.task_id = ?
            ORDER BY tags.name COLLATE NOCASE
            """,
            (row["id"],),
        ).fetchall()
        return Task(
            id=row["id"],
            title=row["title"],
            impact=row["impact"],
            confidence=row["confidence"],
            ease=row["ease"],
            deadline=_parse_stored_deadline(row["deadline"]),
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            tags=tuple(tag_row["name"] for tag_row in tag_rows),
        )

    def _replace_tags(self, task_id: int, tags: Iterable[str]) -> None:
        self.connection.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
        for tag in tags:
            tag_id = self._find_tag_id(tag)
            if tag_id is None:
                cursor = self.connection.execute(
                    "INSERT INTO tags (name) VALUES (?)", (tag,)
                )
                tag_id = cursor.lastrowid
            self.connection.execute(
                "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                (task_id, tag_id),
            )

    def _find_tag_id(self, tag: str) -> int | None:
        tag_key = tag.casefold()
        rows = self.connection.execute(
            "SELECT id, name FROM tags ORDER BY id"
        ).fetchall()
        for row in rows:
            if row["name"].casefold() == tag_key:
                return row["id"]
        return None

    @staticmethod
    def _validated_fields(title, impact, confidence, ease, deadline=None, tags=None):
        return {
            "title": validate_title(title),
            "impact": validate_ice_value(impact, "impact"),
            "confidence": validate_ice_value(confidence, "confidence"),
            "ease": validate_ice_value(ease, "ease"),
            "deadline": parse_deadline(deadline),
            "tags": normalize_tags(tags),
        }

    @staticmethod
    def _score_sort_key(task: Task):
        return (
            -task.score,
            task.deadline is None,
            task.deadline or date.max,
            task.created_at,
            task.id,
        )

    @staticmethod
    def _deadline_sort_key(task: Task):
        return (
            task.deadline is None,
            task.deadline or date.max,
            -task.score,
            task.created_at,
            task.id,
        )

    @staticmethod
    def _created_at_sort_key(task: Task):
        return (-task.created_at.timestamp(), -task.score, task.id)


def _serialize_deadline(deadline: date | None) -> str | None:
    return deadline.isoformat() if deadline is not None else None


def _parse_stored_deadline(value: str | None) -> date | None:
    return None if value is None else date.fromisoformat(value)
