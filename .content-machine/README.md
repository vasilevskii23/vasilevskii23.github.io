# Content Machine Skill Pack

This directory is a portable copy of the Content Machine skill pack for
coding-agent harnesses such as Codex CLI, Claude Code, Cursor, and other
repo-aware agents.

## Tell Your Agent This

> Use Content Machine from `.content-machine`. Read
> `.content-machine/skills/README.md` first, choose the right skill or
> flow, run tools through `npx --no-install cm-agent`, write artifacts under
> `runs/<run-id>/`, and only call a video ready when publish-prep
> passes.

`cm-install` also wrote a managed root instruction block to `AGENTS.md`.
Confirm your harness loads that file before asking for video work.


## Copy-Paste Prompts

Assume the user already works in Claude Code, Codex CLI, Cursor, or a
similar agent harness. Ask for outcomes; let the harness read this pack
and call `npx --no-install cm-agent` only when it needs deterministic execution.

Topic to short:

> Use Content Machine from `.content-machine` to make a 35-second
> vertical explainer about Redis versus PostgreSQL for caching. Pick the
> lane, run the default generation path, write artifacts under
> `runs/redis-cache-short/`, and only call it ready if publish-prep
> passes.

Known lane:

> Use the `reddit-post-over-gameplay` lane for this story. Keep
> gameplay full-screen, show the Reddit opener card for 3-5 seconds, use
> bold captions, and report the final MP4 plus publish-prep artifacts.

Longform clipping:

> Turn this longform video into three candidate shorts. Run the longform-to-shorts flow first, show the candidate plan, ask before rendering, then render only
> the approved candidate after extraction and run publish-prep.

## What Was Installed

- Skills live under `.content-machine/skills/`
- Flows live under `.content-machine/flows/`
- Runtime commands use `npx --no-install cm-agent <tool>`
- Fallback runner path: `node ./node_modules/@45ck/content-machine/agent/run-tool.mjs <tool>`

## Run From Project Root

Node.js 20.6+ is required. The npm package should already be installed
because `cm-install` created this pack. When refreshing, upgrade the
package first:

```bash
npm install --save-dev @45ck/content-machine@latest
npx cm-install --target .content-machine --overwrite --write-instructions
```

List available runtime tools:

```bash
npx --no-install cm-agent list
```

If npm bins are unavailable, use the explicit package path:

```bash
node ./node_modules/@45ck/content-machine/agent/run-tool.mjs list
```

List installed skills:

```bash
cat <<'JSON' | npx --no-install cm-agent skill-catalog
{
  "skillsDir": ".content-machine/skills",
  "includeExamples": true
}
JSON
```

Run diagnostics before real generation:

```bash
cat <<'JSON' | npx --no-install cm-agent doctor-report
{
  "strict": false
}
JSON
```

Run a direct skill example:

```bash
cat .content-machine/skills/generate-short/examples/request.json | \
  npx --no-install cm-agent generate-short
```

List installed flows:

```bash
cat <<'JSON' | npx --no-install cm-agent flow-catalog
{
  "flowsDir": ".content-machine/flows"
}
JSON
```

Run an installed flow:

```bash
cat <<'JSON' | npx --no-install cm-agent run-flow
{
  "flowsDir": ".content-machine/flows",
  "flow": "generate-short",
  "runId": "demo-run",
  "input": {
    "topic": "Redis vs PostgreSQL for caching",
    "publishPrep": { "enabled": true, "platform": "tiktok" }
  }
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


## Source-Repo Paths In Copied Docs

Some copied skill or flow docs may still mention source-checkout paths
such as `scripts/harness/` for contributor context. In an installed
pack, treat those as reference-only and use `npx --no-install cm-agent` for execution.

## Update Or Remove

- Update: `npm install --save-dev @45ck/content-machine@latest`, then
  `npx cm-install --target .content-machine --overwrite --write-instructions`.
- Remove: delete `.content-machine/`, remove any copied root
  instruction snippets, then run `npm uninstall @45ck/content-machine`
  if the package is no longer needed.
- Keep or delete `runs/` separately; it contains user-generated
  outputs and is not part of the installed pack.

## Operating Rules

- Ask for outcomes, not flags: "make a Reddit story short" or "turn
  this long video into three candidate shorts."
- Choose the archetype or skill or flow before rendering.
- Keep source media, rights notes, generated assets, captions, and
  publish-prep output inspectable under `runs/`.
- Do not treat a render as publish-ready unless the review gate passes.
