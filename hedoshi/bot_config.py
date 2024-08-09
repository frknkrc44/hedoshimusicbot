# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from dotenv import dotenv_values
from logging import error

working_proxies = []

values = dotenv_values('config.env')
locals()['_example_var'] = '__REMOVE_THIS_BEFORE_EDIT__'

if _example_var in values:  # type: ignore # noqa: F821
    error(f"Please remove {_example_var}!")  # type: ignore # noqa: F821
    quit()

# add all env values as global import
for item in values.keys():
    try:
        globals()[item] = int(values[item])  # noqa: F821
    except BaseException:
        if values[item] in ["True", "False"]:
            globals()[item] = values[item] == "True"
        else:
            globals()[item] = values[item]
