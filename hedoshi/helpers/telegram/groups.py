# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from time import time
from typing import Dict, Optional

from pyrogram import Client
from pyrogram.types import Chat, Message, User
from pytgcalls import PyTgCalls
from pytgcalls.types import (
    ChatUpdate,
    MediaStream,
    StreamAudioEnded,
    Update,
    VideoQuality,
)

from ...translations import translator as _
from .. import userbots
from ..ffmpeg.ffprobe import get_audio_params, get_duration, get_resolution
from ..format import time_format
from ..query import clear_query, get_next_query, query
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
        clear_query(message.chat.id)

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
    except BaseException:
        clear_query(message.chat.id)

        if "msg" not in locals():
            await reply_message(message, tr("astPlayFail"))
        else:
            await locals()["msg"].edit(tr("astPlayFail"))
    
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
            pyro = get_client(calls)

            call_dict = await calls.calls
            assert len(call_dict) < 10

            chat = await pyro.join_chat(invite_link)
            return chat
        except BaseException:
            continue

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


async def start_stream(
    reply: Message,
    path: str,
    is_video: bool,
    file_name: str,
) -> None:
    if path:
        video_params = get_resolution(path) if is_video else None
        audio_params = get_audio_params(path)

        item = await join_or_change_stream(
            reply,
            MediaStream(
                path,
                video_flags=MediaStream.Flags.IGNORE
                if not is_video
                else MediaStream.Flags.AUTO_DETECT,
                audio_parameters=audio_params,
                video_parameters=video_params or VideoQuality.SD_480p,
            ),
            file_name,
            video=is_video,
        )

        arg: Optional[str] = None
        try:
            arg = QueryItem.query_details_static(
                reply.chat.id,
                file_name,
                time_format(get_duration(path)),
            )
        except BaseException:
            await reply.edit(_.translate_chat("streamTGError", cid=reply.chat.id))
            return

        await reply.edit(
            _.translate_chat(
                "streamQueryAdded" if item else "streamStarted",
                cid=reply.chat.id,
                args=[arg],
            ),
        )
    else:
        await reply.edit(_.translate_chat("streamTGError", cid=reply.chat.id))
        return


async def end_stream(
    client: PyTgCalls,
    update: Update,
    force_skip: bool = False,
    skip_count: int = 1,
) -> None:
    # if video stream ends, StreamAudioEnded and StreamVideoEnded is invoked
    # so we can ignore the video stream end signal
    update_type = type(update)
    if update_type not in [StreamAudioEnded, ChatUpdate]:  # noqa: E721
        return

    item = get_next_query(update.chat_id)

    if item:
        if item.loop and not force_skip:
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
            for i in range(min(skip_count, len(query))):
                get_next_query(update.chat_id, True)

            item = get_next_query(update.chat_id)
    elif update_type == ChatUpdate:
        return

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

last_vc_closed_triggered_dates: Dict[int, float] = {}

async def vc_closed(client: PyTgCalls, update: ChatUpdate):
    if (
        type(Update) != ChatUpdate  # noqa: E721
        or update.status != ChatUpdate.Status.CLOSED_VOICE_CHAT
    ):
        return

    current_time = time()

    if update.chat_id in last_vc_closed_triggered_dates:
        if last_vc_closed_triggered_dates[update.chat_id] - current_time < 3.0:
            return

    last_vc_closed_triggered_dates[update.chat_id] = current_time

    await end_stream(
        client,
        update,
        force_skip=True,
        skip_count=99999999,
    )
