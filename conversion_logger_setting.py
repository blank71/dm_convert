"""The settings of the conversion logger."""


# pylint: disable=global-variable-undefined
def init(conversion_run_id: str, opt_out_data_collection_selection: bool,
         log_env_var: str):
  global run_id
  run_id = conversion_run_id
  global opt_out_data_collection
  opt_out_data_collection = opt_out_data_collection_selection
  global log_env
  log_env = log_env_var


# pylint: enable=global-variable-undefined
