"""The main `Registrar` implementation.

:copyright: (c) 2022-present Tanner B. Corcoran
:license: MIT, see LICENSE for more details.
"""

__author__ = "Tanner B. Corcoran"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022-present Tanner B. Corcoran"


from . import dbutils
from . import models
from . import types
import sqlite3
import typing
import time


class TableMapping(typing.Generic[types.T]):
    def __init_subclass__(cls, table: str = None, *args, **kwargs) -> None:
        cls.table = table

    def __init__(self, registrar: "Registrar") -> None:
        self._registrar = registrar
        self._db_conn = registrar._db_conn
        self._ensure_table_exists()
        self.db = dbutils.db(self._db_conn, self.table)

    def _ensure_table_exists(self) -> None:
        raise NotImplementedError()
    
    def add(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def get(self, *args, **kwargs) -> types.T | list[types.T] | None:
        raise NotImplementedError()

    def remove(self, *args, **kwargs) -> None:
        raise NotImplementedError()
    
    def edit(self, *args, **kwargs) -> typing.Callable:
        raise NotImplementedError()


class Users(TableMapping[models.User], table="USERS"):
    def _ensure_table_exists(self) -> None:
        with self._db_conn as (conn, cur):
            cur.execute("""CREATE TABLE IF NOT EXISTS USERS (
                user_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                active             INTEGER NOT NULL DEFAULT 1,
                timestamp          INTEGER NOT NULL,
                discord_id         TEXT NOT NULL,
                username           TEXT NOT NULL,
                previous_usernames TEXT,
                num_name_changes   INTEGER NOT NULL DEFAULT 0,
                team               INTEGER)""")
            conn.commit()

    def _ensure_discord_id_not_exists(self, discord_id: int | str) -> None:
        if self.get(discord_id=discord_id):
            raise ValueError(f"the discord_id '{discord_id}' already exists "
                             "in the USERS table")
    
    def _ensure_username_not_exists(self, username: str) -> None:
        if self.get(username=username):
            raise ValueError(f"the username '{username}' already exists "
                             "in the USERS table")
    
    def add(self, discord_id: int | str, username: str,
            connection_override: sqlite3.Connection = None, ignore: bool = False) -> int:
        if not ignore:
            self._ensure_discord_id_not_exists(discord_id)
            self._ensure_username_not_exists(username)
        self.db.add([
            dbutils.db.part("discord_id", discord_id, str),
            dbutils.db.part("username", username),
            dbutils.db.part("timestamp", int(time.time()))
        ], connection_override, return_=lambda x: x.lastrowid)

    def get(self, batchsize: int = None, matchall: bool = True,
            user_id: int | types.Expression[int] = types.MISSING,
            active: bool | types.Expression[bool] = types.MISSING,
            timestamp: int | types.Expression[int] = types.MISSING,
            discord_id: int | str | types.Expression[str] = types.MISSING,
            username: str | types.Expression[str] = types.MISSING,
            previous_usernames: types.Expression[list[str]] = types.MISSING,
            num_name_changes: int | types.Expression[int] = types.MISSING,
            team: int | types.Expression[int] = types.MISSING
            ) -> models.User | list[models.User] | None:
        # run db.get
        return self.db.get([
            dbutils.db.part("user_id", user_id),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("discord_id", discord_id, str),
            dbutils.db.part("username", username),
            dbutils.db.part("previous_usernames", previous_usernames, dbutils.ListCompiler(),
                            dbutils.ListDecompiler(str)),
            dbutils.db.part("num_name_changes", num_name_changes),
            dbutils.db.part("team", team)
        ], batchsize, matchall, models.User)

    def remove(self, matchall: bool = True, user_id: int | types.Expression[int] = types.MISSING,
               active: bool | types.Expression[bool] = types.MISSING,
               timestamp: int | types.Expression[int] = types.MISSING,
               discord_id: int | str | types.Expression[str] = types.MISSING,
               username: str | types.Expression[str] = types.MISSING,
               previous_usernames: types.Expression[list[str]] = types.MISSING,
               num_name_changes: int | types.Expression[int] = types.MISSING,
               team: int | types.Expression[int] = types.MISSING,
               connection_override: sqlite3.Connection = None) -> None:
        # run db.remove
        return self.db.remove([
            dbutils.db.part("user_id", user_id),
            dbutils.db.part("active", active),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("discord_id", discord_id, str),
            dbutils.db.part("username", username),
            dbutils.db.part("previous_usernames", previous_usernames, dbutils.ListCompiler(),
                            dbutils.ListDecompiler(str)),
            dbutils.db.part("num_name_changes", num_name_changes),
            dbutils.db.part("team", team)
        ], matchall, connection_override)

    def edit(self, user_id: int = types.MISSING, active: bool = types.MISSING,
             timestamp: int = types.MISSING, discord_id: int | str = types.MISSING,
             username: str = types.MISSING,
             previous_usernames: typing.Iterable[str] = types.MISSING,
             num_name_changes: int = types.MISSING, team: int = types.MISSING):
        
        _editor = self.db.edit([
            dbutils.db.part("user_id", user_id),
            dbutils.db.part("active", active),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("discord_id", discord_id, str),
            dbutils.db.part("username", username),
            dbutils.db.part("previous_usernames", previous_usernames, dbutils.ListCompiler()),
            dbutils.db.part("num_name_changes", num_name_changes),
            dbutils.db.part("team", team)
        ])

        def _edit(matchall: bool = True, user_id: int | types.Expression[int] = types.MISSING,
                  active: bool | types.Expression[bool] = types.MISSING,
                  timestamp: int | types.Expression[int] = types.MISSING,
                  discord_id: int | str | types.Expression[str] = types.MISSING,
                  username: str | types.Expression[str] = types.MISSING,
                  previous_usernames: types.Expression[list[str]] = types.MISSING,
                  num_name_changes: int | types.Expression[int] = types.MISSING,
                  team: int | types.Expression[int] = types.MISSING,
                  connection_override: sqlite3.Connection = None) -> None:
            return _editor([
                dbutils.db.part("user_id", user_id),
                dbutils.db.part("active", active),
                dbutils.db.part("timestamp", timestamp),
                dbutils.db.part("discord_id", discord_id, str),
                dbutils.db.part("username", username),
                dbutils.db.part("previous_usernames", previous_usernames, dbutils.ListCompiler(),
                                dbutils.ListDecompiler(str)),
                dbutils.db.part("num_name_changes", num_name_changes),
                dbutils.db.part("team", team)
            ], matchall, connection_override)

        return _edit


class Teams(TableMapping[models.Team], table="TEAMS"):
    def _ensure_table_exists(self) -> None:
        with self._db_conn as (conn, cur):
            cur.execute("""CREATE TABLE IF NOT EXISTS TEAMS (
                id     INTEGER NOT NULL,
                name   TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1)""")
            conn.commit()

    def add(self, id: int, name: str, connection_override: sqlite3.Connection = None,
            active: bool = types.MISSING) -> None:
        self.db.add([
            dbutils.db.part("id", id),
            dbutils.db.part("name", name),
            dbutils.db.part("active", active)
        ], connection_override)
    
    def get(self, batchsize: int = None, matchall: bool = True,
            id: int | types.Expression[int] = types.MISSING,
            name: str | types.Expression[str] = types.MISSING,
            active: bool | types.Expression[bool] = types.MISSING
            ) -> models.Team | list[models.Team] | None:
        return self.db.get([
            dbutils.db.part("id", id),
            dbutils.db.part("name", name),
            dbutils.db.part("active", active, decompiler=bool)
        ], batchsize, matchall, models.Team)
    
    def remove(self, matchall: bool = True, id: int | types.Expression[int] = types.MISSING,
               name: str | types.Expression[str] = types.MISSING,
               active: bool | types.Expression[bool] = types.MISSING,
               connection_override: sqlite3.Connection = None) -> None:
        return self.db.remove([
            dbutils.db.part("id", id),
            dbutils.db.part("name", name),
            dbutils.db.part("active", active)
        ], matchall, connection_override)

    def edit(self, id: int | types.Expression[int] = types.MISSING,
             name: str | types.Expression[str] = types.MISSING,
             active: bool | types.Expression[bool] = types.MISSING):
        _editor = self.db.edit([
            dbutils.db.part("id", id),
            dbutils.db.part("name", name),
            dbutils.db.part("active", active)
        ])

        def _edit(matchall: bool = True, id: int | types.Expression[int] = types.MISSING,
                  name: str | types.Expression[str] = types.MISSING,
                  active: bool | types.Expression[bool] = types.MISSING,
                  connection_override: sqlite3.Connection = None) -> None:
            return _editor([
                dbutils.db.part("id", id),
                dbutils.db.part("name", name),
                dbutils.db.part("active", active)
            ], matchall, connection_override)

        return _edit


class Serieses(TableMapping[models.Series], table="SERIESES"):
    def _ensure_table_exists(self) -> None:
        with self._db_conn as (conn, cur):
            cur.execute("""CREATE TABLE IF NOT EXISTS SERIESES (
                series_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                specifiers   TEXT,
                active       INTEGER NOT NULL DEFAULT 1,
                timestamp    INTEGER NOT NULL,
                game_ids     TEXT NOT NULL,
                team_1_id    INTEGER NOT NULL,
                team_2_id    INTEGER NOT NULL,
                team_1_score INTEGER NOT NULL,
                team_2_score INTEGER NOT NULL)""")
            conn.commit()
    
    def add(self, game_ids: list[int], team_1_id: int, team_2_id: int, team_1_score: int,
            team_2_score: int, series_id: int = types.MISSING,
            connection_override: sqlite3.Connection = None, **specifiers: str) -> int:
        return self.db.add([
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("specifiers", specifiers or types.MISSING, dbutils.DictCompiler()),
            dbutils.db.part("timestamp", int(time.time())),
            dbutils.db.part("game_ids", game_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score)
        ], connection_override, lambda x: x.lastrowid)
    
    def get(self, batchsize: int = None, matchall: bool = True,
            series_id: int | types.Expression[int] = types.MISSING,
            specifiers: types.Expression[dict[str, str]] = types.MISSING,
            active: bool | types.Expression[bool] = types.MISSING,
            timestamp: int | types.Expression[int] = types.MISSING,
            game_ids: types.Expression[list[int]] = types.MISSING,
            team_1_id: int | types.Expression[int] = types.MISSING,
            team_2_id: int | types.Expression[int] = types.MISSING,
            team_1_score: int | types.Expression[int] = types.MISSING,
            team_2_score: int | types.Expression[int] = types.MISSING
            ) -> models.Series | list[models.Series] | None:
            
        return self.db.get([
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("specifiers", specifiers, dbutils.DictCompiler(),
                            dbutils.DictDecompiler(str, str)),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("game_ids", game_ids, dbutils.ListCompiler(),
                            dbutils.ListDecompiler(int)),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score)
        ], batchsize, matchall, models.Series)
    
    def remove(self, matchall: bool = True,
               series_id: int | types.Expression[int] = types.MISSING,
               specifiers: types.Expression[dict[str, str]] = types.MISSING,
               active: bool | types.Expression[bool] = types.MISSING,
               timestamp: int | types.Expression[int] = types.MISSING,
               game_ids: types.Expression[list[int]] = types.MISSING,
               team_1_id: int | types.Expression[int] = types.MISSING,
               team_2_id: int | types.Expression[int] = types.MISSING,
               team_1_score: int | types.Expression[int] = types.MISSING,
               team_2_score: int | types.Expression[int] = types.MISSING,
               connection_override: sqlite3.Connection = None
               ) -> models.Series | list[models.Series] | None:

        return self.db.remove([
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("specifiers", specifiers, dbutils.DictCompiler()),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("game_ids", game_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score)
        ], matchall, connection_override)
    
    def edit(self, series_id: int = types.MISSING,
             specifiers: dict[str, str] | None = types.MISSING, active: bool = types.MISSING,
             timestamp: int = types.MISSING, game_ids: list[int] = types.MISSING,
             team_1_id: int = types.MISSING, team_2_id: int = types.MISSING,
             team_1_score: int = types.MISSING, team_2_score: int = types.MISSING):
        _editor = self.db.edit([
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("specifiers", specifiers, dbutils.DictCompiler()),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("game_ids", game_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score)
        ])

        def _edit(matchall: bool = True, series_id: int | types.Expression[int] = types.MISSING,
                  specifiers: types.Expression[dict[str, str]] = types.MISSING,
                  active: bool | types.Expression[bool] = types.MISSING,
                  timestamp: int | types.Expression[int] = types.MISSING,
                  game_ids: types.Expression[list[int]] = types.MISSING,
                  team_1_id: int | types.Expression[int] = types.MISSING,
                  team_2_id: int | types.Expression[int] = types.MISSING,
                  team_1_score: int | types.Expression[int] = types.MISSING,
                  team_2_score: int | types.Expression[int] = types.MISSING,
                  connection_override: sqlite3.Connection = None) -> None:
            
            return _editor([
                dbutils.db.part("series_id", series_id),
                dbutils.db.part("specifiers", specifiers, dbutils.DictCompiler()),
                dbutils.db.part("active", active, decompiler=bool),
                dbutils.db.part("timestamp", timestamp),
                dbutils.db.part("game_ids", game_ids, dbutils.ListCompiler()),
                dbutils.db.part("team_1_id", team_1_id),
                dbutils.db.part("team_2_id", team_2_id),
                dbutils.db.part("team_1_score", team_1_score),
                dbutils.db.part("team_2_score", team_2_score)
            ], matchall, connection_override)

        return _edit


class Games(TableMapping[models.Game], table="GAMES"):
    def _ensure_table_exists(self) -> None:
        with self._db_conn as (conn, cur):
            cur.execute("""CREATE TABLE IF NOT EXISTS GAMES (
                game_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                active          INTEGER NOT NULL DEFAULT 1,
                timestamp       INTEGER NOT NULL,
                series_id       INTEGER NOT NULL,
                team_1_id       INTEGER NOT NULL,
                team_2_id       INTEGER NOT NULL,
                team_1_score    INTEGER NOT NULL,
                team_2_score    INTEGER NOT NULL,
                team_1_user_ids TEXT NOT NULL,
                team_2_user_ids TEXT NOT NULL)""")
            conn.commit()
    
    def add(self, series_id: int, team_1_id: int, team_2_id: int, team_1_score: int,
            team_2_score: int, team_1_user_ids: list[int], team_2_user_ids: list[int],
            game_id: int = types.MISSING, connection_override: sqlite3.Connection = None) -> None:
        self.db.add([
            dbutils.db.part("game_id", game_id),
            dbutils.db.part("timestamp", int(time.time())),
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score),
            dbutils.db.part("team_1_user_ids", team_1_user_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_2_user_ids", team_2_user_ids, dbutils.ListCompiler())
        ], connection_override)
    
    def get(self, batchsize: int = None, matchall: bool = True,
            series_id: int | types.Expression[int] = types.MISSING,
            active: bool | types.Expression[bool] = types.MISSING,
            timestamp: int | types.Expression[int] = types.MISSING,
            team_1_id: int | types.Expression[int] = types.MISSING,
            team_2_id: int | types.Expression[int] = types.MISSING,
            team_1_score: int | types.Expression[int] = types.MISSING,
            team_2_score: int | types.Expression[int] = types.MISSING,
            team_1_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
            team_2_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
            game_id: int | types.Expression[int] = types.MISSING
            ) -> models.Game | list[models.Game] | None:
        return self.db.get([
            dbutils.db.part("game_id", game_id),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score),
            dbutils.db.part("team_1_user_ids", team_1_user_ids, dbutils.ListCompiler(),
                            dbutils.ListDecompiler(int)),
            dbutils.db.part("team_2_user_ids", team_2_user_ids, dbutils.ListCompiler(),
                            dbutils.ListDecompiler(int))
        ], batchsize, matchall, models.Game)
    
    def remove(self, matchall: bool = True, series_id: int | types.Expression[int] = types.MISSING,
            active: bool | types.Expression[bool] = types.MISSING,
            timestamp: int | types.Expression[int] = types.MISSING,
            team_1_id: int | types.Expression[int] = types.MISSING,
            team_2_id: int | types.Expression[int] = types.MISSING,
            team_1_score: int | types.Expression[int] = types.MISSING,
            team_2_score: int | types.Expression[int] = types.MISSING,
            team_1_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
            team_2_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
            game_id: int | types.Expression[int] = types.MISSING,
            connection_override: sqlite3.Connection = None) -> None:
        self.db.remove([
            dbutils.db.part("game_id", game_id),
            dbutils.db.part("active", active, decompiler=bool),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score),
            dbutils.db.part("team_1_user_ids", team_1_user_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_2_user_ids", team_2_user_ids, dbutils.ListCompiler())
        ], matchall, connection_override)

    def edit(self, game_id: int = types.MISSING, active: bool = types.MISSING,
             timestamp: int = types.MISSING, series_id: int = types.MISSING,
             team_1_id: int = types.MISSING, team_2_id: int = types.MISSING,
             team_1_score: int = types.MISSING, team_2_score: int = types.MISSING,
             team_1_user_ids: list[int] = types.MISSING,
             team_2_user_ids: list[int] = types.MISSING):
        _editor = self.db.edit([
            dbutils.db.part("game_id", game_id),
            dbutils.db.part("active", active),
            dbutils.db.part("timestamp", timestamp),
            dbutils.db.part("series_id", series_id),
            dbutils.db.part("team_1_id", team_1_id),
            dbutils.db.part("team_2_id", team_2_id),
            dbutils.db.part("team_1_score", team_1_score),
            dbutils.db.part("team_2_score", team_2_score),
            dbutils.db.part("team_1_user_ids", team_1_user_ids, dbutils.ListCompiler()),
            dbutils.db.part("team_2_user_ids", team_2_user_ids, dbutils.ListCompiler())
        ])

        def _edit(matchall: bool = True, series_id: int | types.Expression[int] = types.MISSING,
                  active: bool | types.Expression[bool] = types.MISSING,
                  timestamp: int | types.Expression[int] = types.MISSING,
                  team_1_id: int | types.Expression[int] = types.MISSING,
                  team_2_id: int | types.Expression[int] = types.MISSING,
                  team_1_score: int | types.Expression[int] = types.MISSING,
                  team_2_score: int | types.Expression[int] = types.MISSING,
                  team_1_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
                  team_2_user_ids: list[int] | types.Expression[list[int]] = types.MISSING,
                  game_id: int | types.Expression[int] = types.MISSING,
                  connection_override: sqlite3.Connection = None) -> None:
            
            _editor([
                dbutils.db.part("game_id", game_id),
                dbutils.db.part("active", active, decompiler=bool),
                dbutils.db.part("timestamp", timestamp),
                dbutils.db.part("series_id", series_id),
                dbutils.db.part("team_1_id", team_1_id),
                dbutils.db.part("team_2_id", team_2_id),
                dbutils.db.part("team_1_score", team_1_score),
                dbutils.db.part("team_2_score", team_2_score),
                dbutils.db.part("team_1_user_ids", team_1_user_ids, dbutils.ListCompiler()),
                dbutils.db.part("team_2_user_ids", team_2_user_ids, dbutils.ListCompiler())
            ], matchall, connection_override)

        return _edit


class Registrar:
    def __init__(self, db_path: str) -> None:
        self._db_conn = dbutils.AutoSqliteConnection(db_path)
        self.users = Users(self)
        self.teams = Teams(self)
        self.serieses = Serieses(self)
        self.games = Games(self)
    
    @property
    def series(self) -> Serieses:
        return self.serieses
