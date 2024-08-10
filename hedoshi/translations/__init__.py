# Copyright (C) 2024 frknkrc44 <https://gitlab.com/frknkrc44>
#
# This file is part of HedoshiMusicBot project,
# and licensed under GNU Affero General Public License v3.
# See the GNU Affero General Public License for more details.
#
# All rights reserved. See COPYING, AUTHORS.
#

from os import getcwd, listdir, sep
from os.path import isfile
from json import loads
from logging import info
from typing import List, Optional


class Translator:
    def __init__(
        self,
        sorter: bool = False
    ):
        self.trans_folder = f'{getcwd()}{sep}{__name__.replace(".", sep)}'

        jsons = [
            file
            for file in listdir(self.trans_folder)
            if isfile(f"{self.trans_folder}{sep}{file}") and file[-5:] == ".json"
        ]

        self.sorter_lang_keys = [i[:-5] for i in jsons]

        if not sorter:
            self.default_lang = "tr"
            self.trans_cache = {}

            for file in jsons:
                lang_key = file[:-5]
                with open(f"{self.trans_folder}{sep}{file}") as json:
                    try:
                        self.trans_cache[lang_key] = loads(json.read())
                        info(f"Loaded {lang_key}!")
                    except BaseException as e:
                        info(f"Cannot load {lang_key}!\n{e}")

    def translate_bool(self, bool: bool, lang: Optional[str] = None) -> Optional[str]:
        return self._translate('helpYes' if bool else 'helpNo', lang=lang)

    def translate_chat(
        self,
        keyword: str,
        args: Optional[List] = None,
        default: Optional[str] = None,
        cid: Optional[int] = None,
    ) -> str:
        assert cid
        lang = self.default_lang

        return self._translate(
            keyword=keyword,
            lang=lang,
            args=args,
            default=default
        )

    def _translate(
        self,
        keyword: str,
        lang: Optional[str] = None,
        args: Optional[List] = None,
        default: Optional[str] = None,
    ) -> str:
        lang = lang or self.default_lang

        if lang not in self.trans_cache.keys():
            return self._translate(
                keyword=keyword,
                lang=self.default_lang,
                args=args,
                default=default,
            )

        if keyword not in self.trans_cache[lang]:
            if keyword in self.trans_cache[self.default_lang]:
                return self._parse_args(self.trans_cache[self.default_lang][keyword], args)
            return default or keyword

        return self._parse_args(self.trans_cache[lang][keyword], args)

    def scan_key_not_found(self, keyword):
        not_found_langs = []
        for a in self.trans_cache.keys():
            if keyword not in self.trans_cache[a]:
                not_found_langs.append(a)

        return not_found_langs

    @staticmethod
    def _parse_args(translation: str, args: Optional[List]) -> str:
        if not (args and len(args)):
            return translation

        return translation.format(*args)
