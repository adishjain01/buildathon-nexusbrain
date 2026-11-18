# Intent Lock — 90-second demo recording script

Use the live Vercel demo at https://buildathon-nexusbrain.vercel.app/ in **scripted mode**. This is a mock calendar and the prompt-injection attempts are simulated. Do not call the permission cryptographic or claim a real calendar or autonomous model is connected. The hosted demo's session can reset; if it does, restart the demonstration.

| Time | On screen | Narration |
| --- | --- | --- |
| 0:00–0:12 | Open the demo. Point to the mock calendar and agent playground. | “Agents can be useful, but giving one broad access to a calendar is much more permission than a single task needs. Intent Lock puts a check between the agent and its tools.” |
| 0:12–0:25 | Select **Test Prompt Injection Defense**. Enter `Reschedule the meeting with Priya to Friday at 2 PM` and click **Review task**. | “Here, I ask the agent to move one meeting. Intent Lock turns that request into a proposed permission, which I review before the agent can act.” |
| 0:25–0:38 | Read the exact meeting, date and time in the permission card. Click **Approve & run agent**. | “The permission is for this meeting, this destination, and one successful change. It expires after 15 minutes, and keeps the existing attendees.” |
| 0:38–0:55 | Show the simulated attack banner and the gateway report. Point to blocked cancellation and blocked attendee addition. | “In this scripted simulation, a malicious instruction tries to make the agent exceed that task. The gateway checks the attempted actions against the approved permission and blocks them. The trail shows what was attempted and why.” |
| 0:55–1:08 | Point to the allowed reschedule and updated calendar; show the protected other meeting. | “The permitted reschedule goes through, and the calendar changes. The other meeting remains untouched. A used permission cannot authorize a second change.” |
| 1:08–1:20 | Click **New demo**. Start an incomplete request: `Reschedule the meeting with Priya`; show the clarification. | “If the request is missing the destination date and time, the app asks for them instead of silently choosing a slot.” |
| 1:20–1:30 | Show the workspace and gateway activity. | “This MVP uses a mock calendar and a deterministic scripted agent for a repeatable demo. A local version also supports an optional model; the same gateway checks its proposed actions.” |

## Recording notes

- Use a date and time that are in the future and do not overlap another meeting; replace the example as needed.
- Rehearse once. If the hosted session resets, use the local app or restart the run.
- The simulated injection is not proof that every prompt injection is detected. The gateway only controls actions routed through it.
- Never show, type, or narrate an API key in the recording.
