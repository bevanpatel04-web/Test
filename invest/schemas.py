"""Structured outputs each agent must return. Claude's replies are validated against these."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Shared with the Mildwell team: generic shapes for the brief, FAQs and compliance reviews.
from company.schemas import FAQ, ClaimsReview, DailyBrief  # noqa: F401

AgentName = Literal["facts", "lessons", "social"]


class PlannedTask(BaseModel):
    agent: AgentName
    title: str
    instructions: str
    key: Optional[str] = Field(None, description="Fact key (facts agent) or lesson slug (lessons agent); empty for social")


class TaskPlan(BaseModel):
    reasoning: str = Field(description="One or two sentences on why these tasks matter most today")
    tasks: list[PlannedTask]

    @classmethod
    def example(cls) -> "TaskPlan":
        return cls(
            reasoning="Verify the facts lessons depend on, publish a lesson that needs no facts, and refresh social.",
            tasks=[
                PlannedTask(agent="facts", title="Verify the 2027 Roth IRA income limits",
                            instructions="Use the IRS release or notice.", key="roth_ira_phaseout_single_2027"),
                PlannedTask(agent="lessons", title="Write the compound growth lesson",
                            instructions="Use a $100/month example.", key="compound-growth"),
                PlannedTask(agent="lessons", title="Write the Roth IRA basics lesson",
                            instructions="First-job angle.", key="roth-ira-basics"),
                PlannedTask(agent="social", title="Weekly social pack",
                            instructions="Two short videos, one carousel, one newsletter."),
            ],
        )


class FactVerification(BaseModel):
    key: str
    value: Optional[float] = Field(description="The number itself (percent as 22.36, dollars as 7500); null if not numeric or not found")
    display: str = Field(description="How the site shows it, e.g. '22.36%', '$7,500', '$158,000 to $173,000'")
    as_of: str = Field(description="Period or date the figure applies to, e.g. 'Q3 2026', '2027', '2025 survey'")
    source_name: str = Field(description="Short publisher name, e.g. 'IRS', 'Federal Reserve G.19'")
    sources: list[str] = Field(description="URLs of the official pages the figure came from")
    confidence: Literal["low", "medium", "high"]
    notes: str

    @classmethod
    def example(cls) -> "FactVerification":
        return cls(key="roth_ira_phaseout_single_2027", value=None, display="$158,000 to $173,000", as_of="2027",
                   source_name="IRS", sources=["https://www.irs.gov/newsroom/example-dry-run"],
                   confidence="high", notes="Dry-run example.")


class LessonSection(BaseModel):
    heading: str
    body: str = Field(description="Plain paragraphs; separate paragraphs with a blank line")


class Lesson(BaseModel):
    slug: str
    title: str
    meta_description: str
    hook: str = Field(description="One or two sentences that make a 20-year-old want to keep reading")
    sections: list[LessonSection]
    key_takeaways: list[str]
    try_it: str = Field(description="One sentence inviting the reader to try the calculator with a specific scenario")
    faq: list[FAQ]
    facts_used: list[str] = Field(description="Keys of every verified fact the lesson cites; empty if none")

    @classmethod
    def example(cls) -> "Lesson":
        return cls(
            slug="compound-growth", title="Compound growth, explained with $100 a month",
            meta_description="How $100 a month could grow over time, why starting earlier matters, and the risks.",
            hook="The money you invest at 21 has more years to grow than the money you invest at 31.",
            sections=[
                LessonSection(heading="Growth on growth",
                              body="Compound growth means your gains can earn gains of their own.\n\nIt works in both directions: losses compound too."),
                LessonSection(heading="The catch",
                              body="Markets don't move in a straight line, and investments can lose money."),
            ],
            key_takeaways=["Time is the input you control most.", "Growth is never promised."],
            try_it="Try $100 a month starting at 21 vs. 26 in the calculator.",
            faq=[FAQ(question="Is 6% a year realistic?",
                     answer="Nobody knows future returns. The calculator lets you test cautious and optimistic rates.")],
            facts_used=[],
        )


class VideoScript(BaseModel):
    hook: str = Field(description="On-screen text for the first 2 seconds")
    script: str = Field(description="What the founder says to camera, under 45 seconds")
    on_screen_text: list[str]
    caption: str
    call_to_action: str


class Carousel(BaseModel):
    title: str
    slides: list[str] = Field(description="Text for each slide, 5-8 slides, short")
    caption: str


class Newsletter(BaseModel):
    subject: str
    preview: str
    body: str


class SocialPack(BaseModel):
    videos: list[VideoScript]
    carousels: list[Carousel]
    newsletter: Newsletter

    @classmethod
    def example(cls) -> "SocialPack":
        return cls(
            videos=[VideoScript(hook="What waiting 5 years to invest could cost",
                                script="I ran the numbers on $100 a month... (dry run)",
                                on_screen_text=["$100/month", "Start at 21 vs 26", "Hypothetical 6%/yr"],
                                caption="The math on starting early, and the risk that comes with it.",
                                call_to_action="Try your own numbers at the link in bio.")],
            carousels=[Carousel(title="5 investing red flags", slides=["Promised returns", "Pressure to act fast"],
                                caption="Save this for the next time someone pitches you.")],
            newsletter=Newsletter(subject="The $100 experiment", preview="What time does to small amounts",
                                  body="This week: compound growth, and why it cuts both ways. (dry run)"),
        )
