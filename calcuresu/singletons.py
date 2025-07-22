# Initialise config:
from calcuresu.configuration import Config
from calcuresu.errors import Error


global_config = Config()
error = Error(global_config.LOG_FILE.value)