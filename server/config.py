from environs import Env

env = Env()
env.read_env()

def create_config_obj(env_setting):
    new_config = Config()
    with env.prefixed(env_setting):
        new_config.PORT = env.str("PORT")
        new_config.DEBUG = env.bool("DEBUG", default=False)
        new_config.TESTING = env.bool("TESTING", default=False)
    return new_config

class Config(object):
    DEBUG = False
    HOST = env.str(
        "HOST", default=env.str("DEV_HOST")
    )
    PORT = env.int(
        "PORT", default=env.int("DEV_PORT")
    )

dev_config = create_config_obj("DEV_")
prod_config = create_config_obj("PROD_")
