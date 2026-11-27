/* datawatch cards for Home Assistant dashboards.
 *
 * Titles come from datawatch and are not trusted: they are only ever set as text or as
 * attribute values, never as markup.
 */
const DEFAULT_ENTITY = "sensor.datawatch_dashboard_data_live_work";

const COLOURS = {
  running: "var(--info-color, #039be5)",
  running_tests: "var(--info-color, #039be5)",
  verifying: "var(--info-color, #039be5)",
  in_progress: "var(--info-color, #039be5)",
  completed: "var(--success-color, #43a047)",
  blocked: "var(--warning-color, #ffa600)",
  failed: "var(--error-color, #db4437)",
};

const STYLE = `
  .body { padding: 0 16px 16px; }
  .note { color: var(--secondary-text-color); margin: 4px 0 8px; }
  h3 { font-size: 1em; margin: 12px 0 4px; overflow-wrap: anywhere; }
  .row { display: grid; grid-template-columns: minmax(7em, 38%) 1fr; gap: 8px;
         align-items: center; min-height: 24px; }
  .label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.9em; }
  .track { position: relative; height: 16px; border-radius: 3px;
           background: var(--secondary-background-color); }
  .bar { position: absolute; top: 0; bottom: 0; min-width: 3px; border-radius: 3px;
         box-sizing: border-box; }
  .bar:focus { outline: 2px solid var(--primary-text-color); outline-offset: 1px; }
  .bar.live { border-right: 3px solid var(--primary-text-color); }
  .axis { display: flex; justify-content: space-between; font-size: 0.75em;
          color: var(--secondary-text-color); }
`;

function words(status) {
  return String(status || "unknown").replace(/_/g, " ");
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

class DatawatchGanttCard extends HTMLElement {
  static getStubConfig() {
    return {};
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "title", selector: { text: {} } },
        { name: "entity", selector: { entity: { domain: "sensor", integration: "datawatch" } } },
      ],
    };
  }

  setConfig(config) {
    if (config.entity !== undefined && typeof config.entity !== "string") {
      throw new Error("entity must be the name of the live work sensor");
    }
    this._config = config;
    this._drawn = undefined;
    if (this._hass) this._draw();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._config) this._draw();
  }

  getCardSize() {
    return 6;
  }

  getGridOptions() {
    return { columns: "full", min_columns: 6 };
  }

  _time(value) {
    return new Date(value).toLocaleTimeString(this._hass.locale?.language, {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  _row(label, bars, from, span) {
    const row = element("div", "row");
    const name = element("div", "label", label);
    name.title = label;
    const track = element("div", "track");
    for (const bar of bars) {
      const start = Date.parse(bar.start);
      const end = Date.parse(bar.end);
      if (!Number.isFinite(start) || !Number.isFinite(end)) continue;
      const left = Math.min(100, Math.max(0, ((start - from) / span) * 100));
      const width = Math.min(100 - left, Math.max(0, ((end - start) / span) * 100));
      const node = element("div", bar.live ? "bar live" : "bar");
      node.style.left = `${left.toFixed(2)}%`;
      node.style.width = `${width.toFixed(2)}%`;
      node.style.background = Object.hasOwn(COLOURS, bar.status)
        ? COLOURS[bar.status]
        : "var(--primary-color, #7c3aed)";
      const state = bar.status ? `${words(bar.status)}, ` : "";
      const until = bar.live ? "still running" : this._time(bar.end);
      const said = `${bar.title}: ${state}${this._time(bar.start)} to ${until}`;
      node.title = said;
      node.setAttribute("role", "img");
      node.setAttribute("aria-label", said);
      node.tabIndex = 0;
      track.append(node);
    }
    row.append(name, track);
    return row;
  }

  _message(entity, state) {
    if (!state) {
      return (
        `${entity} was not found. In Settings, Devices & services, datawatch, enable the ` +
        "sensor “Dashboard data: live work”."
      );
    }
    if (state.state === "unavailable" || !state.attributes.data) {
      return "datawatch cannot be read right now.";
    }
    return "";
  }

  _draw() {
    const entity = this._config.entity || DEFAULT_ENTITY;
    const state = this._hass.states[entity];
    const key = state || null;
    if (this._drawn === key) return;
    this._drawn = key;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    const card = document.createElement("ha-card");
    card.setAttribute("header", this._config.title || "datawatch live work");
    const style = element("style", "", STYLE);
    const body = element("div", "body");
    card.append(body);
    this.shadowRoot.replaceChildren(style, card);

    const message = this._message(entity, state);
    if (message) {
      body.append(element("p", "note", message));
      return;
    }
    const data = state.attributes.data;
    const from = Date.parse(data.from);
    const span = Date.parse(data.to) - from;
    if (!Number.isFinite(span) || span <= 0) {
      body.append(element("p", "note", "datawatch cannot be read right now."));
      return;
    }
    body.append(element("p", "note", `Last 6 hours, up to ${this._time(data.to)}.`));
    const axis = element("div", "row");
    const times = element("div", "axis");
    for (const part of [0, 0.5, 1]) times.append(element("span", "", this._time(from + span * part)));
    axis.append(element("div"), times);
    body.append(axis);

    const lanes = data.lanes || [];
    if (lanes.length) {
      body.append(element("h3", "", "Lanes"));
      for (const lane of lanes) {
        const label = lane.bars.length ? lane.name : `${lane.name} (idle)`;
        body.append(this._row(label, lane.bars, from, span));
      }
    }
    for (const work of data.work || []) {
      body.append(element("h3", "", `${work.title} (${words(work.status)})`));
      for (const bar of work.bars) {
        body.append(this._row(`${bar.title} (${words(bar.status)})`, [bar], from, span));
      }
    }
    if (!(data.work || []).length) {
      body.append(
        element("p", "note", "No task of running, blocked or planning work ran in these 6 hours.")
      );
    }
    if (data.not_read > 0) {
      const more = data.not_read === 1 ? "automaton is" : "automata are";
      body.append(element("p", "note", `${data.not_read} more unfinished ${more} not shown.`));
    }
  }
}

if (!customElements.get("datawatch-gantt-card")) {
  customElements.define("datawatch-gantt-card", DatawatchGanttCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "datawatch-gantt-card",
    name: "datawatch Gantt (live work)",
    description: "What each lane and unfinished task ran in the last 6 hours.",
    documentationURL: "https://github.com/dmz006/datawatch-hacs#readme",
  });
}
