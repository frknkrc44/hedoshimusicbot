# Copyright (C) 2023 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from typing import Optional


def time_format(seconds: Optional[int]) -> str:
    # https://stackoverflow.com/a/68321739
    if seconds is not None:
        seconds = int(seconds)
        d = seconds // (3600 * 24)
        h = seconds // 3600 % 24
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        if d > 0:
            return '{:02d}:{:02d}:{:02d}:{:02d}'.format(d, h, m, s)
        elif h > 0:
            return '{:02d}:{:02d}:{:02d}'.format(h, m, s)
        elif m > 0 or s > 0:
            return '{:02d}:{:02d}'.format(m, s)
    return '-'
