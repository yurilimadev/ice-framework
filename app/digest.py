"""Resumo por email das tarefas pendentes para uso fora da interface."""

import smtplib
from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _digest_tasks(repository) -> dict:
    open_tasks = repository.list(status="open", order_by="score")
    try:
        overdue_tasks = repository.list(status="open", overdue=True, order_by="deadline")
    except ValidationError:
        overdue_tasks = []
    return {"open": open_tasks, "overdue": overdue_tasks}


def render_digest_text(tasks: dict) -> str:
    lines = ["ICE Framework - Resumo do dia", ""]
    lines.append(
        f"{len(tasks['open'])} tarefa(s) aberta(s), "
        f"{len(tasks['overdue'])} atrasada(s)."
    )
    for task in tasks["open"]:
        overdue_badge = " (atrasada)" if task in tasks["overdue"] else ""
        deadline = task.deadline.strftime("%d/%m/%Y") if task.deadline else "sem prazo"
        lines.append(
            f"- {task.title} (score {task.score}, prazo {deadline}{overdue_badge})"
        )
    if not tasks["open"]:
        lines.append("- Nenhuma tarefa pendente. Bom descanso!")
    lines.append("")
    lines.append("--")
    lines.append("Enviado pelo ICE Framework - prioridade com clareza.")
    return "\n".join(lines)


def render_digest_html(tasks: dict, today: str | None = None) -> str:
    open_tasks = tasks["open"]
    overdue_tasks = tasks["overdue"]

    rows = []
    for task in open_tasks:
        is_overdue = task in overdue_tasks
        overdue_badge = (
            '<span style="display:inline-block;padding:2px 8px;margin-left:8px;'
            'background:#fff3f1;color:#bb4f55;border-radius:99px;'
            'font-size:11px;font-weight:700;">(atrasada)</span>'
            if is_overdue
            else ""
        )
        deadline = task.deadline.strftime("%d/%m/%Y") if task.deadline else "sem prazo"
        deadline_color = "#bb4f55" if is_overdue else "#536e73"
        rows.append(
            f'<tr style="border-bottom:1px solid #edf2f2;">'
            f'<td style="padding:12px 8px;color:#082f3a;font-size:14px;">'
            f"<strong>{escape(task.title)}</strong>{overdue_badge}<br>"
            f'<span style="color:#536e73;font-size:12px;">'
            f"score {task.score} &middot; I {task.impact} &middot; "
            f"C {task.confidence} &middot; F {task.ease} &middot; "
            f'<span style="color:{deadline_color};font-weight:600;">'
            f"prazo {deadline}</span>"
            f"</span></td></tr>"
        )
    body_rows = "".join(rows) or (
        '<tr><td style="padding:16px 8px;color:#536e73;font-size:14px;">'
        "Nenhuma tarefa pendente. Bom descanso!</td></tr>"
    )

    date_html = (
        f'<span style="color:#b8d1d4;font-size:12px;">{escape(today)}</span>'
        if today
        else ""
    )

    return (
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="background:#eef4f5;padding:24px 12px;" role="presentation">'
        "<tr><td align=\"center\">"
        '<table width="600" cellpadding="0" cellspacing="0" '
        'style="background:#ffffff;border-radius:14px;overflow:hidden;" role="presentation">'
        '<tr><td style="background:#082f3a;padding:20px 24px;" role="presentation">'
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
        '<td style="color:#e7f9fa;font-size:14px;letter-spacing:2px;">'
        'ICE <span style="color:#21d4e7;font-weight:800;">FRAMEWORK</span></td>'
        f"<td align=\"right\">{date_html}</td></tr></table>"
        "</td></tr>"
        "<tr><td style=\"padding:20px 24px 8px;\">"
        f"<span style=\"font-size:15px;font-weight:700;color:#082f3a;\">"
        f"Resumo do dia</span><br>"
        f"<span style=\"color:#536e73;font-size:13px;\">"
        f"{len(open_tasks)} tarefa(s) aberta(s), {len(overdue_tasks)} atrasada(s)."
        "</span>"
        "</td></tr>"
        "<tr><td style=\"padding:8px 24px 20px;\">"
        '<table width="100%" cellpadding="0" cellspacing="0" role="presentation">'
        f"{body_rows}"
        "</table>"
        "</td></tr>"
        '<tr><td style="padding:14px 24px 18px;border-top:1px solid #edf2f2;">'
        '<span style="color:#a6b8ba;font-size:11px;">'
        "Enviado pelo ICE Framework &mdash; prioridade com clareza."
        "</span></td></tr>"
        "</table></td></tr></table>"
    )


def send_digest(app, recipient=None) -> str:
    from flask import current_app

    with app.app_context():
        from .db import get_db
        from .tasks import TaskRepository, ValidationError, today_in_timezone

        repository = TaskRepository(get_db(), app.config["APP_TIMEZONE"])
        tasks = _digest_tasks(repository)
        html = render_digest_html(
            tasks,
            today=today_in_timezone(app.config["APP_TIMEZONE"]).strftime("%d/%m/%Y"),
        )
        text = render_digest_text(tasks)
        to_address = recipient or app.config["DIGEST_TO"]

        config = {
            "host": app.config.get("SMTP_HOST"),
            "port": int(app.config.get("SMTP_PORT", 587)),
            "user": app.config.get("SMTP_USER"),
            "password": app.config.get("SMTP_PASSWORD"),
            "from": app.config.get("SMTP_FROM"),
        }
        missing = [key for key in ("host", "user", "password", "from") if not config[key]]
        if not to_address:
            missing.append("to")
        if missing:
            raise RuntimeError(
                "SMTP incompleto; defina SMTP_HOST, SMTP_PORT, SMTP_USER, "
                "SMTP_PASSWORD, SMTP_FROM e DIGEST_TO."
            )

        multipart = MIMEMultipart("alternative")
        multipart["Subject"] = "ICE Framework - Resumo de tarefas"
        multipart["From"] = config["from"]
        multipart["To"] = to_address
        multipart.attach(MIMEText(text, "plain", "utf-8"))
        multipart.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls()
            server.login(config["user"], config["password"])
            server.send_message(multipart)
        return f"Resumo enviado para {to_address}: {len(tasks['open'])} tarefa(s) aberta(s)."
