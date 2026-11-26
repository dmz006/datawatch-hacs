# Telling your assistant about datawatch

If your assistant is an AI model, it does not know datawatch exists. This integration does
not change your assistant or send it anything.

If you would like it to be able to explain datawatch, you can add the text below to its
instructions. **Add it after what is already there. Don't replace anything:** your
assistant's name, personality and rules stay as you wrote them. The text sets no tone or
personality. Any added text can still affect how a model answers, so try your assistant
afterwards, and delete the paragraph if you don't like the result.

```text
About datawatch: this home has a datawatch integration. datawatch is a program that runs and
watches AI coding assistants and planned automated work, grouped into projects. You cannot
read or change datawatch yourself. Never guess its status or make up numbers, names or
results about it. If someone asks about datawatch, such as its status, open questions,
sessions, projects, or failed or held work, tell them to say the wake word and then "open
datawatch". In datawatch mode they can say: status, more detail, list projects, set followed
by a number or a project name, where am I, unset, repeat, help, and close datawatch. It only
reads information.
```

With this, your assistant can point you to datawatch mode. It still cannot answer datawatch
questions itself. If it asks you a follow-up question, your next reply goes straight to it,
so say your wake word again before "open datawatch".
