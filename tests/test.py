import sys
sys.path.append(".")
from src.leagueregistrar import Registrar
from src.leagueregistrar import dbutils
# from leagueregistrar import dbtools, models, types
# import time

# def _compiler(values: list[str]) -> str:
#     SSA = chr(134)
#     ESA = chr(135)
#     BPH = chr(130)
#     return BPH.join([f"{SSA}{v}{ESA}" for v in values])
# def _decompiler(values: str) -> list[str]:
#     BPH = chr(130)
#     return [v[1:-1] for v in values.split(BPH)]




# r = Registrar("tests/db")
# import sqlite3
# c = sqlite3.connect("tests/db")
# r.users.add("abc123", "abc123", c)
# print(r.users.get())
# c.commit()
# print(r.users.get())

# r.serieses.add([1, 2, 3, 4], 1, 3, 3, 2, week=3, league="2v2", division="Blaze")
# print(r.series.remove(series_id=1))
# print(r.series.get())
# r.series.edit(game_ids=[4, 3, 2, 1], specifiers={"week": "4", "league": "1v1", "division": "Inferno"}, active=False)(series_id=1)
# print(r.users.get(previous_usernames=dbutils.and_(dbutils.substr("previous_username_1"), dbutils.substr("previous_username_0"))))
# r.users.add(12345678901234567890, "username_1")
# print(r.users.edit(previous_usernames=["previous_username_0", "previous_username_1", "previous_username_2"])(user_id=1))
# r.teams.add(1, "team_1")
# r.teams.add(2, "team_2")
# print(r.teams.get())
# print(r.teams.remove(id=1))




# db = dbtools.db(dbtools.AutoSqliteConnection("db"), "USERS")
# # db.add([
# #     dbtools.db.part("registration_timestamp", 0),
# #     dbtools.db.part("discord_id", "0"),
# #     dbtools.db.part("username", ["name_a", "name_b", "name_c"], _compiler, _decompiler)
# # ])
# print(db.get([
#     dbtools.db.part("user_id", types.MISSING),
#     dbtools.db.part("active", types.MISSING, decompiler=bool),
#     dbtools.db.part("timestamp", types.MISSING),
#     dbtools.db.part("discord_id", types.MISSING),
#     dbtools.db.part("username", types.MISSING, decompiler=_decompiler),
#     dbtools.db.part("num_name_changes", types.MISSING),
#     dbtools.db.part("team", types.MISSING)
# ], builder=models.User, matchall=True))














