# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

# Detect the folder name and start the bot
from os.path import basename, dirname

__import__(basename(dirname(__file__))).bot.run()

# TL;DR
# import <botname>
# <botname>.bot.run()
