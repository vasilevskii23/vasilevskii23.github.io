<!-- BEGIN CONTENT MACHINE INSTALL v:1 -->
## Content Machine

Use the materialized Content Machine pack in `.content-machine` for short-form
video work.

- Read `.content-machine/README.md` and `.content-machine/AGENTS.md` before
  planning video work.
- Use `.content-machine/skills/` for capability docs and `.content-machine/flows/` for multi-step flows.
- Execute runtime tools with `npx --no-install cm-agent <tool>`.
- Pass `skillsDir: ".content-machine/skills"` to skill discovery tools and `flowsDir: ".content-machine/flows"` to flow tools.
- Write artifacts under `runs/<run-id>/` and do not call a video ready until
  publish-prep passes.
<!-- END CONTENT MACHINE INSTALL -->
