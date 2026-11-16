import json
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FFPROBE = shutil.which("ffprobe")


@pytest.fixture()
def studio_tmp(tmp_path, monkeypatch):
    """Point every studio write (scripts, media, manifest) at a temp folder; the curriculum stays read-only."""
    from studio import config
    site = tmp_path / "site"
    monkeypatch.setattr(config, "SCRIPTS_DIR", tmp_path / "scripts")
    monkeypatch.setattr(config, "OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(config, "SITE_DIR", site)
    monkeypatch.setattr(config, "MEDIA_DIR", site / "media" / "videos")
    monkeypatch.setattr(config, "VERTICAL_DIR", site / "media" / "vertical")
    monkeypatch.setattr(config, "MANIFEST", site / "media" / "videos" / "manifest.json")
    return tmp_path


def _first_lesson(with_risk_note: bool):
    from studio.script import load_curriculum
    for level in load_curriculum()["levels"]:
        for module in level["modules"]:
            for lesson in module["lessons"]:
                if bool(lesson.get("risk_note")) == with_risk_note:
                    return lesson
    pytest.skip("curriculum has no such lesson")


def _tiny_script(slug="tiny-test"):
    from studio.script import Scene, VideoScript
    return VideoScript(slug=slug, title="Tiny test", scenes=[
        Scene(kind="title", heading="A tiny test video", narration="This is a short test.", on_screen="Two seconds"),
        Scene(kind="end", heading="Your turn", narration="That is all.", on_screen="Try the calculator."),
    ])


def _probe(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,pix_fmt:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


# ---- Script stage ---------------------------------------------------------------------------------
def test_dry_run_generates_a_reviewed_script_with_fakellm(studio_tmp):
    from company.llm import FakeLLM
    from studio import config, script
    from studio.__main__ import main

    lesson = _first_lesson(with_risk_note=True)
    llm = FakeLLM()
    s = script.generate(lesson["slug"], llm, facts={})
    assert llm.calls[0] == "VideoScript" and "ClaimsReview" in llm.calls   # drafted, then AI-reviewed
    assert (s.slug, s.title, s.risk_note) == (lesson["slug"], lesson["title"], lesson["risk_note"])
    assert script._norm(lesson["risk_note"]) in script._norm(" ".join(x.narration for x in s.scenes))  # spoken
    assert s.scenes[0].kind == "title" and s.scenes[-1].kind == "end"
    assert script.check(s, {}) == []

    assert main(["script", lesson["slug"], "--dry-run"]) == 0       # the CLI path writes to scratch, not scripts/
    saved = config.OUT_DIR / "dry-run" / f"{lesson['slug']}.json"
    assert script.VideoScript.model_validate_json(saved.read_text()).slug == lesson["slug"]
    assert not config.SCRIPTS_DIR.exists()


def test_hype_script_is_rejected_at_generation_and_at_render(studio_tmp):
    from company.schemas import ClaimsReview
    from studio import script
    from studio.__main__ import main

    hype = script.VideoScript.example()
    hype.scenes[1].narration = "This fund is guaranteed to double your money. Act now!"

    class HypeLLM:
        calls = 0

        def structured(self, *, system, prompt, schema, effort="medium"):
            self.calls += 1
            return hype.model_copy(deep=True) if schema is script.VideoScript else ClaimsReview.example()

    llm = HypeLLM()
    with pytest.raises(ValueError, match="compliance check twice"):
        script.generate(_first_lesson(with_risk_note=False)["slug"], llm, facts={})
    assert llm.calls == 2                                              # one draft, one rewrite, then dropped

    hype.slug = "hype-test"
    script.save(hype)
    with pytest.raises(script.ScriptError, match="guarantee"):
        script.load("hype-test")
    assert main(["render", "hype-test", "--voice", "none"]) == 1       # the renderer refuses it too


def test_sample_scripts_and_fixed_screen_text_pass_the_claims_filter():
    from invest.claims import find_violations
    from studio import config, render, script

    paths = sorted((REPO / "studio" / "scripts").glob("*.json"))
    assert len(paths) >= 3
    facts = script.verified_public_facts()
    for p in paths:
        s = script.load(p, facts)
        assert script.find_lesson(s.slug), f"{s.slug} is not in the curriculum"
        assert 60 <= script.estimated_seconds(s) <= 130
    fixed = [config.AI_LABEL, config.EDU_LABEL, render.QUIZ_FOOTER, *render.PILLS.values()]
    assert find_violations("\n".join(fixed)) == []


# ---- Render stage ---------------------------------------------------------------------------------
@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_tiny_low_res_two_second_render_is_fast(studio_tmp):
    from studio import config
    from studio.render import render

    t = time.time()
    r = render(_tiny_script(), size=(320, 180), fps=12, seconds=2.0, update_manifest=False)
    assert time.time() - t < 30
    assert r.mp4.exists() and r.mp4.stat().st_size > 1000
    assert r.poster.exists() and r.captions.exists()
    assert r.narration == "none" and abs(r.duration - 2.0) < 0.01
    assert not config.MANIFEST.exists()                                # previews never touch the manifest
    if FFPROBE:
        info = _probe(r.mp4)
        video = [s for s in info["streams"] if s["codec_type"] == "video"][0]
        assert (video["codec_name"], video["width"], video["height"], video["pix_fmt"]) == ("h264", 320, 180, "yuv420p")
        assert abs(float(info["format"]["duration"]) - 2.0) < 0.2


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_tiny_render_with_offline_voice_has_audio(studio_tmp):
    from studio.voice import FliteVoice
    if not FliteVoice.available():
        pytest.skip("libflite not installed")
    from studio.render import render
    r = render(_tiny_script(), voice=FliteVoice(), size=(320, 180), fps=12, seconds=2.0, update_manifest=False)
    assert r.narration == "flite"
    if FFPROBE:
        assert {s["codec_type"] for s in _probe(r.mp4)["streams"]} == {"video", "audio"}


def test_growth_math_matches_the_site_calculator():
    from studio.charts import compact_money, money, nice_ticks, project
    final = project(25, 65, 100, 0.06)[-1]
    assert (money(final[1]), money(final[2])) == ("$191,700", "$48,000")
    assert money(project(25, 65, 100, 0.06, delay=5)[-1][1]) == "$138,000"
    assert compact_money(999960) == "$1M" and compact_money(247400) == "$247.4K"
    assert nice_ticks(191700, 4) == [0, 50000, 100000, 150000, 200000]
    node = shutil.which("node")
    if node:  # exact agreement with calc.js, the calculator's own math
        js = ("const P=require(process.argv[1]);const r=P.project({startAge:22,endAge:60,monthly:250,rate:0.07,"
              "delay:3});console.log(JSON.stringify(r.points.map(p=>[p.balance,p.contributed])))")
        out = subprocess.run([node, "-e", js, str(REPO / "invest" / "site" / "assets" / "calc.js")],
                             capture_output=True, text=True, check=True).stdout
        ours = [(b, c) for _, b, c in project(22, 60, 250, 0.07, delay=3)]
        for (jb, jc), (pb, pc) in zip(json.loads(out), ours, strict=True):
            assert abs(jb - pb) < 1e-6 and jc == pc


# ---- Captions -------------------------------------------------------------------------------------
def test_vtt_is_valid_and_timed_from_the_narration():
    from studio import config, script
    from studio.captions import chunks, to_vtt, validate_vtt
    from studio.render import plan_timeline

    s = script.load(REPO / "studio" / "scripts" / "compound-growth-explained.json")
    tl = plan_timeline(s, voice=None)
    vtt = to_vtt(tl.cues)
    assert vtt.startswith("WEBVTT\n") and validate_vtt(vtt, tl.duration) == []
    narration = " ".join(sc.narration for sc in s.scenes)
    assert " ".join(c.text for c in tl.cues).split() == narration.split()   # every spoken word, in order
    words = len(narration.split())
    assert 125 <= tl.wpm <= 150, tl.wpm                                     # words-per-minute timing
    assert abs(tl.cues[0].start - 0.9) < 1e-6 and tl.cues[-1].end <= tl.duration
    assert all(len(c) <= 84 for c in chunks(narration)) and words > 100
    # Bad files are caught.
    assert validate_vtt("hello")
    assert validate_vtt("WEBVTT\n\n00:00:02.000 --> 00:00:01.000\nbackwards\n")
    assert validate_vtt("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\na\n\n00:00:01.000 --> 00:00:03.000\nb\n")
    # The committed sample captions are valid for their videos.
    doc = json.loads(config.MANIFEST.read_text())
    for slug, e in doc["videos"].items():
        assert validate_vtt((config.SITE_DIR / e["captions"]).read_text(), e["duration_s"] + 1) == [], slug


# ---- Manifest -------------------------------------------------------------------------------------
def test_committed_manifest_matches_the_contract():
    from studio import config, manifest
    from studio.script import find_lesson

    doc = json.loads(config.MANIFEST.read_text())
    assert manifest.validate(doc) == []
    assert len(doc["videos"]) >= 3
    for slug, e in doc["videos"].items():
        assert find_lesson(slug), slug
        assert e["approved"] is False                                  # only the founder approves
        assert 60 <= e["duration_s"] <= 125
    size = sum(p.stat().st_size for p in (config.SITE_DIR / "media").rglob("*") if p.is_file())
    assert size < 15_000_000, f"media is {size / 1e6:.1f} MB"


def test_manifest_upsert_approve_and_reset(studio_tmp):
    from studio import config, manifest

    for ext in ("mp4", "vtt", "jpg"):
        config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        (config.MEDIA_DIR / f"what-a-budget-is-for.{ext}").write_bytes(b"x")
    entry = manifest.upsert("what-a-budget-is-for", 93.6, "none")
    assert entry == {"mp4": "media/videos/what-a-budget-is-for.mp4", "captions": "media/videos/what-a-budget-is-for.vtt",
                     "poster": "media/videos/what-a-budget-is-for.jpg", "duration_s": 94, "narration": "none",
                     "ai_label": "Made with AI, reviewed by a person", "approved": False}
    assert manifest.approve("what-a-budget-is-for")["approved"] is True
    manifest.upsert("what-a-budget-is-for", 95, "none")                 # a re-render needs a fresh approval
    doc = manifest.load()
    assert doc["videos"]["what-a-budget-is-for"]["approved"] is False
    assert manifest.validate(doc) == []
    with pytest.raises(KeyError):
        manifest.approve("no-such-video")
    doc["videos"]["what-a-budget-is-for"]["extra"] = 1
    assert manifest.validate(doc)


def test_speakable_fixes_offline_voice_pronunciation():
    from studio.voice import get_voice, speakable
    assert speakable("Made with AI, reviewed by a person") == "Made with A.I., reviewed by a person"
    assert speakable("A Roth IRA or a 401(k)") == "A Roth I.R.A. or a four oh one K"
    assert get_voice("none").synthesize("anything") is None
    with pytest.raises(ValueError):
        get_voice("no-such-voice")
