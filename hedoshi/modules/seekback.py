from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from ..helpers.telegram.cmd_register import register
from ..helpers import get_next_query, replace_query, QueryItem
from ..helpers.telegram.groups import find_active_userbot, join_or_change_stream
from .. import translator as _


@register(cmd='seekback|geriatla')
async def seekback(message: Message):
    userbot = await find_active_userbot(message)
    if userbot:
        try:
            seconds = int(message.command[1])
            assert seconds > 0
        except:
            return

        item = get_next_query(message.chat.id)
        if not item:
            return

        msg = await message.reply(_.translate_chat('streamBackSeeking', cid=item.chat_id))
        played = await userbot.played_time(item.chat_id)
        skip = item.skip - (played + seconds)
        if skip < 0:
            skip = 0

        if type(item.stream) == AudioPiped:
            piped = AudioPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f'-ss {skip}'
            )
        else:
            piped = AudioVideoPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
                video_parameters=HighQualityVideo(),
                additional_ffmpeg_parameters=f'-ss {skip}'
            )

        replace_query(item, QueryItem(
            piped, item.duration, skip, item.chat_id))
        await join_or_change_stream(
            message=msg,
            stream=piped,
            action=1,
        )
        await msg.edit(_.translate_chat('streamBackSeeked', cid=item.chat_id))
