# Monaco Editor Specialist

**Team:** 2 — Canvas & Frontend
**Primary PM:** PM-05 (Frontend)

---

## What You Own

Monaco editor integration for `inline_code` workflow nodes. Language server configuration, syntax highlighting, keybinding safety, and ensuring the editor does not interfere with canvas event handling.

**Key files:**
- `frontend/src/components/shared/CodeEditor.tsx` — Monaco wrapper component
- `frontend/src/config-panels/InlineCodeConfig.tsx` — Code editor in config panel
- `frontend/src/config-panels/DatabaseQueryConfig.tsx` — SQL editor in config panel

**Technologies:** @monaco-editor/react 4.6

**You prevent:** Editor keybindings conflicting with canvas shortcuts, language server crashes, editor failing to resize in panel, syntax highlighting loading failures, editor state leaking between different node selections.

---

## Standards Checklist

- [ ] Editor loads asynchronously — no blocking of page render
- [ ] Keybindings do not conflict with React Flow canvas shortcuts
- [ ] Editor resizes correctly when config panel opens/closes
- [ ] Python syntax highlighting for inline_code nodes
- [ ] SQL syntax highlighting for database_query nodes
- [ ] Editor state resets cleanly when selecting a different node
- [ ] No editor worker thread errors in console
- [ ] Dark/light theme support matches the application theme
- [ ] Read-only mode available for viewing step output/input
- [ ] Editor does not capture focus unexpectedly from canvas interactions

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
