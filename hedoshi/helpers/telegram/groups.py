# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from typing import Optional

from pyrogram import Client
from pyrogram.types import Chat, Message, User
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, StreamAudioEnded, Update

from ...translations import translator as _
from .. import userbots
from ..ffmpeg.ffprobe import get_duration
from ..query import get_next_query, query
from ..query_item import QueryItem
from .msg_funcs import reply_message


async def is_member_alive(chat: Chat, user: User) -> bool:
    try:
        chat_member = await chat.get_member(user.id)
        return chat_member.restricted_by is None
    except BaseException:
        return False


async def join_or_change_stream(
    message: Message,
    stream: MediaStream,
    file_name: str,
    action: int = 0,
    video: bool = False,
) -> Optional[QueryItem]:
    def tr(key: str) -> str:
        return _.translate_chat(key, cid=message.chat.id)

    calls = await find_active_userbot(message)
    if not calls:
        locals()["msg"] = await reply_message(message, tr("astJoining"))
        try:
            added = await add_userbot(message)
            assert added
            calls = await find_active_userbot(message)
        except BaseException:
            pass

    if not calls:
        await locals()['msg'].edit(tr('astJoinFail'))
        return None

    if action == 0:
        seconds = get_duration(stream._media_path)
        if not seconds:
            if 'msg' not in locals():
                await reply_message(message, tr("astDurationFail"))
            else:
                await locals()['msg'].edit(tr('astDurationFail'))
            return None

        item = QueryItem(
            stream,
            seconds,
            0,
            message.chat.id,
            file_name,
            video=video,
        )

        try:
            assert await is_active(message.chat.id, calls)
            query.append(item)

            return item
        except BaseException:
            pass

        query.append(item)

    try:
        await calls.play(
            message.chat.id,
            stream,
        )
    except BaseException as e:
        if 'msg' not in locals():
            await reply_message(message, tr("astPlayFail"))
        else:
            await locals()['msg'].edit(tr('astPlayFail'))
        raise e
    
    return None


async def find_active_userbot(message: Message) -> Optional[PyTgCalls]:
    for calls in userbots:
        pyrogram: Client = get_client(calls)
        try:
            chat = await pyrogram.get_chat(message.chat.id)
            alive = await is_member_alive(chat, pyrogram.me)
            assert alive  # type: ignore
            return calls
        except BaseException:
            pass

    return None

async def is_active(group_id: int, calls: PyTgCalls) -> bool:
    try:
        return await calls.played_time(group_id)
    except BaseException:
        return get_next_query(group_id) is not None

def get_client(calls: PyTgCalls) -> Client:
    return calls._mtproto

async def find_active_userbot_client(message: Message) -> Optional[Client]:
    userbot = await find_active_userbot(message)
    if userbot:
        return get_client(userbot)

    return None


async def add_userbot(message: Message) -> bool:
    invite_link: str = await message.chat.export_invite_link()

    for calls in userbots:
        try:
            chat = await get_client(calls).join_chat(invite_link)
            return chat
        except BaseException:
            return False

    return False


async def get_current_duration(message: Message) -> Optional[int]:
    calls = await find_active_userbot(message)
    if calls:
        query = get_next_query(message.chat.id)
        if query:
            try:
                time = await calls.played_time(query.chat_id)
                return query.skip + time
            except BaseException:
                pass

    return None


async def stream_end(client: PyTgCalls, update: Update, force_skip: bool = False) -> None:
    # if video stream ends, StreamAudioEnded and StreamVideoEnded is invoked
    # so we can ignore the video stream end signal
    if type(update) != StreamAudioEnded:  # noqa: E721
        return

    item = get_next_query(update.chat_id)
    if item and item.loop and not force_skip:
        item.skip = 0
        item.stream = MediaStream(
            item.stream._media_path,
            video_flags=MediaStream.Flags.IGNORE
            if not item.video
            else MediaStream.Flags.AUTO_DETECT,
            audio_parameters=item.stream._audio_parameters,
            video_parameters=item.stream._video_parameters,
        )
    else:
        get_next_query(update.chat_id, True)
        item = get_next_query(update.chat_id)

    from ... import bot

    if item:
        msg = await bot.send_message(
            update.chat_id,
            text=_.translate_chat(
                "streamLoop" if item.loop and not force_skip else "streamNext",
                cid=update.chat_id,
                args=[item.query_details()],
            ),
        )
        await join_or_change_stream(
            msg,
            item.stream,
            item.file_name,
            1,
            item.video,
        )
        return

    try:
        await client.leave_call(update.chat_id)
    except BaseException:
        pass

    await bot.send_message(
        update.chat_id, text=_.translate_chat("streamEnd", cid=update.chat_id)
    )
