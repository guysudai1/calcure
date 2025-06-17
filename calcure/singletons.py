# Initialise config:
from calcure.configuration import Config
from calcure.errors import Error


global_config = Config()
error = Error(global_config.LOG_FILE)