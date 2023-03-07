from types import FunctionType
from pyrogram import Client, ContinuePropagation, StopPropagation, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, Chat
from pyrogram.enums import ChatType
from pyrogram.enums.parse_mode import ParseMode
from traceback import format_exc
from logging import info

locals()['botmain'] = __import__(__name__.split('.')[
    0], fromlist=['bot', 'bot_config', 'translator'])
bot = locals()['botmain'].bot
bot_config = locals()['botmain'].bot_config
_ = locals()['botmain'].translator

bot_owner = bot_config.BOT_OWNER  # type: ignore
prefixes = ['/', '\\', '|', '!', '₺']


def is_owner(message: Message):
    return message.from_user.id == bot_owner


async def is_admin(message: Message):
    member = await message.chat.get_member(message.from_user.id)
    return member.promoted_by is not None


async def is_bot_admin(chat: Chat):
    member = await chat.get_member(bot.me.id)  # type: ignore
    return member.promoted_by is not None


def register(
    cmd: str | None,
    admin: bool = False,
    bot_admin: bool | None = None,
    group: bool = True,
    private: bool = False,
    owner: bool = False,
    notify_user: bool = True,
    min_args: int = 0,
    max_args: int = -1,
):

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
                    await message.reply(_.translate_chat("errNotAdmin"))
                return

            if bot_admin and not (await is_bot_admin(message.chat)):
                if notify_user:
                    await message.reply(_.translate_chat("errNotBotAdmin"))
                return

            if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP) and not group:
                if notify_user:
                    await message.reply(_.translate_chat("errGroupRestricted"))
                return

            if message.chat.type == ChatType.PRIVATE and not private:
                if notify_user:
                    await message.reply(_.translate_chat("errPrivateRestricted"))
                return

            if message.command and len(message.command) < min_args:
                if notify_user:
                    await message.reply(_.translate_chat("errMinArgs", args=[min_args - 1]))
                return

            if max_args > -1 and message.command and len(message.command) > max_args:
                if notify_user:
                    await message.reply(_.translate_chat("errMaxArgs", args=[max_args]))
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
