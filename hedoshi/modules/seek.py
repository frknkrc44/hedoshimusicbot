from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from ..helpers.telegram.cmd_register import register
from ..helpers import get_next_query, replace_query, QueryItem
from ..helpers.telegram.groups import find_active_userbot, join_or_change_stream
from .. import translator as _


@register(cmd='seek|ileriatla')
async def seek(message: Message):
    await _seek(message, False)


@register(cmd='seekback|geriatla')
async def sback(message: Message):
    await _seek(message, True)


async def _seek(message: Message, back_mode: bool):
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

        msg = await message.reply(_.translate_chat(
            'streamBackSeeking' if back_mode else 'streamSeeking', cid=item.chat_id))
        played = await userbot.played_time(item.chat_id)
        if back_mode:
            skip = item.skip - (played + seconds)
            if skip < 0:
                skip = 0
        else:
            skip = item.skip + played + seconds
            if skip >= item.duration:
                skip = item.duration

        if type(item.stream) == AudioPiped:
            piped = AudioPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f'-ss {skip}' if skip > 0 else ''
            )
        else:
            piped = AudioVideoPiped(
                path=item.stream._path,
                audio_parameters=HighQualityAudio(),
                video_parameters=HighQualityVideo(),
                additional_ffmpeg_parameters=f'-ss {skip}' if skip > 0 else ''
            )

        replace_query(item, QueryItem(
            piped, item.duration, skip, item.chat_id, item.loop))
        await join_or_change_stream(
            message=msg,
            stream=piped,
            action=1,
        )
        await msg.edit(_.translate_chat(
            'streamBackSeeked' if back_mode else 'streamSeeked', cid=item.chat_id))
