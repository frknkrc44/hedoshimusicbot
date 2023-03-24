# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from pyrogram import Client
from dotenv import dotenv_values

values = dotenv_values('config.env')

userbot = Client(
    ':memory:',
    api_id=values['API_ID'],  # type: ignore
    api_hash=values['API_HASH'],  # type: ignore
    in_memory=bool(values.get('CREATE_SESSION_MEMORY', False)),
)

with userbot:
    print(userbot.export_session_string())
