"""Social agent: short-video scripts, an Instagram carousel and the weekly newsletter."""
from __future__ import annotations

import json
from datetime import date

from .. import config, publish
from ..claims import CLAIMS_POLICY
from ..schemas import SocialPack
from .compliance import write_reviewed

SYSTEM = f"""You are the social media lead for {config.BRAND}. {config.MISSION}
Audience: 18-25 year olds in the US on TikTok, Instagram Reels, YouTube Shorts and Instagram carousels, plus a
weekly email newsletter. The founder films short videos talking to camera: write first-person scripts they can
read in under 45 seconds, casual and honest. Hooks spark curiosity; never clickbait, fear or FOMO.
Write 2 videos, 1 carousel (5-8 short slides) and 1 newsletter (under 300 words). Send people to the free
calculator (the homepage) and to published lessons. Mention only paths that exist.
Use only the verified facts provided. A disclaimer is added to every caption automatically, so don't write one.

{CLAIMS_POLICY}"""


def pack_text(p: SocialPack) -> str:
    return "\n".join([
        *(f"{v.hook}\n{v.script}\n{' '.join(v.on_screen_text)}\n{v.caption}\n{v.call_to_action}" for v in p.videos),
        *(f"{c.title}\n{' | '.join(c.slides)}\n{c.caption}" for c in p.carousels),
        p.newsletter.subject, p.newsletter.preview, p.newsletter.body,
    ])


def run(task: dict, llm) -> dict:
    paths = ["/", "/learn/", "/rules.html"] + [f"/learn/{s}.html" for s in publish.published_slugs()]
    facts = {k: {f: v[f] for f in publish.PUBLIC_FACT_FIELDS} for k, v in publish.verified_facts().items()}
    prompt = (f"Existing site paths: {paths}\nVerified facts:\n{json.dumps(facts, indent=1)}\n\n"
              f"CEO instructions: {task['instructions']}")
    pack = write_reviewed(llm, system=SYSTEM, prompt=prompt, schema=SocialPack, to_text=pack_text, facts=facts,
                          label="Social pack")
    return pack.model_dump()


def on_approve(task: dict) -> str:
    pack = SocialPack(**task["result"])
    disclaimer = config.DISCLAIMER_SHORT
    lines = [f"# Social pack — task #{task['id']} ({date.today().isoformat()})", ""]
    for i, v in enumerate(pack.videos, 1):
        lines += [f"## Video {i}", f"**Hook (on screen, first 2 seconds):** {v.hook}", "", v.script, "",
                  "**On-screen text:** " + " → ".join(v.on_screen_text), "",
                  f"**Caption:** {v.caption} {disclaimer}", "", f"**Call to action:** {v.call_to_action}", ""]
    for c in pack.carousels:
        lines += [f"## Carousel: {c.title}", *[f"{n}. {s}" for n, s in enumerate(c.slides, 1)], "",
                  f"**Caption:** {c.caption} {disclaimer}", ""]
    n = pack.newsletter
    lines += ["## Newsletter", f"**Subject:** {n.subject}  ", f"**Preview:** {n.preview}", "", n.body, "",
              f"_{disclaimer}_", "", f"Calculator link: {config.SITE_URL}/", ""]
    path = config.OUTBOX_DIR / f"{date.today().isoformat()}-task-{task['id']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    return f"Ready to post: {path.relative_to(config.ROOT)}"
