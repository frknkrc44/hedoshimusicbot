# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

# Detect the folder name and start the bot
__import__(
    (lambda path:
        getattr(path, 'basename')(getattr(path, 'dirname')(__file__))
     )(__import__('os.path', fromlist=['dirname', 'basename']).os.path)
).bot.run()

# TL;DR
# import <botname>
# <botname>.bot.run()
