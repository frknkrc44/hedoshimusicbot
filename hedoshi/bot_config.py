# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from logging import error

from dotenv import dotenv_values

working_proxies = []

values = dotenv_values("config.env")

if "__REMOVE_THIS_BEFORE_EDIT__" in values:
    error("Please remove __REMOVE_THIS_BEFORE_EDIT__!")
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
