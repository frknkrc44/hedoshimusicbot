# Copyright (C) 2020-2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

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
