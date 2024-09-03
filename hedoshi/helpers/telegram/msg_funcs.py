# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from asyncio import sleep
from datetime import datetime
from traceback import format_exc

from pyrogram import ContinuePropagation
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import (ForceReply, InlineKeyboardMarkup, Message,
                            MessageEntity, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove)


async def reply_message(
    message: Message,
    text: str,
    old_reply_message: Message = None,
    quote: bool = None,
    parse_mode: ParseMode | None = None,
    entities: list[MessageEntity] = None,
    disable_web_page_preview: bool = None,
    disable_notification: bool = None,
    reply_to_message_id: int = None,
    schedule_date: datetime = None,
    protect_content: bool = None,
    reply_markup: InlineKeyboardMarkup
    | ReplyKeyboardMarkup
    | ReplyKeyboardRemove
    | ForceReply
    | None = None,
    force_reply: bool = True,
):
    reply_id = (
        reply_to_message_id or message.id
        if force_reply and not message.service
        else None
    )

    try:
        if old_reply_message and old_reply_message.media:
            return await old_reply_message.copy(
                message.chat.id,
                caption=text,
                parse_mode=parse_mode,
                caption_entities=entities,
                disable_notification=disable_notification,
                reply_to_message_id=reply_id,
                schedule_date=schedule_date,
                protect_content=protect_content,
                reply_markup=reply_markup,
            )

        return await message._client.send_message(
            message.chat.id,
            text,
            partial_reply=quote,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=reply_markup,
        )
    except FloodWait as e:
        print("Flood wait:", e.value)
        await sleep(e.value)

        return await reply_message(
            message=message,
            text=text,
            old_reply_message=old_reply_message,
            quote=quote,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=reply_markup,
            force_reply=force_reply,
        )
    except BaseException:
        print(format_exc())
        raise ContinuePropagation


async def edit_message(
    message: Message,
    text: str,
    parse_mode: ParseMode | None = None,
    entities: list[MessageEntity] = None,
    disable_web_page_preview: bool = None,
    reply_markup: InlineKeyboardMarkup = None,
):
    try:
        return await message.edit(
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
        )
    except FloodWait as e:
        print(f"Flood wait for {e.value}, ignored editing message")

        return message
    except BaseException:
        print("An unknown error occurred, ignored editing message")
        print(format_exc())

        return message
