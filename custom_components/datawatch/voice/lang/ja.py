"""Japanese: what datawatch mode listens for. What it says is in ja_texts.py.

Japanese has no spaces between words, and speech-to-text may or may not add some, so they
are ignored. Patterns that match what was heard allow for them with \\s*.
"""

from __future__ import annotations

import re

from ..grammar import Grammar, Language
from .ja_texts import TEXTS

# The first wording of each command is the one the replies quote.
_PHRASES: dict[str, tuple[str, ...]] = {
    "STATUS": ("ステータス", "状況", "状況を教えて", "ステータスを教えて"),
    "DETAIL": ("詳しく", "詳細", "もっと詳しく", "詳しく教えて"),
    "LIST_PROJECTS": ("プロジェクト一覧", "プロジェクトの一覧", "プロジェクト"),
    "MORE": ("もっと", "次", "続き", "次へ", "続けて"),
    "WHERE": ("今どこ", "いまどこ", "フォーカスは", "フォーカスは何"),
    "UNSET": ("フォーカス解除", "フォーカスを解除", "フォーカスを解除して"),
    "REPEAT": ("もう一度", "もう一回", "繰り返して", "もう一度言って"),
    "HELP": ("ヘルプ", "何が言える", "何と言えばいい"),
    "EXIT": ("終了", "ストップ", "終わり", "終了して", "datawatchを終了"),
    "QUESTIONS": (
        "質問",
        "質問を読んで",
        "質問一覧",
        "質問はある",
        "未解決の質問",
        "最初の質問",
    ),
    "NEXT_QUESTION": ("次の質問", "スキップ", "この質問をスキップ"),
    "OWN_WORDS": ("自分の言葉で回答", "自分の言葉で答える"),
    # Only these send an answer, so there is no shorter form such as "はい".
    "CONFIRM": ("回答を確定", "回答確定", "回答を確定して", "解答を確定"),
    # Like the answer, each of these sends one kind of thing and nothing else.
    "CONFIRM_AUTOMATON": (
        "オートメーションを確定",
        "オートメーション確定",
        "オートマトンを確定",
    ),
    "CONFIRM_BUG": ("バグを確定", "バグ確定"),
    "CONFIRM_SEND": ("送信を確定", "送信確定"),
    "CANCEL": ("キャンセル", "取り消し", "取り消して", "回答をキャンセル"),
    "ATTENTION": ("要対応", "対応が必要なもの", "何に対応が必要"),
    "PLANS": ("プラン", "プラン一覧", "プランはいくつ"),
    "OVERVIEW": ("概要", "プロジェクトの概要"),
    "WHATS_NEXT": ("次の予定", "次は何", "次にやること"),
    "AUTOMATIONS": ("オートメーション", "オートメーション一覧"),
    "RUNNING": ("実行中", "何が実行中", "実行中のオートマタ"),
    "HELD": ("保留項目", "保留中", "何が保留中"),
    "WHY": (
        "なぜ",
        "どうして",
        "なぜブロックされているの",
        "なぜ保留なの",
        "なぜ失敗したの",
        "なぜ止まっているの",
    ),
    "TASKS": ("タスク", "タスク一覧", "タスクを見せて"),
    "PROGRESS": ("進捗", "どこまで進んだ", "進み具合"),
    "SESSIONS": ("セッション", "セッション一覧"),
    "WAITING": ("待機中のセッション", "入力待ちのセッション", "何が待っている"),
    "RUNNING_SESSIONS": ("実行中のセッション", "どのセッションが実行中"),
    "FAILED_SESSIONS": ("失敗したセッション", "どのセッションが失敗した"),
    "FINISHED": ("完了した作業", "何が完了した", "最近完了したもの"),
    "RESULTS": ("結果", "結果を教えて", "何が変わった"),
    "REPORTS": ("レポート", "レポート一覧"),
    "SET_THIS": ("それに設定", "それを設定", "それにフォーカス"),
    "GO_BACK": ("戻る", "戻って", "一つ戻る"),
    "ALL_QUESTIONS": ("すべての質問", "全部の質問", "全ての質問"),
    "ITS_QUESTIONS": ("関連する質問", "それの質問", "それに関する質問"),
    "HISTORY": ("履歴", "何があった", "履歴を見せて"),
    "AUTOMATA": ("オートマタ", "オートマタ一覧", "オートマトン一覧"),
    "ALERTS": ("アラート", "アラート一覧", "アラートはある", "未読アラート"),
    "ORDER": ("並び順", "今の並び順", "並び順は"),
    "ORDER_NAME": ("名前順", "名前順にして", "名前で並べ替え"),
    "ORDER_RECENT": ("新しい順", "新しい順にして", "新しい順に並べ替え"),
}


def _numbers() -> dict[str, int]:
    """One to fifty-nine, in characters and as read aloud, and the "-tsu" counters."""
    characters = "一二三四五六七八九"
    readings = ("いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう")
    found: dict[str, int] = {}
    for units, ten in ((characters, "十"), (readings, "じゅう")):
        found |= {word: value for value, word in enumerate(units, start=1)}
        for tens in range(1, 6):
            opening = ten if tens == 1 else f"{units[tens - 1]}{ten}"
            found[opening] = tens * 10
            found |= {f"{opening}{unit}": tens * 10 + n for n, unit in enumerate(units, start=1)}
    counters = ("ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ")
    found |= {word: value for value, word in enumerate(counters, start=1)}
    found |= {f"{word}つ": value for value, word in enumerate(characters, start=1)}
    return found | {"し": 4, "しち": 7, "く": 9}


_NUMBERS = _numbers()
# Digits or a number word, longest first so that "にじゅう" is not read as "に".
_NUMBER = r"(?:\d+|" + "|".join(sorted(_NUMBERS, key=len, reverse=True)) + r")"
_AFTER = r"(?:番目|番|ばんめ|ばん)?"
# A numbered line or a name, such as "2番" or "roof".
_LINE = r"(?:番号)?(?P<chosen>.+?)" + _AFTER
_ASKING = r"(?:の|ですか|なの|んですか)?"
_STUCK = (
    r"(?:ブロックされている|ブロックされてる|ブロック中|保留中|保留|失敗した"
    r"|止まっている|止まってる)?"
)
# What may follow the words that open an action.
_DOING = r"(?:して(?:ください|下さい)?|する|ください)?(?:\s*お願いします)?"


def _starting(opening: str) -> re.Pattern[str]:
    """Words that open an action, matched on what speech-to-text wrote."""
    return re.compile(rf"^\W*(?:{opening}){_DOING}[\s、。,，:：.\-]*", re.IGNORECASE)


def _of_line(ending: str) -> re.Pattern[str]:
    """A question about one line, such as "2のタスク"."""
    return re.compile(_LINE + rf"の{ending}(?:を(?:見せて|教えて|読んで))?")


# The punctuation the sentences are put together with, as Japanese writes it.
_PUNCTUATION = (
    (re.compile(r"\.(?=\s|$)"), "。"),
    (re.compile(r"[,:]\s"), "、"),
    (re.compile(r"\s*([。？！、])\s*"), r"\1"),
    (re.compile(r"。{2,}"), "。"),
    (re.compile(r"、+(?=[。？！])"), ""),
    (re.compile(r"(?<=[。？！])[。、]"), ""),
)


def _tidy(reply: str) -> str:
    for pattern, replacement in _PUNCTUATION:
        reply = pattern.sub(replacement, reply)
    return reply


GRAMMAR = Grammar(
    phrases=_PHRASES,
    numbers=_NUMBERS,
    apostrophes="'\N{RIGHT SINGLE QUOTATION MARK}",
    polite=re.compile(r"(?:をお願いします|お願いします|おねがいします|ください|下さい)$"),
    number=re.compile(rf"(?:番号|ナンバー)?(?P<chosen>{_NUMBER}){_AFTER}"),
    own_words=re.compile(
        r"^\W*(?:(?:私|わたし|僕)\s*の\s*)?(?:回答|解答|答え|返事)\s*は[\s、。,，:：.\-]*"
    ),
    actions=(
        (
            "ADD_AUTOMATON",
            _starting(r"(?:新しい\s*)?(?:オートメーション|オートマトン)\s*(?:を\s*)?(?:追加|作成)"),
        ),
        ("ADD_BUG", _starting(r"(?:新しい\s*)?(?:バグ|不具合)\s*(?:を\s*)?(?:追加|報告)")),
        (
            "SEND_SESSION",
            _starting(r"(?:セッション\s*(?:に|へ)|コマンド\s*を)\s*(?:送信|送って)"),
        ),
    ),
    about_one=(
        ("WHY", re.compile(_LINE + rf"(?:は|が)?(?:なぜ|どうして){_STUCK}{_ASKING}")),
        ("WHY", re.compile(r"(?:なぜ|どうして)" + _LINE + rf"(?:(?:は|が){_STUCK}{_ASKING})?")),
        ("TASKS", _of_line("タスク(?:一覧)?")),
        ("PROGRESS", _of_line("進捗")),
        ("RESULTS", _of_line("結果")),
        ("ITS_QUESTIONS", _of_line("質問")),
        ("HISTORY", _of_line("履歴")),
    ),
    about=re.compile(_LINE + r"について(?:詳しく)?(?:教えて)?"),
    choose=re.compile(
        r"(?:選択肢|オプション)(?:の)?(?:番号)?(.+?)"
        + _AFTER
        + r"(?:を?(?:選ぶ|選んで|選択して|選択)|にする)?"
        + r"|(.+?)"
        + _AFTER
        + r"を(?:選ぶ|選んで|選択して|選択)"
    ),
    set_command=re.compile(
        r"(?P<chosen>.+?)に(?:設定して|設定する|設定|フォーカスして|フォーカス)"
    ),
    set_item=re.compile(
        r"(?:フォーカスを)?(?P<kind>プラン|オートメーション|オートマトン|タスク|セッション)"
        r"(?:の)?(?P<chosen>.+)"
    ),
    item_kinds={
        "プラン": "plan",
        "オートメーション": "automation",
        "オートマトン": "automaton",
        "タスク": "task",
        "セッション": "session",
    },
    set_filler=re.compile(r"^(?:フォーカスを)?"),
    set_project=re.compile(r"プロジェクト(?:の)?(?P<chosen>.+)"),
    report_filler=(
        re.compile(r"(?:を)?(?:読んで|読み上げて|実行して|実行|教えて|聞かせて)$"),
        re.compile(r"^(?:私の|わたしの|僕の)"),
        re.compile(r"(?:の)?(?:レポート|報告)$"),
    ),
    entry_sentences=(
        "(datawatch|data watch|データウォッチ)[を](開いて|開始して|起動して)",
        "(datawatch|data watch|データウォッチ)",
    ),
    entry_examples=("datawatchを開いて", "データウォッチを開いて", "datawatch"),
    entry_names=(
        "datawatch",
        "データウォッチ",
        "datawatchを開いて",
        "データウォッチを開いて",
        "datawatchを開始して",
        "datawatchを起動して",
    ),
    spaced=False,
)

LANGUAGE = Language(code="ja", grammar=GRAMMAR, texts=TEXTS, tidy=_tidy)
