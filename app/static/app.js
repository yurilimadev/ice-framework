(() => {
  const dismissDelay = 4000;

  document.querySelectorAll("[data-message]").forEach((message) => {
    let dismissed = false;

    const dismiss = () => {
      if (dismissed) return;
      dismissed = true;
      message.classList.add("is-dismissing");
      window.setTimeout(() => message.remove(), 220);
    };

    message.querySelector("[data-dismiss-message]")?.addEventListener("click", dismiss);
    window.setTimeout(dismiss, dismissDelay);
  });
})();

(() => {
  const REGION = "data-dynamic-region";
  const SLOW_DELAY = 300;

  const region = (name, root) =>
    (root || document).querySelector(`[${REGION}="${name}"]`);

  const initDynamicFilters = () => {
    const form = document.querySelector(".filter-form");
    if (!form || !region("task-area") || !window.fetch) return;

    let controller = null;
    let slowTimer = null;

    const showSyncError = (area) => {
      if (area.querySelector(".sync-error")) return;
      const notice = document.createElement("div");
      notice.className = "sync-error";
      notice.setAttribute("role", "status");
      notice.textContent =
        "Nao consegui atualizar a lista. Ajuste os filtros e tente de novo.";
      area.prepend(notice);
    };

    const finish = (after) => {
      window.clearTimeout(slowTimer);
      const area = region("task-area");
      if (area) {
        area.classList.remove("is-refreshing", "is-slow");
        area.removeAttribute("aria-busy");
      }
      if (typeof after === "function") after();
    };

    const applyFilters = async () => {
      const params = new URLSearchParams(new FormData(form)).toString();
      const url = params ? `${form.action}?${params}` : form.action;

      if (controller) controller.abort();
      controller = new AbortController();

      const current = region("task-area");
      current?.querySelector(".sync-error")?.remove();
      current?.classList.add("is-refreshing");
      current?.setAttribute("aria-busy", "true");
      window.clearTimeout(slowTimer);
      slowTimer = window.setTimeout(
        () => region("task-area")?.classList.add("is-slow"),
        SLOW_DELAY,
      );

      try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const doc = new DOMParser().parseFromString(
          await response.text(),
          "text/html",
        );
        const openGroups = new Set(
          [...document.querySelectorAll("[data-group-block][open]")].map(
            (block) => block.dataset.sectionGroupId,
          ),
        );
        ["filter-feedback", "task-area", "view-count"].forEach((name) => {
          const local = region(name);
          const remote = region(name, doc);
          if (local && remote) local.replaceWith(remote);
        });
        document.querySelectorAll("[data-group-block]").forEach((block) => {
          if (openGroups.has(block.dataset.sectionGroupId)) block.open = true;
        });
        document.dispatchEvent(new Event("groups-updated"));
        window.history.replaceState(null, "", url);
        finish(() => {
          region("task-area")?.scrollTo(0, 0);
          window.scrollTo(0, 0);
        });
      } catch (error) {
        if (error && error.name === "AbortError") return;
        finish(() => {
          const area = region("task-area");
          if (area) showSyncError(area);
        });
      }
    };

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      applyFilters();
    });
    form.addEventListener("change", applyFilters);
  };

  initDynamicFilters();
})();

(() => {
  const BLOCK = "[data-group-block]";

  const sync = () => {
    const button = document.querySelector("[data-toggle-groups]");
    if (!button) return;
    const blocks = [...document.querySelectorAll(BLOCK)];
    const expanded = blocks.length > 0 && blocks.every((block) => block.open);
    button.textContent = expanded ? "Recolher grupos" : "Expandir grupos";
    button.setAttribute("aria-expanded", expanded ? "true" : "false");
  };

  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-toggle-groups]");
    if (!button) return;
    const blocks = [...document.querySelectorAll(BLOCK)];
    const shouldOpen = !blocks.every((block) => block.open);
    blocks.forEach((block) => {
      block.open = shouldOpen;
    });
    sync();
  });

  document.addEventListener(
    "toggle",
    (event) => {
      if (event.target.matches?.(BLOCK)) sync();
    },
    true,
  );

  document.addEventListener("groups-updated", sync);
  sync();
})();

(() => {
  const fallbackCopy = (text) => {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.append(field);
    field.select();
    document.execCommand("copy");
    field.remove();
  };

  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-target]");
    if (!button) return;
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const text = target.textContent || "";
    try {
      await navigator.clipboard.writeText(text);
    } catch (_error) {
      fallbackCopy(text);
    }
    const original = button.textContent;
    button.textContent = "Copiado";
    window.setTimeout(() => {
      button.textContent = original;
    }, 1600);
  });
})();

(() => {
  document.querySelectorAll("form[data-busy-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[data-busy-button]");
      if (!button) return;
      button.disabled = true;
      const label = form.querySelector("[data-busy-text]");
      if (label && form.dataset.busyLabel) label.textContent = form.dataset.busyLabel;
    });
  });
})();
