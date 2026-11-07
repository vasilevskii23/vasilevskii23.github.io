# Content Machine Installed Pack

These instructions apply to the materialized Content Machine pack in
`.content-machine`.

## Role Split

- `skills/` are decision and craft docs: when to use a capability,
  what inputs it needs, and what quality bar it must meet.
- `flows/` are orchestration docs: multi-step paths, gates, and run-scoped outputs.
- `cm-agent` is execution only: use it when a skill or flow needs a
  deterministic JSON-stdio runtime tool.
- Primary runner: `npx --no-install cm-agent <tool>`.
- Fallback runner: `node ./node_modules/@45ck/content-machine/agent/run-tool.mjs <tool>`.

## How To Use It

1. Choose the lane first, then choose a skill for one capability or a flow for a multi-step run.
2. Read `.content-machine/skills/README.md`, then the relevant
   `skills/<name>/SKILL.md`.
3. For executable multi-step work, use `run-flow` and pass
   `"flowsDir": ".content-machine/flows"`.
4. For one stage, call the direct tool named by the skill.
5. Write artifacts under `runs/<run-id>/` unless the user asks for a
   different output directory.
6. Run publish-prep or the skill's listed validation before saying a
   video is ready.

Assume the human is operating through Claude Code, Codex CLI, Cursor, or
a similar harness. Interpret requests as outcomes first, not as demands
that the user choose low-level flags.

## Useful Commands

```bash
npx --no-install cm-agent list

cat <<'JSON' | npx --no-install cm-agent skill-catalog
{
  "skillsDir": ".content-machine/skills",
  "includeExamples": true
}
JSON
```

```bash
cat <<'JSON' | npx --no-install cm-agent doctor-report
{
  "strict": false
}
JSON
```

```bash
cat <<'JSON' | npx --no-install cm-agent flow-catalog
{
  "flowsDir": ".content-machine/flows"
}
JSON

cat <<'JSON' | npx --no-install cm-agent run-flow
{
  "flowsDir": ".content-machine/flows",
  "flow": "generate-short",
  "runId": "demo-run",
  "input": { "topic": "Example short" }
}
JSON
```

Plan longform clips before rendering:

```bash
cat <<'JSON' | npx --no-install cm-agent run-flow
{
  "flowsDir": ".content-machine/flows",
  "flow": "longform-to-shorts",
  "runId": "source-clips",
  "input": {
    "timestampsPath": "input/source/timestamps.json",
    "sourceMediaPath": "input/source/source.mp4",
    "maxCandidates": 3
  }
}
JSON
```


## Human Prompt Pattern

When the user asks for video work, prefer this interpretation:

> Pick the right Content Machine skill or flow, explain the lane briefly,
> run the needed JSON-stdio tools, keep artifacts inspectable, and only
> call the output ready when validation passes.

## Source-Repo Path Warning

If a copied doc mentions `scripts/harness/`, use it only as source-repo
context. Installed projects should execute tools with
`npx --no-install cm-agent <tool>` unless the user is working inside the
Content Machine checkout.
