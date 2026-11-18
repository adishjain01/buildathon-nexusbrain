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

A local calendar simulator, permission review screen, deterministic policy gateway, decision trail, and a small scripted agent. The user chooses one meeting, a date range, allowed weekdays and start times. They review the precise permission before activating it. The gateway permits one matching reschedule for 15 minutes, preserves all other fields, checks for conflicts and stale meeting state, and records allowed and blocked attempts. Reset restores the calendar and revokes the permission.

The demo agent deliberately tries to add an attendee, tries a disallowed weekday if one exists, and then searches for an available permitted slot. It is a **scripted, deterministic agent**, not an LLM; it makes actual calls to the gateway. The separate `agent.py` uses the gateway HTTP endpoint and has no direct calendar access. The browser's demo button runs the same behavior in the server for convenience.

### The hardest part

The policy must fail closed: wrong meeting, action type, extra fields, expired or used permission, stale meeting and conflicting slots are rejected before mutation. Policy evaluation and mutation occur under one process lock. The typed constraint field accepts a small explicit grammar: `after 2 PM`, `before 5 PM`, and `never Friday` (also `never on Friday`), joined with `and`. It rejects unsupported text in full, applies recognized constraints to the structured controls, and requires review before approval; it does not claim to understand arbitrary language. Times are server-local, start-time bounds are inclusive, and the chosen range is limited to 32 calendar days. The mock calendar has no notification or third-party side effects.

This is a prototype, not production security: there is no authentication, persistence, real calendar integration, or protection against processes that bypass the local server. External services can have hidden side effects, and user review cannot infer unstated preferences. Do not expose this demo server to the internet.

### Run it

Requires Python 3.10+; no dependencies or API keys.

```bash
python intent-lock/server.py
```

Open http://127.0.0.1:8000. Run tests with `python -m unittest discover -s intent-lock -v`. To run the independent HTTP agent instead of the browser button, approve a fresh permission and run `python intent-lock/agent.py` in another terminal; refresh the page to see its decision trail.

### Demo

1. Select Project sync with Priya. Choose a date range, then type `only allow rescheduling after 2 PM and never on Friday` and apply it. Review and approve the exact displayed permission.
2. Click **Run demo agent**. The decision trail shows blocked attempts and a permitted reschedule; the calendar updates.
3. Reset, approve another permission, and let a judge choose a different target, action or time using **Test an action**. Show the reason it was blocked. A permitted action consumes the permission, so a repeat is blocked.
4. Use Reset between demos. To change a constraint, review and approve a fresh permission.


