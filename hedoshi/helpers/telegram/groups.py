from typing import Optional
from pyrogram import Client
from pyrogram.types import Message, User, Chat
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped, GroupCall
from ..ffmpeg.ffprobe import get_duration
from .. import userbots, query
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
):
    calls = await find_active_userbot(message)
    if not calls:
        locals()['msg'] = await message.reply('Assistant joining...')
        try:
            await add_userbot(message)
            calls = await find_active_userbot(message)
        except:
            pass

    if not calls:
        await locals()['msg'].edit('Failed to join assistant!')
        return

    if action == 0:
        seconds = await get_duration(stream._path)
        if not seconds:
            if 'msg' not in locals():
                await message.reply('Failed to get duration!')
            else:
                await locals()['msg'].edit('Failed to get duration!')
            return

        item = QueryItem(stream, seconds, 0, message.chat.id)
        query.append(item)

        try:
            call: GroupCall = await calls.get_active_call(message.chat.id)
            return item
        except:
            pass

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


async def find_active_userbot(message: Message) -> PyTgCalls | None:
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


async def find_active_userbot_client(message: Message) -> Client | None:
    userbot = await find_active_userbot(message)
    if userbot:
        return get_client(userbot)

    return None


async def add_userbot(message: Message):
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
