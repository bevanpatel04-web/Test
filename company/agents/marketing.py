"""Marketing agent: Pinterest pins, short-video scripts and the weekly newsletter."""
from __future__ import annotations

from datetime import date

from .. import config, site
from ..claims import CLAIMS_POLICY
from ..schemas import MarketingPack
from .content import review

SYSTEM = f"""You are the marketing lead for {config.BRAND}. {config.MISSION}
Audience: adults with eczema or sensitive skin, and parents of kids with eczema, in the US.
Channels: Pinterest (search-driven, evergreen), short vertical video (founder talking to camera — the founder has
eczema; write scripts in first person they can read in under 45 seconds), and a weekly email newsletter.
Goal: drive people to the free ZIP-code water check and city guides, and grow the email list.
Write 5 pins, 2 video scripts and 1 newsletter. Link only to paths that exist.

{CLAIMS_POLICY}"""


def pack_text(pack: MarketingPack) -> str:
    return "\n".join([*(f"{p.title} {p.description}" for p in pack.pins),
                      *(f"{v.hook} {v.script} {v.call_to_action}" for v in pack.video_scripts),
                      pack.newsletter.subject, pack.newsletter.body])


def run(task: dict, llm) -> dict:
    paths = ["/", "/cities/"] + [f"/cities/{s}.html" for s in site.published_slugs()]
    prompt = f"Existing site paths: {paths}\n\nCEO instructions: {task['instructions']}"
    pack = llm.structured(system=SYSTEM, prompt=prompt, schema=MarketingPack, effort="medium")
    issues = review(llm, pack_text(pack))
    if issues:
        pack = llm.structured(system=SYSTEM, schema=MarketingPack, effort="medium",
                              prompt=prompt + "\n\nPrevious draft broke the claims policy:\n- " + "\n- ".join(issues))
        issues = review(llm, pack_text(pack))
        if issues:
            raise ValueError("Marketing pack failed the claims check twice: " + "; ".join(issues))
    return pack.model_dump()


def on_approve(task: dict) -> str:
    pack = MarketingPack(**task["result"])
    lines = [f"# Marketing pack — task #{task['id']} ({date.today().isoformat()})", "", "## Pinterest pins", ""]
    for p in pack.pins:
        lines += [f"**{p.title}**  ", p.description + "  ", f"Link: {config.SITE_URL}{p.target_path}", ""]
    lines += ["## Video scripts", ""]
    for i, v in enumerate(pack.video_scripts, 1):
        lines += [f"### Video {i}", f"**Hook (on screen):** {v.hook}", "", v.script, "", f"**CTA:** {v.call_to_action}", ""]
    lines += ["## Newsletter", "", f"**Subject:** {pack.newsletter.subject}", "", pack.newsletter.body, ""]
    path = config.OUTBOX_DIR / f"{date.today().isoformat()}-task-{task['id']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    return f"Ready to post: {path.relative_to(config.ROOT)}"
