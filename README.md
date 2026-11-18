# 🚀 Buildathon: Make Wednesdays Great Again

**Masters' Union · For AI Developers · Winner gets Rs. 25,000**

> **Every team must build in a fork of this repository.** Projects not built in a fork of this repo won't be judged.

| | |
|---|---|
| **Date** | Wednesday, 18 November 2026 |
| **Hacking** | **3:00 PM – 7:00 PM IST** (code freeze at 7:00 PM sharp) |
| **Venue** | CDS Audi, 8th floor |
| **Prize** | Rs. 25,000 to the winning team |
| **Register your fork** | 👉 **[https://forms.gle/ZJUYKwTYjsMsVB2b9](https://forms.gle/ZJUYKwTYjsMsVB2b9)** (**deadline 3:30 PM IST**) |
| **Final submission** | Your fork as it stands at **7:00 PM IST**. There's nothing else to submit. |

> 🤖 **Using an AI coding agent?** Point it at [`AGENTS.md`](AGENTS.md). It has the full event brief, tracks, judging and rules in a form agents can read directly. Claude Code loads it automatically through `CLAUDE.md`, and Codex reads `AGENTS.md` natively.

---

## 🎯 Pick one build track

| # | Track | Brief |
|---|---|---|
| **01** | **Build for the Physical World** | Make a real-world task easier, faster or more reliable. Show it in a realistic scenario. |
| **02** | **Build for AI Agents** | Find something an agent struggles with. Build the tool that fixes it, then demo the agent using it. |
| **03** | **Build in Your Area of Expertise** | Pick a field you know firsthand. Ship a working product that improves how people handle it today. |

## ⚖️ How you'll be judged (each criterion is ⅓ of your score)

| Criterion | The question judges ask |
|---|---|
| **Working product** | Does it do what you say it does? Show the core workflow in your demo. |
| **Problem insight** | Who faces this problem, and why does it happen? |
| **Depth of execution** | How well did you solve the hardest part of the build? |

---

## Why fork this repo?

Everyone starts from the same commit (the **genesis commit**) at the same time. Organizers can then check that:
- all code was written **during** the Buildathon and not brought in from an earlier project,
- teams commit steadily instead of pasting in one huge AI-generated dump at the end,
- every repo stays public and visible while you build.

The organizers track every fork automatically: commits, timing and activity. Read [RULES.md](RULES.md) before you write any code.

---

## ✅ Setup (about 5 minutes, do it at 3:00 PM)

**In short:** fork → register your fork in the form **by 3:30 PM** → build → push before 7:00 PM.

### 1. Fork this repo
Click **Fork** (top right). On the fork screen:
- **Owner:** one team member's personal account. Only **one fork per team**.
- **Repository name:** `buildathon-<team-name>`, for example `buildathon-byte-bandits`
- Click **Create fork**.

> ⚠️ Don't download a ZIP or copy the files into a new repo. **It has to be a real GitHub fork**, or the tracker can't see you.

### 2. Keep it public
Forks of a public repo are public. **Don't make it private, archive it, or delete it** until judging is over.

### 3. Add your teammates
In your fork: **Settings → Collaborators → Add people**. Add each teammate's GitHub account so their commits count toward the team.

### 4. Enable Actions
Open the **Actions** tab of your fork and click **"I understand my workflows, go ahead and enable them"**. This runs the automatic check on every push.

### 5. Make your registration commit (your first commit)
Fill in [`team.json`](team.json). `track` must be one of `physical-world`, `ai-agents` or `area-of-expertise`. Then:

```bash
git clone https://github.com/<your-username>/buildathon-<team-name>.git
cd buildathon-<team-name>
# edit team.json
git add team.json
git commit -m "register: <team name>"
git push
```

The **Hackathon check** in the Actions tab should go green ✅. If it's red, open the run to see what's wrong in `team.json`.

### 6. Register your fork (deadline: 3:30 PM IST)
👉 **[https://forms.gle/ZJUYKwTYjsMsVB2b9](https://forms.gle/ZJUYKwTYjsMsVB2b9)**

It's a 4-question Google Form: team name, fork link, track, team members. It connects your repo to the organizers' live tracker.

- Fill it in **once per team**, right after forking, and **no later than 3:30 PM IST**. **Teams that don't register can't be tracked.**
- Paste your **fork's** URL (`https://github.com/<you>/buildathon-<team-name>`), not this starter repo's.
- Need to change something? Use the **"Edit your response"** link on the confirmation page. Don't fill it in twice.
- **Final submission is automatic.** Whatever is pushed to your fork at 7:00 PM IST is what gets judged.

---

## 🛠 While you build (3:00 – 7:00 PM)

- Put your code anywhere in the repo (`app/`, `src/`, `frontend/`, `backend/`…). There's no required layout.
- **Commit early, commit often**, at least every 30 minutes of real work, with messages that say what changed.
- **Push regularly.** Commits you never push don't exist to the tracker.
- AI coding tools (Claude Code, Codex, Cursor, Copilot…) are **allowed and encouraged**. Keep `AGENTS.md` and `CLAUDE.md` in the repo; they keep your agent within the rules.
- Before 7:00 PM, replace the "Your project" section below with your project's README.

## 🧊 Code freeze: 7:00 PM IST

At 7:00 PM the tracker takes a snapshot of every fork. **Commits pushed after code freeze are ignored.** Judges look at your last commit before 7:00 PM.

## ❌ Things that get you flagged

- Rewriting history (`git push --force`, rebasing away the genesis commit, squashing everything into one commit)
- Commits dated before 3:00 PM
- One or two giant commits containing most of the project
- A repo that isn't a fork of this one, or that's private or deleted

See [RULES.md](RULES.md) for the full list.

---

## Your project

**Submission: Working prototype (MVP)** — a running application with real policy checks against a simulated calendar; it is not a production service or a static mockup.

**Team:** NexusBrain — Adish Jain ([@adishjain01](https://github.com/adishjain01))  
**Track:** Build for AI Agents (`ai-agents`)

### The problem

People ask agents to perform a specific task, but the tools agents use may grant broad access to a whole calendar. A prompt alone does not enforce the user's limits, and a successful tool call can make an unintended change. Intent Lock turns a reviewed, task-specific permission into a gateway decision before an agent can write to the mock calendar.

### What we built

A local calendar simulator, permission review screen, deterministic policy gateway, decision trail, and a choice of scripted or OpenRouter-powered agent. The user enters a supported calendar task in chat and reviews the proposed meeting, action and limits. They review the precise permission before activating it. The gateway permits one matching action for 15 minutes, preserves other fields, checks stale meeting state and rescheduling conflicts, and records allowed and blocked attempts. Reset restores the calendar and revokes the permission.

For a rescheduling permission, the demo agent tries to add an attendee, tries a disallowed weekday if one exists, then searches for an available permitted slot. For an attendee permission, it tries cancellation and an unapproved attendee before adding the approved person. Scripted mode is deterministic and uses the gateway. Optional OpenRouter mode uses a free model to choose tool calls; every proposed action still passes through the same deterministic gateway. The model may behave differently on each run, including choosing no action. The separate `agent.py` uses the gateway HTTP endpoint and has no direct calendar access. The browser offers both modes; the separate script uses the repeatable scripted behavior.

### The hardest part

The policy must fail closed: wrong meeting, action type, extra fields, expired or used permission, stale meeting, past times and conflicting slots are rejected before mutation. Policy evaluation and mutation occur under one process lock. Without a key, the local chat parser accepts a small explicit grammar, for example `Reschedule the meeting with Priya this week after 2 PM and never Friday` or `Add Taylor to the meeting with Priya`. Unsupported wording is rejected. In OpenRouter mode, a model interprets a wider range of language and proposes a permission for user review. Models may misunderstand or omit details, so compare the proposal with the entire request. Unsupported actions, including attendee removal, cannot be authorized. Reschedule defaults to the current calendar week and 09:00–23:59 server-local time; the review shows the exact boundaries. Times after a stated time are strict to the minute. The mock calendar sends no invitations or notifications.

The prompt-injection and conflict options are simulations. Scripted mode attempts preselected actions through the gateway, while the model may make different decisions or ignore the injected mock note. This is not evidence of protection against all prompt injection.

This is a prototype, not production security: there is no authentication, persistence, real calendar integration, or protection against processes that bypass the local server. External services can have hidden side effects, and user review cannot infer unstated preferences. Do not expose this demo server to the internet.

### Run it

Requires Python 3.10+; no dependencies or API keys.

```bash
python intent-lock/server.py
```

On Windows, you can instead double-click `intent-lock/start-demo.bat`. Keep the terminal window open, then open http://127.0.0.1:8000/ in a browser on the same machine. Press **R** in that terminal to restart the server after a code change, or **Q** to stop and exit. Restart resets the mock calendar, permission and session-only key. If port 8000 is already in use, run `python intent-lock/server.py --port 8001` and open http://127.0.0.1:8001/. If the server is running in a sandbox or remote environment, its localhost may not be reachable from your desktop browser; run it in a normal local terminal. Run tests with `python -m unittest discover -s intent-lock -v`. To run the independent HTTP agent instead of the browser button, approve a fresh permission and run `python intent-lock/agent.py` in another terminal; refresh the page to see its decision trail.

### Optional OpenRouter agent

Scripted mode works without a key. To enable model mode, enter a key in the app and click **Use key** under **Agent settings**. The server holds it in memory until restart or until you click **Clear key**; it is not written to a file. Alternatively, copy `intent-lock/.env.example` to `intent-lock/.env`, add your own `OPENROUTER_API_KEY`, and restart the server. The key stays server-side and `.env` is ignored by Git. Clearing the session key does not remove an independently configured environment or `.env` key. Select **OpenRouter free model** in the UI after approving a permission. Only use the seeded mock calendar: the selected permission and mock meeting data and task text are sent to OpenRouter and its model provider. The model routes through `openrouter/free`; availability and rate limits can vary. If intent interpretation is rate-limited or returns invalid output, the app falls back to the local interpreter only for exact supported phrases and clearly labels that fallback; the scripted agent then runs. Other tasks must be retried or rephrased. If an agent run fails, inspect the audit trail before retrying, since an action may have already succeeded. You can select scripted mode for a repeatable fallback.

### Demo

1. Choose **Prompt injection** and type `Reschedule the meeting with Priya this week after 2 PM and never Friday` in the chat. Click **Review task**.
2. Check the proposed permission and click **Approve & run agent**. In scripted mode, the injection is a simulated instruction to cancel another meeting. The gateway blocks it and displays the attempted actions and reasons; an allowed future reschedule updates the calendar.
3. Click **New demo** and try **Calendar conflict** or `Add Taylor to the meeting with Priya`. Review and approve each new permission. The scripted chat parser supports the examples shown in the interface; model mode interprets broader language but requires careful review.
4. Optional: use **Agent settings** to choose the free OpenRouter model. Model results vary and the injection may not cause a tool call; scripted mode is the repeatable fallback.
