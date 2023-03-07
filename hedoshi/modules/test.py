from ..helpers import userbots
from ..helpers.cmd_register import register
from ..helpers.groups import join_or_change_stream
from pyrogram.types import Message
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, HighQualityVideo
from os import getcwd

@register(cmd='vtest', private=False)
async def test_vcalls(message: Message):
    msg = await message.reply_text('Testing video call...')
    await join_or_change_stream(
        message,
        AudioVideoPiped(
            f'{getcwd()}/example.mp4',
            audio_parameters=HighQualityAudio(),
            video_parameters=HighQualityVideo(),
        ),
    )
    await msg.edit('Done!')

@register(cmd='atest', private=False)
async def test_acalls(message: Message):
    msg = await message.reply_text('Testing audio call...')
    await join_or_change_stream(
        message,
        AudioPiped(
            f'{getcwd()}/example.mp3',
            audio_parameters=HighQualityAudio(),
        ),
    )
    await msg.edit('Done!')