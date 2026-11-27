"""Japanese: what datawatch mode says, keyed by the English sentence."""

TEXTS: dict[str, str] = {
    ", ": "、",
    "A warning": "警告",
    "Added a draft automaton to project {project}, but I could not name it, so it may show "
    "as untitled. Do not add it again.": (
        "プロジェクト{project}に下書きのオートマトンを追加しましたが、名前を付けられませんでし"
        "た。無題と表示されることがあります。もう一度追加しないでください。"
    ),
    "Added a draft automaton to project {project}, named {title}. I did not ask datawatch "
    "to plan or start it.": (
        "プロジェクト{project}に、{title}という名前の下書きのオートマトンを追加しました。"
        "datawatchに計画や開始は依頼していません。"
    ),
    "All projects": "すべてのプロジェクト",
    "Also {number} archived.": "ほかにアーカイブ済みが{number}件あります。",
    "An alert": "アラート",
    "An error": "エラー",
    "Answer sent. Say next question.": "回答を送信しました。次の質問、と言ってください。",
    "Automation {line}": "オートメーション {line}",
    "Automaton {title}: {state}.": "オートマトン {title}: {state}。",
    "Back.": "戻りました。",
    "Bug reported for project {project}.": "プロジェクト{project}のバグを報告しました。",
    "Cancelled. Nothing was sent.": "キャンセルしました。何も送信していません。",
    "Choose a session first: say sessions, then its number.": (
        "先にセッションを選んでください。セッション、と言ってから番号を言ってください。"
    ),
    "Choose something first, then say history.": "先に何かを選んでから、履歴、と言ってください。",
    "Choose something first, then say its questions. Or say questions.": (
        "先に何かを選んでから、関連する質問、と言ってください。または、質問、と言ってください。"
    ),
    "Choose something first: say its number, then set it.": (
        "先に何かを選んでください。番号を言ってから、それに設定、と言ってください。"
    ),
    "Closing datawatch.": "datawatchを終了します。",
    "Datawatch activated.": "datawatchを開始しました。",
    "Datawatch mode works from a voice device.": "datawatchモードは音声デバイスで使えます。",
    "Elsewhere: {counts}.": "そのほか: {counts}。",
    "Focus cleared. Now showing everything.": "フォーカスを解除しました。すべてを表示します。",
    "Focus: {focus}.": "フォーカス: {focus}。",
    "For a full reason say why and its number.": (
        "理由をすべて聞くには、なぜ、と番号を言ってください。"
    ),
    "For the task {title}: {reason}": "タスク{title}について: {reason}",
    "For the {item}.": "{item}について。",
    "For the {item}: {number} unread alert, newest first.": (
        "{item}の未読アラートは{number}件です。新しい順です。"
    ),
    "For the {item}: {number} unread alerts, newest first.": (
        "{item}の未読アラートは{number}件です。新しい順です。"
    ),
    "Go ahead. Describe the bug, or cancel.": (
        "どうぞ。バグの内容を話すか、キャンセル、と言ってください。"
    ),
    "Go ahead. Say what the automation should do, or cancel.": (
        "どうぞ。オートメーションにしてほしいことを話すか、キャンセル、と言ってください。"
    ),
    "Go ahead. Say what to send, or cancel.": (
        "どうぞ。送る内容を話すか、キャンセル、と言ってください。"
    ),
    "Go ahead. Say your answer, or cancel.": "どうぞ。回答を話すか、キャンセル、と言ってください。",
    "I can read the first {number}.": "最初の{number}件を読み上げられます。",
    "I can't reach datawatch, so nothing was sent. Say it again.": (
        "datawatchに接続できないため、何も送信していません。もう一度言ってください。"
    ),
    "I can't reach datawatch, so nothing was sent. Say my answer or option again.": (
        "datawatchに接続できないため、何も送信していません。自分の言葉で回答、または選択肢を、"
        "もう一度言ってください。"
    ),
    "I can't reach datawatch. Try again, or say stop.": (
        "datawatchに接続できません。もう一度試すか、終了、と言ってください。"
    ),
    "I can't read a session's history by voice. Open it in datawatch.": (
        "セッションの履歴は音声で読み上げられません。datawatchで開いてください。"
    ),
    "I couldn't find a plan matching {name}.": "{name}に一致するプランは見つかりませんでした。",
    "I couldn't find a project matching {name}. Say list projects.": (
        "{name}に一致するプロジェクトは見つかりませんでした。プロジェクト一覧、と言ってください。"
    ),
    "I couldn't find a session matching {name}.": (
        "{name}に一致するセッションは見つかりませんでした。"
    ),
    "I couldn't find a task matching {name}.": "{name}に一致するタスクは見つかりませんでした。",
    "I couldn't find an automation matching {name}.": (
        "{name}に一致するオートメーションは見つかりませんでした。"
    ),
    "I couldn't find an automaton matching {name}.": (
        "{name}に一致するオートマトンは見つかりませんでした。"
    ),
    "I couldn't find {name} among the automata that need attention, are running, are on "
    "hold or finished recently.": (
        "対応が必要、実行中、保留中、または最近完了したオートマタの中に、{name}は見つかりません"
        "でした。"
    ),
    "I did not keep your words.": "お話しの内容は保存していません。",
    "I didn't understand three times. Closing datawatch.": (
        "3回続けて聞き取れませんでした。datawatchを終了します。"
    ),
    "I don't know whether it was sent. Check datawatch before saying it again.": (
        "送信できたかどうか分かりません。もう一度言う前にdatawatchで確認してください。"
    ),
    "I don't know whether the answer was sent. Say questions to check.": (
        "回答を送信できたかどうか分かりません。質問、と言って確認してください。"
    ),
    "I found {number} matches.": "{number}件が一致しました。",
    "I found {number} matches. Say set and a number.": (
        "{number}件が一致しました。番号と、に設定、を言ってください。"
    ),
    "I found {number} matching {name}. Say a number.": (
        "{name}に一致するものが{number}件ありました。番号を言ってください。"
    ),
    "I haven't read a number {number}. Say more, or pick a number you heard.": (
        "{number}番はまだ読み上げていません。もっと、と言うか、聞いた番号を選んでください。"
    ),
    "I haven't read a number {number}. Say more, or pick one you heard.": (
        "{number}番はまだ読み上げていません。もっと、と言うか、聞いたものを選んでください。"
    ),
    "I haven't read a question yet. Say questions.": (
        "まだ質問を読み上げていません。質問、と言ってください。"
    ),
    "In project {project}: {lead}{counts} across all projects.": (
        "プロジェクト{project}: {lead}すべてのプロジェクトで{counts}。"
    ),
    "In project {project}: {lead}{counts}.": "プロジェクト{project}: {lead}{counts}。",
    "In the automaton {title}.": "オートマトン{title}内です。",
    "It changed {files} in {packages}, and added {tests}.": (
        "{packages}の{files}を変更し、{tests}を追加しました。"
    ),
    "It has no tasks.": "タスクはありません。",
    "It has {number} member.": "メンバーは{number}件です。",
    "It has {number} members.": "メンバーは{number}件です。",
    "It is blocking work.": "作業を止めています。",
    "It is on hold: {reason}": "保留中です: {reason}",
    "It uses {backend}.": "{backend}を使っています。",
    "Its description": "説明",
    "Its goal": "目標",
    "Its goal: {goal}.": "目標: {goal}。",
    "Last activity {when}.": "最後の活動は{when}です。",
    "New work is paused.": "新しい作業は一時停止中です。",
    "Next: {title}, in the plan {plan}.": "次は{title}、プラン{plan}の中です。",
    "Next: {title}.": "次は{title}です。",
    "No automata are running across all projects.": (
        "どのプロジェクトでも、実行中のオートマタはありません。"
    ),
    "No automata are running in project {project}.": (
        "プロジェクト{project}に実行中のオートマタはありません。"
    ),
    "No automata have completed across all projects.": (
        "どのプロジェクトでも、完了したオートマタはありません。"
    ),
    "No automata have completed in project {project}.": (
        "プロジェクト{project}で完了したオートマタはありません。"
    ),
    "No focus. Showing everything.": "フォーカスはありません。すべてを表示しています。",
    "No reason given": "理由の記載はありません",
    "Not sent yet.": "まだ送信していません。",
    "Not sent yet. Say confirm answer, or cancel.": (
        "まだ送信していません。回答を確定、またはキャンセル、と言ってください。"
    ),
    "Not sent yet. Say confirm automation, or cancel.": (
        "まだ送信していません。オートメーションを確定、またはキャンセル、と言ってください。"
    ),
    "Not sent yet. Say confirm bug, or cancel.": (
        "まだ送信していません。バグを確定、またはキャンセル、と言ってください。"
    ),
    "Not sent yet. Say confirm send, or cancel.": (
        "まだ送信していません。送信を確定、またはキャンセル、と言ってください。"
    ),
    "Not sent yet. This is {target}. Your words: {words}": (
        "まだ送信していません。内容は{target}です。あなたの言葉: {words}"
    ),
    "Nothing is marked as next in any project.": (
        "どのプロジェクトにも、次の項目は指定されていません。"
    ),
    "Nothing is marked as next.": "次の項目は指定されていません。",
    "Nothing is on hold.": "保留中のものはありません。",
    "Nothing needs your attention.": "対応が必要なものはありません。",
    "Number {number} is the {item}. Say set {number}.": (
        "{number}番は{item}です。{number}に設定、と言ってください。"
    ),
    "Option {number}: {label}": "選択肢{number}: {label}",
    "Order: by name, for sessions, automations and running work. Say the list again to "
    "hear it that way. Say most recent first to switch.": (
        "並び順は名前順です。対象はセッション、オートメーション、実行中の作業です。もう一度一覧"
        "を聞くと、この順になります。切り替えるには、新しい順、と言ってください。"
    ),
    "Order: most recent first, for sessions, automations and running work. Say the list "
    "again to hear it that way. Say sort by name to switch.": (
        "並び順は新しい順です。対象はセッション、オートメーション、実行中の作業です。もう一度一"
        "覧を聞くと、この順になります。切り替えるには、名前順、と言ってください。"
    ),
    "Plan {line}.": "プラン {line}。",
    "Plan {number}, {line}.": "プラン{number}、{line}。",
    "Project {project}": "プロジェクト{project}",
    "Project {project} has no current plans.": "プロジェクト{project}に現在のプランはありません。",
    "Project {project} has {number} current plan.": (
        "プロジェクト{project}の現在のプランは{number}件です。"
    ),
    "Project {project} has {number} current plans.": (
        "プロジェクト{project}の現在のプランは{number}件です。"
    ),
    "Project {project} no longer exists, so the focus is cleared.": (
        "プロジェクト{project}はなくなったため、フォーカスを解除しました。"
    ),
    "Project {project}.": "プロジェクト{project}。",
    "Project {project}. {next}": "プロジェクト{project}。{next}",
    "Project {project}: {plans}.": "プロジェクト{project}: {plans}。",
    "Question {number} of {total}, from datawatch.": (
        "datawatchからの質問です。{total}件中{number}件目。"
    ),
    "Question {number} of {total}, from the supervisor.": (
        "スーパーバイザーからの質問です。{total}件中{number}件目。"
    ),
    "Reason: {reason}": "理由: {reason}",
    "Say attention, running or held items, then a number.": (
        "要対応、実行中、または保留項目、と言ってから番号を言ってください。"
    ),
    "Say confirm answer to send it, or cancel.": (
        "送信するには回答を確定、やめるにはキャンセル、と言ってください。"
    ),
    "Say confirm automation to send it, or cancel.": (
        "送信するにはオートメーションを確定、やめるにはキャンセル、と言ってください。"
    ),
    "Say confirm bug to send it, or cancel.": (
        "送信するにはバグを確定、やめるにはキャンセル、と言ってください。"
    ),
    "Say confirm send to send it, or cancel.": (
        "送信するには送信を確定、やめるにはキャンセル、と言ってください。"
    ),
    "Say more detail for more.": "続きは、詳しく、と言ってください。",
    "Say more, or set and a number or name.": (
        "もっと、と言うか、番号か名前と、に設定、を言ってください。"
    ),
    "Say more, or which number?": "もっと、と言いますか。それとも何番ですか。",
    "Say more.": "もっと、と言ってください。",
    "Say option and a number, my answer, more detail, or next question.": (
        "選択肢と番号、自分の言葉で回答、詳しく、または次の質問、と言ってください。"
    ),
    "Say plans or automations, choose one, then say automata.": (
        "プラン、またはオートメーション、と言って一つ選んでから、オートマタ、と言ってください。"
    ),
    "Say why, or tasks.": "なぜ、またはタスク、と言ってください。",
    "Sending to a session is not turned on yet. It is waiting for datawatch's access "
    "controls. Nothing was sent.": (
        "セッションへの送信はまだ有効になっていません。datawatchのアクセス制御を待っています。"
        "何も送信していません。"
    ),
    "Sent to the {item}.": "{item}に送信しました。",
    "Session named {name}: {state}.": "{name}という名前のセッション: {state}。",
    "Sessions, automations and running work are listed by name. Say most recent first to switch.": (
        "セッション、オートメーション、実行中の作業は名前順です。切り替えるには、新しい順、と言"
        "ってください。"
    ),
    "Sessions, automations and running work are listed most recent first. Say sort by name "
    "to switch.": (
        "セッション、オートメーション、実行中の作業は新しい順です。切り替えるには、名前順、と言"
        "ってください。"
    ),
    "Set a plan or an automaton first, then set the task.": (
        "先にプランかオートマトンを設定してから、タスクを設定してください。"
    ),
    "Set a project first: say list projects, or set and a project name.": (
        "先にプロジェクトを設定してください。プロジェクト一覧、と言うか、プロジェクト名と、に設"
        "定、を言ってください。"
    ),
    "Something went wrong in datawatch mode. Closing datawatch.": (
        "datawatchモードで問題が起きました。datawatchを終了します。"
    ),
    "Sorry, I didn't get that. Say help.": (
        "すみません、分かりませんでした。ヘルプ、と言ってください。"
    ),
    "Still there?": "まだいますか。",
    "Task {number}, {title}: {state}.": "タスク{number}、{title}: {state}。",
    "Task {title}: {state}.": "タスク{title}: {state}。",
    "Tasks are listed for a plan or an automaton.": (
        "タスクの一覧は、プランかオートマトンで使えます。"
    ),
    "That is a session. I can only say what is in the list and its details.": (
        "それはセッションです。一覧とその詳細にある内容だけを読み上げられます。"
    ),
    "That is all.": "以上です。",
    "That is the end of the list.": "一覧はここまでです。",
    "That is the last question.": "これが最後の質問です。",
    "That question was already answered or withdrawn. Nothing was sent.": (
        "その質問はすでに回答されたか取り下げられています。何も送信していません。"
    ),
    "That session is {state} now, not waiting for input. Nothing was sent.": (
        "そのセッションは今は{state}で、入力待ちではありません。何も送信していません。"
    ),
    "The asker recommends option {number}.": "質問者のおすすめは選択肢{number}です。",
    "The automation {title}": "オートメーション{title}",
    "The automaton {title}": "オートマトン{title}",
    "The datawatch certificate has changed. Check it in Home Assistant. Closing datawatch.": (
        "datawatchの証明書が変わりました。Home Assistantで確認してください。datawatchを終了します。"
    ),
    "The most recently updated come first, which may not be the order they finished.": (
        "最近更新されたものから順に読みます。完了した順とは限りません。"
    ),
    "The plan {title}": "プラン{title}",
    "The question begins: {words}": "質問の始まりはこうです: {words}",
    "The rest: {parts}.": "残り: {parts}。",
    "The {item}": "{item}",
    "There are no current plans.": "現在のプランはありません。",
    "There are no open questions.": "未解決の質問はありません。",
    "There are no projects.": "プロジェクトはありません。",
    "There are no unread alerts.": "未読のアラートはありません。",
    "There are no waiting, running or failed sessions.": (
        "待機中、実行中、失敗のセッションはありません。"
    ),
    "There is no answer waiting.": "確定を待っている回答はありません。",
    "There is no list yet. Say list projects.": (
        "まだ一覧がありません。プロジェクト一覧、と言ってください。"
    ),
    "There is no option {number}.": "選択肢{number}はありません。",
    "There is nothing to go back to.": "戻る先がありません。",
    "There is nothing waiting to be sent.": "送信を待っているものはありません。",
    "This question has no more detail.": "この質問にそれ以上の詳細はありません。",
    "This voice device can't hold a datawatch conversation.": (
        "この音声デバイスではdatawatchの会話ができません。"
    ),
    "To read the rest, open datawatch.": "続きを読むには、datawatchを開いてください。",
    "To see what it said, open it in datawatch.": (
        "セッションの発言を見るには、datawatchで開いてください。"
    ),
    "What it is for": "目的",
    "Which number?": "何番ですか。",
    "Why the asker recommends it: {reason}": "質問者がすすめる理由: {reason}",
    "You can say: questions, next question, option and a number, my answer, confirm "
    "answer, cancel, status, more detail, attention, running, held items, tell me about a "
    "number or name, why, tasks, progress, results, what finished, sessions, waiting "
    "sessions, running sessions, failed sessions, plans, overview, what's next, "
    "automations, reports or a report's name, list projects, more, set and a number or "
    "name, set it, its questions, all questions, automata, history, add automation, add "
    "bug, send to session, go back, where am I, alerts, list order, sort by name, most "
    "recent first, unset, repeat, or stop.": (
        "次のように言えます。質問、次の質問、選択肢と番号、自分の言葉で回答、回答を確定、キャン"
        "セル、ステータス、詳しく、要対応、実行中、保留項目、番号か名前について教えて、なぜ、タ"
        "スク、進捗、結果、完了した作業、セッション、待機中のセッション、実行中のセッション、失"
        "敗したセッション、プラン、概要、次の予定、オートメーション、レポートまたはレポート名、"
        "プロジェクト一覧、もっと、番号か名前に設定、それに設定、関連する質問、すべての質問、オ"
        "ートマタ、履歴、オートメーションを追加、バグを報告、セッションに送信、戻る、今どこ、ア"
        "ラート、並び順、名前順、新しい順、フォーカス解除、もう一度、終了。"
    ),
    "You have no reports yet. Add one on the datawatch page in Home Assistant.": (
        "レポートはまだありません。Home Assistantのdatawatchのページで追加してください。"
    ),
    "You have {number} report: {names}. Say a name.": (
        "レポートは{number}件です: {names}。名前を言ってください。"
    ),
    "You have {number} reports: {names}. Say a name.": (
        "レポートは{number}件です: {names}。名前を言ってください。"
    ),
    "Your answer was not sent.": "回答は送信していません。",
    "Your assistant didn't answer. Try again, or say stop.": (
        "アシスタントから返事がありませんでした。もう一度試すか、終了、と言ってください。"
    ),
    "Your assistant had nothing to say.": "アシスタントからの返答はありませんでした。",
    "Your automation was not sent.": "オートメーションは送信していません。",
    "Your bug was not sent.": "バグは送信していません。",
    "Your choice: option {number}, {label}": "あなたの選択: 選択肢{number}、{label}",
    "Your message was not sent.": "メッセージは送信していません。",
    "Your words: {words}": "あなたの言葉: {words}",
    "a bug for project {project}": "プロジェクト{project}のバグ",
    "a message to the {item}": "{item}へのメッセージ",
    "a new draft automaton in project {project}": (
        "プロジェクト{project}の新しい下書きのオートマトン"
    ),
    "active": "アクティブ",
    "active {when}": "活動は{when}",
    "all new work is paused.": "新しい作業はすべて一時停止中です。",
    "approved": "承認済み",
    "archived": "アーカイブ済み",
    "at least {count}": "少なくとも{count}",
    "automation {title}": "オートメーション{title}",
    "automaton {title}": "オートマトン{title}",
    "awaiting approval": "承認待ち",
    "blocked": "ブロック中",
    "cancelled": "キャンセル済み",
    "completed": "完了",
    "datawatch added it to an open draft bug group.": (
        "datawatchは、開いている下書きのバグのグループに追加しました。"
    ),
    "datawatch did not accept it, so nothing was sent. The session may be showing a prompt "
    "to answer in datawatch.": (
        "datawatchが受け付けなかったため、何も送信していません。セッションに、datawatchで答える"
        "必要のある確認が出ているかもしれません。"
    ),
    "datawatch did not accept it. Nothing was sent.": (
        "datawatchが受け付けませんでした。何も送信していません。"
    ),
    "datawatch gives no folder for project {project}. Nothing was sent.": (
        "datawatchにプロジェクト{project}のフォルダーがありません。何も送信していません。"
    ),
    "datawatch gives no history for a plan.": "datawatchにプランの履歴はありません。",
    "datawatch gives no reason.": "datawatchは理由を示していません。",
    "datawatch has no change record for it.": "datawatchに変更の記録はありません。",
    "datawatch has no history for {title}.": "datawatchに{title}の履歴はありません。",
    "datawatch links no open questions to the {item}. There are {number} open questions in "
    "all. Say all questions.": (
        "datawatchで{item}に関連付けられた未解決の質問はありません。全体では{number}件あります"
        "。すべての質問、と言ってください。"
    ),
    "datawatch links no open questions to the {item}. There is {number} open question in "
    "all. Say all questions.": (
        "datawatchで{item}に関連付けられた未解決の質問はありません。全体では{number}件あります"
        "。すべての質問、と言ってください。"
    ),
    "datawatch links no unread alerts to the {item}. There are {number} unread alerts in "
    "all. Say unset, then alerts.": (
        "datawatchで{item}に関連付けられた未読アラートはありません。全体では{number}件あります"
        "。フォーカス解除、と言ってから、アラート、と言ってください。"
    ),
    "datawatch links no unread alerts to the {item}. There is {number} unread alert in "
    "all. Say unset, then alerts.": (
        "datawatchで{item}に関連付けられた未読アラートはありません。全体では{number}件あります"
        "。フォーカス解除、と言ってから、アラート、と言ってください。"
    ),
    "datawatch made a new draft bug group for it.": (
        "datawatchは新しい下書きのバグのグループを作りました。"
    ),
    "datawatch made a one-task draft for it.": "datawatchはタスクが1つの下書きを作りました。",
    "datawatch no longer has that session. Nothing was sent.": (
        "datawatchにそのセッションはもうありません。何も送信していません。"
    ),
    "datawatch no longer has the project {project}. Nothing was sent.": (
        "datawatchにプロジェクト{project}はもうありません。何も送信していません。"
    ),
    "datawatch no longer has the {item}, so I moved your focus up.": (
        "datawatchに{item}はもうないため、フォーカスを一つ上に移しました。"
    ),
    "datawatch no longer has the {item}.": "datawatchに{item}はもうありません。",
    "datawatch records history for an automaton, not for one task. Choose its automaton to "
    "hear it.": (
        "datawatchの履歴はオートマトンごとで、タスクごとではありません。履歴を聞くには、そのオ"
        "ートマトンを選んでください。"
    ),
    "datawatch refused access. Check the token in Home Assistant. Closing datawatch.": (
        "datawatchがアクセスを拒否しました。Home Assistantでトークンを確認してください。"
        "datawatchを終了します。"
    ),
    "datawatch refused that answer because it looks like it holds a secret. Nothing was sent.": (
        "秘密の情報が含まれているようなので、datawatchはその回答を拒否しました。何も送信してい"
        "ません。"
    ),
    "datawatch refused that answer. Nothing was sent.": (
        "datawatchはその回答を拒否しました。何も送信していません。"
    ),
    "datawatch says: {reason}": "datawatchの説明: {reason}",
    "datawatch's bug intake is turned off for project {project}. Nothing was sent.": (
        "プロジェクト{project}では、datawatchのバグ受付がオフです。何も送信していません。"
    ),
    "done": "完了済み",
    "draft": "下書き",
    "error": "エラー",
    "failed": "失敗",
    "held": "保留中",
    "in progress": "進行中",
    "just now": "たった今",
    "not shipped": "未リリース",
    "not started": "未開始",
    "paused": "一時停止中",
    "plan {title}": "プラン{title}",
    "planning": "計画中",
    "project {project}": "プロジェクト{project}",
    "queued": "順番待ち",
    "review needed": "レビューが必要",
    "running": "実行中",
    "session {title}": "セッション{title}",
    "shipped": "リリース済み",
    "shipped in {release}": "{release}でリリース済み",
    "task {title}": "タスク{title}",
    "unknown": "不明",
    "unnamed": "名前なし",
    "untitled": "無題",
    "waiting decision": "判断待ち",
    "waiting for input": "入力待ち",
    "waiting for review": "レビュー待ち",
    "warning": "警告",
    "{counts} across all projects.": "すべてのプロジェクトで{counts}。",
    "{done} of {number} task completed.": "タスク{number}件中{done}件が完了しました。",
    "{done} of {number} tasks completed.": "タスク{number}件中{done}件が完了しました。",
    "{done} of {total} automata done": "オートマタ{total}件中{done}件が完了",
    "{done} of {total} automata done.": "オートマタ{total}件中{done}件が完了。",
    "{done} of {total} tasks completed": "タスク{total}件中{done}件が完了",
    "{first} and {last}": "{first}と{last}",
    "{found} among the newest {number}": "新しい{number}件のうち{found}",
    "{kind} from {when}": "{kind}、{when}",
    "{lead}{counts}.": "{lead}{counts}。",
    "{name} has no automata.": "{name}にオートマタはありません。",
    "{name} has no tasks.": "{name}にタスクはありません。",
    "{name} has nothing in it. Change it on the datawatch page in Home Assistant.": (
        "{name}には何も入っていません。Home Assistantのdatawatchのページで変更してください。"
    ),
    "{name} has {number} automata.": "{name}のオートマタは{number}件です。",
    "{name} has {number} automaton.": "{name}のオートマトンは{number}件です。",
    "{name} has {number} task.": "{name}のタスクは{number}件です。",
    "{name} has {number} tasks.": "{name}のタスクは{number}件です。",
    "{number} automata are running across all projects.": (
        "すべてのプロジェクトで{number}件のオートマタが実行中です。"
    ),
    "{number} automata are running in project {project}.": (
        "プロジェクト{project}で{number}件のオートマタが実行中です。"
    ),
    "{number} automata have completed across all projects.": (
        "すべてのプロジェクトで{number}件のオートマタが完了しました。"
    ),
    "{number} automata have completed in project {project}.": (
        "プロジェクト{project}で{number}件のオートマタが完了しました。"
    ),
    "{number} automata need attention, across all projects: {parts}.": (
        "すべてのプロジェクトで{number}件のオートマタに対応が必要です: {parts}。"
    ),
    "{number} automaton has completed across all projects.": (
        "すべてのプロジェクトで{number}件のオートマトンが完了しました。"
    ),
    "{number} automaton has completed in project {project}.": (
        "プロジェクト{project}で{number}件のオートマトンが完了しました。"
    ),
    "{number} automaton is running across all projects.": (
        "すべてのプロジェクトで{number}件のオートマトンが実行中です。"
    ),
    "{number} automaton is running in project {project}.": (
        "プロジェクト{project}で{number}件のオートマトンが実行中です。"
    ),
    "{number} automaton needs attention, across all projects: {parts}.": (
        "すべてのプロジェクトで{number}件のオートマトンに対応が必要です: {parts}。"
    ),
    "{number} current plan": "現在のプラン{number}件",
    "{number} current plans": "現在のプラン{number}件",
    "{number} day ago": "{number}日前",
    "{number} days ago": "{number}日前",
    "{number} failed or blocked automata": "失敗またはブロック中のオートマタ{number}件",
    "{number} failed or blocked automaton": "失敗またはブロック中のオートマトン{number}件",
    "{number} failed session": "失敗したセッション{number}件",
    "{number} failed sessions": "失敗したセッション{number}件",
    "{number} file": "ファイル{number}件",
    "{number} files": "ファイル{number}件",
    "{number} finished or set aside with tasks held for review": (
        "完了または見送りで、レビュー保留のタスクがあるもの{number}件"
    ),
    "{number} held item": "保留項目{number}件",
    "{number} held items": "保留項目{number}件",
    "{number} hour ago": "{number}時間前",
    "{number} hours ago": "{number}時間前",
    "{number} item is on hold, across all projects.": (
        "すべてのプロジェクトで{number}件が保留中です。"
    ),
    "{number} items are on hold, across all projects.": (
        "すべてのプロジェクトで{number}件が保留中です。"
    ),
    "{number} member": "メンバー{number}件",
    "{number} members": "メンバー{number}件",
    "{number} minute ago": "{number}分前",
    "{number} minutes ago": "{number}分前",
    "{number} not started": "未開始{number}件",
    "{number} open question": "未解決の質問{number}件",
    "{number} open question, across all projects.": (
        "すべてのプロジェクトで未解決の質問は{number}件です。"
    ),
    "{number} open questions": "未解決の質問{number}件",
    "{number} open questions, across all projects.": (
        "すべてのプロジェクトで未解決の質問は{number}件です。"
    ),
    "{number} package": "パッケージ{number}件",
    "{number} packages": "パッケージ{number}件",
    "{number} plan": "プラン{number}件",
    "{number} plans": "プラン{number}件",
    "{number} plans archived.": "アーカイブ済みのプランは{number}件です。",
    "{number} project": "プロジェクト{number}件",
    "{number} project has something next.": "{number}件のプロジェクトに次の項目があります。",
    "{number} projects": "プロジェクト{number}件",
    "{number} projects have something next.": "{number}件のプロジェクトに次の項目があります。",
    "{number} running": "実行中{number}件",
    "{number} session waiting for input": "入力待ちのセッション{number}件",
    "{number} sessions waiting for input": "入力待ちのセッション{number}件",
    "{number} task held for review": "レビュー保留のタスク{number}件",
    "{number} task is stuck. First: {title}, {state}.": (
        "{number}件のタスクが止まっています。最初は{title}、{state}です。"
    ),
    "{number} tasks are stuck. First: {title}, {state}.": (
        "{number}件のタスクが止まっています。最初は{title}、{state}です。"
    ),
    "{number} tasks held for review": "レビュー保留のタスク{number}件",
    "{number} test": "テスト{number}件",
    "{number} tests": "テスト{number}件",
    "{number} unread alert, across all projects, newest first.": (
        "すべてのプロジェクトで未読アラートは{number}件です。新しい順です。"
    ),
    "{number} unread alerts, across all projects, newest first.": (
        "すべてのプロジェクトで未読アラートは{number}件です。新しい順です。"
    ),
    "{number} warning or error": "警告またはエラー{number}件",
    "{number} warnings or errors": "警告またはエラー{number}件",
    "{number} {state}": "{state}{number}件",
    "{number}, session named {name}, {state}": "{number}、{name}という名前のセッション、{state}",
    "{plans} in {projects}.": "{projects}に{plans}。",
    "{start}, and more": "{start}、ほか",
    "{start}, and more. See datawatch for the rest.": (
        "{start}、ほかにもあります。続きはdatawatchで確認してください。"
    ),
    "{title} has no tasks.": "{title}にタスクはありません。",
    "{title} has {number} entries. The latest: {lines}": (
        "{title}の記録は{number}件です。新しいもの: {lines}"
    ),
    "{title} has {number} entry. The latest: {lines}": (
        "{title}の記録は{number}件です。最新: {lines}"
    ),
    "{title} is {state}.": "{title}は{state}です。",
    "{what}, by {actor}": "{what}、実行者は{actor}",
    "{where}: no automations.": "{where}: オートメーションはありません。",
    "{where}: sessions, {counts}.": "{where}: セッションは{counts}。",
    "{where}: {number} automation, {parts}.": "{where}: オートメーション{number}件、{parts}。",
    "{where}: {number} automations, {parts}.": "{where}: オートメーション{number}件、{parts}。",
}
