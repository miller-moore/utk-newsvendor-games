from os import environ

# NOTE: participant/session fields: https://otree.readthedocs.io/en/latest/rounds.html?#participant-fields
# NOTE: attributes can always be stored in participant.vars/session.vars (dictionaries)
# NOTE: however, they may also be assigned as familiar class properties (e.g. object.myattr) if added first to PARTICIPANT_FIELDS/SESSION_FIELDS

# This allows to set any type of data to player.participant (not constrained to oTree's orm column types)
PARTICIPANT_FIELDS = [
    "uuid",
    "starttime",
    "is_planner",
    "years_as_planner",
    "company_name",
    "does_consent",
    "unit_costs",
    "stock_units",
    "treatment",
    # "demand_rvs",
    "history",
    "game_results",
    "payoff_round",
]

# NOTE: session fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#session-fields
SESSION_FIELDS = []

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']
SESSION_CONFIG_DEFAULTS = dict(
    doc="",
    use_secure_urls=False,
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
)

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
]

# Rooms
ROOMS = [
    dict(
        name="pilotstudy",
        display_name="Student pilot study",
    )
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

# for security, best to set admin password in an environment variable
ADMIN_USERNAME = environ.get("OTREE_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")
AUTH_LEVEL = environ.get("OTREE_AUTH_LEVEL", "DEMO")


DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "5694079434357"
