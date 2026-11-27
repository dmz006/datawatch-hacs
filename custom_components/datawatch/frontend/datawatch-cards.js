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

/* Every word the cards show, in each language datawatch has. A language is added here and
   nowhere else. datawatch's own names and titles are data: they are never translated. */
const TEXT = {
  en: {
    badProject: "project must be the name of a datawatch project",
    restart: "Restart Home Assistant, then reload this page.",
    unreachable: "datawatch cannot be read right now.",
    kept: (time) => `Showing what was read at ${time}.`,
    loading: "Loading…",
    listJoin: ", ",
    statuses: {},
    gantt: {
      name: "datawatch Gantt (project)",
      about: "A project's automations and automata over time, with counts.",
      title: "datawatch Gantt",
      project: "Project",
      days: (days) => `${days} days`,
      all: "All",
      notStarted: "no tasks started yet",
      span: (first, last) => `${first} to ${last}`,
      progress: (done, total) => `${done} of ${total} done`,
      count: (number, status) => `${number} ${status}`,
      done: "done",
      says: (status) => `datawatch: ${status}`,
      unlisted: (number) => `${number} more are not listed.`,
      noProjects: "datawatch has no projects.",
      summary: (automations, automata, done, time) =>
        `${automations} automations · ${automata} automata, ${done} done · as of ${time}`,
      nothing: "Nothing to show for this project in this range.",
      now: "now",
      more: (left) => `Show more (${left} left)`,
      older: (number) =>
        `${number} ${number === 1 ? "automation is" : "automations are"} older than this range.`,
      legend: "Solid bar: first start to latest finished task. Dashed: still open.",
      loose: "Automata in no automation",
    },
    lanes: {
      name: "datawatch lane activity",
      about: "One line for each lane: how busy it was over the last 6 hours.",
      title: "datawatch lane activity",
      note: (time) => `How busy each lane was, last 6 hours, up to ${time}.`,
      onAverage: (lane, percent) => `${lane} ${percent}% on average`,
      chart: (summary) => `Lane activity. ${summary}.`,
      noneBusy: "No lane was busy.",
      latest: (percent) => `latest ${percent}%`,
      average: (percent) => `average ${percent}%`,
      overlap: "Lines can lie on top of each other. Tap a name to pick it out.",
      idle: (names) => `Idle the whole time: ${names}.`,
      none: "datawatch reported no lanes.",
    },
  },
  de: {
    badProject: "project muss der Name eines datawatch-Projekts sein",
    restart: "Starte Home Assistant neu und lade dann diese Seite neu.",
    unreachable: "datawatch kann gerade nicht gelesen werden.",
    kept: (time) => `Angezeigt wird der Stand von ${time}.`,
    loading: "Wird geladen …",
    listJoin: ", ",
    statuses: {
      done: "fertig", completed: "abgeschlossen", archived: "archiviert", running: "läuft",
      planning: "in Planung", blocked: "blockiert", failed: "fehlgeschlagen",
      needs_review: "wartet auf Prüfung", revisions_asked: "Änderungen angefragt",
      held: "angehalten", paused: "pausiert", draft: "Entwurf", active: "aktiv",
      cancelled: "abgebrochen", approved: "genehmigt", unknown: "unbekannt",
    },
    gantt: {
      name: "datawatch-Gantt (Projekt)",
      about: "Die Automatisierungen und Automaten eines Projekts im Zeitverlauf, mit Zählern.",
      title: "datawatch-Gantt",
      project: "Projekt",
      days: (days) => `${days} Tage`,
      all: "Alle",
      notStarted: "noch keine Aufgabe begonnen",
      span: (first, last) => `${first} bis ${last}`,
      progress: (done, total) => `${done} von ${total} fertig`,
      count: (number, status) => `${number} × ${status}`,
      done: "fertig",
      says: (status) => `datawatch: ${status}`,
      unlisted: (number) => `${number} weitere werden nicht aufgeführt.`,
      noProjects: "datawatch hat keine Projekte.",
      summary: (automations, automata, done, time) =>
        `Automatisierungen: ${automations} · Automaten: ${automata}, fertig: ${done} · Stand ${time}`,
      nothing: "Für dieses Projekt gibt es in diesem Zeitraum nichts anzuzeigen.",
      now: "jetzt",
      more: (left) => `Mehr anzeigen (noch ${left})`,
      older: (number) => `Älter als dieser Zeitraum: ${number}.`,
      legend: "Durchgehender Balken: vom ersten Start bis zur zuletzt fertigen Aufgabe. " +
        "Gestrichelt: noch offen.",
      loose: "Automaten ohne Automatisierung",
    },
    lanes: {
      name: "datawatch-Lane-Aktivität",
      about: "Eine Linie je Lane: wie ausgelastet sie in den letzten 6 Stunden war.",
      title: "datawatch-Lane-Aktivität",
      note: (time) => `Auslastung jeder Lane in den letzten 6 Stunden, bis ${time}.`,
      onAverage: (lane, percent) => `${lane} im Mittel ${percent} %`,
      chart: (summary) => `Lane-Aktivität. ${summary}.`,
      noneBusy: "Keine Lane war ausgelastet.",
      latest: (percent) => `zuletzt ${percent} %`,
      average: (percent) => `Mittel ${percent} %`,
      overlap: "Linien können übereinander liegen. Tippe auf einen Namen, um ihn hervorzuheben.",
      idle: (names) => `Die ganze Zeit untätig: ${names}.`,
      none: "datawatch hat keine Lanes gemeldet.",
    },
  },
  es: {
    badProject: "project debe ser el nombre de un proyecto de datawatch",
    restart: "Reinicia Home Assistant y vuelve a cargar esta página.",
    unreachable: "No se puede leer datawatch ahora.",
    kept: (time) => `Se muestra lo leído a las ${time}.`,
    loading: "Cargando…",
    listJoin: ", ",
    statuses: {
      done: "hecho", completed: "completado", archived: "archivado", running: "ejecutando",
      planning: "planificando", blocked: "bloqueado", failed: "fallido",
      needs_review: "pendiente de revisión", revisions_asked: "cambios solicitados",
      held: "en espera", paused: "en pausa", draft: "borrador", active: "activo",
      cancelled: "cancelado", approved: "aprobado", unknown: "desconocido",
    },
    gantt: {
      name: "Gantt de datawatch (proyecto)",
      about: "Las automatizaciones y los autómatas de un proyecto en el tiempo, con recuentos.",
      title: "Gantt de datawatch",
      project: "Proyecto",
      days: (days) => `${days} días`,
      all: "Todo",
      notStarted: "ninguna tarea iniciada",
      span: (first, last) => `del ${first} al ${last}`,
      progress: (done, total) => `${done} de ${total} hechos`,
      count: (number, status) => `${status}: ${number}`,
      done: "hecho",
      says: (status) => `datawatch: ${status}`,
      unlisted: (number) => `No se muestran ${number} más.`,
      noProjects: "datawatch no tiene proyectos.",
      summary: (automations, automata, done, time) =>
        `Automatizaciones: ${automations} · autómatas: ${automata}, hechos: ${done} · a las ${time}`,
      nothing: "No hay nada que mostrar de este proyecto en este periodo.",
      now: "ahora",
      more: (left) => `Mostrar más (quedan ${left})`,
      older: (number) => `Automatizaciones anteriores a este periodo: ${number}.`,
      legend: "Barra continua: del primer inicio a la última tarea terminada. " +
        "Discontinua: sigue abierto.",
      loose: "Autómatas sin automatización",
    },
    lanes: {
      name: "Actividad de carriles de datawatch",
      about: "Una línea por carril: lo ocupado que estuvo en las últimas 6 horas.",
      title: "Actividad de carriles de datawatch",
      note: (time) => `Ocupación de cada carril en las últimas 6 horas, hasta las ${time}.`,
      onAverage: (lane, percent) => `${lane} ${percent} % de media`,
      chart: (summary) => `Actividad de carriles. ${summary}.`,
      noneBusy: "Ningún carril estuvo ocupado.",
      latest: (percent) => `último ${percent} %`,
      average: (percent) => `media ${percent} %`,
      overlap: "Las líneas pueden superponerse. Toca un nombre para destacarlo.",
      idle: (names) => `Inactivos todo el tiempo: ${names}.`,
      none: "datawatch no informó de ningún carril.",
    },
  },
  fr: {
    badProject: "project doit être le nom d'un projet datawatch",
    restart: "Redémarrez Home Assistant, puis rechargez cette page.",
    unreachable: "Impossible de lire datawatch pour le moment.",
    kept: (time) => `Affichage des données lues à ${time}.`,
    loading: "Chargement…",
    listJoin: ", ",
    statuses: {
      done: "terminé", completed: "terminé", archived: "archivé", running: "en cours",
      planning: "planification", blocked: "bloqué", failed: "échoué",
      needs_review: "en attente de révision", revisions_asked: "révisions demandées",
      held: "en attente", paused: "en pause", draft: "brouillon", active: "actif",
      cancelled: "annulé", approved: "approuvé", unknown: "inconnu",
    },
    gantt: {
      name: "Gantt datawatch (projet)",
      about: "Les automatisations et les automates d'un projet dans le temps, avec des totaux.",
      title: "Gantt datawatch",
      project: "Projet",
      days: (days) => `${days} jours`,
      all: "Tout",
      notStarted: "aucune tâche commencée",
      span: (first, last) => `du ${first} au ${last}`,
      progress: (done, total) => `${done} sur ${total} terminés`,
      count: (number, status) => `${status} : ${number}`,
      done: "terminé",
      says: (status) => `datawatch : ${status}`,
      unlisted: (number) => `${number} de plus ne sont pas affichés.`,
      noProjects: "datawatch n'a aucun projet.",
      summary: (automations, automata, done, time) =>
        `Automatisations : ${automations} · automates : ${automata}, terminés : ${done} · à ${time}`,
      nothing: "Rien à afficher pour ce projet sur cette période.",
      now: "maintenant",
      more: (left) => `Afficher plus (${left} restants)`,
      older: (number) => `Automatisations antérieures à cette période : ${number}.`,
      legend: "Barre pleine : du premier début à la dernière tâche terminée. " +
        "Pointillés : encore ouvert.",
      loose: "Automates hors automatisation",
    },
    lanes: {
      name: "Activité des voies datawatch",
      about: "Une ligne par voie : son occupation sur les 6 dernières heures.",
      title: "Activité des voies datawatch",
      note: (time) => `Occupation de chaque voie sur les 6 dernières heures, jusqu'à ${time}.`,
      onAverage: (lane, percent) => `${lane} ${percent} % en moyenne`,
      chart: (summary) => `Activité des voies. ${summary}.`,
      noneBusy: "Aucune voie n'a été occupée.",
      latest: (percent) => `dernière valeur ${percent} %`,
      average: (percent) => `moyenne ${percent} %`,
      overlap: "Les lignes peuvent se superposer. Touchez un nom pour le mettre en évidence.",
      idle: (names) => `Voies inactives sur toute la période : ${names}.`,
      none: "datawatch n'a signalé aucune voie.",
    },
  },
  ja: {
    badProject: "project には datawatch のプロジェクト名を指定してください",
    restart: "Home Assistant を再起動してから、このページを再読み込みしてください。",
    unreachable: "現在 datawatch を読み取れません。",
    kept: (time) => `${time} に読み取った内容を表示しています。`,
    loading: "読み込み中…",
    listJoin: "、",
    statuses: {
      done: "完了", completed: "完了", archived: "アーカイブ", running: "実行中",
      planning: "計画中", blocked: "ブロック中", failed: "失敗",
      needs_review: "レビュー待ち", revisions_asked: "修正依頼あり",
      held: "保留中", paused: "一時停止", draft: "下書き", active: "有効",
      cancelled: "キャンセル", approved: "承認済み", unknown: "不明",
    },
    gantt: {
      name: "datawatch ガント (プロジェクト)",
      about: "プロジェクトのオートメーションとオートマタの推移と件数を表示します。",
      title: "datawatch ガント",
      project: "プロジェクト",
      days: (days) => `${days} 日間`,
      all: "すべて",
      notStarted: "開始したタスクはありません",
      span: (first, last) => `${first} ～ ${last}`,
      progress: (done, total) => `${total} 件中 ${done} 件完了`,
      count: (number, status) => `${status} ${number} 件`,
      done: "完了",
      says: (status) => `datawatch: ${status}`,
      unlisted: (number) => `ほかに ${number} 件あります (表示していません)。`,
      noProjects: "datawatch にプロジェクトはありません。",
      summary: (automations, automata, done, time) =>
        `オートメーション ${automations} 件 · オートマタ ${automata} 件 (完了 ${done} 件) · ${time} 現在`,
      nothing: "この期間にこのプロジェクトで表示するものはありません。",
      now: "現在",
      more: (left) => `さらに表示 (残り ${left} 件)`,
      older: (number) => `この期間より古いオートメーション: ${number} 件`,
      legend: "実線のバー: 最初の開始から最後に完了したタスクまで。破線: 未完了。",
      loose: "オートメーションに属さないオートマタ",
    },
    lanes: {
      name: "datawatch レーンの稼働状況",
      about: "レーンごとに 1 本の線で、直近 6 時間の稼働状況を表示します。",
      title: "datawatch レーンの稼働状況",
      note: (time) => `直近 6 時間の各レーンの稼働状況 (${time} まで)。`,
      onAverage: (lane, percent) => `${lane} 平均 ${percent}%`,
      chart: (summary) => `レーンの稼働状況。${summary}。`,
      noneBusy: "稼働したレーンはありません。",
      latest: (percent) => `最新 ${percent}%`,
      average: (percent) => `平均 ${percent}%`,
      overlap: "線が重なることがあります。名前をタップすると強調表示されます。",
      idle: (names) => `期間中ずっと待機: ${names}`,
      none: "datawatch から報告されたレーンはありません。",
    },
  },
};

/* The language to show for a tag such as "de-CH". English where there is no translation. */
function textFor(tag) {
  const base = String(tag || "").toLowerCase().split(/[-_]/)[0];
  return Object.hasOwn(TEXT, base) ? TEXT[base] : TEXT.en;
}

/* For what is needed before a card has been given Home Assistant: its language, as far as
   the page knows it. */
function pageText() {
  const hass = document.querySelector("home-assistant")?.hass;
  return textFor(hass?.locale?.language || hass?.language || navigator.language);
}

function words(status, text) {
  const key = String(status || "unknown");
  // A status without a translation is shown as datawatch writes it.
  return Object.hasOwn(text.statuses, key) ? text.statuses[key] : key.replace(/_/g, " ");
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
    const before = this._words;
    this._hass = hass;
    this._words = textFor(hass.locale?.language || hass.language);
    if (first && this._config) this._load();
    // A card already showing is drawn again when the viewer changes language.
    else if (!first && this._words !== before && this.shadowRoot) this._draw();
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
      // Which text, not the words: the language can change while it is shown.
      problem = error?.code === "unknown_command" ? "restart" : "unreachable";
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
      const said = [this._words[this._problem]];
      if (this._data) said.push(this._words.kept(this._time(this._data.to)));
      const note = element("p", "note problem", said.join(" "));
      note.setAttribute("role", "alert");
      body.append(note);
    }
    if (!this._data && !this._problem) body.append(element("p", "note", this._words.loading));
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
      throw new Error(pageText().badProject);
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
    const text = this._words.gantt;
    const controls = element("div", "controls");
    const select = element("select");
    select.setAttribute("aria-label", text.project);
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
    for (const days of [7, 30, 90, 0]) {
      const button = element("button", "choice", days ? text.days(days) : text.all);
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
    const text = this._words.gantt;
    if (!item.start) return text.notStarted;
    const first = this._day(item.start);
    const last = this._day(item.last || item.start);
    return first === last ? first : text.span(first, last);
  }

  _row(row, key) {
    const said = this._words.gantt;
    // datawatch does not name the automata outside any automation: the card does.
    const name = key === "loose" ? said.loose : row.name;
    const item = element("div", "item");
    const head = element("button", "head");
    head.type = "button";
    const open = this._opened.has(key);
    head.setAttribute("aria-expanded", String(open));
    const text = element("div");
    text.append(element("div", "name", `${open ? "▾" : "▸"} ${name}`));
    const parts = [said.progress(row.done, row.total)];
    for (const [status, count] of Object.entries(row.counts)) {
      parts.push(said.count(count, words(status, this._words)));
    }
    const reported = row.state ? said.says(words(row.state, this._words)) : "";
    if (row.finished) {
      // Every automaton is done. datawatch's own word stays beside it.
      parts.push(said.done);
      if (row.state && row.state !== "completed") parts.push(reported);
    } else if (row.state) {
      parts.push(reported);
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
          element(
            "div",
            "meta",
            `${words(automaton.status, this._words)} · ${this._dates(automaton)}`
          )
        );
        const inner = element("div", "line");
        inner.append(label, this._track(automaton, automaton.status));
        kid.append(inner);
        kids.append(kid);
      }
      if (row.more > 0) kids.append(element("p", "note", said.unlisted(row.more)));
      item.append(kids);
    }
    return item;
  }

  _draw() {
    const text = this._words.gantt;
    const body = this._frame(text.title);
    this._controls(body);
    const data = this._data;
    if (!data) return;
    if (!data.project) {
      body.append(element("p", "note", text.noProjects));
      return;
    }
    body.append(
      element(
        "p",
        "note",
        text.summary(data.automations, data.automata, data.done, this._time(data.to))
      )
    );
    // Keyed by datawatch's id, so an open row stays open when the order changes.
    const rows = data.rows.map((row, index) => [row, row.id || `row-${index}`]);
    const total = rows.length + (data.loose ? 1 : 0);
    if (!total) {
      body.append(element("p", "note", text.nothing));
    } else {
      const axis = element("div", "axis");
      axis.setAttribute("aria-hidden", "true");
      const from = Date.parse(data.from);
      const span = Date.parse(data.to) - from;
      axis.append(
        element("span", "", this._day(from)),
        element("span", "", this._day(from + span / 2)),
        element("span", "", text.now)
      );
      body.append(axis);
    }
    for (const [row, key] of rows.slice(0, this._shown)) body.append(this._row(row, key));
    if (rows.length > this._shown) {
      const more = element("button", "more", text.more(rows.length - this._shown));
      more.type = "button";
      more.addEventListener("click", () => {
        this._shown += PAGE;
        this._draw();
      });
      body.append(more);
    }
    // Always reachable, however long the list above is.
    if (data.loose) body.append(this._row(data.loose, "loose"));
    if (data.hidden > 0) body.append(element("p", "note", text.older(data.hidden)));
    body.append(element("p", "note", text.legend));
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
    const said = this._words.lanes;
    const summary = active.map(({ lane }) => said.onAverage(lane.name, lane.average));
    chart.setAttribute(
      "aria-label",
      active.length ? said.chart(summary.join(this._words.listJoin)) : said.noneBusy
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
    const said = this._words.lanes;
    const body = this._frame(said.title);
    const data = this._data;
    if (!data) return;
    this._width = this.clientWidth;
    const width = Math.max(260, Math.round((this._width || 360) - 24));
    const busy = (lane) => lane.points.some(([, value]) => value > 0);
    const active = data.lanes
      .filter(busy)
      .map((lane, index) => ({ lane, style: LINES[index % LINES.length] }));
    body.append(
      element("p", "note", said.note(this._time(data.to))),
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
      const figures = [];
      if (latest !== null) figures.push(said.latest(Math.round(latest)));
      if (lane.average !== null) figures.push(said.average(Math.round(lane.average)));
      const shown = `${lane.name}: ${figures.join(this._words.listJoin)}`;
      key.append(swatch, element("span", "", shown));
      key.addEventListener("click", () => {
        this._picked = this._picked === lane.name ? undefined : lane.name;
        this._draw();
      });
      keys.append(key);
    }
    body.append(keys);
    if (active.length > 1) {
      body.append(element("p", "note", said.overlap));
    }
    const idle = data.lanes.filter((lane) => !busy(lane)).map((lane) => lane.name);
    if (idle.length) {
      body.append(element("p", "note", said.idle(idle.join(this._words.listJoin))));
    }
    if (!data.lanes.length) body.append(element("p", "note", said.none));
  }
}

function offer(type, kind, card) {
  if (customElements.get(type)) return;
  customElements.define(type, kind);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type,
    // Read when the card picker is opened, so that it is in the viewer's language.
    get name() {
      return pageText()[card].name;
    },
    get description() {
      return pageText()[card].about;
    },
    documentationURL: "https://github.com/dmz006/datawatch-hacs#readme",
  });
}

offer("datawatch-gantt-card", DatawatchGanttCard, "gantt");
offer("datawatch-lanes-card", DatawatchLanesCard, "lanes");
