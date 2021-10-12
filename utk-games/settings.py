from os import environ

# NOTE: participant fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#participant-fields
# NOTE: participant fields are stored internally as participant.vars, but also participant.xyz is same as participant.vars['xyz']

# This allows to set any type of data to player.participant (not constrained to oTree's orm column types)
PARTICIPANT_FIELDS = ["starttime", "treatment", "unit_costs", "demand_rvs", "stock_units", "game_results", "endtime"]

# NOTE: session fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#session-fields
# NOTE: session fields are stored internally in session.vars
SESSION_FIELDS = ["global_var_1", "global_var_2"]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']
SESSION_CONFIG_DEFAULTS = dict(
    doc="",
    use_secure_urls=True,
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
)

SESSION_CONFIGS = [
    dict(
        name="demandplanning",
        display_name="Demand Planning Game",
        num_demo_participants=1,
        app_sequence=["demandplanning"],
    ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "5694079434357"
