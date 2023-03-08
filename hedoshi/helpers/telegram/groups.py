from pyrogram import Client
from pyrogram.types import Message, User, Chat
from pytgcalls import PyTgCalls
from pytgcalls.types import InputStream
from .. import userbots
from ... import bot


async def is_member_alive(chat: Chat, user: User) -> bool:
    try:
        chat_member = await chat.get_member(user.id)
        return chat_member.restricted_by is None
    except:
        return False


async def join_or_change_stream(message: Message, stream: InputStream):
    calls = await find_active_userbot(message)
    if not calls:
        msg = await bot.send_message(message.chat.id, 'Assistant joining...')
        try:
            await add_userbot(message)
            calls = await find_active_userbot(message)
        except:
            pass

    if not calls:
        await msg.edit('Failed to join assistant!')
        return

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
    for calls in userbots:
        result = await bot.add_chat_members(
            message.chat.id, get_client(calls).me.id)  # type: ignore
        if result:
            return True

    return False
