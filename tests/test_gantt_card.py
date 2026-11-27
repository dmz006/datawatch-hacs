"""The Gantt card in a real headless browser. Skipped where there is no Chrome.

All data is made up. Some titles are written to look like markup, to prove the card shows
them as text and never runs them.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

CARD = Path(__file__).parents[1] / "custom_components/datawatch/frontend/datawatch-cards.js"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
HOSTILE = '<img src=x onerror="window.taken=1">'
BREAKOUT = '"><script>window.taken=2</script>'

PAGE = """<!doctype html><meta charset="utf-8"><body><pre id="result"></pre>
<script type="module">
%(card)s
const out = {};
const HOSTILE = %(hostile)s, BREAKOUT = %(breakout)s;
const bar = (title, start, end, extra) =>
  ({ title, start: `2026-03-10T${start}:00+00:00`, end: `2026-03-10T${end}:00+00:00`,
     live: false, ...extra });
const data = {
  from: "2026-03-10T06:00:00+00:00", to: "2026-03-10T12:00:00+00:00", not_read: 2,
  lanes: [{ name: HOSTILE, bars: [bar(BREAKOUT, "09:00", "12:00", { live: true })] },
          { name: "blue", bars: [] }],
  work: [{ title: HOSTILE, status: "running", bars: [
    bar(BREAKOUT, "06:00", "07:30", { status: "completed" }),
    bar("Odd", "07:00", "08:00", { status: "constructor" }),
    bar("No time", "x", "y", { status: "failed" })] }],
};
const card = document.createElement("datawatch-gantt-card");
card.setConfig({ title: HOSTILE });
document.body.append(card);
const states = (state) => ({ states: state ? { [E]: state } : {}, locale: { language: "en-US" } });
const E = "sensor.datawatch_dashboard_data_live_work";
const root = () => card.shadowRoot;
const text = () => root().querySelector(".body").textContent;
card.hass = states(undefined);
out.missing = text();
card.hass = states({ state: "unavailable", attributes: {} });
out.unavailable = text();
card.hass = states({ state: "2", attributes: { data: { from: "x", to: "y" } } });
out.unreadable = text();
const good = { state: "2", attributes: { data } };
card.hass = states(good);
const first = root().querySelector("ha-card");
card.hass = states(good);
out.keptWhenUnchanged = first === root().querySelector("ha-card");
out.text = text();
out.header = root().querySelector("ha-card").getAttribute("header");
out.bars = [...root().querySelectorAll(".bar")].map((n) => ({
  left: n.style.left, width: n.style.width, live: n.classList.contains("live"),
  said: n.getAttribute("aria-label"), colour: n.style.background, focusable: n.tabIndex === 0 }));
card.hass = states({ state: "1", attributes: { data: { ...data, not_read: 1 } } });
out.one = text();
card.hass = states({ state: "0", attributes: { data: { ...data, work: [], not_read: 0 } } });
out.quiet = text();
out.badConfig = "accepted";
try { card.setConfig({ entity: 5 }); } catch { out.badConfig = "refused"; }
out.listed = window.customCards.map((c) => c.type);
out.form = customElements.get("datawatch-gantt-card").getConfigForm().schema.map((f) => f.name);
setTimeout(() => {
  out.taken = window.taken ?? null;
  out.markupMade = root().querySelectorAll("img, script").length;
  document.getElementById("result").textContent = JSON.stringify(out);
}, 500);
</script></body>"""


@pytest.fixture(scope="module")
def shown(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    if CHROME is None:
        pytest.skip("no Chrome here")
    folder = tmp_path_factory.mktemp("card")
    page = folder / "card.html"
    values = {"hostile": json.dumps(HOSTILE), "breakout": json.dumps(BREAKOUT)}
    # A closing script tag inside the made-up titles must not end the test page's script.
    safe = {key: value.replace("</", "<\\/") for key, value in values.items()}
    page.write_text(PAGE % {"card": CARD.read_text(), **safe})
    command = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run"]
    command += [f"--user-data-dir={folder / 'profile'}", "--virtual-time-budget=5000"]
    if os.environ.get("CI"):
        command.append("--no-sandbox")
    command += ["--dump-dom", page.as_uri()]
    done = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
    found = re.search(r'<pre id="result">(.*?)</pre>', done.stdout, re.S)
    assert found and found.group(1), done.stderr[-2000:]
    result: dict[str, Any] = json.loads(html.unescape(found.group(1)))
    return result


def test_titles_that_look_like_markup_are_shown_as_text_and_never_run(
    shown: dict[str, Any],
) -> None:
    assert shown["taken"] is None and shown["markupMade"] == 0
    assert HOSTILE in shown["text"] and shown["header"] == HOSTILE
    assert any(BREAKOUT in bar["said"] for bar in shown["bars"])


def test_bars_sit_at_their_times_and_say_them(shown: dict[str, Any]) -> None:
    lane, done, odd = shown["bars"]
    assert (lane["left"], lane["width"], lane["live"]) == ("50%", "50%", True)
    assert "still running" in lane["said"]
    assert (done["left"], done["width"], done["live"]) == ("0%", "25%", False)
    assert "completed, " in done["said"] and " to " in done["said"]
    assert "success-color" in done["colour"]
    # A status that is also the name of something built in gets the ordinary colour.
    assert "primary-color" in odd["colour"]
    assert all(bar["focusable"] for bar in shown["bars"])


def test_the_card_says_what_is_idle_hidden_or_wrong(shown: dict[str, Any]) -> None:
    assert "blue (idle)" in shown["text"]
    assert "2 more unfinished automata are not shown." in shown["text"]
    assert "1 more unfinished automaton is not shown." in shown["one"]
    assert "(running)" in shown["text"]
    assert "enable the sensor" in shown["missing"]
    assert shown["unavailable"] == shown["unreadable"] == "datawatch cannot be read right now."
    assert "No task of running, blocked or planning work ran" in shown["quiet"]


def test_the_card_is_in_the_picker_and_checks_its_settings(shown: dict[str, Any]) -> None:
    assert shown["listed"] == ["datawatch-gantt-card"]
    assert shown["form"] == ["title", "entity"]
    assert shown["badConfig"] == "refused"
    assert shown["keptWhenUnchanged"] is True
