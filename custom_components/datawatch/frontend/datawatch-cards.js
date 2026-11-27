/* datawatch cards for Home Assistant dashboards: a project Gantt and lane activity.
 *
 * Laid out for a phone first, and nothing needs a pointer to be hovered over it.
 * Names and titles come from datawatch and are not trusted: they are only ever set as text
 * or as attribute values, never as markup.
 */
const REFRESH_MS = 5 * 60 * 1000;
const PAGE = 20;
const SVG = "http://www.w3.org/2000/svg";

const COLOURS = {
  done: "var(--success-color, #43a047)",
  completed: "var(--success-color, #43a047)",
  archived: "var(--success-color, #43a047)",
  running: "var(--info-color, #039be5)",
  planning: "var(--info-color, #039be5)",
  blocked: "var(--warning-color, #ffa600)",
  failed: "var(--error-color, #db4437)",
  needs_review: "#8e24aa",
  revisions_asked: "#8e24aa",
  held: "#8d6e63",
  paused: "#8d6e63",
};
const OTHER_COLOUR = "#9e9e9e";

// Colour and dash pattern both differ, so lines can be told apart without colour.
const LINES = [
  ["#1e88e5", ""],
  ["#fb8c00", "9 4"],
  ["#43a047", "2 3"],
  ["#8e24aa", "12 3 2 3"],
  ["#e53935", "5 5"],
  ["#00897b", "14 4"],
  ["#6d4c41", "2 6"],
  ["#757575", "9 3 2 3 2 3"],
];

const STYLE = `
  ha-card { overflow: hidden; }
  .body { padding: 0 12px 12px; container-type: inline-size; }
  .note { color: var(--secondary-text-color); font-size: 0.85em; margin: 4px 0 8px; }
  .controls { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
  select, button { font: inherit; color: var(--primary-text-color); }
  select, .choice, .more { min-height: 36px; border-radius: 6px; padding: 0 10px;
    border: 1px solid var(--divider-color, #ccc);
    background: var(--card-background-color, transparent); }
  select { max-width: 100%; }
  .choice[aria-pressed="true"] { border-color: var(--primary-color, #03a9f4);
    box-shadow: inset 0 0 0 1px var(--primary-color, #03a9f4); font-weight: 600; }
  .item { border-top: 1px solid var(--divider-color, #ddd); padding: 6px 0; }
  button.head { all: unset; display: block; width: 100%; cursor: pointer; }
  button.head:focus-visible, .choice:focus-visible, .more:focus-visible, .key:focus-visible {
    outline: 2px solid var(--primary-color, #03a9f4); outline-offset: 1px; }
  .name { overflow-wrap: anywhere; }
  .head .name { font-weight: 600; }
  .meta { font-size: 0.8em; color: var(--secondary-text-color); overflow-wrap: anywhere; }
  .track { position: relative; height: 12px; margin-top: 4px; border-radius: 3px;
    background: var(--secondary-background-color, #eee); }
  .bar { position: absolute; top: 0; bottom: 0; min-width: 4px; border-radius: 3px; }
  .open { position: absolute; top: 5px; height: 0; border-top: 2px dashed; }
  .kids { padding-left: 14px; }
  .kids .item { border-top-style: dotted; }
  .kids .track { height: 8px; }
  .kids .open { top: 3px; }
  .axis { display: flex; justify-content: space-between; font-size: 0.75em;
    color: var(--secondary-text-color); }
  .more { width: 100%; margin-top: 8px; cursor: pointer; }
  svg { display: block; width: 100%; }
  .keys { display: flex; flex-direction: column; gap: 2px; margin-top: 6px; }
  .key { all: unset; display: flex; align-items: center; gap: 8px; min-height: 32px;
    cursor: pointer; font-size: 0.9em; overflow-wrap: anywhere; }
  .key svg { flex: 0 0 34px; width: 34px; }
  .key[aria-pressed="true"] { font-weight: 600; }
  @container (min-width: 620px) {
    .line { display: grid; grid-template-columns: minmax(0, 46%) 1fr; gap: 10px;
      align-items: center; }
    .line .track { margin-top: 0; }
    .axis { margin-left: calc(46% + 10px); }
  }
`;

function words(status) {
  return String(status || "unknown").replace(/_/g, " ");
}

function colour(status) {
  return Object.hasOwn(COLOURS, status) ? COLOURS[status] : OTHER_COLOUR;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function drawn(tag, attributes, text) {
  const node = document.createElementNS(SVG, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

function remembered(key) {
  try {
    return window.localStorage.getItem(key) ?? undefined;
  } catch {
    return undefined;
  }
}

function remember(key, value) {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // A browser that stores nothing just forgets the choice.
  }
}

/* What both cards do: ask Home Assistant, again every five minutes while on screen. */
class DatawatchCard extends HTMLElement {
  setConfig(config) {
    this._config = this._checked(config);
    if (this._hass) this._load();
  }

  _checked(config) {
    return { ...config };
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first && this._config) this._load();
  }

  connectedCallback() {
    if (this._timer) return;
    this._timer = window.setInterval(() => this._load(), REFRESH_MS);
    if (this._hass && this._config && this._stale) this._load();
    this._stale = false;
  }

  disconnectedCallback() {
    window.clearInterval(this._timer);
    this._timer = undefined;
    this._stale = true;
  }

  async _load() {
    if (!this._hass) return;
    // Only the newest request counts: an earlier one may answer later.
    const asked = (this._asked || 0) + 1;
    this._asked = asked;
    this._loading = true;
    if (!this._data) this._draw();
    let data;
    let problem = "";
    try {
      data = await this._hass.callWS(this._request());
    } catch (error) {
      problem =
        error?.code === "unknown_command"
          ? "Restart Home Assistant, then reload this page."
          : "datawatch cannot be read right now.";
    }
    if (asked !== this._asked) return;
    this._loading = false;
    this._problem = problem;
    if (data) this._data = data;
    this._draw();
  }

  _time(value) {
    return new Date(value).toLocaleTimeString(this._hass.locale?.language, {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  _day(value) {
    return new Date(value).toLocaleDateString(this._hass.locale?.language, {
      month: "short",
      day: "numeric",
    });
  }

  /* A fresh card body, with any problem said at the top. */
  _frame(title) {
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    const card = document.createElement("ha-card");
    card.setAttribute("header", this._config.title || title);
    const body = element("div", "body");
    card.append(body);
    this.shadowRoot.replaceChildren(element("style", "", STYLE), card);
    if (this._problem) {
      const kept = this._data ? ` Showing what was read at ${this._time(this._data.to)}.` : "";
      const note = element("p", "note problem", this._problem + kept);
      note.setAttribute("role", "alert");
      body.append(note);
    }
    if (!this._data && !this._problem) body.append(element("p", "note", "Loading…"));
    return body;
  }
}

class DatawatchGanttCard extends DatawatchCard {
  static getStubConfig() {
    return {};
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "title", selector: { text: {} } },
        { name: "project", selector: { text: {} } },
      ],
    };
  }

  _checked(config) {
    if (config.project !== undefined && typeof config.project !== "string") {
      throw new Error("project must be the name of a datawatch project");
    }
    // A card added with an earlier version may still name a sensor. It is not used.
    this._project = config.project || remembered("datawatch-gantt-project");
    const saved = remembered("datawatch-gantt-days");
    this._days = saved !== undefined && [7, 30, 90, 0].includes(Number(saved)) ? Number(saved) : 30;
    this._opened = new Set();
    this._shown = PAGE;
    this._data = undefined;
    return { ...config };
  }

  getCardSize() {
    return 8;
  }

  getGridOptions() {
    return { columns: "full", min_columns: 6 };
  }

  _request() {
    const request = { type: "datawatch/gantt", days: this._days };
    if (this._project) request.project = this._project;
    return request;
  }

  _choose(project, days) {
    this._project = project;
    this._days = days;
    if (project) remember("datawatch-gantt-project", project);
    remember("datawatch-gantt-days", String(days));
    this._opened.clear();
    this._shown = PAGE;
    this._data = undefined;
    this._problem = "";
    this._load();
  }

  _controls(body) {
    const controls = element("div", "controls");
    const select = element("select");
    select.setAttribute("aria-label", "Project");
    const current = this._data?.project || this._project;
    // Kept while another project or range is loading, so the menu stays usable.
    if (this._data?.projects) this._names = this._data.projects;
    const names = this._names || (current ? [current] : []);
    for (const name of names) {
      const option = element("option", "", name);
      option.value = name;
      option.selected = name === current;
      select.append(option);
    }
    select.addEventListener("change", () => this._choose(select.value, this._days));
    if (names.length) controls.append(select);
    for (const [days, label] of [[7, "7 days"], [30, "30 days"], [90, "90 days"], [0, "All"]]) {
      const button = element("button", "choice", label);
      button.type = "button";
      button.setAttribute("aria-pressed", String(days === this._days));
      button.addEventListener("click", () => this._choose(current, days));
      controls.append(button);
    }
    body.append(controls);
  }

  /* A bar from the first start to the latest finished work, dashed on to now if open.
     Running work is drawn the same way: only finished work makes the bar solid. */
  _track(item, state) {
    const track = element("div", "track");
    track.setAttribute("aria-hidden", "true");
    const from = Date.parse(this._data.from);
    const to = Date.parse(this._data.to);
    const at = (value) => Math.min(100, Math.max(0, ((value - from) / (to - from)) * 100));
    const start = Date.parse(item.start);
    if (!Number.isFinite(start)) return track;
    const last = Date.parse(item.last);
    const end = Number.isFinite(last) ? last : start;
    // Work that ended before this range has no bar in it.
    if (end >= from) {
      const bar = element("div", "bar");
      bar.style.left = `${at(start).toFixed(2)}%`;
      bar.style.width = `${Math.max(0, at(end) - at(start)).toFixed(2)}%`;
      bar.style.background = colour(state);
      track.append(bar);
    }
    if (item.open && at(end) < 99) {
      const rest = element("div", "open");
      rest.style.left = `${at(end).toFixed(2)}%`;
      rest.style.width = `${(100 - at(end)).toFixed(2)}%`;
      rest.style.borderTopColor = colour(state);
      track.append(rest);
    }
    return track;
  }

  _dates(item) {
    if (!item.start) return "no tasks started yet";
    const first = this._day(item.start);
    const last = this._day(item.last || item.start);
    return first === last ? first : `${first} to ${last}`;
  }

  _row(row, key) {
    const item = element("div", "item");
    const head = element("button", "head");
    head.type = "button";
    const open = this._opened.has(key);
    head.setAttribute("aria-expanded", String(open));
    const text = element("div");
    text.append(element("div", "name", `${open ? "▾" : "▸"} ${row.name}`));
    const parts = [`${row.done} of ${row.total} done`];
    for (const [status, count] of Object.entries(row.counts)) {
      parts.push(`${count} ${words(status)}`);
    }
    if (row.finished) {
      // Every automaton is done. datawatch's own word stays beside it.
      parts.push(
        row.state && row.state !== "completed" ? `done · datawatch: ${words(row.state)}` : "done"
      );
    } else if (row.state) {
      parts.push(`datawatch: ${words(row.state)}`);
    }
    text.append(element("div", "meta", parts.join(" · ")));
    const line = element("div", "line");
    const state = row.finished ? "done" : row.running ? "running" : row.state;
    line.append(text, this._track(row, state));
    head.append(line);
    head.addEventListener("click", () => {
      if (open) this._opened.delete(key);
      else this._opened.add(key);
      this._draw();
      this.shadowRoot.querySelector(`[data-key="${CSS.escape(key)}"]`)?.focus();
    });
    head.dataset.key = key;
    item.append(head);
    if (open) {
      const kids = element("div", "kids");
      for (const automaton of row.automata) {
        const kid = element("div", "item");
        const label = element("div");
        label.append(
          element("div", "name", automaton.title),
          element("div", "meta", `${words(automaton.status)} · ${this._dates(automaton)}`)
        );
        const inner = element("div", "line");
        inner.append(label, this._track(automaton, automaton.status));
        kid.append(inner);
        kids.append(kid);
      }
      if (row.more > 0) kids.append(element("p", "note", `${row.more} more are not listed.`));
      item.append(kids);
    }
    return item;
  }

  _draw() {
    const body = this._frame("datawatch Gantt");
    this._controls(body);
    const data = this._data;
    if (!data) return;
    if (!data.project) {
      body.append(element("p", "note", "datawatch has no projects."));
      return;
    }
    body.append(
      element(
        "p",
        "note",
        `${data.automations} automations · ${data.automata} automata, ${data.done} done · ` +
          `as of ${this._time(data.to)}`
      )
    );
    // Keyed by datawatch's id, so an open row stays open when the order changes.
    const rows = data.rows.map((row, index) => [row, row.id || `row-${index}`]);
    const total = rows.length + (data.loose ? 1 : 0);
    if (!total) {
      body.append(element("p", "note", "Nothing to show for this project in this range."));
    } else {
      const axis = element("div", "axis");
      axis.setAttribute("aria-hidden", "true");
      const from = Date.parse(data.from);
      const span = Date.parse(data.to) - from;
      axis.append(
        element("span", "", this._day(from)),
        element("span", "", this._day(from + span / 2)),
        element("span", "", "now")
      );
      body.append(axis);
    }
    for (const [row, key] of rows.slice(0, this._shown)) body.append(this._row(row, key));
    if (rows.length > this._shown) {
      const more = element("button", "more", `Show more (${rows.length - this._shown} left)`);
      more.type = "button";
      more.addEventListener("click", () => {
        this._shown += PAGE;
        this._draw();
      });
      body.append(more);
    }
    // Always reachable, however long the list above is.
    if (data.loose) body.append(this._row(data.loose, "loose"));
    if (data.hidden > 0) {
      const them = data.hidden === 1 ? "automation is" : "automations are";
      body.append(element("p", "note", `${data.hidden} ${them} older than this range.`));
    }
    body.append(
      element("p", "note", "Solid bar: first start to latest finished task. Dashed: still open.")
    );
  }
}

class DatawatchLanesCard extends DatawatchCard {
  static getStubConfig() {
    return {};
  }

  static getConfigForm() {
    return { schema: [{ name: "title", selector: { text: {} } }] };
  }

  getCardSize() {
    return 5;
  }

  getGridOptions() {
    return { columns: "full", min_columns: 6 };
  }

  _request() {
    return { type: "datawatch/lanes" };
  }

  connectedCallback() {
    super.connectedCallback();
    if (!this._watching && window.ResizeObserver) {
      this._watching = new ResizeObserver(() => {
        if (this._data && this.clientWidth !== this._width) this._draw();
      });
      this._watching.observe(this);
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._watching?.disconnect();
    this._watching = undefined;
  }

  _chart(active, width) {
    const height = 220;
    const left = 38;
    const right = 8;
    const top = 8;
    const bottom = 22;
    const from = Date.parse(this._data.from);
    const to = Date.parse(this._data.to);
    const x = (value) => left + ((value - from) / (to - from)) * (width - left - right);
    const y = (percent) => top + (1 - percent / 100) * (height - top - bottom);
    const chart = drawn("svg", { viewBox: `0 0 ${width} ${height}`, height, role: "img" });
    const summary = active.map(({ lane }) => `${lane.name} ${lane.average}% on average`);
    chart.setAttribute(
      "aria-label",
      active.length ? `Lane activity. ${summary.join(", ")}.` : "No lane was busy."
    );
    const text = { fill: "var(--secondary-text-color, #666)", "font-size": "11" };
    for (const percent of [0, 50, 100]) {
      chart.append(
        drawn("line", {
          x1: left, x2: width - right, y1: y(percent), y2: y(percent),
          stroke: "var(--divider-color, #ddd)",
        }),
        drawn("text", { ...text, x: left - 4, y: y(percent) + 4, "text-anchor": "end" }, `${percent}%`)
      );
    }
    for (const [part, anchor] of [[0, "start"], [0.5, "middle"], [1, "end"]]) {
      const moment = from + (to - from) * part;
      chart.append(
        drawn("text", { ...text, x: x(moment), y: height - 6, "text-anchor": anchor }, this._time(moment))
      );
    }
    for (const { lane, style } of active) {
      const faded = this._picked && this._picked !== lane.name;
      const line = drawn("polyline", {
        points: lane.points
          .map(([when, busy]) => `${x(Date.parse(when)).toFixed(1)},${y(busy).toFixed(1)}`)
          .join(" "),
        fill: "none",
        stroke: style[0],
        "stroke-dasharray": style[1],
        "stroke-width": this._picked === lane.name ? 4 : 2.5,
        opacity: faded ? 0.15 : 1,
      });
      line.dataset.lane = lane.name;
      chart.append(line);
    }
    return chart;
  }

  _draw() {
    const body = this._frame("datawatch lane activity");
    const data = this._data;
    if (!data) return;
    this._width = this.clientWidth;
    const width = Math.max(260, Math.round((this._width || 360) - 24));
    const busy = (lane) => lane.points.some(([, value]) => value > 0);
    const active = data.lanes
      .filter(busy)
      .map((lane, index) => ({ lane, style: LINES[index % LINES.length] }));
    body.append(
      element("p", "note", `How busy each lane was, last 6 hours, up to ${this._time(data.to)}.`),
      this._chart(active, width)
    );
    const keys = element("div", "keys");
    for (const { lane, style } of active) {
      const key = element("button", "key");
      key.type = "button";
      key.setAttribute("aria-pressed", String(this._picked === lane.name));
      const swatch = drawn("svg", { viewBox: "0 0 34 8", height: 8, "aria-hidden": "true" });
      swatch.append(
        drawn("line", {
          x1: 0, x2: 34, y1: 4, y2: 4, stroke: style[0],
          "stroke-width": 3, "stroke-dasharray": style[1],
        })
      );
      const latest = lane.points.length ? lane.points[lane.points.length - 1][1] : null;
      const now = latest === null ? "" : `latest ${Math.round(latest)}%, `;
      const average = lane.average === null ? "" : `average ${Math.round(lane.average)}%`;
      key.append(swatch, element("span", "", `${lane.name}: ${now}${average}`));
      key.addEventListener("click", () => {
        this._picked = this._picked === lane.name ? undefined : lane.name;
        this._draw();
      });
      keys.append(key);
    }
    body.append(keys);
    if (active.length > 1) {
      body.append(element("p", "note", "Lines can lie on top of each other. Tap a name to pick it out."));
    }
    const idle = data.lanes.filter((lane) => !busy(lane)).map((lane) => lane.name);
    if (idle.length) body.append(element("p", "note", `Idle the whole time: ${idle.join(", ")}.`));
    if (!data.lanes.length) body.append(element("p", "note", "datawatch reported no lanes."));
  }
}

function offer(type, kind, name, description) {
  if (customElements.get(type)) return;
  customElements.define(type, kind);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type,
    name,
    description,
    documentationURL: "https://github.com/dmz006/datawatch-hacs#readme",
  });
}

offer(
  "datawatch-gantt-card",
  DatawatchGanttCard,
  "datawatch Gantt (project)",
  "A project's automations and automata over time, with counts."
);
offer(
  "datawatch-lanes-card",
  DatawatchLanesCard,
  "datawatch lane activity",
  "One line for each lane: how busy it was over the last 6 hours."
);
