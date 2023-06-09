# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from typing import Optional
from pyrogram import Client
from pyrogram.types import Message, User, Chat
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo, StreamAudioEnded, Update
from ..ffmpeg.ffprobe import get_duration
from .. import userbots, query, get_next_query
from ..query_item import QueryItem

async def is_member_alive(chat: Chat, user: User) -> bool:
    try:
        chat_member = await chat.get_member(user.id)
        return chat_member.restricted_by is None
    except:
        return False


async def join_or_change_stream(
    message: Message,
    stream: AudioPiped | AudioVideoPiped,
    action: int = 0,
) -> Optional[QueryItem]:
    from ... import translator as _

    def tr(key: str) -> str:
        return _.translate_chat(key, cid=message.chat.id)

    calls = await find_active_userbot(message)
    if not calls:
        locals()['msg'] = await message.reply(tr('astJoining'))
        try:
            await add_userbot(message)
            calls = await find_active_userbot(message)
        except:
            pass

    if not calls:
        await locals()['msg'].edit(tr('astJoinFail'))
        return None

    if action == 0:
        seconds = await get_duration(stream._path)
        if not seconds:
            if 'msg' not in locals():
                await message.reply(tr('astDurationFail'))
            else:
                await locals()['msg'].edit(tr('astDurationFail'))
            return None

        item = QueryItem(stream, seconds, 0, message.chat.id)
        query.append(item)

        try:
            await calls.get_active_call(message.chat.id)
            return item
        except:
            pass

    try:
        try:
            await calls.get_call(message.chat.id)
            await calls.change_stream(
                message.chat.id,
                stream,
            )
        except:
            await calls.join_group_call(
                message.chat.id,
                stream,
            )
    except BaseException as e:
        if 'msg' not in locals():
            await message.reply(tr('astPlayFail'))
        else:
            await locals()['msg'].edit(tr('astPlayFail'))
        raise e
    
    return None


async def find_active_userbot(message: Message) -> Optional[PyTgCalls]:
    for calls in userbots:
        pyrogram: Client = get_client(calls)
        try:
            chat = await pyrogram.get_chat(message.chat.id)
            if await is_member_alive(chat, pyrogram.me):  # type: ignore
                return calls
        except:
            pass

    return None


def get_client(calls: PyTgCalls) -> Client:
    return calls._app._bind_client._app


async def find_active_userbot_client(message: Message) -> Optional[Client]:
    userbot = await find_active_userbot(message)
    if userbot:
        return get_client(userbot)

    return None


async def add_userbot(message: Message) -> bool:
    from ... import bot

    for calls in userbots:
        result = await bot.add_chat_members(
            message.chat.id, get_client(calls).me.id)  # type: ignore
        if result:
            return True

    return False


async def get_current_duration(message: Message) -> Optional[int]:
    calls = await find_active_userbot(message)
    from .. import get_next_query
    if calls:
        query = get_next_query(message.chat.id)
        if query:
            try:
                time = await calls.played_time(query.chat_id)
                return query.skip + time
            except:
                pass

    return None


async def stream_end(client: PyTgCalls, update: Update, force_skip: bool = False) -> None:
    # if video stream ends, StreamAudioEnded and StreamVideoEnded is invoked
    # so we can ignore the video stream end signal
    if type(update) != StreamAudioEnded:
        return

    item = get_next_query(update.chat_id, True)
    print(item)
    if item and item.loop and not force_skip:
        if type(item.stream) == AudioPiped:
            piped = AudioPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
            )
        else:
            piped = AudioVideoPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
                video_parameters=HighQualityVideo(),
            )

        item.stream = piped
        item.skip = 0
        query.insert(0, item)

    from ... import bot, translator

    item = get_next_query(update.chat_id)
    if item:
        msg = await bot.send_message(
            update.chat_id,
            text=translator.translate_chat(
                'streamLoop' if item.loop and not force_skip else 'streamNext',
                cid=update.chat_id,
            )
        )
        await join_or_change_stream(msg, item.stream, 1)
        return

    try:
        await client.leave_group_call(update.chat_id)
    except:
        pass

    await bot.send_message(
        update.chat_id,
        text=translator.translate_chat(
            'streamEnd', cid=update.chat_id)
    )
