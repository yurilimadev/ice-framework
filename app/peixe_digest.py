"""Resumos diario e semanal do Peixe-piloto por email."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from .peixe import InteractionKind, PeixeRepository
from .peixe_routes import _quest, build_message


CHANNEL_LABELS = {
    "whatsapp": "WhatsApp",
    "linkedin": "LinkedIn",
    "email": "Email",
    "instagram": "Instagram",
    "presencial": "Presencial",
}


def _pain(repository, lead):
    pain = repository.get_setting("current_pain")
    if pain:
        return pain
    ocean = (repository.get_setting("current_ocean") or "").casefold()
    if ocean == "odontologia":
        return "falta de paciente e agenda"
    return f"os desafios de {lead.sector}"


def _mission(repository):
    lead = repository.daily_mission()
    if lead is None:
        return None, None, None
    pain = _pain(repository, lead)
    return lead, pain, build_message(lead)


def render_daily_text(repository, base_url="https://ice.yurilimadev.com") -> str:
    lead, pain, message = _mission(repository)
    lines = ["PEIXE-PILOTO - MISSAO DE HOJE", ""]
    if lead is None:
        lines.append("Nenhuma missao pendente. Cadastre um lead ou ajuste os follow-ups.")
    else:
        lines.append(f"Empresa: {lead.company}")
        if lead.contact:
            lines.append(f"Contato: {lead.contact}")
        lines.append(f"Canal: {CHANNEL_LABELS.get(lead.channel.value, lead.channel.value)}")
        lines.append(f"Observacao: {lead.observation}")
        lines.append("")
        lines.append("Mensagem sugerida:")
        lines.append(message)
    lines.extend(
        [
            "",
            f"XP: {repository.xp_total()} | Nivel: {repository.level()} | "
            f"Streak: {repository.streak()} dia(s)",
        ]
    )
    followups = repository.followups_due()
    lines.append(f"Follow-ups vencidos: {len(followups)}")
    for item in followups:
        lines.append(f"- {item.company} ({item.next_action_at.strftime('%d/%m/%Y')})")
    lines.extend(["", f"Abra o Peixe: {base_url}/peixe", "", "--", "ICE Framework - prioridade com clareza."])
    return "\n".join(lines)


def render_daily_html(
    repository,
    base_url="https://ice.yurilimadev.com",
    today: str | None = None,
) -> str:
    lead, pain, message = _mission(repository)
    followups = repository.followups_due()
    date_html = (
        f'<span style="color:#b8d1d4;font-size:12px;">{escape(today)}</span>'
        if today
        else ""
    )
    if lead is None:
        mission_html = (
            '<p style="margin:0;color:#536e73;font-size:14px;">'
            "Nenhuma missao pendente. Cadastre um lead ou ajuste os follow-ups.</p>"
        )
    else:
        contact = f"{escape(lead.contact)} &middot; " if lead.contact else ""
        mission_html = (
            f'<p style="margin:0 0 4px;color:#536e73;font-size:12px;">'
            f"{contact}{CHANNEL_LABELS.get(lead.channel.value, lead.channel.value)}"
            f" &middot; {escape(pain)}</p>"
            f'<h2 style="margin:0 0 6px;color:#082f3a;font-size:20px;">'
            f"{escape(lead.company)}</h2>"
            f'<p style="margin:0 0 12px;color:#31535a;font-size:13px;">'
            f"{escape(lead.observation)}</p>"
            '<div style="padding:14px 16px;background:#f7fbfb;border:1px dashed #b8dfe2;'
            'border-radius:9px;color:#082f3a;font-size:14px;white-space:pre-wrap;">'
            f"{escape(message)}</div>"
        )
    followup_rows = "".join(
        f'<li style="margin:4px 0;color:#31535a;font-size:13px;">'
        f"{escape(item.company)} &middot; "
        f"{item.next_action_at.strftime('%d/%m/%Y')}</li>"
        for item in followups
    ) or '<li style="color:#536e73;font-size:13px;">Nenhum follow-up vencido.</li>'

    return (
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="background:#eef4f5;padding:24px 12px;" role="presentation">'
        '<tr><td align="center">'
        '<table width="600" cellpadding="0" cellspacing="0" '
        'style="background:#ffffff;border-radius:14px;overflow:hidden;" role="presentation">'
        '<tr><td style="background:#082f3a;padding:20px 24px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
        '<td style="color:#e7f9fa;font-size:14px;letter-spacing:2px;">'
        'PEIXE <span style="color:#f0b34a;font-weight:800;">PILOTO</span></td>'
        f'<td align="right">{date_html}</td></tr></table></td></tr>'
        '<tr><td style="padding:20px 24px 8px;">'
        '<span style="font-size:15px;font-weight:700;color:#082f3a;">'
        "Missao de hoje</span></td></tr>"
        f'<tr><td style="padding:0 24px 16px;">{mission_html}</td></tr>'
        '<tr><td style="padding:0 24px 16px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
        '<td style="padding:10px 12px;background:#fff7ef;border-radius:9px;color:#c65f45;'
        'font-size:12px;font-weight:700;">'
        f"XP {repository.xp_total()} &middot; {escape(repository.level())} &middot; "
        f"streak {repository.streak()} dia(s)</td></tr></table></td></tr>"
        '<tr><td style="padding:0 24px 18px;">'
        '<span style="display:block;margin-bottom:6px;color:#536e73;font-size:12px;'
        'font-weight:700;text-transform:uppercase;letter-spacing:1px;">'
        "Follow-ups vencidos</span>"
        f'<ul style="margin:0;padding-left:18px;">{followup_rows}</ul></td></tr>'
        '<tr><td style="padding:14px 24px 18px;border-top:1px solid #edf2f2;">'
        f'<a href="{escape(base_url)}/peixe" style="color:#087d91;font-size:13px;'
        'font-weight:700;text-decoration:none;">Abrir Peixe-piloto</a></td></tr>'
        "</table></td></tr></table>"
    )


def render_weekly_text(repository, base_url="https://ice.yurilimadev.com") -> str:
    progress = repository.weekly_progress()
    kinds = repository.weekly_kind_counts()
    quest = _quest(repository, progress)
    lines = [
        "PEIXE-PILOTO - FECHAMENTO DA SEMANA",
        "",
        f"Mensagens: {progress['messages']}",
        f"Respostas: {progress['replies']}",
        f"Conversas: {progress['conversations']}",
        f"Propostas: {kinds[InteractionKind.PROPOSAL.value]}",
        f"Pilotos: {kinds[InteractionKind.PILOT.value]}",
        "",
        f"Quest: {quest['percent']}% concluida",
        f"Doce: {'liberado' if quest['doce'] else 'ainda nao liberado'}",
        f"XP: {repository.xp_total()} | Nivel: {repository.level()} | "
        f"Streak: {repository.streak()} dia(s)",
        "",
        f"Aprendizado: {repository.get_setting('weekly_learning') or '-'}",
        f"Bloqueio: {repository.get_setting('weekly_blocker') or '-'}",
        "",
        f"Abra a semana: {base_url}/peixe/semana",
        "",
        "--",
        "ICE Framework - prioridade com clareza.",
    ]
    return "\n".join(lines)


def render_weekly_html(
    repository,
    base_url="https://ice.yurilimadev.com",
    today: str | None = None,
) -> str:
    progress = repository.weekly_progress()
    kinds = repository.weekly_kind_counts()
    quest = _quest(repository, progress)
    date_html = (
        f'<span style="color:#b8d1d4;font-size:12px;">{escape(today)}</span>'
        if today
        else ""
    )
    metrics = (
        ("Mensagens", progress["messages"]),
        ("Respostas", progress["replies"]),
        ("Conversas", progress["conversations"]),
        ("Propostas", kinds[InteractionKind.PROPOSAL.value]),
        ("Pilotos", kinds[InteractionKind.PILOT.value]),
    )
    metric_cells = "".join(
        f'<td style="padding:10px 8px;text-align:center;">'
        f'<span style="display:block;color:#082f3a;font-size:20px;font-weight:800;">'
        f"{value}</span>"
        f'<span style="color:#536e73;font-size:11px;text-transform:uppercase;">'
        f"{label}</span></td>"
        for label, value in metrics
    )
    learning = escape(repository.get_setting("weekly_learning") or "-")
    blocker = escape(repository.get_setting("weekly_blocker") or "-")

    return (
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="background:#eef4f5;padding:24px 12px;" role="presentation">'
        '<tr><td align="center">'
        '<table width="600" cellpadding="0" cellspacing="0" '
        'style="background:#ffffff;border-radius:14px;overflow:hidden;" role="presentation">'
        '<tr><td style="background:#082f3a;padding:20px 24px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
        '<td style="color:#e7f9fa;font-size:14px;letter-spacing:2px;">'
        'PEIXE <span style="color:#f0b34a;font-weight:800;">PILOTO</span></td>'
        f'<td align="right">{date_html}</td></tr></table></td></tr>'
        '<tr><td style="padding:20px 24px 6px;">'
        '<span style="font-size:15px;font-weight:700;color:#082f3a;">'
        "Fechamento da semana</span></td></tr>"
        '<tr><td style="padding:0 18px 10px;"><table width="100%" cellpadding="0" '
        f'cellspacing="0" role="presentation"><tr>{metric_cells}</tr></table></td></tr>'
        '<tr><td style="padding:0 24px 14px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
        '<td style="padding:10px 12px;background:#fff7ef;border-radius:9px;color:#c65f45;'
        'font-size:12px;font-weight:700;">'
        f"Quest {quest['percent']}% &middot; "
        f"Doce: {'liberado' if quest['doce'] else 'pendente'} &middot; "
        f"XP {repository.xp_total()} &middot; {escape(repository.level())}"
        "</td></tr></table></td></tr>"
        f'<tr><td style="padding:0 24px 16px;color:#31535a;font-size:13px;">'
        f"<strong>Aprendizado:</strong> {learning}<br>"
        f"<strong>Bloqueio:</strong> {blocker}</td></tr>"
        '<tr><td style="padding:14px 24px 18px;border-top:1px solid #edf2f2;">'
        f'<a href="{escape(base_url)}/peixe/semana" style="color:#087d91;font-size:13px;'
        'font-weight:700;text-decoration:none;">Abrir fechamento da semana</a>'
        "</td></tr></table></td></tr></table>"
    )


def _send(app, subject, text, html, recipient, target_label):
    config = {
        "host": app.config.get("SMTP_HOST"),
        "port": int(app.config.get("SMTP_PORT", 587)),
        "user": app.config.get("SMTP_USER"),
        "password": app.config.get("SMTP_PASSWORD"),
        "from": app.config.get("SMTP_FROM"),
    }
    to_address = (
        recipient or app.config.get("PEIXE_TO") or app.config.get("DIGEST_TO")
    )
    missing = [key for key in ("host", "user", "password", "from") if not config[key]]
    if missing:
        raise RuntimeError(
            "SMTP incompleto; defina SMTP_HOST, SMTP_PORT, SMTP_USER, "
            "SMTP_PASSWORD e SMTP_FROM."
        )
    if not to_address:
        raise RuntimeError(
            "Destino do Peixe ausente; defina PEIXE_TO ou DIGEST_TO."
        )

    multipart = MIMEMultipart("alternative")
    multipart["Subject"] = subject
    multipart["From"] = config["from"]
    multipart["To"] = to_address
    multipart.attach(MIMEText(text, "plain", "utf-8"))
    multipart.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(config["host"], config["port"]) as server:
        server.starttls()
        server.login(config["user"], config["password"])
        server.send_message(multipart)
    return f"{target_label} enviado para {to_address}."


def send_peixe_daily(app, recipient=None) -> str:
    with app.app_context():
        from .db import get_db

        repository = PeixeRepository(get_db(), app.config["APP_TIMEZONE"])
        base_url = app.config.get("PEIXE_BASE_URL") or "https://ice.yurilimadev.com"
        text = render_daily_text(repository, base_url)
        html = render_daily_html(repository, base_url)
    return _send(
        app,
        "Peixe-piloto — missão de hoje",
        text,
        html,
        recipient,
        "Resumo diario do Peixe",
    )


def send_peixe_weekly(app, recipient=None) -> str:
    with app.app_context():
        from .db import get_db

        repository = PeixeRepository(get_db(), app.config["APP_TIMEZONE"])
        base_url = app.config.get("PEIXE_BASE_URL") or "https://ice.yurilimadev.com"
        text = render_weekly_text(repository, base_url)
        html = render_weekly_html(repository, base_url)
    return _send(
        app,
        "Peixe-piloto — fechamento da semana",
        text,
        html,
        recipient,
        "Fechamento semanal do Peixe",
    )
