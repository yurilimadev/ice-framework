from __future__ import annotations

from datetime import date

import smtplib

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
from .digest import send_digest
from .tasks import (
    TagNotFoundError,
    Task,
    TaskNotFoundError,
    TaskRepository,
    TaskStatus,
    ValidationError,
    normalize_tags,
    parse_deadline,
    today_in_timezone,
    validate_ice_value,
    validate_tag_name,
    validate_title,
)


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.app_context_processor
def _digest_availability():
    config = current_app.config
    ready = all(
        config.get(key)
        for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "DIGEST_TO")
    )
    return {"digest_ready": ready}


def _back_url():
    target = request.referrer
    if target and target.startswith(request.host_url):
        return target
    return url_for("tasks.index")


def _repository() -> TaskRepository:
    return TaskRepository(get_db(), current_app.config["APP_TIMEZONE"])


def _task_view(task: Task):
    today = today_in_timezone(current_app.config["APP_TIMEZONE"])
    return {
        "id": task.id,
        "title": task.title,
        "impact": task.impact,
        "confidence": task.confidence,
        "ease": task.ease,
        "deadline": task.deadline,
        "status": task.status.value,
        "created_at": task.created_at,
        "tags": task.tags,
        "score": task.score,
        "overdue": task.is_overdue(today),
    }


def _messages():
    return get_flashed_messages(with_categories=True)


def _render_index(repository, *, filters, errors=None):
    if errors:
        tasks = []
    else:
        try:
            tasks = repository.list(
                status=filters["status_value"],
                overdue=filters["overdue_value"],
                tags=filters["tags"],
                order_by=filters["order"],
            )
        except (ValidationError, ValueError) as error:
            field = getattr(error, "field", None) or "filters"
            errors = {field: str(error)}
            tasks = []

    return render_template(
        "index.html",
        tasks=[_task_view(task) for task in tasks],
        available_tags=repository.available_tags(),
        filters={
            "status": filters["status"],
            "overdue": filters["overdue"],
            "tag": filters["tags"],
            "order": filters["order"],
        },
        errors=errors or {},
        messages=_messages(),
    )


def _list_filters():
    status = request.args.get("status", "open")
    status_values = {
        "open": TaskStatus.OPEN,
        "completed": TaskStatus.COMPLETED,
        "all": None,
    }
    if status not in status_values:
        raise ValidationError("Status de filtro invalido.", "status")

    overdue = request.args.get("overdue")
    if overdue not in (None, "1"):
        raise ValidationError("O filtro de atraso deve usar o valor 1.", "overdue")

    order = request.args.get("order", "score")
    if order not in {"score", "deadline", "created_at"}:
        raise ValidationError("Ordenacao invalida.", "order")

    tags = request.args.getlist("tag")
    if any(not tag.strip() for tag in tags):
        raise ValidationError("As tags de filtro nao podem ser vazias.", "tag")
    try:
        normalize_tags(tags)
    except ValidationError as error:
        raise ValidationError(str(error), "tag") from None

    return {
        "status": status,
        "status_value": status_values[status],
        "overdue": overdue == "1",
        "overdue_value": True if overdue == "1" else None,
        "tags": tags,
        "order": order,
    }


def _form_values(task: Task | None = None):
    if task is None:
        return {
            "title": "",
            "impact": "",
            "confidence": "",
            "ease": "",
            "deadline": "",
            "tags": "",
        }
    return {
        "title": task.title,
        "impact": str(task.impact),
        "confidence": str(task.confidence),
        "ease": str(task.ease),
        "deadline": task.deadline.isoformat() if task.deadline else "",
        "tags": ", ".join(task.tags),
    }


def _parse_form(form):
    values = {
        "title": form.get("title", ""),
        "impact": form.get("impact", ""),
        "confidence": form.get("confidence", ""),
        "ease": form.get("ease", ""),
        "deadline": form.get("deadline", ""),
        "tags": form.get("tags", ""),
    }
    errors = {}
    parsed = {}

    try:
        parsed["title"] = validate_title(values["title"])
    except ValidationError as error:
        errors[error.field] = str(error)

    for field in ("impact", "confidence", "ease"):
        raw_value = values[field]
        try:
            parsed[field] = validate_ice_value(int(raw_value), field)
        except ValidationError as error:
            errors[error.field] = str(error)
        except (TypeError, ValueError):
            errors[field] = "Informe um numero inteiro entre 1 e 10."

    try:
        parsed["deadline"] = parse_deadline(values["deadline"] or None)
    except ValidationError as error:
        errors[error.field] = str(error)

    raw_tags = values["tags"].split(",") if values["tags"].strip() else None
    try:
        parsed["tags"] = normalize_tags(raw_tags)
    except ValidationError as error:
        errors[error.field] = str(error)
    return values, parsed, errors


def _form_error_context(task, values, error):
    errors = {getattr(error, "field", None) or "form": str(error)}
    return render_template(
        "task_form.html",
        task=task,
        errors=errors,
        form_values=values,
    ), 400


@tasks_bp.get("/")
def index():
    repository = _repository()
    try:
        filters = _list_filters()
    except ValidationError as error:
        filters = {
            "status": request.args.get("status", "open"),
            "status_value": TaskStatus.OPEN,
            "overdue": request.args.get("overdue"),
            "overdue_value": None,
            "tags": request.args.getlist("tag"),
            "order": request.args.get("order", "score"),
        }
        response = _render_index(repository, filters=filters, errors={error.field: str(error)})
        return response, 400
    return _render_index(repository, filters=filters)


@tasks_bp.get("/tasks/new")
def new_task():
    return render_template(
        "task_form.html",
        task=None,
        errors={},
        form_values=_form_values(),
    )


@tasks_bp.post("/tasks")
def create_task():
    values, parsed, errors = _parse_form(request.form)
    if errors:
        return render_template(
            "task_form.html", task=None, errors=errors, form_values=values
        ), 400

    try:
        _repository().create(**parsed)
    except ValidationError as error:
        return _form_error_context(None, values, error)
    flash("Tarefa criada.", "success")
    return redirect(url_for("tasks.index"), code=303)


@tasks_bp.get("/tasks/<int:task_id>/edit")
def edit_task(task_id):
    try:
        task = _repository().get(task_id)
    except TaskNotFoundError:
        abort(404)
    return render_template(
        "task_form.html",
        task=task,
        errors={},
        form_values=_form_values(task),
    )


@tasks_bp.post("/tasks/<int:task_id>")
def update_task(task_id):
    repository = _repository()
    try:
        task = repository.get(task_id)
    except TaskNotFoundError:
        abort(404)

    values, parsed, errors = _parse_form(request.form)
    if errors:
        return render_template(
            "task_form.html", task=task, errors=errors, form_values=values
        ), 400

    try:
        repository.update(task_id, **parsed)
    except ValidationError as error:
        return _form_error_context(task, values, error)
    flash("Tarefa atualizada.", "success")
    return redirect(url_for("tasks.index"), code=303)


@tasks_bp.post("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    try:
        _repository().complete(task_id)
    except TaskNotFoundError:
        abort(404)
    flash("Tarefa concluida.", "success")
    return redirect(url_for("tasks.index"), code=303)


@tasks_bp.post("/tasks/<int:task_id>/reopen")
def reopen_task(task_id):
    try:
        _repository().reopen(task_id)
    except TaskNotFoundError:
        abort(404)
    flash("Tarefa reaberta.", "success")
    return redirect(url_for("tasks.index"), code=303)


@tasks_bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    try:
        _repository().delete(task_id)
    except TaskNotFoundError:
        abort(404)
    flash("Tarefa excluida.", "success")
    return redirect(url_for("tasks.index"), code=303)


@tasks_bp.get("/tags")
def list_tags():
    repository = _repository()
    return render_template(
        "tags.html",
        tags=repository.list_tags_with_usage(),
        messages=get_flashed_messages(with_categories=True),
    )


@tasks_bp.post("/tags/<int:tag_id>/rename")
def rename_tag(tag_id):
    new_name = request.form.get("name", "")
    try:
        _repository().rename_tag(tag_id, new_name)
    except TagNotFoundError:
        abort(404)
    except ValidationError as error:
        flash(str(error), "error")
        return redirect(url_for("tasks.list_tags"), code=303)
    flash("Tag renomeada.", "success")
    return redirect(url_for("tasks.list_tags"), code=303)


@tasks_bp.post("/tags/<int:tag_id>/delete")
def delete_tag(tag_id):
    try:
        _repository().delete_tag(tag_id)
    except TagNotFoundError:
        abort(404)
    flash("Tag excluida.", "success")
    return redirect(url_for("tasks.list_tags"), code=303)


@tasks_bp.post("/tags/merge")
def merge_tags():
    source_id = int(request.form.get("source_id", 0))
    target_id = int(request.form.get("target_id", 0))
    try:
        target_name = _repository().merge_tags(source_id, target_id)
    except TagNotFoundError:
        abort(404)
    except ValidationError as error:
        flash(str(error), "error")
        return redirect(url_for("tasks.list_tags"), code=303)
    flash(f"Tags mescladas em '{target_name}'.", "success")
    return redirect(url_for("tasks.list_tags"), code=303)


@tasks_bp.post("/digest/send")
def send_digest_email():
    try:
        message = send_digest(current_app)
    except (RuntimeError, smtplib.SMTPException, OSError) as error:
        flash(f"Nao consegui enviar o resumo: {error}", "error")
        return redirect(_back_url(), code=303)
    flash(message, "success")
    return redirect(_back_url(), code=303)
