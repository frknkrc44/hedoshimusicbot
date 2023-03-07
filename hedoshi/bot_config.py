from dotenv import dotenv_values
from logging import error

values = dotenv_values('config.env')
locals()['_example_var'] = '__REMOVE_THIS_BEFORE_EDIT__'

if _example_var in values:  # type: ignore
    error(f'Please remove {_example_var}!')  # type: ignore
    quit()

# add all env values as global import
for item in values.keys():
    try:
        globals()[item] = int(values[item])  # type: ignore
    except:
        globals()[item] = values[item]
