"""The two cards in a real headless browser, at phone and desktop widths.

Skipped where there is no Chrome. All data is made up. Some names are written to look like
markup, to prove the cards show them as text and never run them.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fake_datawatch import made_up_chart_data

from custom_components.datawatch import charts

CARDS = Path(__file__).parents[1] / "custom_components/datawatch/frontend/datawatch-cards.js"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
HOSTILE = '<img src=x onerror="window.taken=1">'
BREAKOUT = '"><script>window.taken=2</script>'
NOW = datetime(2026, 3, 10, 12, tzinfo=UTC)

PAGE = """<!doctype html><meta charset="utf-8"><body style="margin:0"><pre id="result"></pre>
<style>ha-card { display: block; }</style>
<script type="module">
%(cards)s
const GANTT = %(gantt)s, LANES = %(lanes)s;
const out = {};
const tick = () => new Promise((done) => setTimeout(done, 20));
let asked = [], answer = () => Promise.resolve(GANTT);
const hass = { locale: { language: "en-US" },
  callWS: (request) => { asked.push(request); return answer(request); } };

function mount(type, width, config) {
  const card = document.createElement(type);
  card.style.cssText = `display:block;width:${width}px`;
  card.setConfig(config);
  document.body.append(card);
  card.hass = hass;
  return card;
}
const all = (card, query) => [...card.shadowRoot.querySelectorAll(query)];
const text = (card) => card.shadowRoot.querySelector(".body").textContent;
const button = (card, label) => all(card, "button").find((b) => b.textContent.startsWith(label));

async function run() {
  localStorage.clear();
  // An entity left over from 0.10.0 is accepted and not used.
  const old = { title: GANTT.rows[0].name, entity: "sensor.x" };
  const card = mount("datawatch-gantt-card", 360, old);
  out.loading = text(card);
  card.hass = hass;
  await tick();
  out.firstAsked = asked.slice();
  out.text = text(card);
  out.header = card.shadowRoot.querySelector("ha-card").getAttribute("header");
  out.options = all(card, "option").map((o) => [o.value, o.selected]);
  out.pressed = all(card, ".choice")
    .filter((b) => b.ariaPressed === "true").map((b) => b.textContent);
  out.rows = all(card, "button.head").length;
  out.phoneLayout = getComputedStyle(card.shadowRoot.querySelector(".line")).display;
  out.phoneOverflow = card.shadowRoot.querySelector(".body").scrollWidth;
  out.bars = all(card, "button.head .bar")
    .map((n) => [n.style.left, n.style.width, n.style.background]);
  out.dashes = all(card, "button.head .open").length;
  all(card, "button.head")[0].click();
  out.expanded = all(card, "button.head")[0].getAttribute("aria-expanded");
  out.kids = all(card, ".kids .item").map((n) => n.textContent);
  button(card, "Show more").click();
  out.afterMore = all(card, "button.head").length;
  out.stillOpen = all(card, ".kids").length;
  asked = [];
  button(card, "7 days").click();
  out.whileLoading = [text(card).includes("Loading"), all(card, "option").length];
  await tick();
  const select = card.shadowRoot.querySelector("select");
  select.value = "elm";
  select.dispatchEvent(new Event("change"));
  await tick();
  out.laterAsked = asked.slice();
  const kept = (name) => localStorage.getItem(`datawatch-gantt-${name}`);
  out.saved = [kept("project"), kept("days")];

  // A refresh that fails keeps what was shown and says so.
  answer = () => Promise.reject({ code: "unreachable" });
  await card._load();
  out.keptAfterFailure = text(card);
  answer = () => Promise.reject({ code: "unknown_command" });
  await card._load();
  out.oldServer = text(card);

  // An earlier request that answers late is ignored.
  let late;
  answer = () => new Promise((done) => (late = done));
  const slow = card._load();
  const first = late;
  answer = () => Promise.resolve({ ...GANTT, automations: 222 });
  await card._load();
  first({ ...GANTT, automations: 111 });
  await slow;
  out.afterLate = text(card);

  out.badConfig = "accepted";
  try { card.setConfig({ project: 5 }); } catch { out.badConfig = "refused"; }

  answer = () => Promise.resolve({ projects: [], project: null });
  localStorage.clear();
  const empty = mount("datawatch-gantt-card", 360, {});
  await tick();
  out.noProjects = text(empty);

  answer = () => Promise.resolve(GANTT);
  const wide = mount("datawatch-gantt-card", 900, {});
  await tick();
  out.wideLayout = getComputedStyle(wide.shadowRoot.querySelector(".line")).display;

  answer = () => Promise.resolve(LANES);
  asked = [];
  const lanes = mount("datawatch-lanes-card", 360, {});
  await tick();
  out.lanesAsked = asked.slice(0, 1);
  out.lanesText = text(lanes);
  const had = (node, name) => node.getAttribute(name);
  out.lines = all(lanes, "polyline")
    .map((n) => [had(n, "stroke-dasharray"), had(n, "opacity"), had(n, "points")]);
  const picture = lanes.shadowRoot.querySelector("svg[role=img]");
  out.chartSays = had(picture, "aria-label");
  out.chartWidth = had(picture, "viewBox");
  all(lanes, "button.key")[0].click();
  out.picked = all(lanes, "polyline").map((n) => n.getAttribute("opacity"));
  out.pressedKey = all(lanes, "button.key")[0].ariaPressed;
  out.lanesOverflow = lanes.shadowRoot.querySelector(".body").scrollWidth;
  lanes.remove();
  out.stopped = lanes._timer === undefined;

  // Each card speaks the language of the person looking at it.
  const shape = (node) => Object.entries(node).map(([key, value]) =>
    typeof value === "object" ? [key, shape(value)] : [key, typeof value]);
  out.shapes = Object.fromEntries(Object.entries(TEXT).map(([k, v]) => [k, shape(v)]));
  const english = hass.locale;
  out.languages = {};
  for (const language of ["de", "es", "fr", "ja-JP", "nl"]) {
    hass.locale = { language };
    localStorage.clear();
    answer = () => Promise.resolve(GANTT);
    const spoken = mount("datawatch-gantt-card", 360, {});
    await tick();
    all(spoken, "button.head")[0].click();
    const found = { gantt: text(spoken),
      choices: all(spoken, ".choice").map((b) => b.textContent),
      overflow: spoken.shadowRoot.querySelector(".body").scrollWidth };
    answer = () => Promise.reject({ code: "unreachable" });
    await spoken._load();
    found.problem = spoken.shadowRoot.querySelector(".problem").textContent;
    answer = () => Promise.resolve(LANES);
    const drawnLanes = mount("datawatch-lanes-card", 360, {});
    await tick();
    found.lanes = text(drawnLanes);
    found.chart = drawnLanes.shadowRoot.querySelector("svg[role=img]").getAttribute("aria-label");
    out.languages[language] = found;
  }
  // A change of language redraws a card that is already showing.
  hass.locale = english;
  answer = () => Promise.resolve(GANTT);
  const changing = mount("datawatch-gantt-card", 360, {});
  await tick();
  changing.hass = { ...hass, locale: { language: "de" } };
  out.redrawn = text(changing);
  Object.defineProperty(navigator, "language", { value: "fr-FR", configurable: true });
  out.pickerFrench = window.customCards.map((c) => [c.name, c.description]);
  Object.defineProperty(navigator, "language", { value: "en-US", configurable: true });

  out.listed = window.customCards.map((c) => c.type);
  await new Promise((done) => setTimeout(done, 300));
  out.taken = window.taken ?? null;
  out.markupMade = [card, wide, lanes].reduce((n, c) => n + all(c, "img, script").length, 0);
}
run().catch((error) => (out.crashed = String(error.stack || error)))
  .finally(() => (document.getElementById("result").textContent = JSON.stringify(out)));
</script></body>"""


def made_up() -> tuple[dict[str, Any], dict[str, Any]]:
    timeline, automations, lanes = made_up_chart_data(NOW)
    timeline["projects"][0]["automata"][0]["title"] = BREAKOUT
    automations[0]["name"] = HOSTILE
    # Enough rows that some wait behind "Show more".
    for number in range(25):
        ident = f"x{number}"
        timeline["projects"][0]["automata"].append(
            {"id": ident, "title": "Extra", "status": "blocked"}
        )
        automations.append(
            {"id": f"e{number}", "name": "Extra", "status": "draft", "members": [{"prd_id": ident}]}
        )
    found = {"projects": ["elm", "oak"], "project": "oak"}
    found.update(charts.gantt(timeline, automations, NOW, 30))
    activity = charts.lanes(lanes, NOW)
    second = {"name": HOSTILE, "average": 10.0, "points": activity["lanes"][0]["points"]}
    activity["lanes"].insert(1, second)
    return found, activity


@pytest.fixture(scope="module")
def shown(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    if CHROME is None:
        pytest.skip("no Chrome here")
    folder = tmp_path_factory.mktemp("cards")
    gantt, lanes = made_up()
    # A closing script tag inside a made-up name must not end the test page's own script.
    values = {
        "cards": CARDS.read_text(),
        "gantt": json.dumps(gantt).replace("</", "<\\/"),
        "lanes": json.dumps(lanes).replace("</", "<\\/"),
    }
    page = folder / "cards.html"
    page.write_text(PAGE % values)
    command = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run"]
    command += [f"--user-data-dir={folder / 'profile'}", "--window-size=1000,900"]
    command.append("--virtual-time-budget=8000")
    if os.environ.get("CI"):
        command.append("--no-sandbox")
    command += ["--allow-file-access-from-files", "--dump-dom", page.as_uri()]
    done = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
    found = re.search(r'<pre id="result">(.*?)</pre>', done.stdout, re.S)
    assert found and found.group(1), done.stderr[-2000:]
    result: dict[str, Any] = json.loads(html.unescape(found.group(1)))
    assert "crashed" not in result, result["crashed"]
    return result


def test_names_that_look_like_markup_are_shown_as_text_and_never_run(
    shown: dict[str, Any],
) -> None:
    assert shown["taken"] is None and shown["markupMade"] == 0
    assert HOSTILE in shown["text"] and shown["header"] == HOSTILE
    assert any(BREAKOUT in kid for kid in shown["kids"])
    assert HOSTILE in shown["lanesText"]


def test_the_gantt_asks_once_and_shows_counts_with_datawatchs_word(shown: dict[str, Any]) -> None:
    assert "Loading" in shown["loading"]
    assert shown["firstAsked"] == [{"type": "datawatch/gantt", "days": 30}]
    assert "28 automations · 32 automata, 4 done · as of " in shown["text"]
    assert "1 of 2 done · 1 running · datawatch: draft" in shown["text"]
    assert shown["options"] == [["elm", False], ["oak", True]]
    assert shown["pressed"] == ["30 days"]


def test_rows_open_to_their_automata_and_stay_open(shown: dict[str, Any]) -> None:
    assert shown["expanded"] == "true"
    assert len(shown["kids"]) == 2 and "running · " in shown["kids"][0]
    assert "completed · " in shown["kids"][1]
    # Twenty rows and the automata outside any automation, then the rest.
    assert shown["rows"] == 21 and shown["afterMore"] > 21 and shown["stillOpen"] == 1


def test_bars_show_the_work_and_dashes_show_what_is_open(shown: dict[str, Any]) -> None:
    first = shown["bars"][0]
    assert float(first[0].rstrip("%")) == pytest.approx(83.33, abs=0.05)
    # Even running work is solid only up to its latest finished task, a day before now.
    ends = float(first[0].rstrip("%")) + float(first[1].rstrip("%"))
    assert ends == pytest.approx(96.67, abs=0.05)
    assert "info-color" in first[2]
    # Open work with dates: the running row and the stray one. Undated rows have none.
    assert shown["dashes"] == 2


def test_choosing_a_range_or_project_asks_again_and_is_remembered(shown: dict[str, Any]) -> None:
    assert shown["whileLoading"] == [True, 2]
    assert shown["laterAsked"] == [
        {"type": "datawatch/gantt", "days": 7, "project": "oak"},
        {"type": "datawatch/gantt", "days": 7, "project": "elm"},
    ]
    assert shown["saved"] == ["elm", "7"]


def test_problems_are_said_and_late_replies_ignored(shown: dict[str, Any]) -> None:
    assert (
        "datawatch cannot be read right now. Showing what was read at" in shown["keptAfterFailure"]
    )
    assert "of 2 done" in shown["keptAfterFailure"]
    assert "Restart Home Assistant, then reload this page." in shown["oldServer"]
    assert "222 automations" in shown["afterLate"] and "111 automations" not in shown["afterLate"]
    assert "datawatch has no projects." in shown["noProjects"]
    assert shown["badConfig"] == "refused"


def test_a_phone_gets_a_stacked_layout_that_fits(shown: dict[str, Any]) -> None:
    assert shown["phoneLayout"] != "grid" and shown["wideLayout"] == "grid"
    assert shown["phoneOverflow"] <= 360 and shown["lanesOverflow"] <= 360


def test_the_lane_chart_draws_a_line_per_busy_lane_and_names_the_idle(
    shown: dict[str, Any],
) -> None:
    assert shown["lanesAsked"] == [{"type": "datawatch/lanes"}]
    red, other = shown["lines"]
    assert red[0] != other[0], "lines differ by pattern, not only colour"
    assert len(red[2].split()) == 2
    assert shown["chartWidth"] == "0 0 336 220"
    assert shown["chartSays"].startswith("Lane activity. red 62.5% on average")
    assert "red: latest 100%, average 63%" in shown["lanesText"]
    assert "Idle the whole time: blue." in shown["lanesText"]
    assert shown["picked"] == ["1", "0.15"] and shown["pressedKey"] == "true"
    assert shown["stopped"] is True


def test_every_language_has_every_card_text(shown: dict[str, Any]) -> None:
    shapes = shown["shapes"]
    assert sorted(shapes) == ["de", "en", "es", "fr", "ja"]
    # English shows datawatch's own status words; every translation covers the same ones.
    statuses = {language: dict(shape)["statuses"] for language, shape in shapes.items()}
    assert statuses.pop("en") == [] and statuses["de"]
    for language, shape in shapes.items():
        assert [part for part in shape if part[0] != "statuses"] == [
            part for part in shapes["en"] if part[0] != "statuses"
        ], language
    assert all(found == statuses["de"] for found in statuses.values())


@pytest.mark.parametrize(
    ("language", "gantt", "all_choice", "problem", "lanes"),
    [
        ("de", "1 von 2 fertig", "Alle", "datawatch kann gerade nicht gelesen werden.", "Lane"),
        ("es", "1 de 2 hechos", "Todo", "No se puede leer datawatch ahora.", "carril"),
        ("fr", "1 sur 2 terminés", "Tout", "Impossible de lire datawatch pour le moment.", "voie"),
        ("ja-JP", "2 件中 1 件完了", "すべて", "現在 datawatch を読み取れません。", "レーン"),
        ("nl", "1 of 2 done", "All", "datawatch cannot be read right now.", "lane"),
    ],
)
def test_the_cards_follow_the_viewers_language(
    shown: dict[str, Any], language: str, gantt: str, all_choice: str, problem: str, lanes: str
) -> None:
    found = shown["languages"][language]
    assert gantt in found["gantt"]
    assert found["choices"][-1] == all_choice
    assert problem in found["problem"]
    assert lanes in found["lanes"] and found["chart"]
    assert found["overflow"] <= 360
    # datawatch's names are data and are never translated.
    assert HOSTILE in found["gantt"] and HOSTILE in found["lanes"]
    # Server-side English never reaches a translated card.
    if language != "nl":
        assert "Automata in no automation" not in found["gantt"]
        assert "running" not in found["gantt"]


def test_a_change_of_language_redraws_the_card(shown: dict[str, Any]) -> None:
    assert "1 von 2 fertig" in shown["redrawn"]


def test_the_card_picker_follows_the_language(shown: dict[str, Any]) -> None:
    assert shown["pickerFrench"][0][0] == "Gantt datawatch (projet)"


def test_both_cards_are_in_the_picker(shown: dict[str, Any]) -> None:
    assert shown["listed"] == ["datawatch-gantt-card", "datawatch-lanes-card"]
