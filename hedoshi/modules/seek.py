from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from ..helpers.telegram.cmd_register import register
from ..helpers import get_next_query, replace_query, QueryItem
from ..helpers.telegram.groups import find_active_userbot, join_or_change_stream
from .. import translator as _


@register(cmd='seek|atla')
async def seek(message: Message):
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

        msg = await message.reply(_.translate_chat('streamSeeking', cid=item.chat_id))
        played = await userbot.played_time(item.chat_id)
        skip = item.skip + played + seconds
        if skip >= item.duration:
            skip = item.duration

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
        await msg.edit(_.translate_chat('streamSeeked', cid=item.chat_id))
