try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass

from os import environ

# NOTE: participant/session fields: https://otree.readthedocs.io/en/latest/rounds.html?#participant-fields
# NOTE: attributes can always be stored in participant.vars/session.vars (dictionaries)
# NOTE: however, they may also be assigned as familiar class properties (e.g. object.myattr) if added first to PARTICIPANT_FIELDS/SESSION_FIELDS

# This allows to set any type of data to player.participant (not constrained to oTree's orm column types)
PARTICIPANT_FIELDS = [
    "uuid",
    "starttime",
    "is_planner",
    "gender_identity",
    "years_as_planner",
    "job_title",
    "does_consent",
    "prolific_id",
    "company_name",
    "work_country",
    "nationality",
    "unit_costs",
    "stock_units",
    "treatment",  # Treatment
    # "demand_rvs",
    "history",
    "game_results",
    "practice_results",
    "payoff_round",
    "q1",
    "q2",
    "donation_fund",
]

# NOTE: session fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#session-fields
SESSION_FIELDS = []

# Global session configs that apply when not defined in the app-specific session config dictionary,
# As a reminder, exact config settings at runtime are accessible in Page methods from the player argument - that is, `player.session.config.get(..., )`.
# For more details, see pages.py (specifically lines that contain "player.session.config").
SESSION_CONFIG_DEFAULTS = dict(
    doc="",
    use_secure_urls=False,
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    is_pilot_test=True,
    prolific_code="5B4E4089",
)


#
SESSION_CONFIGS = [
    dict(
        name="disruption",
        display_name="Disruption Game",
        num_demo_participants=1,
        app_sequence=["disruption"],
    ),
    dict(
        name="shorthorizon",
        display_name="Short Horizon Game",
        num_demo_participants=1,
        app_sequence=["shorthorizon"],
    ),
    # dict(
    #     name="back_button",
    #     display_name="Back button for multiple instructions pages",
    #     num_demo_participants=1,
    #     app_sequence=["back_button"],
    #     references=["https://www.otreehub.com/projects/otree-snippets/"]
    # ),
]

# Rooms
ROOMS = [
    dict(
        name="pilotstudy1",
        display_name="Student pilot study - 1",
    ),
    dict(
        name="pilotstudy2",
        display_name="Student pilot study - 2",
    ),
    dict(
        name="pilotstudy3",
        display_name="Student pilot study - 3",
    ),
    dict(
        name="pilotstudy4",
        display_name="Student pilot study - 4",
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

# for security, best to set admin password in an environment variable
ADMIN_USERNAME = environ.get("OTREE_ADMIN_USERNAME", "admin")
if environ.get("OTREE_ADMIN_PASSWORD"):
    ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")
    AUTH_LEVEL = environ.get("OTREE_AUTH_LEVEL", "DEMO")


DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "5694079434357"
