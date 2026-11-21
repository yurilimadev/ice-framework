from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .tasks import ValidationError


class LeadNotFoundError(LookupError):
    pass


class LeadStatus(str, Enum):
    NEW = "novo"
    TO_SEND = "a_enviar"
    SENT = "enviado"
    REPLIED = "respondeu"
    CONVERSATION = "conversa"
    PROPOSAL = "proposta"
    PILOT = "piloto"
    WON = "ganho"
    LOST = "perdido"
    PAUSED = "pausado"


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"
    EMAIL = "email"
    INSTAGRAM = "instagram"
    PRESENCIAL = "presencial"
    SYSTEM = "sistema"


class InteractionKind(str, Enum):
    MESSAGE = "mensagem"
    REPLY = "resposta"
    CONVERSATION = "conversa"
    PROPOSAL = "proposta"
    PILOT = "piloto"
    NOTE = "nota"
    PAUSE = "pausa"


LEAD_CHANNELS = (
    Channel.WHATSAPP,
    Channel.LINKEDIN,
    Channel.EMAIL,
    Channel.INSTAGRAM,
    Channel.PRESENCIAL,
)

XP_BY_KIND = {
    InteractionKind.MESSAGE: 10,
    InteractionKind.REPLY: 15,
    InteractionKind.CONVERSATION: 30,
    InteractionKind.PROPOSAL: 50,
    InteractionKind.PILOT: 150,
    InteractionKind.NOTE: 0,
    InteractionKind.PAUSE: 0,
}

LEVELS = (
    (700, "Capitão"),
    (300, "Timoneiro"),
    (100, "Piloto"),
    (0, "Aprendiz"),
)

TRANSITIONS = {
    LeadStatus.NEW: {LeadStatus.TO_SEND, LeadStatus.LOST},
    LeadStatus.TO_SEND: {LeadStatus.SENT, LeadStatus.LOST},
    LeadStatus.SENT: {LeadStatus.REPLIED, LeadStatus.PAUSED, LeadStatus.LOST},
    LeadStatus.REPLIED: {
        LeadStatus.CONVERSATION,
        LeadStatus.PAUSED,
        LeadStatus.LOST,
    },
    LeadStatus.CONVERSATION: {
        LeadStatus.PROPOSAL,
        LeadStatus.PAUSED,
        LeadStatus.LOST,
    },
    LeadStatus.PROPOSAL: {LeadStatus.PILOT, LeadStatus.PAUSED, LeadStatus.LOST},
    LeadStatus.PILOT: {LeadStatus.WON, LeadStatus.PAUSED, LeadStatus.LOST},
    LeadStatus.PAUSED: {LeadStatus.SENT, LeadStatus.LOST},
    LeadStatus.WON: set(),
    LeadStatus.LOST: set(),
}


def xp_for(kind: InteractionKind | str) -> int:
    try:
        return XP_BY_KIND[InteractionKind(kind)]
    except (TypeError, ValueError):
        return 0


def level_for(xp: int) -> str:
    for threshold, name in LEVELS:
        if xp >= threshold:
            return name
    return "Aprendiz"


def _required_text(value, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field} deve ser texto.", field)
    normalized = value.strip()
    if not normalized:
        raise ValidationError(f"{field} e obrigatorio.", field)
    if len(normalized) > max_length:
        raise ValidationError(
            f"{field} deve ter no maximo {max_length} caracteres.", field
        )
    return normalized


def _optional_text(value, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{field} deve ser texto.", field)
    normalized = value.strip()
    return normalized or None


def validate_lead_channel(value: Channel | str) -> Channel:
    try:
        channel = Channel(value)
    except (TypeError, ValueError):
        raise ValidationError("Canal invalido.", "channel") from None
    if channel not in LEAD_CHANNELS:
        raise ValidationError("Canal invalido.", "channel")
    return channel


def validate_interaction_channel(value: Channel | str) -> Channel:
    try:
        return Channel(value)
    except (TypeError, ValueError):
        raise ValidationError("Canal invalido.", "channel") from None


def validate_kind(value: InteractionKind | str) -> InteractionKind:
    try:
        return InteractionKind(value)
    except (TypeError, ValueError):
        raise ValidationError("Tipo de interacao invalido.", "kind") from None


def validate_status(value: LeadStatus | str) -> LeadStatus:
    try:
        return LeadStatus(value)
    except (TypeError, ValueError):
        raise ValidationError("Status invalido.", "status") from None


def parse_next_action(value: date | str | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        raise ValidationError(
            "A proxima acao deve ser uma data sem horario.", "next_action_at"
        )
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise ValidationError(
        "A proxima acao deve usar o formato AAAA-MM-DD.", "next_action_at"
    )


def _serialize_date(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _coerce_timestamp(value: datetime | None = None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc).replace(microsecond=0)


@dataclass(frozen=True)
class Lead:
    id: int
    company: str
    contact: str | None
    sector: str
    city: str
    channel: Channel
    handle: str
    observation: str
    status: LeadStatus
    next_action_at: date | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id < 1:
            raise ValidationError("O id do lead e invalido.", "id")
        object.__setattr__(self, "company", _required_text(self.company, "company", 120))
        object.__setattr__(self, "contact", _optional_text(self.contact, "contact"))
        object.__setattr__(self, "sector", _required_text(self.sector, "sector", 60))
        object.__setattr__(self, "city", _required_text(self.city, "city", 60))
        object.__setattr__(self, "channel", validate_lead_channel(self.channel))
        object.__setattr__(self, "handle", _required_text(self.handle, "handle", 200))
        object.__setattr__(
            self, "observation", _required_text(self.observation, "observation", 200)
        )
        object.__setattr__(self, "status", validate_status(self.status))
        object.__setattr__(
            self, "next_action_at", parse_next_action(self.next_action_at)
        )
        object.__setattr__(self, "created_at", _coerce_timestamp(self.created_at))
        object.__setattr__(self, "updated_at", _coerce_timestamp(self.updated_at))


@dataclass(frozen=True)
class Interaction:
    id: int
    lead_id: int
    kind: InteractionKind
    channel: Channel
    notes: str | None
    created_at: datetime

    def __post_init__(self):
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id < 1:
            raise ValidationError("O id da interacao e invalido.", "id")
        if (
            not isinstance(self.lead_id, int)
            or isinstance(self.lead_id, bool)
            or self.lead_id < 1
        ):
            raise ValidationError("O lead da interacao e invalido.", "lead_id")
        object.__setattr__(self, "kind", validate_kind(self.kind))
        object.__setattr__(self, "channel", validate_interaction_channel(self.channel))
        object.__setattr__(self, "notes", _optional_text(self.notes, "notes"))
        object.__setattr__(self, "created_at", _coerce_timestamp(self.created_at))


class PeixeRepository:
    def __init__(self, connection: sqlite3.Connection, timezone_name="America/Sao_Paulo"):
        self.connection = connection
        self.timezone_name = timezone_name

    def create_lead(
        self,
        company: str,
        sector: str,
        city: str,
        channel: Channel | str,
        handle: str,
        observation: str,
        contact: str | None = None,
        next_action_at: date | str | None = None,
    ) -> Lead:
        company = _required_text(company, "company", 120)
        sector = _required_text(sector, "sector", 60)
        city = _required_text(city, "city", 60)
        channel = validate_lead_channel(channel)
        handle = _required_text(handle, "handle", 200)
        observation = _required_text(observation, "observation", 200)
        contact = _optional_text(contact, "contact")
        next_action = parse_next_action(next_action_at)
        duplicate = self.connection.execute(
            "SELECT id FROM leads WHERE channel = ? AND handle = ?",
            (channel.value, handle),
        ).fetchone()
        if duplicate is not None:
            raise ValidationError("Ja existe um lead com este canal e contato.", "handle")

        now = _coerce_timestamp().isoformat()
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO leads
                    (company, contact, sector, city, channel, handle, observation,
                     status, next_action_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company,
                    contact,
                    sector,
                    city,
                    channel.value,
                    handle,
                    observation,
                    LeadStatus.NEW.value,
                    _serialize_date(next_action),
                    now,
                    now,
                ),
            )
        return self.get_lead(cursor.lastrowid)

    def update_lead(
        self,
        lead_id: int,
        company: str,
        sector: str,
        city: str,
        channel: Channel | str,
        handle: str,
        observation: str,
        contact: str | None = None,
    ) -> Lead:
        self.get_lead(lead_id)
        company = _required_text(company, "company", 120)
        sector = _required_text(sector, "sector", 60)
        city = _required_text(city, "city", 60)
        channel = validate_lead_channel(channel)
        handle = _required_text(handle, "handle", 200)
        observation = _required_text(observation, "observation", 200)
        contact = _optional_text(contact, "contact")
        duplicate = self.connection.execute(
            "SELECT id FROM leads WHERE channel = ? AND handle = ? AND id != ?",
            (channel.value, handle, lead_id),
        ).fetchone()
        if duplicate is not None:
            raise ValidationError("Ja existe um lead com este canal e contato.", "handle")

        now = _coerce_timestamp().isoformat()
        with self.connection:
            self.connection.execute(
                """
                UPDATE leads
                SET company = ?, contact = ?, sector = ?, city = ?, channel = ?,
                    handle = ?, observation = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    company,
                    contact,
                    sector,
                    city,
                    channel.value,
                    handle,
                    observation,
                    now,
                    lead_id,
                ),
            )
        return self.get_lead(lead_id)

    def get_lead(self, lead_id: int) -> Lead:
        row = self.connection.execute(
            "SELECT * FROM leads WHERE id = ?", (lead_id,)
        ).fetchone()
        if row is None:
            raise LeadNotFoundError(f"Lead nao encontrado: {lead_id}")
        return self._lead_from_row(row)

    def list_leads(self, status: LeadStatus | str | None = None) -> list[Lead]:
        status_filter = None if status is None else validate_status(status)
        rows = self.connection.execute(
            "SELECT * FROM leads ORDER BY created_at DESC, id DESC"
        ).fetchall()
        leads = [self._lead_from_row(row) for row in rows]
        if status_filter is None:
            return leads
        return [lead for lead in leads if lead.status is status_filter]

    def update_status(self, lead_id: int, status: LeadStatus | str) -> Lead:
        current = self.get_lead(lead_id)
        target = validate_status(status)
        if target is current.status:
            return current
        if target not in TRANSITIONS[current.status]:
            raise ValidationError(
                f"Transicao de {current.status.value} para {target.value} nao permitida.",
                "status",
            )
        now = _coerce_timestamp().isoformat()
        with self.connection:
            self.connection.execute(
                "UPDATE leads SET status = ?, updated_at = ? WHERE id = ?",
                (target.value, now, lead_id),
            )
        return self.get_lead(lead_id)

    def set_next_action(self, lead_id: int, value: date | str | None) -> Lead:
        next_action = parse_next_action(value)
        self.get_lead(lead_id)
        now = _coerce_timestamp().isoformat()
        with self.connection:
            self.connection.execute(
                "UPDATE leads SET next_action_at = ?, updated_at = ? WHERE id = ?",
                (_serialize_date(next_action), now, lead_id),
            )
        return self.get_lead(lead_id)

    def log_interaction(
        self,
        lead_id: int,
        kind: InteractionKind | str,
        channel: Channel | str | None = None,
        notes: str | None = None,
        created_at: datetime | None = None,
    ) -> Interaction:
        lead = self.get_lead(lead_id)
        kind = validate_kind(kind)
        channel = validate_interaction_channel(channel or lead.channel.value)
        notes = _optional_text(notes, "notes")
        timestamp = _coerce_timestamp(created_at)
        if kind is InteractionKind.MESSAGE and lead.status in (
            LeadStatus.WON,
            LeadStatus.LOST,
        ):
            raise ValidationError(
                "Nao e possivel enviar mensagem para lead encerrado.", "status"
            )

        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO interactions (lead_id, kind, channel, notes, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (lead_id, kind.value, channel.value, notes, timestamp.isoformat()),
            )
            if kind is InteractionKind.MESSAGE:
                next_action = (
                    timestamp.astimezone(ZoneInfo(self.timezone_name)).date()
                    + timedelta(days=3)
                )
                self.connection.execute(
                    """
                    UPDATE leads
                    SET status = ?, next_action_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        LeadStatus.SENT.value,
                        _serialize_date(next_action),
                        timestamp.isoformat(),
                        lead_id,
                    ),
                )
        return self.get_interaction(cursor.lastrowid)

    def get_interaction(self, interaction_id: int) -> Interaction:
        row = self.connection.execute(
            "SELECT * FROM interactions WHERE id = ?", (interaction_id,)
        ).fetchone()
        if row is None:
            raise LookupError(f"Interacao nao encontrada: {interaction_id}")
        return self._interaction_from_row(row)

    def list_interactions(self, lead_id: int | None = None) -> list[Interaction]:
        if lead_id is None:
            rows = self.connection.execute(
                "SELECT * FROM interactions ORDER BY created_at DESC, id DESC"
            ).fetchall()
        else:
            self.get_lead(lead_id)
            rows = self.connection.execute(
                """
                SELECT * FROM interactions
                WHERE lead_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (lead_id,),
            ).fetchall()
        return [self._interaction_from_row(row) for row in rows]

    def daily_mission(self) -> Lead | None:
        today = self._today()
        candidates = [
            lead
            for lead in self.list_leads()
            if lead.status in (LeadStatus.TO_SEND, LeadStatus.SENT)
            and (lead.next_action_at is None or lead.next_action_at <= today)
        ]
        candidates.sort(
            key=lambda lead: (
                lead.next_action_at is None,
                lead.next_action_at or date.min,
                lead.created_at,
                lead.id,
            )
        )
        return candidates[0] if candidates else None

    def followups_due(self) -> list[Lead]:
        today = self._today()
        due = [
            lead
            for lead in self.list_leads(status=LeadStatus.SENT)
            if lead.next_action_at is not None and lead.next_action_at < today
        ]
        due.sort(key=lambda lead: (lead.next_action_at, lead.created_at, lead.id))
        return due

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        row = self.connection.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return default if row is None else row["value"]

    def set_setting(self, key: str, value: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("A chave da configuracao e invalida.", "key")
        if not isinstance(value, str):
            raise ValidationError("O valor da configuracao deve ser texto.", "value")
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key.strip(), value),
            )

    def pipeline_counts(self) -> dict[str, int]:
        counts = {status.value: 0 for status in LeadStatus}
        rows = self.connection.execute(
            "SELECT status, COUNT(*) AS total FROM leads GROUP BY status"
        ).fetchall()
        for row in rows:
            counts[row["status"]] = row["total"]
        return counts

    def xp_total(self) -> int:
        rows = self.connection.execute("SELECT kind FROM interactions").fetchall()
        return sum(xp_for(row["kind"]) for row in rows)

    def level(self) -> str:
        return level_for(self.xp_total())

    def streak(self) -> int:
        message_days = set()
        for interaction in self.list_interactions():
            if interaction.kind is InteractionKind.MESSAGE:
                message_days.add(self._local_date(interaction.created_at))
        if not message_days:
            return 0
        today = self._today()
        if today in message_days:
            cursor = today
        elif today - timedelta(days=1) in message_days:
            cursor = today - timedelta(days=1)
        else:
            return 0
        count = 0
        while cursor in message_days:
            count += 1
            cursor -= timedelta(days=1)
        return count

    def weekly_progress(self) -> dict[str, int]:
        today = self._today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)
        progress = {"messages": 0, "replies": 0, "conversations": 0}
        for interaction in self.list_interactions():
            local_day = self._local_date(interaction.created_at)
            if not start <= local_day < end:
                continue
            if interaction.kind is InteractionKind.MESSAGE:
                progress["messages"] += 1
            elif interaction.kind is InteractionKind.REPLY:
                progress["replies"] += 1
            elif interaction.kind is InteractionKind.CONVERSATION:
                progress["conversations"] += 1
        return progress

    def weekly_kind_counts(self) -> dict[str, int]:
        today = self._today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)
        counts = {kind.value: 0 for kind in InteractionKind}
        for interaction in self.list_interactions():
            local_day = self._local_date(interaction.created_at)
            if start <= local_day < end:
                counts[interaction.kind.value] += 1
        return counts

    def badges(self) -> tuple[str, ...]:
        kinds = {interaction.kind for interaction in self.list_interactions()}
        earned = []
        if InteractionKind.MESSAGE in kinds:
            earned.append("primeira_mensagem")
        if InteractionKind.REPLY in kinds:
            earned.append("primeira_resposta")
        if InteractionKind.CONVERSATION in kinds:
            earned.append("primeira_conversa")
        if InteractionKind.PILOT in kinds:
            earned.append("primeiro_piloto")
        if self._has_four_week_streak():
            earned.append("streak_4_semanas")
        return tuple(earned)

    def _has_four_week_streak(self) -> bool:
        weeks = set()
        for interaction in self.list_interactions():
            if interaction.kind is InteractionKind.MESSAGE:
                local_day = self._local_date(interaction.created_at)
                weeks.add(local_day - timedelta(days=local_day.weekday()))
        for week in weeks:
            if all(
                week + timedelta(days=7 * offset) in weeks for offset in range(4)
            ):
                return True
        return False

    def _today(self) -> date:
        try:
            return datetime.now(ZoneInfo(self.timezone_name)).date()
        except (TypeError, ValueError, ZoneInfoNotFoundError):
            raise ValidationError("Fuso horario invalido.", "timezone") from None

    def _local_date(self, timestamp: datetime) -> date:
        return timestamp.astimezone(ZoneInfo(self.timezone_name)).date()

    def _lead_from_row(self, row) -> Lead:
        return Lead(
            id=row["id"],
            company=row["company"],
            contact=row["contact"],
            sector=row["sector"],
            city=row["city"],
            channel=Channel(row["channel"]),
            handle=row["handle"],
            observation=row["observation"],
            status=LeadStatus(row["status"]),
            next_action_at=_parse_stored_date(row["next_action_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _interaction_from_row(row) -> Interaction:
        return Interaction(
            id=row["id"],
            lead_id=row["lead_id"],
            kind=InteractionKind(row["kind"]),
            channel=Channel(row["channel"]),
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


def _parse_stored_date(value: str | None) -> date | None:
    return None if value is None else date.fromisoformat(value)
