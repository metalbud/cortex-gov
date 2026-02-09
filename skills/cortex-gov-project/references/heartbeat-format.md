# Multi-agent HEARTBEAT.md format

Use this exact format so OpenClaw agents include their ID in updates:

- Agent: Read <CONTROL_DOC> if it exists in workspace context. Follow the rules set in that doc strictly. Do not infer or repeat old tasks from prior chats. Complete the first available TODO task and update your status, then post a short summary of changes in #dev (discord) with your agent ID.
- If no task to do in <CONTROL_DOC> reply with HEARTBEAT_OK and include your agent ID
- Workspace: <absolute workspace path>
