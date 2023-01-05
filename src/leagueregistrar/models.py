"""Models used in `registrar`.

:copyright: (c) 2022-present Tanner B. Corcoran
:license: MIT, see LICENSE for more details.
"""

__author__ = "Tanner B. Corcoran"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022-present Tanner B. Corcoran"


import prepr


class Generic:
    def __repr__(self, *args, **kwargs) -> prepr.pstr:
        _dict = {k:getattr(self, k) for k in self.__slots__}
        return prepr.prepr(self).kwargs(**_dict).build(simple=True, *args, **kwargs)


class User(Generic):
    __slots__ = ("user_id", "active", "timestamp", "discord_id", "username", "previous_usernames",
                 "num_name_changes", "team")

    def __init__(self, user_id: int, active: bool, timestamp: int, discord_id: str,
                 username: str, previous_usernames: list[str], num_name_changes: int,
                 team: int | None) -> None:
        self.user_id = user_id
        self.active = active
        self.timestamp = timestamp
        self.discord_id = discord_id
        self.username = username
        self.previous_usernames = previous_usernames
        self.num_name_changes = num_name_changes
        self.team = team


class Team(Generic):
    __slots__ = ("team_id", "name", "active")
    def __init__(self, team_id: int, name: str, active: bool) -> None:
        self.team_id = team_id
        self.name = name
        self.active = active


class Series(Generic):
    __slots__ = ("series_id", "specifiers", "active", "timestamp", "game_ids", "team_1_id",
                 "team_2_id", "team_1_score", "team_2_score")
    def __init__(self, series_id: int, specifiers: dict | None, active: bool, timestamp: int,
                 game_ids: list[int], team_1_id: int, team_2_id: int, team_1_score: int,
                 team_2_score: int) -> None:
        self.series_id = series_id
        self.specifiers = specifiers
        self.active = active
        self.timestamp = timestamp
        self.game_ids = game_ids
        self.team_1_id = team_1_id
        self.team_2_id = team_2_id
        self.team_1_score = team_1_score
        self.team_2_score = team_2_score


class Game(Generic):
    __slots__ = ("game_id", "active", "timestamp", "series_id", "team_1_id", "team_2_id",
                 "team_1_score", "team_2_score", "team_1_user_ids", "team_2_user_ids")
    def __init__(self, game_id: int, active: bool, timestamp: int, series_id: int, team_1_id: int,
                 team_2_id: int, team_1_score: int, team_2_score: int, team_1_user_ids: list[int],
                 team_2_user_ids: list[int]) -> None:
        self.game_id = game_id
        self.active = active
        self.timestamp = timestamp
        self.series_id = series_id
        self.team_1_id = team_1_id
        self.team_2_id = team_2_id
        self.team_1_score = team_1_score
        self.team_2_score = team_2_score
        self.team_1_user_ids = team_1_user_ids
        self.team_2_user_ids = team_2_user_ids
