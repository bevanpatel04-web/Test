#!/usr/bin/env python3
"""Patient Money learning app: membership unit economics, content cost and growth path.

Run it:   python3 docs/finance-app/model.py
Needs:    Python 3.8+ and nothing else (standard library only).

Edit the INPUTS dict below. Everything after it is arithmetic.

How each input is labeled:
  SOURCED     a published figure. URL and the date we checked it are in the comment.
  DERIVED     calculated from sourced figures.
  ASSUMPTION  our own estimate. The spread between the three scenarios is our
              honest range. These are what the first 90 days must measure.

Words used in the output:
  free signup   someone who creates a free account (email) and can use Level 1.
  member        a paying member (monthly or annual plan).
  conversion    share of free signups who become members within about 3 months.
  MRR           monthly recurring revenue, before fees. An annual plan counts as
                its price / 12 each month (the usual convention), even though
                the cash arrives up front.
  gross profit  what a member pays, minus payment fees, refunds and the running
                cost of serving them. It does not pay the founder.
  LTV           lifetime value: expected gross profit from one new member over
                their whole membership.
  CAC           customer acquisition cost: marketing spend per new member.

Main simplifications (read before trusting the output):
  1. Monthly members leave at a flat monthly churn rate. Real churn is higher in
     month 1 and lower later; a flat rate gives the same average lifetime.
  2. Annual members renew once at the "first renewal" rate, then at the "later
     renewal" rate each year after.
  3. Conversions from a month's free signups arrive over 3 months
     (conversion_timing). Later conversions (e.g. from email a year on) are upside.
  4. Paid channels (creators, ads) run a test for a few months. After the test the
     model keeps paying for a channel only if its LTV/CAC is at least
     keep_channel_if_ltv_cac. A passing channel's budget then grows with revenue.
     Costs per signup stay flat as spend grows (in reality they rise).
  5. The founder's own time is not cash. It is shown in hours and, where useful,
     valued at founder_hour_value so you can see what it is worth.
  6. Sales tax/VAT is collected on top of the price and passed on, so it is
     excluded from revenue. The cost of the tax tool is included in fees.
"""
from __future__ import annotations

# =============================================================================
# INPUTS: edit these
# =============================================================================
INPUTS = {
    "shared": {
        # ---- Prices (DRAFT, docs/app/BRIEF.md; see pricing.md) ----
        "price_monthly": 8.00,
        "price_annual": 60.00,
        "student_discount": 0.40,   # ASSUMPTION: 40% off for verified students (pricing.md)
        # Benchmark, SOURCED: RevenueCat State of Subscription Apps 2026, Education
        # category medians: $9.99 a month, $44.99 a year; D35 download-to-paid 3.1% (iOS).
        #   https://www.revenuecat.com/state-of-subscription-apps-2026-education (checked 2026-11-15)

        # ---- Payment fees ----
        # SOURCED: Stripe US: cards 2.9% + $0.30; Stripe Billing (subscriptions) 0.7% of
        # billing volume; Stripe Tax 0.5% per transaction (no-code); dispute fee $15.
        #   https://stripe.com/pricing (checked 2026-11-15)
        "stripe_pct": 0.029,
        "stripe_fixed": 0.30,
        "stripe_billing_pct": 0.007,
        "stripe_tax_pct": 0.005,
        # SOURCED: Apple Small Business Program (under $1M proceeds a year): 15%;
        # standard rate 30%. https://developer.apple.com/app-store/small-business-program/
        # (checked 2026-11-15). Subscriptions drop to 15% after a subscriber's first paid
        # year even without the program (https://www.revenuecat.com/blog/engineering/app-store-fees).
        # Google Play subscriptions: 15% (https://support.google.com/googleplay/android-developer/answer/112622).
        # US apps may link out to web checkout; Apple charges 0% on US link-outs while a
        # court sets a rate (Apple proposed 15%), per reports as of Aug 2026:
        # https://macdailynews.com/2026/08/14/u-s-supreme-court-clears-path-for-app-store-commission-showdown-as-apple-must-defend-its-rates-in-lower-court/
        "app_store_rates": [0.15, 0.30],

        # ---- Claude API, $ per million tokens: (input, output, cache read) ----
        # SOURCED: platform.claude.com/docs/en/about-claude/pricing (as of 2026-11-03):
        # Opus 5.5 $4/$20 (cache reads $0.20), Sonnet 5.5 $2/$10 (cache reads $0.10),
        # Haiku 5.5 $0.10/$0.50. Haiku cache-read price is an ASSUMPTION (10% of input).
        # Batch API: 50% off for jobs that can wait (same page).
        "claude": {"opus": (4.00, 20.00, 0.20),
                   "sonnet": (2.00, 10.00, 0.10),
                   "haiku": (0.10, 0.50, 0.01)},
        "batch_discount": 0.50,

        # ---- Video hosting ----
        # SOURCED: Cloudflare Stream: $5 per 1,000 minutes stored per month (prepaid),
        # $1 per 1,000 minutes delivered; encoding free.
        #   https://developers.cloudflare.com/stream/pricing/ (checked 2026-11-15)
        "stream_per_1000_min_delivered": 1.00,
        "stream_per_1000_min_stored": 5.00,

        # ---- The library ----
        "lessons": 45,              # BRIEF.md: about 45 lessons, 5 levels
        "free_lessons": 9,          # ASSUMPTION: Level 1 = about 1/5 of the library
        "clips_per_lesson": 2,      # ASSUMPTION: short clips cut from each lesson for TikTok/Reels
        "tts_chars_per_minute": 900,  # ASSUMPTION: about 150 spoken words x 6 characters
        "founder_hour_value": 40.0,   # ASSUMPTION: what an hour of founder time is worth ($25-75)

        # ---- Email ----
        # SOURCED: Kit Creator plan $33/month at 1,000 subscribers; free Newsletter plan
        # up to 10,000 (fewer automations). https://kit.com/pricing (checked 2026-11-15)
        # ASSUMPTION: about $0.009 per extra contact per month above 1,000 (rough fit to
        # Kit's tiers; check before you pass 5,000 contacts).
        "email_base_month": 33.0,
        "email_per_contact_above_1k": 0.009,
        "free_list_monthly_decay": 0.04,  # ASSUMPTION: free contacts who unsubscribe or go cold

        # ---- Fixed monthly running costs ----
        "fixed_monthly": {
            # SOURCED: Vercel Pro $20/month (https://vercel.com/pricing); Cloudflare Workers
            # Paid from $5/month (https://developers.cloudflare.com/workers/platform/pricing/).
            "Web hosting (Vercel Pro or Cloudflare)": 20.0,
            # DERIVED: about 45 x 3 min + clips < 1,000 minutes = one $5 block (Cloudflare Stream).
            "Video storage (1,000-minute block)": 5.0,
            # SOURCED: ElevenLabs Creator $22/month (https://elevenlabs.io/pricing/api).
            "Voice (TTS) plan for fixes and refresh": 22.0,
            "Claude API for support drafts and social captions": 30.0,  # ASSUMPTION
            "Bookkeeping / accounting tool": 20.0,                      # ASSUMPTION
            # SOURCED: Cloudflare Registrar .com about $10.46/yr at cost (third-party
            # listings, 2026; https://domainoffer.net/tld/com/cloudflare). Rounded up.
            "Domain (per month)": 1.0,
        },

        # ---- Acquisition rules ----
        "conversion_timing": [0.5, 0.3, 0.2],  # ASSUMPTION: share of conversions in months 0, 1, 2
        "keep_channel_if_ltv_cac": 1.5,        # ASSUMPTION: keep paying for a channel above this
        "reinvest_share": 0.30,                # ASSUMPTION: share of last month's net revenue for passing paid channels
        "max_paid_budget_month": 10_000,       # ASSUMPTION: cap per channel (costs per signup rise with spend)

        # ---- Report settings ----
        "mrr_targets": [10_000, 50_000, 100_000],
        "months_to_simulate": 72,
        "conversion_grid": [0.02, 0.04, 0.06, 0.08],
        "cost_per_signup_grid": [1.0, 2.5, 5.0, 10.0],

        # ---- Pricing options compared in section 8 (see pricing.md) ----
        # conv_mult / churn_mult / renewal_mult are ASSUMPTIONS relative to option A.
        "pricing_options": {
            "A. $8/mo or $60/yr (draft)":
                {"monthly": 8.0, "annual": 60.0, "conv_mult": 1.00, "churn_mult": 1.00,
                 "renewal_mult": 1.00, "annual_share_add": 0.00},
            "A2. $10/mo or $60/yr (pricier monthly)":
                {"monthly": 10.0, "annual": 60.0, "conv_mult": 0.95, "churn_mult": 1.00,
                 "renewal_mult": 1.00, "annual_share_add": 0.15},
            "B. $12/mo or $90/yr":
                {"monthly": 12.0, "annual": 90.0, "conv_mult": 0.75, "churn_mult": 1.10,
                 "renewal_mult": 0.95, "annual_share_add": 0.00},
            "C. $149 one-time lifetime path":
                {"lifetime": 149.0, "conv_mult": 0.70, "active_months": 24},
        },
        # Gifts (pricing.md): a 12-month gift sold at the annual price, no auto-renew.
        "gift_price": 60.0,
        "gift_recipient_renews": 0.20,   # ASSUMPTION: share who pay for a second year themselves

        # ---- Launch budget, first 6 months (see launch-budget.md) ----
        # None = filled in by the model from the content-cost section.
        # Sources: legal at $362/hour, Clio national average lawyer rate (updated
        # Oct 2026, https://www.clio.com/resources/legal-trends/compare-lawyer-rates/);
        # USPTO trademark base fee $350 per class (since Jan 2025; e.g.
        # https://beancount.io/blog/2026/09/27/how-much-does-trademark-cost-2026-uspto-fees-guide);
        # professional liability about $88/month (Insureon average,
        # https://www.insureon.com/small-business-insurance/professional-liability/cost);
        # creator posts $200-1,000 for 10K-50K followers (TTCalculator/Hootsuite 2026,
        # https://ttcalculator.net/learn/brand-deal-rates-by-followers/); Apple Developer
        # Program $99/year, Google Play $25 once (well-known list prices).
        "launch_budget": [
            # (item, lean $, full $, note)
            ("Video library: Claude + voice, 45 lessons (x2 for retakes)", None, None,
             "model section 3, cash only"),
            ("Voice (TTS) plan while producing", 22 * 2, 99 * 2,
             "ElevenLabs Creator 2 mo / Pro 2 mo"),
            ("Expert fact review of all lessons", 0, 1_500,
             "ASSUMPTION: 15 h x $100 freelance financial educator"),
            ("Music, fonts, design assets", 0, 300, "ASSUMPTION"),
            ("Domain (.com, 1 year)", 11, 11, "Cloudflare at cost"),
            ("Hosting + video, 6 months", 60, 150, "Cloudflare $5+$5 / Vercel $20+$5"),
            ("Email tool, 6 months", 0, 198, "Kit free / Creator $33"),
            ("Legal review (terms, privacy, refunds, disclaimers)", 1_100, 2_900,
             "3 h / 8 h at $362"),
            ("Trademark filing (1 class)", 0, 350, "USPTO base fee"),
            ("Company formation (if not done)", 150, 300, "ASSUMPTION: state fees vary"),
            ("Insurance, 6 months", 0, 530, "Insureon avg ~$88/mo"),
            ("Creator tests", 600, 4_000, "lean: 2-3 micro creators"),
            ("Paid ads test", 300, 2_000, "Meta/TikTok, small test"),
            ("Claude API for the app, support and social, 6 months", 180, 360,
             "ASSUMPTION $30 / $60 a month"),
            ("Bookkeeping tool, 6 months", 0, 120, "lean: spreadsheet"),
            ("App store accounts (for later native apps)", 0, 124, "Apple $99/yr + Google $25"),
        ],
        "launch_contingency": {"lean": 0.15, "full": 0.10},
    },

    "scenarios": {
        # ---------------------------------------------------------------------
        "conservative": {
            # -- Plan mix and discounts --
            "annual_share": 0.35,     # ASSUMPTION: share of new members who pick annual
            "student_share": 0.25,    # ASSUMPTION: share of members on the student price
            "refund_rate": 0.05,      # ASSUMPTION (RevenueCat: app refund medians ~3-4%)
            "app_store_share": 0.0,   # web first (BRIEF.md); see section 1 for app-store cases

            # -- Funnel --
            # ASSUMPTION ranges anchored on: RevenueCat SOSA 2026 freemium median 2.1%
            # D35 conversion (all categories) and 3.1% for Education (iOS, includes hard
            # paywalls); ChartMogul: 3-5% "good" for freemium self-serve
            # (https://chartmogul.com/reports/saas-conversion-report/); First Page Sage via
            # Userpilot: 2.6% for EdTech (https://userpilot.com/blog/freemium-to-premium).
            "conversion": 0.02,
            # ASSUMPTION anchored on RevenueCat SOSA 2026: monthly plans keep a median
            # ~8-10% after 12 months (implies ~18-19% average monthly churn, so this
            # conservative case is about the median app); annual plans' median first
            # renewal is 23-40% by category.
            #   https://www.revenuecat.com/sosa-2026-insights-part-2 (checked 2026-11-15)
            "monthly_churn": 0.20,
            "annual_first_renewal": 0.20,
            "annual_later_renewal": 0.45,

            # -- Running costs per paying member per month --
            "video_minutes_per_member_month": 20,   # ASSUMPTION (incl. rewatching)
            "free_video_minutes_per_signup": 15,    # ASSUMPTION: Level 1 viewing, once
            "hosting_var_per_member_month": 0.05,   # ASSUMPTION: database, auth, logs
            "support_tickets_per_member_month": 0.06,  # ASSUMPTION
            "minutes_per_ticket": 12,               # ASSUMPTION
            "support_cost_per_hour": 30.0,          # ASSUMPTION: contractor rate, or founder time
            # AI tutor if added later: questions a month, model, tokens in/out per question
            "ai_tutor": {"on": False, "questions": 20, "model": "opus", "tin": 6_000, "tout": 600},

            # -- Content production, per lesson --
            # Each step: (model, calls per lesson, input tokens per call, output tokens per call)
            # ASSUMPTION: token counts are estimates for a 2-4 minute lesson.
            "content_steps": {
                "Script drafts": ("opus", 4, 15_000, 3_000),
                "Compliance + fact review": ("opus", 4, 12_000, 2_000),
                "Scenes, charts, animation code": ("opus", 6, 30_000, 8_000),
                "Short-clip hooks + captions": ("sonnet", 2, 5_000, 1_000),
            },
            "token_waste_factor": 2.0,    # ASSUMPTION: failed runs and retries
            "cached_input_share": 0.0,    # ASSUMPTION: share of input served from prompt cache
            "batch_share": 0.0,           # ASSUMPTION: share of calls sent via Batch API
            "minutes_per_lesson": 4.0,    # BRIEF.md: 2-4 minute videos
            # TTS: price per 1,000 characters and takes per finished minute.
            # SOURCED: Google Cloud Studio voices $160 per 1M characters
            # (https://cloud.google.com/text-to-speech/pricing, checked 2026-11-15).
            "tts_price_per_1k_chars": 0.16,
            "tts_takes": 3.0,             # ASSUMPTION: re-records for fixes
            "review_minutes_per_lesson": 90,  # ASSUMPTION: founder watches, checks facts, approves
            "review_minutes_per_clip": 8,
            "refresh_share_per_year": 0.35,   # ASSUMPTION: lessons re-made each year (limits, rules change)
            "fact_check_minutes_per_lesson_year": 15,

            # -- Acquisition --
            # Organic short video (clips from the lessons): free signups in month 1,
            # monthly growth, cap. ASSUMPTION; this is the biggest unknown in the model.
            "organic_m1": 100, "organic_growth": 0.06, "organic_cap": 2_000,
            "social_hours_per_week": 8,   # ASSUMPTION: founder time posting and replying
            # Creators (flat-fee sponsored posts). ASSUMPTION within the sourced price range
            # ($200-1,000 per post for 10K-50K followers, 2026 guides; see launch_budget).
            "creator_cost_per_post": 600, "creator_views_per_post": 15_000,
            "creator_click_rate": 0.004, "creator_signup_rate": 0.25,
            "creator_test_budget": 200, "creator_test_months": (2, 4),
            # Paid ads (Meta/TikTok). SOURCED range: 2026 third-party benchmarks put Meta
            # traffic CPC around $0.60 and education lead CPC $1.25-2.10, finance higher
            # (https://www.webtonic.io/blog/education-coaching-facebook-ads-statistics,
            # https://searchengineland.com/facebook-ad-costs-fall-as-traffic-and-lead-performance-improves-report-488433).
            "ads_cpc": 2.10, "ads_signup_rate": 0.15,
            "ads_test_budget": 100, "ads_test_months": (3, 5),
        },
        # ---------------------------------------------------------------------
        "base": {
            "annual_share": 0.50,
            "student_share": 0.20,
            "refund_rate": 0.03,
            "app_store_share": 0.0,

            "conversion": 0.04,
            "monthly_churn": 0.15,
            "annual_first_renewal": 0.30,
            # SOURCED-ish: a secondary write-up of RevenueCat data reports 44-64% median
            # retention at the second annual renewal (unverified against RevenueCat).
            "annual_later_renewal": 0.55,

            "video_minutes_per_member_month": 15,
            "free_video_minutes_per_signup": 10,
            "hosting_var_per_member_month": 0.03,
            "support_tickets_per_member_month": 0.04,
            "minutes_per_ticket": 10,
            "support_cost_per_hour": 30.0,
            # DERIVED: 10 questions on Sonnet 5.5 at 4,000 in + 400 out = about $0.10/month.
            "ai_tutor": {"on": False, "questions": 10, "model": "sonnet", "tin": 4_000, "tout": 400},

            "content_steps": {
                "Script drafts": ("opus", 3, 12_000, 2_500),
                "Compliance + fact review": ("opus", 3, 10_000, 1_500),
                "Scenes, charts, animation code": ("sonnet", 4, 25_000, 6_000),
                "Short-clip hooks + captions": ("sonnet", 2, 4_000, 800),
            },
            "token_waste_factor": 1.5,
            "cached_input_share": 0.30,
            "batch_share": 0.0,
            "minutes_per_lesson": 3.0,
            # SOURCED: ElevenLabs API v3 / Multilingual v2 $0.08 per 1K characters;
            # Flash/Turbo $0.04 (https://elevenlabs.io/pricing/api, checked 2026-11-15).
            "tts_price_per_1k_chars": 0.08,
            "tts_takes": 2.0,
            "review_minutes_per_lesson": 45,
            "review_minutes_per_clip": 5,
            "refresh_share_per_year": 0.25,
            "fact_check_minutes_per_lesson_year": 10,

            "organic_m1": 300, "organic_growth": 0.10, "organic_cap": 8_000,
            "social_hours_per_week": 6,
            "creator_cost_per_post": 400, "creator_views_per_post": 25_000,
            "creator_click_rate": 0.008, "creator_signup_rate": 0.30,
            "creator_test_budget": 400, "creator_test_months": (2, 6),
            "ads_cpc": 1.20, "ads_signup_rate": 0.25,
            "ads_test_budget": 300, "ads_test_months": (3, 6),
        },
        # ---------------------------------------------------------------------
        "optimistic": {
            "annual_share": 0.60,
            "student_share": 0.15,
            "refund_rate": 0.02,
            "app_store_share": 0.0,

            "conversion": 0.07,
            "monthly_churn": 0.09,
            "annual_first_renewal": 0.40,
            "annual_later_renewal": 0.65,

            "video_minutes_per_member_month": 12,
            "free_video_minutes_per_signup": 8,
            "hosting_var_per_member_month": 0.02,
            "support_tickets_per_member_month": 0.02,
            "minutes_per_ticket": 8,
            "support_cost_per_hour": 30.0,
            "ai_tutor": {"on": False, "questions": 10, "model": "haiku", "tin": 4_000, "tout": 400},

            "content_steps": {
                "Script drafts": ("sonnet", 2, 10_000, 2_000),
                "Compliance + fact review": ("opus", 2, 8_000, 1_200),
                "Scenes, charts, animation code": ("sonnet", 3, 20_000, 5_000),
                "Short-clip hooks + captions": ("haiku", 2, 4_000, 800),
            },
            "token_waste_factor": 1.2,
            "cached_input_share": 0.50,
            "batch_share": 0.50,
            "minutes_per_lesson": 2.5,
            # SOURCED: Google Cloud Chirp 3 HD voices $30 per 1M characters (same page).
            "tts_price_per_1k_chars": 0.03,
            "tts_takes": 1.5,
            "review_minutes_per_lesson": 30,
            "review_minutes_per_clip": 3,
            "refresh_share_per_year": 0.15,
            "fact_check_minutes_per_lesson_year": 5,

            "organic_m1": 600, "organic_growth": 0.15, "organic_cap": 25_000,
            "social_hours_per_week": 5,
            "creator_cost_per_post": 250, "creator_views_per_post": 50_000,
            "creator_click_rate": 0.012, "creator_signup_rate": 0.40,
            "creator_test_budget": 800, "creator_test_months": (2, 6),
            "ads_cpc": 0.60, "ads_signup_rate": 0.35,
            "ads_test_budget": 500, "ads_test_months": (3, 6),
        },
    },
}

SCENARIOS = ("conservative", "base", "optimistic")

# =============================================================================
# CALCULATIONS: no need to edit below this line
# =============================================================================


# ---- 1. Revenue per member --------------------------------------------------
def avg_price(price, s, sh):
    """Average price actually paid, after the student discount."""
    return price * (1.0 - s["student_share"] * sh["student_discount"])


def kept(price, s, sh, store_rate=None):
    """What we keep from one payment after processor/store fees and refunds."""
    if store_rate is None:
        fee = price * (sh["stripe_pct"] + sh["stripe_billing_pct"] + sh["stripe_tax_pct"]) + sh["stripe_fixed"]
    else:
        fee = price * store_rate
    return price * (1.0 - s["refund_rate"]) - fee


def kept_blended(price, s, sh):
    """Web and app-store members mixed by app_store_share (app store at the 15% rate)."""
    w = s["app_store_share"]
    return (1 - w) * kept(price, s, sh) + w * kept(price, s, sh, sh["app_store_rates"][0])


# ---- 3. Content cost --------------------------------------------------------
def call_cost(sh, model, tin, tout, cached=0.0, batch=0.0):
    pin, pout, pcache = sh["claude"][model]
    cost = (tin * (1 - cached) * pin + tin * cached * pcache + tout * pout) / 1e6
    return cost * (1 - batch * sh["batch_discount"])


def content_cost(s, sh):
    steps = {}
    for label, (model, calls, tin, tout) in s["content_steps"].items():
        steps[label] = calls * call_cost(sh, model, tin, tout, s["cached_input_share"], s["batch_share"]) \
            * s["token_waste_factor"]
    claude = sum(steps.values())
    tts_per_min = sh["tts_chars_per_minute"] / 1000.0 * s["tts_price_per_1k_chars"] * s["tts_takes"]
    tts = tts_per_min * s["minutes_per_lesson"]
    review_min = s["review_minutes_per_lesson"] + sh["clips_per_lesson"] * s["review_minutes_per_clip"]
    cash = claude + tts
    n = sh["lessons"]
    hv = sh["founder_hour_value"]
    lib_hours = n * review_min / 60.0
    refresh_cash = n * s["refresh_share_per_year"] * cash
    refresh_hours = (n * s["refresh_share_per_year"] * review_min
                     + n * s["fact_check_minutes_per_lesson_year"]) / 60.0
    return {
        "steps": steps, "claude": claude, "tts_per_min": tts_per_min, "tts": tts, "cash": cash,
        "review_min": review_min, "time_value": review_min / 60.0 * hv,
        "all_in": cash + review_min / 60.0 * hv,
        "lib_cash": n * cash, "lib_hours": lib_hours, "lib_all_in": n * cash + lib_hours * hv,
        "video_minutes": n * s["minutes_per_lesson"],
        "refresh_cash": refresh_cash, "refresh_hours": refresh_hours,
        "refresh_all_in": refresh_cash + refresh_hours * hv,
    }


# ---- 4. Running costs ---------------------------------------------------------
def ai_tutor_cost(s, sh):
    t = s["ai_tutor"]
    return t["questions"] * call_cost(sh, t["model"], t["tin"], t["tout"], cached=0.5)


def running(s, sh, tutor=None):
    """Variable cost of one paying member for one month."""
    tutor = s["ai_tutor"]["on"] if tutor is None else tutor
    c = {
        "Video bandwidth": s["video_minutes_per_member_month"] * sh["stream_per_1000_min_delivered"] / 1000,
        "Hosting (database, auth, logs)": s["hosting_var_per_member_month"],
        "Support time": s["support_tickets_per_member_month"] * s["minutes_per_ticket"] / 60
                        * s["support_cost_per_hour"],
        "Email": sh["email_per_contact_above_1k"],
        "AI tutor (if added)": ai_tutor_cost(s, sh) if tutor else 0.0,
    }
    return c


def fixed_month(sh):
    return sum(sh["fixed_monthly"].values())


def email_cost(contacts, sh):
    return sh["email_base_month"] + max(0.0, contacts - 1000) * sh["email_per_contact_above_1k"]


# ---- 2. Funnel and lifetime value ---------------------------------------------
def unit(s, sh, pm=None, pa=None):
    pm = sh["price_monthly"] if pm is None else pm
    pa = sh["price_annual"] if pa is None else pa
    a = s["annual_share"]
    am, aa = avg_price(pm, s, sh), avg_price(pa, s, sh)
    km, ka = kept_blended(am, s, sh), kept_blended(aa, s, sh)
    run = sum(running(s, sh).values())
    gp_m = km - run                        # per month, monthly plan
    gp_a = ka - 12 * run                   # per year, annual plan
    life_m = 1.0 / s["monthly_churn"]      # expected paid months
    life_a = 1.0 + s["annual_first_renewal"] / (1.0 - s["annual_later_renewal"])  # expected paid years
    ltv_m, ltv_a = gp_m * life_m, gp_a * life_a
    ltv = (1 - a) * ltv_m + a * ltv_a
    # Steady state: active members per 1 new member a month
    M, A = (1 - a) * life_m, a * 12 * life_a
    arpu = (M * am + A * aa / 12) / (M + A)       # MRR per member, before fees
    gp_pm = (M * gp_m + A * gp_a / 12) / (M + A)  # gross profit per member-month
    rev_life = (1 - a) * am * life_m + a * aa * life_a
    return {"am": am, "aa": aa, "km": km, "ka": ka, "run": run, "gp_m": gp_m, "gp_a": gp_a,
            "life_m": life_m, "life_a": life_a, "ltv_m": ltv_m, "ltv_a": ltv_a, "ltv": ltv,
            "M": M, "A": A, "stock_per_inflow": M + A, "annual_mix_active": A / (M + A),
            "arpu": arpu, "gp_pm": gp_pm, "rev_life": rev_life,
            "avg_months": (M + A)}  # average months a new member stays paid


# ---- 5. Acquisition -------------------------------------------------------------
def channels(s, sh, u=None):
    u = u or unit(s, sh)
    conv = s["conversion"]
    creator_signups = (s["creator_views_per_post"] * s["creator_click_rate"] * s["creator_signup_rate"])
    out = {
        "Creators (flat fee)": {"cps": s["creator_cost_per_post"] / creator_signups,
                                "signups_per_post": creator_signups},
        "Paid ads": {"cps": s["ads_cpc"] / s["ads_signup_rate"]},
    }
    for ch in out.values():
        ch["cac"] = ch["cps"] / conv
        ch["payback"] = ch["cac"] / u["gp_pm"] if u["gp_pm"] > 0 else float("inf")
        ch["ltv_cac"] = u["ltv"] / ch["cac"]
    return out


def organic_time_cac(s, sh, month):
    signups = min(s["organic_cap"], s["organic_m1"] * (1 + s["organic_growth"]) ** (month - 1))
    hours = s["social_hours_per_week"] * 52 / 12
    return hours * sh["founder_hour_value"] / (signups * s["conversion"]), signups


# ---- 6. Growth path ---------------------------------------------------------------
def simulate(s, sh, months=None, conv=None, organic_cap=None, paid=True):
    months = months or sh["months_to_simulate"]
    conv = s["conversion"] if conv is None else conv
    cap = s["organic_cap"] if organic_cap is None else organic_cap
    u = unit(s, sh)
    ch = channels(s, sh, u)
    a = s["annual_share"]
    timing = sh["conversion_timing"]
    run = u["run"]
    cc = content_cost(s, sh)
    passing = [k for k, v in ch.items() if v["ltv_cac"] >= sh["keep_channel_if_ltv_cac"]] if paid else []
    tests = {"Creators (flat fee)": ("creator_test_budget", "creator_test_months"),
             "Paid ads": ("ads_test_budget", "ads_test_months")}
    signups_hist = []
    mon = 0.0
    cohorts = []  # annual: [start_month, count]
    free_contacts = 0.0
    cum = {"signups": 0.0, "mkt": 0.0, "cash": 0.0, "paid_new": 0.0}
    last_net = 0.0
    low_cash = 0.0
    rows = []
    for m in range(1, months + 1):
        organic = min(cap, s["organic_m1"] * (1 + s["organic_growth"]) ** (m - 1))
        spend = {}
        for name, (bk, mk) in tests.items():
            lo, hi = s[mk]
            b = 0.0
            if paid and lo <= m <= hi:
                b = s[bk]
            elif paid and m > hi and name in passing:
                b = min(sh["max_paid_budget_month"],
                        max(s[bk], sh["reinvest_share"] * last_net / max(1, len(passing))))
            spend[name] = b
        paid_signups = sum(spend[k] / ch[k]["cps"] for k in spend)
        signups = organic + paid_signups
        signups_hist.append(signups)
        new_paid = conv * sum(timing[k] * signups_hist[-1 - k]
                              for k in range(len(timing)) if len(signups_hist) > k)
        new_m, new_a = (1 - a) * new_paid, a * new_paid
        mon = mon * (1 - s["monthly_churn"]) + new_m
        renew = 0.0
        for c in cohorts:
            age = m - c[0]
            if age > 0 and age % 12 == 0:
                c[1] *= s["annual_first_renewal"] if age == 12 else s["annual_later_renewal"]
                renew += c[1]
        cohorts.append([m, new_a])
        ann = sum(c[1] for c in cohorts)
        members = mon + ann
        mrr = mon * u["am"] + ann * u["aa"] / 12
        net_mrr = mon * u["km"] + ann * u["ka"] / 12  # accrual view, after fees and refunds
        cash_in = mon * u["km"] + (new_a + renew) * u["ka"]
        free_contacts = free_contacts * (1 - sh["free_list_monthly_decay"]) + signups - new_paid
        var_cost = members * (run - sh["email_per_contact_above_1k"]) \
            + signups * s["free_video_minutes_per_signup"] * sh["stream_per_1000_min_delivered"] / 1000 \
            + email_cost(free_contacts + members, sh)
        mkt = sum(spend.values())
        cash_out = var_cost + fixed_month(sh) + cc["refresh_cash"] / 12 + mkt
        cum["signups"] += signups
        cum["mkt"] += mkt
        cum["cash"] += cash_in - cash_out
        cum["paid_new"] += new_paid
        low_cash = min(low_cash, cum["cash"])
        last_net = net_mrr
        rows.append({"m": m, "signups": signups, "organic": organic, "paid_signups": paid_signups,
                     "new_paid": new_paid, "members": members, "monthly": mon, "annual": ann,
                     "mrr": mrr, "net_mrr": net_mrr, "cash_in": cash_in, "cash_out": cash_out,
                     "op_profit": net_mrr - (var_cost + fixed_month(sh) + cc["refresh_cash"] / 12 + mkt),
                     "mkt": mkt, "cum_signups": cum["signups"], "cum_mkt": cum["mkt"],
                     "cum_cash": cum["cash"], "free_contacts": free_contacts})
    return {"rows": rows, "passing": passing, "low_cash": low_cash}


def first_month(path, key, target):
    for r in path["rows"]:
        if r[key] >= target:
            return r
    return None


def first_profit_month(path):
    """First month from which gross profit covers all running and marketing costs
    in every later month (excludes founder pay and the launch budget)."""
    found = None
    for r in reversed(path["rows"]):
        if r["op_profit"] < 0:
            break
        found = r
    return found


def needs_for(target, s, sh, u=None):
    u = u or unit(s, sh)
    members = target / u["arpu"]
    inflow = members / u["stock_per_inflow"]
    return {"members": members, "new_paid_month": inflow, "signups_month": inflow / s["conversion"]}


# ---- 8. Pricing options -------------------------------------------------------------
def option_result(opt, s, sh, signups=1000, horizon=24):
    u0 = unit(s, sh)
    run = u0["run"]
    conv = s["conversion"] * opt["conv_mult"]
    members = signups * conv
    if "lifetime" in opt:
        price = avg_price(opt["lifetime"], s, sh)
        gp = kept_blended(price, s, sh) - run * opt["active_months"]
        return {"members": members, "ltv": gp, "gp_h": members * gp, "gp_life": members * gp,
                "mrr10k": None, "signups10k": None, "max_cps": gp * conv / 3, "arpu": None,
                "first_pay": kept_blended(price, s, sh)}
    s2 = dict(s)
    s2["monthly_churn"] = min(0.95, s["monthly_churn"] * opt["churn_mult"])
    s2["annual_first_renewal"] = s["annual_first_renewal"] * opt["renewal_mult"]
    s2["annual_later_renewal"] = s["annual_later_renewal"] * opt["renewal_mult"]
    s2["annual_share"] = min(0.95, s["annual_share"] + opt["annual_share_add"])
    s2["conversion"] = conv
    u = unit(s2, sh, opt["monthly"], opt["annual"])
    a, c = s2["annual_share"], s2["monthly_churn"]
    months_paid_h = sum((1 - c) ** t for t in range(horizon))
    years_paid_h = 1 + (s2["annual_first_renewal"] if horizon > 12 else 0) \
        + (s2["annual_first_renewal"] * s2["annual_later_renewal"] if horizon > 24 else 0)
    gp_h = members * ((1 - a) * u["gp_m"] * months_paid_h + a * u["gp_a"] * years_paid_h)
    n = needs_for(10_000, s2, sh, u)
    return {"members": members, "ltv": u["ltv"], "gp_h": gp_h, "gp_life": members * u["ltv"],
            "mrr10k": n["members"], "signups10k": n["signups_month"],
            "max_cps": u["ltv"] * conv / 3, "arpu": u["arpu"],
            "first_pay": (1 - a) * u["km"] + a * u["ka"]}


def signups_per_arm(p0, p1, z_alpha=1.96, z_power=0.84):
    """Free signups per group to tell conversion p0 from p1 (two-proportion test)."""
    return (z_alpha + z_power) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / (p0 - p1) ** 2


# ---- Launch budget ----------------------------------------------------------------
def launch_budget(sh):
    cc = content_cost(INPUTS["scenarios"]["base"], sh)
    cons = content_cost(INPUTS["scenarios"]["conservative"], sh)
    items = []
    for item, lean, full, note in sh["launch_budget"]:
        if lean is None:
            lean = round(cc["lib_cash"] * 2, -1)
            full = round(cons["lib_cash"] * 2, -1)
            note = f"base x2 / conservative x2 ({note})"
        items.append((item, lean, full, note))
    lean_sub = sum(i[1] for i in items)
    full_sub = sum(i[2] for i in items)
    ctg = sh["launch_contingency"]
    return {"items": items, "lean_sub": lean_sub, "full_sub": full_sub,
            "lean_ctg": lean_sub * ctg["lean"], "full_ctg": full_sub * ctg["full"],
            "lean": lean_sub * (1 + ctg["lean"]), "full": full_sub * (1 + ctg["full"])}


# =============================================================================
# REPORT
# =============================================================================
def money(x, cents=False):
    if x is None:
        return "n/a"
    if x == float("inf"):
        return "never"
    sign = "-" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x:,.2f}" if cents else f"{sign}${x:,.0f}"


def pct(x, d=0):
    return "n/a" if x is None else f"{x * 100:.{d}f}%"


def num(x, d=0):
    return "n/a" if x is None else f"{x:,.{d}f}"


def months_txt(x):
    if x is None or x == float("inf") or x > 120:
        return "never" if x == float("inf") else ">120"
    return f"{x:.1f}"


def table(title, header, rows, widths=None):
    widths = widths or [44] + [14] * (len(header) - 1)
    print(title)
    line = "".join(h.ljust(widths[0]) if i == 0 else h.rjust(widths[i]) for i, h in enumerate(header))
    print(line)
    print("-" * len(line))
    for r in rows:
        if r is None:
            print()
            continue
        print("".join(str(c).ljust(widths[0]) if i == 0 else str(c).rjust(widths[i])
                      for i, c in enumerate(r)))
    print()


def main():
    sh = INPUTS["shared"]
    sc = INPUTS["scenarios"]
    names = ["Conservative", "Base", "Optimistic"]
    U = {k: unit(sc[k], sh) for k in SCENARIOS}
    C = {k: content_cost(sc[k], sh) for k in SCENARIOS}
    CH = {k: channels(sc[k], sh, U[k]) for k in SCENARIOS}
    P = {k: simulate(sc[k], sh) for k in SCENARIOS}
    cols = lambda f: [f(k) for k in SCENARIOS]  # noqa: E731
    pm, pa = sh["price_monthly"], sh["price_annual"]

    print("=" * 86)
    print("PATIENT MONEY LEARNING APP: MEMBERSHIP FINANCE MODEL")
    print(f"Draft price: ${pm:.0f}/month or ${pa:.0f}/year. Web checkout (Stripe) first. All US dollars.")
    print("Nothing here is a forecast: it is arithmetic on sourced figures and labeled assumptions.")
    print("=" * 86)
    print()

    # 1. Revenue per member ------------------------------------------------------
    b = sc["base"]
    r15, r30 = sh["app_store_rates"]
    rows = [
        ["List price per payment", money(pm, True), money(pa, True), money(pa / 12, True)],
        ["Stripe fees (2.9% + 30c + 0.7% + 0.5% tax)", money(pm - kept(pm, {**b, "refund_rate": 0}, sh), True),
         money(pa - kept(pa, {**b, "refund_rate": 0}, sh), True), ""],
        ["  as % of price", pct(1 - kept(pm, {**b, "refund_rate": 0}, sh) / pm, 1),
         pct(1 - kept(pa, {**b, "refund_rate": 0}, sh) / pa, 1), ""],
        ["Kept via Stripe web checkout", money(kept(pm, {**b, "refund_rate": 0}, sh), True),
         money(kept(pa, {**b, "refund_rate": 0}, sh), True),
         money(kept(pa, {**b, "refund_rate": 0}, sh) / 12, True)],
        [f"Kept via App Store at {pct(r15)} (small business)", money(pm * (1 - r15), True),
         money(pa * (1 - r15), True), money(pa * (1 - r15) / 12, True)],
        [f"Kept via App Store at {pct(r30)} (standard, year 1)", money(pm * (1 - r30), True),
         money(pa * (1 - r30), True), money(pa * (1 - r30) / 12, True)],
    ]
    table("1a. WHAT WE KEEP FROM ONE PAYMENT (list price, before refunds and student discounts)",
          ["", "Monthly", "Annual", "Annual / 12"], rows, [48, 12, 12, 13])

    rows = [
        ["Share of new members choosing annual", *cols(lambda k: pct(sc[k]["annual_share"]))],
        ["Share of members on the student price", *cols(lambda k: pct(sc[k]["student_share"]))],
        ["Refunds (share of revenue)", *cols(lambda k: pct(sc[k]["refund_rate"]))],
        ["Average monthly price paid", *cols(lambda k: money(U[k]["am"], True))],
        ["Average annual price paid", *cols(lambda k: money(U[k]["aa"], True))],
        ["Kept per monthly payment (Stripe)", *cols(lambda k: money(U[k]["km"], True))],
        ["Kept per annual payment (Stripe)", *cols(lambda k: money(U[k]["ka"], True))],
        ["Share of ACTIVE members on annual", *cols(lambda k: pct(U[k]["annual_mix_active"]))],
        ["MRR per active member (before fees)", *cols(lambda k: money(U[k]["arpu"], True))],
    ]
    table("1b. REVENUE PER MEMBER BY SCENARIO (annual members stay longer, so they are most of the base)",
          ["", *names], rows)

    rows = []
    for label, share, rate in (("All web (Stripe)", 0.0, None),
                               ("Half via App Store at 15%", 0.5, r15),
                               ("Half via App Store at 30%", 0.5, r30),
                               ("All via App Store at 30%", 1.0, r30)):
        def kept_mix(price, k, share=share, rate=rate):
            s = sc[k]
            if rate is None:
                return kept(price, s, sh)
            return (1 - share) * kept(price, s, sh) + share * kept(price, s, sh, rate)
        rows.append([label, *cols(lambda k: money(
            (1 - sc[k]["annual_share"]) * kept_mix(U[k]["am"], k) * U[k]["life_m"]
            + sc[k]["annual_share"] * kept_mix(U[k]["aa"], k) * U[k]["life_a"]))])
    table("1c. REVENUE KEPT PER NEW MEMBER OVER THEIR LIFETIME, BY CHECKOUT CHANNEL (before running costs)",
          ["", *names], rows)

    # 2. Funnel and LTV ----------------------------------------------------------
    rows = [
        ["Free-to-paid conversion (within ~3 months)", *cols(lambda k: pct(sc[k]["conversion"], 1))],
        ["Monthly plan: churn per month", *cols(lambda k: pct(sc[k]["monthly_churn"]))],
        ["  = still paying after 12 months", *cols(lambda k: pct((1 - sc[k]["monthly_churn"]) ** 12))],
        ["  expected months paid", *cols(lambda k: num(U[k]["life_m"], 1))],
        ["Annual plan: first renewal rate", *cols(lambda k: pct(sc[k]["annual_first_renewal"]))],
        ["  later renewals", *cols(lambda k: pct(sc[k]["annual_later_renewal"]))],
        ["  expected years paid", *cols(lambda k: num(U[k]["life_a"], 2))],
        ["Blended: average months a member stays", *cols(lambda k: num(U[k]["avg_months"], 1))],
        None,
        ["Running cost per member per month", *cols(lambda k: money(U[k]["run"], True))],
        ["Gross profit per month, monthly plan", *cols(lambda k: money(U[k]["gp_m"], True))],
        ["Gross profit per year, annual plan", *cols(lambda k: money(U[k]["gp_a"], True))],
        ["LTV, monthly-plan member", *cols(lambda k: money(U[k]["ltv_m"], True))],
        ["LTV, annual-plan member", *cols(lambda k: money(U[k]["ltv_a"], True))],
        ["LTV, blended new member", *cols(lambda k: money(U[k]["ltv"], True))],
        ["Gross profit per member-month (blended)", *cols(lambda k: money(U[k]["gp_pm"], True))],
        ["LTV per FREE signup (LTV x conversion)", *cols(lambda k: money(U[k]["ltv"] * sc[k]["conversion"], True))],
    ]
    table("2. FUNNEL AND LIFETIME VALUE (LTV = lifetime gross profit; Stripe checkout)", ["", *names], rows)

    # 3. Content cost --------------------------------------------------------------
    rows = [["CLAUDE TOKENS PER LESSON (incl. retries)", "", "", ""]]
    for label in sc["base"]["content_steps"]:
        rows.append([f"  {label}", *cols(lambda k, l=label: money(C[k]["steps"][l], True))])
        rows.append([f"    model, calls", *cols(lambda k, l=label: f"{sc[k]['content_steps'][l][0]} x{sc[k]['content_steps'][l][1]}")])
    rows += [
        ["  Claude total per lesson", *cols(lambda k: money(C[k]["claude"], True))],
        ["Narration (TTS) per finished minute", *cols(lambda k: money(C[k]["tts_per_min"], True))],
        ["  price per 1,000 characters, takes", *cols(lambda k: f"${sc[k]['tts_price_per_1k_chars']:.2f} x{sc[k]['tts_takes']:.1f}")],
        ["Minutes per lesson", *cols(lambda k: num(sc[k]["minutes_per_lesson"], 1))],
        ["Narration per lesson", *cols(lambda k: money(C[k]["tts"], True))],
        ["Rendering (ffmpeg, local)", "$0.00", "$0.00", "$0.00"],
        ["CASH COST PER VIDEO", *cols(lambda k: money(C[k]["cash"], True))],
        ["Founder review per lesson + its clips, min", *cols(lambda k: num(C[k]["review_min"]))],
        [f"  valued at ${sh['founder_hour_value']:.0f}/hour", *cols(lambda k: money(C[k]["time_value"], True))],
        ["ALL-IN COST PER VIDEO (cash + time)", *cols(lambda k: money(C[k]["all_in"], True))],
        None,
        [f"LIBRARY OF {sh['lessons']} LESSONS", "", "", ""],
        ["  Minutes of video", *cols(lambda k: num(C[k]["video_minutes"]))],
        ["  Cash", *cols(lambda k: money(C[k]["lib_cash"]))],
        ["  Founder review hours", *cols(lambda k: num(C[k]["lib_hours"], 1))],
        ["  All-in (cash + time)", *cols(lambda k: money(C[k]["lib_all_in"]))],
        ["YEARLY REFRESH", "", "", ""],
        ["  Lessons re-made per year", *cols(lambda k: pct(sc[k]["refresh_share_per_year"]))],
        ["  Cash per year", *cols(lambda k: money(C[k]["refresh_cash"]))],
        ["  Founder hours per year", *cols(lambda k: num(C[k]["refresh_hours"], 1))],
        ["  All-in per year", *cols(lambda k: money(C[k]["refresh_all_in"]))],
    ]
    table("3. CONTENT COST (Claude for script + review + visuals, TTS per minute, founder review)",
          ["", *names], rows)

    # 4. Running costs ---------------------------------------------------------------
    rows = [["PER PAYING MEMBER PER MONTH", "", "", ""]]
    rk = {k: running(sc[k], sh, tutor=True) for k in SCENARIOS}
    for label in rk["base"]:
        rows.append([f"  {label}", *cols(lambda k, l=label: money(rk[k][l], True))])
    rows += [
        ["  Total without AI tutor", *cols(lambda k: money(sum(running(sc[k], sh, tutor=False).values()), True))],
        ["  Total with AI tutor", *cols(lambda k: money(sum(rk[k].values()), True))],
        ["  AI tutor model, questions a month", *cols(lambda k: f"{sc[k]['ai_tutor']['model']} x{sc[k]['ai_tutor']['questions']}")],
        ["  as % of the monthly price", *cols(lambda k: pct(sum(running(sc[k], sh, tutor=False).values()) / pm, 1))],
        ["PER FREE SIGNUP (once): Level 1 video", *cols(lambda k: money(
            sc[k]["free_video_minutes_per_signup"] * sh["stream_per_1000_min_delivered"] / 1000, True))],
        None,
        ["FIXED COSTS PER MONTH (all scenarios)", "", "", ""],
    ]
    for label, v in sh["fixed_monthly"].items():
        rows.append([f"  {label}", money(v), "", ""])
    rows.append(["  Email tool (Kit) at 1,000 contacts", money(sh["email_base_month"]), "", ""])
    rows.append(["  + per free contact above 1,000, per month", money(sh["email_per_contact_above_1k"], True), "", ""])
    rows.append(["  Total fixed", money(fixed_month(sh) + sh["email_base_month"]), "", ""])
    rows.append(["  = members to cover fixed costs", *cols(lambda k: num((fixed_month(sh) + sh["email_base_month"]) / U[k]["gp_pm"]))])
    table("4. RUNNING COSTS", ["", *names], rows, [52, 13, 13, 13])

    # 5. Acquisition --------------------------------------------------------------------
    rows = []
    for ch_name in CH["base"]:
        rows += [
            [ch_name.upper(), "", "", ""],
            ["  Cost per free signup", *cols(lambda k, c=ch_name: money(CH[k][c]["cps"], True))],
            ["  CAC per paying member", *cols(lambda k, c=ch_name: money(CH[k][c]["cac"]))],
            ["  Payback, months of gross profit", *cols(lambda k, c=ch_name: months_txt(CH[k][c]["payback"]))],
            ["  LTV / CAC", *cols(lambda k, c=ch_name: f"{CH[k][c]['ltv_cac']:.1f}x")],
            ["  Kept after test?", *cols(lambda k, c=ch_name: "yes" if c in P[k]["passing"] else "no")],
        ]
    rows[1:1] = [["  Free signups per sponsored post", *cols(lambda k: num(CH[k]["Creators (flat fee)"]["signups_per_post"]))]]
    rows += [
        ["ORGANIC SHORT VIDEO (clips from lessons)", "", "", ""],
        ["  Cash CAC", "$0", "$0", "$0"],
        ["  Founder hours per week", *cols(lambda k: num(sc[k]["social_hours_per_week"]))],
        ["  Free signups, month 1", *cols(lambda k: num(sc[k]["organic_m1"]))],
        ["  Growth per month, cap", *cols(lambda k: f"{pct(sc[k]['organic_growth'])}, {num(sc[k]['organic_cap'])}")],
        ["  Time-valued CAC, month 1", *cols(lambda k: money(organic_time_cac(sc[k], sh, 1)[0]))],
        ["  Time-valued CAC, month 12", *cols(lambda k: money(organic_time_cac(sc[k], sh, 12)[0]))],
        None,
        ["MOST YOU CAN PAY PER FREE SIGNUP", "", "", ""],
        ["  for LTV/CAC = 3", *cols(lambda k: money(U[k]["ltv"] * sc[k]["conversion"] / 3, True))],
        ["  for payback within 6 months", *cols(lambda k: money(U[k]["gp_pm"] * 6 * sc[k]["conversion"], True))],
    ]
    table("5. ACQUISITION BY CHANNEL (CAC = cost per free signup / conversion)", ["", *names], rows)

    # 6. Targets --------------------------------------------------------------------------
    horizon = sh["months_to_simulate"]
    rows = []
    for t in sh["mrr_targets"]:
        need = {k: needs_for(t, sc[k], sh, U[k]) for k in SCENARIOS}
        hit = {k: first_month(P[k], "mrr", t) for k in SCENARIOS}
        rows += [
            [f"{money(t)} MRR", "", "", ""],
            ["  Paying members needed", *cols(lambda k: num(need[k]["members"]))],
            ["  New members per month to hold it", *cols(lambda k: num(need[k]["new_paid_month"]))],
            ["  Free signups per month to hold it", *cols(lambda k: num(need[k]["signups_month"]))],
            ["  Month reached (path below)", *cols(lambda k: f"month {hit[k]['m']}" if hit[k] else f">{horizon}")],
            ["  Free signups so far, total", *cols(lambda k: num(hit[k]["cum_signups"]) if hit[k] else "-")],
            ["  Marketing cash spent so far", *cols(lambda k: money(hit[k]["cum_mkt"]) if hit[k] else "-")],
        ]
    rows.append(None)
    rows.append(["PATH SNAPSHOTS (month: members / MRR)", "", "", ""])
    for m in (6, 12, 24, 36, 48, 60, 72):
        if m <= horizon:
            rows.append([f"  month {m}", *cols(lambda k, m=m: f"{num(P[k]['rows'][m - 1]['members'])} / "
                                                         f"{money(P[k]['rows'][m - 1]['mrr'])}")])
    rows.append(["  free signups in month 12", *cols(lambda k: num(P[k]["rows"][11]["signups"]))])
    rows.append(["  free signups in month 24", *cols(lambda k: num(P[k]["rows"][23]["signups"]))])
    fp = {k: first_profit_month(P[k]) for k in SCENARIOS}
    rows.append(["Covers its running + marketing costs from", *cols(lambda k: f"month {fp[k]['m']}" if fp[k] else f">{horizon}")])
    rows.append(["Lowest cumulative operating cash", *cols(lambda k: money(P[k]["low_cash"]))])
    rows.append(["Cumulative operating cash at month 24", *cols(lambda k: money(P[k]["rows"][23]["cum_cash"]))])
    rows.append(["(both exclude founder pay and the launch budget)", "", "", ""])
    table("6. TARGETS AND MONTHS TO REACH THEM (month 1 = public launch)", ["", *names], rows, [46, 19, 19, 20])

    # 7. Sensitivity -------------------------------------------------------------------------
    ub = U["base"]
    rows = []
    for cps in sh["cost_per_signup_grid"]:
        r = [money(cps, True)]
        for cv in sh["conversion_grid"]:
            bb = dict(b, conversion=cv)
            ltv = unit(bb, sh)["ltv"]
            r.append(f"{ltv / (cps / cv):.1f}x")
        rows.append(r)
    table("7a. BASE CASE: LTV/CAC BY COST PER FREE SIGNUP (rows) AND CONVERSION (columns); 3x is healthy",
          ["Cost/signup", *[pct(c) for c in sh["conversion_grid"]]], rows, [14, 10, 10, 10, 10])

    rows = []
    for churn in (0.09, 0.12, 0.15, 0.20):
        for r1 in (0.20, 0.30, 0.40):
            bb = dict(b, monthly_churn=churn, annual_first_renewal=r1)
            uu = unit(bb, sh)
            rows.append([pct(churn), pct(r1), money(uu["ltv"], True), num(needs_for(10_000, bb, sh, uu)["members"]),
                         num(needs_for(10_000, bb, sh, uu)["signups_month"])])
    table("7b. BASE CASE: HOW RETENTION MOVES LTV AND THE $10K MRR TARGET",
          ["Monthly churn", "1st renewal", "LTV", "Members $10K", "Signups/mo"], rows, [14, 12, 12, 14, 12])

    rows = []
    for conv in (0.02, 0.04, 0.06):
        for capx in (0.5, 1.0, 2.0):
            p = simulate(b, sh, conv=conv, organic_cap=b["organic_cap"] * capx)
            hits = [first_month(p, "mrr", t) for t in sh["mrr_targets"]]
            rows.append([pct(conv), num(b["organic_cap"] * capx),
                         *[f"month {h['m']}" if h else f">{horizon}" for h in hits]])
    table("7c. BASE CASE: MONTH EACH TARGET IS REACHED, BY CONVERSION AND ORGANIC REACH (cap on free signups/month)",
          ["Conversion", "Organic cap", *[money(t) for t in sh["mrr_targets"]]], rows, [12, 13, 12, 12, 12])

    rows = []
    for share in (0.25, 0.50, 0.75):
        bb = dict(b, annual_share=share)
        uu = unit(bb, sh)
        nn = needs_for(10_000, bb, sh, uu)
        rows.append([pct(share), pct(uu["annual_mix_active"]), money(uu["arpu"], True), money(uu["ltv"], True),
                     num(nn["members"]), num(nn["signups_month"])])
    table("7d. BASE CASE: MONTHLY VS ANNUAL MIX (share of NEW members choosing annual)",
          ["New on annual", "Active annual", "MRR/member", "LTV", "Members $10K", "Signups/mo"],
          rows, [14, 14, 12, 10, 14, 12])

    # 8. Pricing options ----------------------------------------------------------------------
    rows = []
    for name, opt in sh["pricing_options"].items():
        r = option_result(opt, b, sh)
        rows.append([name, pct(b["conversion"] * opt["conv_mult"], 1), num(r["members"], 0),
                     money(r["first_pay"], True), money(r["ltv"], True), money(r["gp_h"]),
                     money(r["max_cps"], True), num(r["mrr10k"]) if r["mrr10k"] else "n/a"])
    table("8a. BASE CASE: PRICING OPTIONS PER 1,000 FREE SIGNUPS (conversion changes are ASSUMPTIONS)",
          ["Option", "Conv.", "Members", "1st pay", "LTV", "GP 24 mo", "Max $/signup", "Mbrs $10K"],
          rows, [40, 7, 9, 10, 10, 10, 13, 11])

    rows = []
    p0 = b["conversion"]
    for p1 in (p0 * 0.70, p0 * 0.75, p0 * 1.25, p0 * 1.5):
        n = signups_per_arm(p0, p1)
        rows.append([pct(p0, 1), pct(p1, 1), num(n), num(2 * n / max(1.0, P["base"]["rows"][5]["signups"]), 1)])
    table("8c. BASE CASE: FREE SIGNUPS PER PRICE ARM TO DETECT A CONVERSION CHANGE (80% power, 5% significance)",
          ["Price A conv.", "Price B conv.", "Signups/arm", "Months at m6 pace"], rows, [16, 15, 14, 19])

    gift_net = kept(sh["gift_price"], dict(b, refund_rate=0.0), sh) - 12 * ub["run"]
    gift_ev = gift_net + sh["gift_recipient_renews"] * (ub["gp_a"]) * ub["life_a"]
    stud = {k: dict(sc[k], student_share=0.0) for k in SCENARIOS}
    rows = [
        ["Gift: 12 months at the annual price, net of costs", money(gift_net, True)],
        [f"  + {pct(sh['gift_recipient_renews'])} of recipients then pay themselves", money(gift_ev, True)],
        ["Student price: annual", money(pa * (1 - sh["student_discount"]), True)],
        ["  kept per student annual payment (Stripe)", money(kept(pa * (1 - sh["student_discount"]), dict(b, refund_rate=0.0), sh), True)],
        ["MRR per member with no student discounts", money(unit(stud["base"], sh)["arpu"], True)],
        ["MRR per member at base student share", money(ub["arpu"], True)],
    ]
    table("8b. BASE CASE: GIFTS AND STUDENT DISCOUNT", ["", "Value"], rows, [56, 14])

    # 9. Launch budget -------------------------------------------------------------------------
    lb = launch_budget(sh)
    rows = [[i[0], money(i[1]), money(i[2])] for i in lb["items"]]
    rows += [None,
             ["Subtotal", money(lb["lean_sub"]), money(lb["full_sub"])],
             [f"Contingency ({pct(sh['launch_contingency']['lean'])} / {pct(sh['launch_contingency']['full'])})",
              money(lb["lean_ctg"]), money(lb["full_ctg"])],
             ["TOTAL, FIRST 6 MONTHS", money(lb["lean"]), money(lb["full"])],
             ["Founder review hours for the library (base / conservative)",
              num(C["base"]["lib_hours"]), num(C["conservative"]["lib_hours"])]]
    table("9. LAUNCH BUDGET, FIRST 6 MONTHS (cash; see launch-budget.md for notes)",
          ["", "Lean", "Fuller"], rows, [62, 10, 10])

    # Sanity checks -------------------------------------------------------------------------------
    problems = []
    for k in SCENARIOS:
        u = U[k]
        if not (u["ltv"] > 0 and u["gp_m"] > 0 and u["gp_a"] > 0):
            problems.append(f"{k}: non-positive gross profit")
        if not 0 < u["annual_mix_active"] < 1:
            problems.append(f"{k}: active mix out of range")
        if not u["km"] < u["am"] or not u["ka"] < u["aa"]:
            problems.append(f"{k}: fees not deducted")
        # Steady state: constant inflow of 100 new members/month for 20 years.
        s = sc[k]
        mon, coh = 0.0, []
        for m in range(1, 241):
            mon = mon * (1 - s["monthly_churn"]) + 100 * (1 - s["annual_share"])
            for c in coh:
                age = m - c[0]
                if age > 0 and age % 12 == 0:
                    c[1] *= s["annual_first_renewal"] if age == 12 else s["annual_later_renewal"]
            coh.append([m, 100 * s["annual_share"]])
        sim_stock = mon + sum(c[1] for c in coh)
        if abs(sim_stock / (100 * u["stock_per_inflow"]) - 1) > 0.10:
            problems.append(f"{k}: steady-state members off ({sim_stock:.0f} vs {100 * u['stock_per_inflow']:.0f})")
        rows = P[k]["rows"]
        if any(r["members"] < 0 or r["mrr"] < 0 for r in rows):
            problems.append(f"{k}: negative members or MRR")
        if abs(sum(sh["conversion_timing"]) - 1) > 1e-9:
            problems.append("conversion_timing must sum to 1")
    order = [U[k]["ltv"] for k in SCENARIOS]
    if not order[0] < order[1] < order[2]:
        problems.append("LTV not ordered conservative < base < optimistic")
    print("Sanity checks:", "all passed" if not problems else "; ".join(problems))


if __name__ == "__main__":
    main()
