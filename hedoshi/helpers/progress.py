from time import time

from pyrogram.types import Message

from ..translations import translator as _


async def progress_func_wrapper(
    reply: Message, current: int, total: int, upload: bool = False
) -> None:
    from .. import bot_config

    ignore_progress = (
        bot_config.BOT_IGNORE_PROGRESS
        if hasattr(bot_config, "BOT_IGNORE_PROGRESS")
        else False
    )

    if ignore_progress:
        return

    percent = int((current / total) * 100)
    last_percent = globals().get(f"last_percent_{reply.chat.id}_{reply.id}", -1)
    last_epoch: int = globals().get(f"last_percent_epoch_{reply.chat.id}_{reply.id}", 0)
    current_epoch = int(time())
    if percent != last_percent and (current_epoch - last_epoch) > 3:
        globals()[f"last_percent_{reply.chat.id}_{reply.id}"] = percent
        globals()[f"last_percent_epoch_{reply.chat.id}_{reply.id}"] = current_epoch

        try:
            await reply.edit(
                _.translate_chat(
                    "mvUploading" if upload else "mvDownloading",
                    args=[percent],
                    cid=reply.chat.id,
                )
            )
        except BaseException:
            pass
