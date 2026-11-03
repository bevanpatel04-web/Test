"""Structured outputs each agent must return. Claude's replies are validated against these."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

AgentName = Literal["water_data", "content", "marketing"]


class PlannedTask(BaseModel):
    agent: AgentName
    title: str
    instructions: str
    city_slug: Optional[str] = Field(None, description="Slug from the city list, when the task is about one city")


class TaskPlan(BaseModel):
    reasoning: str = Field(description="One or two sentences on why these tasks matter most today")
    tasks: list[PlannedTask]

    @classmethod
    def example(cls) -> "TaskPlan":
        return cls(
            reasoning="Verify data before writing about it; publish pages for verified cities.",
            tasks=[
                PlannedTask(agent="water_data", title="Verify Phoenix water data",
                            instructions="Check the latest CCR.", city_slug="phoenix-az"),
                PlannedTask(agent="content", title="Write Phoenix city page",
                            instructions="Use verified data.", city_slug="phoenix-az"),
                PlannedTask(agent="marketing", title="Weekly content pack",
                            instructions="Pins, two video scripts and a newsletter."),
            ],
        )


class CityVerification(BaseModel):
    city_slug: str
    utility: str
    hardness_mg_l: Optional[float] = Field(description="Typical/average total hardness in mg/L as CaCO3; null if not found")
    disinfectant: Literal["chlorine", "chloramine", "unknown"]
    report_year: Optional[int] = None
    sources: list[str] = Field(description="URLs of the utility report(s) the numbers came from")
    confidence: Literal["low", "medium", "high"]
    notes: str

    @classmethod
    def example(cls) -> "CityVerification":
        return cls(city_slug="phoenix-az", utility="City of Phoenix Water Services", hardness_mg_l=240,
                   disinfectant="chlorine", report_year=2025,
                   sources=["https://www.phoenix.gov/waterservices/waterquality"],
                   confidence="high", notes="Average of reported range (dry-run example).")


class FAQ(BaseModel):
    question: str
    answer: str


class CityPage(BaseModel):
    slug: str
    title: str
    meta_description: str
    intro: str
    hardness_section: str
    disinfectant_section: str
    what_you_can_do: list[str]
    faq: list[FAQ]

    @classmethod
    def example(cls) -> "CityPage":
        return cls(
            slug="phoenix-az", title="Phoenix Water and Sensitive Skin",
            meta_description="Phoenix tap water is very hard and chlorinated. What that means for sensitive skin.",
            intro="Phoenix has some of the hardest tap water in the US.",
            hardness_section="Hardness averages around 240 mg/L, which is very hard.",
            disinfectant_section="Phoenix disinfects with chlorine.",
            what_you_can_do=["Use a carbon or KDF shower filter with chlorine test results.",
                             "Keep showers short and lukewarm."],
            faq=[FAQ(question="Does a shower filter soften water?",
                     answer="Generally no. Filters reduce chlorine; only a softener reduces hardness.")],
        )


class ClaimsReview(BaseModel):
    approved: bool
    issues: list[str] = Field(description="Each problematic sentence and why; empty if approved")

    @classmethod
    def example(cls) -> "ClaimsReview":
        return cls(approved=True, issues=[])


class Pin(BaseModel):
    title: str
    description: str
    target_path: str = Field(description="Site path the pin links to, e.g. / or /cities/phoenix-az.html")


class VideoScript(BaseModel):
    hook: str = Field(description="First 2 seconds, on-screen text")
    script: str
    call_to_action: str


class Newsletter(BaseModel):
    subject: str
    body: str


class MarketingPack(BaseModel):
    pins: list[Pin]
    video_scripts: list[VideoScript]
    newsletter: Newsletter

    @classmethod
    def example(cls) -> "MarketingPack":
        return cls(
            pins=[Pin(title="Is your water hard on your skin?", description="Check your ZIP free.", target_path="/")],
            video_scripts=[VideoScript(hook="My eczema flared every time I moved cities.",
                                       script="Here's what I learned about water...",
                                       call_to_action="Check your ZIP code at the link in bio.")],
            newsletter=Newsletter(subject="What's in your shower?", body="This week we checked..."),
        )


class DailyBrief(BaseModel):
    headline: str
    completed: list[str]
    needs_your_approval: list[str]
    next_up: list[str]
    risks_or_blockers: list[str]

    @classmethod
    def example(cls) -> "DailyBrief":
        return cls(headline="Dry run: the team ran end to end.", completed=["Ran all agents in dry-run mode."],
                   needs_your_approval=["Review the queued items."], next_up=["Connect the API key."],
                   risks_or_blockers=[])
