# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from types import FunctionType
from pyrogram import Client, ContinuePropagation, StopPropagation, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, Chat
from pyrogram.enums import ChatType
from pyrogram.enums.parse_mode import ParseMode
from traceback import format_exc
from logging import info
from typing import Optional


def is_owner(message: Message):
    from ... import bot_config

    return message.from_user.id == bot_config.BOT_OWNER


async def is_admin(message: Message):
    member = await message.chat.get_member(message.from_user.id)
    return member.promoted_by is not None


async def is_bot_admin(chat: Chat):
    from ... import bot

    member = await chat.get_member(bot.me.id)
    return member.privileges and member.privileges.can_invite_users


def register(
    cmd: Optional[str],
    admin: bool = False,
    bot_admin: Optional[bool] = None,
    group: bool = True,
    private: bool = False,
    owner: bool = False,
    notify_user: bool = True,
    min_args: int = 0,
    max_args: int = -1,
):
    from ... import bot, bot_config, translator as _
    bot_owner = bot_config.BOT_OWNER
    prefixes = ['/', '\\', '|', '!', '₺']

    if bot_admin is None:
        bot_admin = admin

    min_args = min_args + 1

    filter = (
        filters.command(cmd.split('|'), prefixes=prefixes)
        if cmd
        else filters.incoming & filters.regex(f'^[^{"".join(prefixes)}]')
    )

    if owner:
        filter &= filters.user(bot_owner)

    def msg_decorator(func: FunctionType):
        async def msg_handler(client: Client, message: Message):
            if message.empty or not message.chat:
                return

            if message.chat.type == ChatType.CHANNEL:
                return

            if admin and (not await is_admin(message) or not is_owner(message)):
                if notify_user:
                    await message.reply(_.translate_chat("errNotAdmin", cid=message.chat.id))
                return

            if bot_admin and not (await is_bot_admin(message.chat)):
                if notify_user:
                    await message.reply(_.translate_chat("errNotBotAdmin", cid=message.chat.id))
                return

            if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP) and not group:
                if notify_user:
                    await message.reply(_.translate_chat("errGroupRestricted", cid=message.chat.id))
                return

            if message.chat.type == ChatType.PRIVATE and not private:
                if notify_user:
                    await message.reply(_.translate_chat("errPrivateRestricted", cid=message.chat.id))
                return

            if message.command and len(message.command) < min_args:
                if notify_user:
                    await message.reply(_.translate_chat("errMinArgs", args=[min_args - 1], cid=message.chat.id))
                return

            if max_args > -1 and message.command and len(message.command) > max_args:
                if notify_user:
                    await message.reply(_.translate_chat("errMaxArgs", args=[max_args], cid=message.chat.id))
                return

            try:
                await func(message)
            except (ContinuePropagation, StopPropagation) as pyrogram_related:
                raise pyrogram_related
            except BaseException:
                assert message._client
                await message._client.send_message(bot_owner, format_exc(), parse_mode=ParseMode.DISABLED)
                raise StopPropagation

        bot.add_handler(MessageHandler(msg_handler, filter))
        if cmd:
            info(f'Register command {cmd.split("|")}!')

    return msg_decorator
