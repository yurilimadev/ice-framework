from __future__ import annotations

import re
import smtplib
from datetime import date, datetime, timedelta
from urllib.parse import quote
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from .db import get_db
from .peixe import (
    Channel,
    InteractionKind,
    LeadNotFoundError,
    LeadStatus,
    PeixeRepository,
    ValidationError,
)
from .tasks import TaskRepository


peixe_bp = Blueprint("peixe", __name__)


@peixe_bp.app_context_processor
def _messages_context():
    return {"messages": get_flashed_messages(with_categories=True)}


def _repository() -> PeixeRepository:
    return PeixeRepository(get_db(), current_app.config["APP_TIMEZONE"])


def _digest_ready() -> bool:
    config = current_app.config
    smtp_ready = all(
        config.get(key)
        for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM")
    )
    return smtp_ready and bool(config.get("PEIXE_TO") or config.get("DIGEST_TO"))


def _task_repository() -> TaskRepository:
    return TaskRepository(get_db(), current_app.config["APP_TIMEZONE"])


def _today() -> date:
    return datetime.now(ZoneInfo(current_app.config["APP_TIMEZONE"])).date()


def _back_url(default_endpoint, **values):
    target = request.referrer
    if target and target.startswith(request.host_url):
        return target
    return url_for(default_endpoint, **values)


def _pain(repository, lead):
    pain = repository.get_setting("current_pain")
    if pain:
        return pain
    ocean = (repository.get_setting("current_ocean") or "").casefold()
    if ocean == "odontologia":
        return "falta de paciente e agenda"
    return f"os desafios de {lead.sector}"


def build_message(lead):
    contact = lead.contact or lead.company
    observation = lead.observation.rstrip(". ")
    sector = lead.sector.strip()
    if sector.casefold() == "odontologia":
        sector_phrase = "clínicas odontológicas"
    else:
        sector_phrase = f"clínicas de {sector.lower()}"
    return (
        f"Oi, {contact}, tudo bem? Vi que {observation}.\n"
        f"Estou pesquisando como {sector_phrase} de {lead.city} atraem "
        "pacientes novos. Posso te fazer 2 perguntas rápidas? Não é venda."
    )


def _whatsapp_digits(handle: str) -> str:
    digits = re.sub(r"\D", "", handle)
    if digits.startswith("550"):
        digits = f"55{digits[3:]}"
    elif digits.startswith("0"):
        digits = digits[1:]
    if digits and not digits.startswith("55"):
        digits = f"55{digits}"
    return digits


def _channel_link(lead, message):
    text = quote(message)
    if lead.channel is Channel.WHATSAPP:
        digits = _whatsapp_digits(lead.handle)
        if not digits:
            return None
        return {
            "url": f"https://wa.me/{digits}?text={text}",
            "label": "Abrir WhatsApp",
        }
    if lead.channel is Channel.EMAIL:
        if "@" not in lead.handle:
            return None
        subject = quote(f"Conversa rápida sobre {lead.sector}")
        return {
            "url": f"mailto:{lead.handle}?subject={subject}&body={text}",
            "label": "Enviar email",
        }
    if lead.channel is Channel.LINKEDIN:
        url = (
            lead.handle
            if lead.handle.startswith("http")
            else f"https://www.linkedin.com/in/{quote(lead.handle)}"
        )
        return {"url": url, "label": "Abrir LinkedIn"}
    if lead.channel is Channel.INSTAGRAM:
        url = (
            lead.handle
            if lead.handle.startswith("http")
            else f"https://www.instagram.com/{quote(lead.handle)}"
        )
        return {"url": url, "label": "Abrir Instagram"}
    return None


def _lead_contact(lead, repository):
    pain = _pain(repository, lead)
    message = build_message(lead)
    return {
        "pain": pain,
        "message": message,
        "link": _channel_link(lead, message),
    }


def _quest(repository, progress=None):
    progress = progress or repository.weekly_progress()
    targets = {
        "messages": int(repository.get_setting("weekly_messages") or 5),
        "replies": int(repository.get_setting("weekly_replies") or 2),
        "conversations": int(repository.get_setting("weekly_conversations") or 1),
    }
    items = []
    for key, label in (
        ("messages", "Mensagens"),
        ("replies", "Respostas"),
        ("conversations", "Conversas"),
    ):
        current = progress[key]
        target = max(targets[key], 1)
        items.append(
            {
                "key": key,
                "label": label,
                "current": current,
                "target": target,
                "percent": min(100, round(current / target * 100)),
                "done": current >= target,
            }
        )
    overall = round(sum(item["percent"] for item in items) / len(items))
    return {
        "items": items,
        "percent": overall,
        "done": all(item["done"] for item in items),
        "doce": progress["messages"] >= targets["messages"],
    }


def _pipeline_leads(repository, status_value):
    leads = repository.list_leads()
    counts = repository.pipeline_counts()
    if status_value:
        leads = [lead for lead in leads if lead.status.value == status_value]
    return leads, counts


@peixe_bp.get("/peixe")
def dashboard():
    repository = _repository()
    mission = repository.daily_mission()
    contact = _lead_contact(mission, repository) if mission else None
    progress = repository.weekly_progress()
    return render_template(
        "peixe/dashboard.html",
        mission=mission,
        contact=contact,
        xp=repository.xp_total(),
        level=repository.level(),
        streak=repository.streak(),
        badges=repository.badges(),
        quest=_quest(repository, progress),
        progress=progress,
        followups=repository.followups_due(),
        top_tasks=_task_repository().list(status="open")[:3],
        counts=repository.pipeline_counts(),
        ocean=repository.get_setting("current_ocean", "odontologia"),
        city=repository.get_setting("current_city", "Natal"),
        peixe_digest_ready=_digest_ready(),
    )


@peixe_bp.get("/peixe/leads")
def leads():
    repository = _repository()
    status_value = request.args.get("status", "")
    if status_value and status_value not in {status.value for status in LeadStatus}:
        flash("Status de filtro invalido.", "error")
        return redirect(url_for("peixe.leads"), code=303)
    pipeline, counts = _pipeline_leads(repository, status_value)
    return render_template(
        "peixe/leads.html",
        leads=pipeline,
        counts=counts,
        status=status_value,
        statuses=list(LeadStatus),
    )


@peixe_bp.get("/peixe/leads/new")
def new_lead():
    return render_template(
        "peixe/lead_form.html",
        lead=None,
        errors={},
        form_values=_lead_form_values(),
    )


def _lead_form_values(lead=None):
    if lead is None:
        return {
            "company": "",
            "contact": "",
            "sector": "odontologia",
            "city": "Natal",
            "channel": "whatsapp",
            "handle": "",
            "observation": "",
        }
    return {
        "company": lead.company,
        "contact": lead.contact or "",
        "sector": lead.sector,
        "city": lead.city,
        "channel": lead.channel.value,
        "handle": lead.handle,
        "observation": lead.observation,
    }


@peixe_bp.post("/peixe/leads")
def create_lead():
    values = {
        "company": request.form.get("company", ""),
        "contact": request.form.get("contact", ""),
        "sector": request.form.get("sector", ""),
        "city": request.form.get("city", ""),
        "channel": request.form.get("channel", ""),
        "handle": request.form.get("handle", ""),
        "observation": request.form.get("observation", ""),
    }
    try:
        lead = _repository().create_lead(
            company=values["company"],
            contact=values["contact"] or None,
            sector=values["sector"],
            city=values["city"],
            channel=values["channel"],
            handle=values["handle"],
            observation=values["observation"],
        )
    except ValidationError as error:
        return (
            render_template(
                "peixe/lead_form.html",
                lead=None,
                errors={error.field or "form": str(error)},
                form_values=values,
            ),
            400,
        )
    flash("Lead criado.", "success")
    return redirect(url_for("peixe.lead_detail", lead_id=lead.id), code=303)


@peixe_bp.get("/peixe/leads/<int:lead_id>/editar")
def edit_lead(lead_id):
    repository = _repository()
    try:
        lead = repository.get_lead(lead_id)
    except LeadNotFoundError:
        abort(404)
    return render_template(
        "peixe/lead_form.html",
        lead=lead,
        errors={},
        form_values=_lead_form_values(lead),
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/editar")
def update_lead(lead_id):
    repository = _repository()
    try:
        lead = repository.get_lead(lead_id)
    except LeadNotFoundError:
        abort(404)
    values = {
        "company": request.form.get("company", ""),
        "contact": request.form.get("contact", ""),
        "sector": request.form.get("sector", ""),
        "city": request.form.get("city", ""),
        "channel": request.form.get("channel", ""),
        "handle": request.form.get("handle", ""),
        "observation": request.form.get("observation", ""),
    }
    try:
        lead = repository.update_lead(
            lead_id,
            company=values["company"],
            contact=values["contact"] or None,
            sector=values["sector"],
            city=values["city"],
            channel=values["channel"],
            handle=values["handle"],
            observation=values["observation"],
        )
    except LeadNotFoundError:
        abort(404)
    except ValidationError as error:
        return (
            render_template(
                "peixe/lead_form.html",
                lead=lead,
                errors={error.field or "form": str(error)},
                form_values=values,
            ),
            400,
        )
    flash("Lead atualizado.", "success")
    return redirect(url_for("peixe.lead_detail", lead_id=lead.id), code=303)


@peixe_bp.get("/peixe/leads/<int:lead_id>")
def lead_detail(lead_id):
    repository = _repository()
    try:
        lead = repository.get_lead(lead_id)
    except LeadNotFoundError:
        abort(404)
    return render_template(
        "peixe/lead_detail.html",
        lead=lead,
        contact=_lead_contact(lead, repository),
        interactions=repository.list_interactions(lead_id),
    )


def _change_status(lead_id, status, kind, message):
    repository = _repository()
    try:
        lead = repository.get_lead(lead_id)
        repository.update_status(lead.id, status)
        repository.log_interaction(lead.id, kind)
    except LeadNotFoundError:
        abort(404)
    except ValidationError as error:
        flash(str(error), "error")
        return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)
    flash(message, "success")
    return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)


@peixe_bp.post("/peixe/leads/<int:lead_id>/send")
def send_message(lead_id):
    repository = _repository()
    try:
        lead = repository.get_lead(lead_id)
        repository.log_interaction(lead.id, InteractionKind.MESSAGE)
    except LeadNotFoundError:
        abort(404)
    except ValidationError as error:
        flash(str(error), "error")
        return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)
    flash("Mensagem registrada. Follow-up em 3 dias.", "success")
    return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)


@peixe_bp.post("/peixe/leads/<int:lead_id>/reply")
def register_reply(lead_id):
    return _change_status(
        lead_id, LeadStatus.REPLIED, InteractionKind.REPLY, "Resposta registrada."
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/conversation")
def register_conversation(lead_id):
    return _change_status(
        lead_id,
        LeadStatus.CONVERSATION,
        InteractionKind.CONVERSATION,
        "Conversa registrada.",
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/proposal")
def register_proposal(lead_id):
    return _change_status(
        lead_id, LeadStatus.PROPOSAL, InteractionKind.PROPOSAL, "Proposta registrada."
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/pilot")
def register_pilot(lead_id):
    return _change_status(
        lead_id, LeadStatus.PILOT, InteractionKind.PILOT, "Piloto registrado."
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/pause")
def pause_lead(lead_id):
    return _change_status(
        lead_id, LeadStatus.PAUSED, InteractionKind.PAUSE, "Lead pausado."
    )


@peixe_bp.post("/peixe/leads/<int:lead_id>/note")
def add_note(lead_id):
    repository = _repository()
    try:
        repository.get_lead(lead_id)
    except LeadNotFoundError:
        abort(404)
    notes = request.form.get("notes", "").strip()
    if not notes:
        flash("Escreva a nota antes de salvar.", "error")
        return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)
    try:
        repository.log_interaction(lead_id, InteractionKind.NOTE, notes=notes)
    except LeadNotFoundError:
        abort(404)
    except ValidationError as error:
        flash(str(error), "error")
        return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)
    flash("Nota registrada.", "success")
    return redirect(_back_url("peixe.lead_detail", lead_id=lead_id), code=303)


@peixe_bp.get("/peixe/semana")
def week():
    repository = _repository()
    progress = repository.weekly_progress()
    weekly_kinds = repository.weekly_kind_counts()
    extra = {
        "proposals": weekly_kinds[InteractionKind.PROPOSAL.value],
        "pilots": weekly_kinds[InteractionKind.PILOT.value],
    }
    next_leads = sorted(
        repository.list_leads(),
        key=lambda lead: (
            lead.next_action_at is None,
            lead.next_action_at or date.max,
            lead.created_at,
        ),
    )[:5]
    return render_template(
        "peixe/week.html",
        progress=progress,
        quest=_quest(repository, progress),
        xp=repository.xp_total(),
        level=repository.level(),
        streak=repository.streak(),
        next_leads=next_leads,
        extra=extra,
        learning=repository.get_setting("weekly_learning", ""),
        blocker=repository.get_setting("weekly_blocker", ""),
    )


@peixe_bp.post("/peixe/semana")
def save_week():
    repository = _repository()
    repository.set_setting("weekly_learning", request.form.get("learning", ""))
    repository.set_setting("weekly_blocker", request.form.get("blocker", ""))
    flash("Fechamento da semana atualizado.", "success")
    return redirect(url_for("peixe.week"), code=303)


@peixe_bp.post("/peixe/email/daily")
def send_daily_email():
    from .peixe_digest import send_peixe_daily

    try:
        message = send_peixe_daily(current_app._get_current_object())
    except (RuntimeError, smtplib.SMTPException, OSError) as error:
        flash(f"Nao consegui enviar o resumo diario: {error}", "error")
        return redirect(_back_url("peixe.dashboard"), code=303)
    flash(message, "success")
    return redirect(_back_url("peixe.dashboard"), code=303)


@peixe_bp.post("/peixe/email/weekly")
def send_weekly_email():
    from .peixe_digest import send_peixe_weekly

    try:
        message = send_peixe_weekly(current_app._get_current_object())
    except (RuntimeError, smtplib.SMTPException, OSError) as error:
        flash(f"Nao consegui enviar o fechamento: {error}", "error")
        return redirect(_back_url("peixe.dashboard"), code=303)
    flash(message, "success")
    return redirect(_back_url("peixe.dashboard"), code=303)


@peixe_bp.get("/peixe/agenda")
def agenda():
    repository = _repository()
    today = _today()
    horizon = today + timedelta(days=7)
    days = {
        today + timedelta(days=offset): []
        for offset in range(7)
    }
    for lead in repository.list_leads():
        if lead.next_action_at is not None and today <= lead.next_action_at < horizon:
            days[lead.next_action_at].append(lead)
    return render_template("peixe/agenda.html", days=days, today=today)
