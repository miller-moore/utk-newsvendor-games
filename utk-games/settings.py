from os import environ

# NOTE: participant fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#participant-fields
# NOTE: participant fields are stored internally as participant.vars, but also participant.xyz is same as participant.vars['xyz']
PARTICIPANT_FIELDS = ["treatment"]

# NOTE: session fields docs: https://otree.readthedocs.io/en/latest/rounds.html?#session-fields
# NOTE: session fields are stored internally in session.vars
SESSION_FIELDS = ["session_name", "some_other_session_field", "game_number"]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']
SESSION_CONFIG_DEFAULTS = dict(
    doc="",
    use_secure_urls=True,
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    # NOTE: custom fields - see SESSION_FIELDS list below to init these as extra session attributes
    game_number=2,
    session_name="SweetSessionNameBro",
    some_other_session_field="'this here is the value for some other session field my man'",
)

SESSION_CONFIGS = [
    # dict(
    #     name="public_goods",
    #     app_sequence=["public_goods"],
    #     num_demo_participants=3,
    # ),
    dict(
        name="demandplan",
        app_sequence=["demandplan_1"],  # , "demandplan_2"],
        num_demo_participants=1,
        participation_fee=0.35,
    ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "5694079434357"
