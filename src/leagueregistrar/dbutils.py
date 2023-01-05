"""Numerous SQLite database utilities used by `registrar` as well as the end-user.

:copyright: (c) 2022-present Tanner B. Corcoran
:license: MIT, see LICENSE for more details.
"""

__author__ = "Tanner B. Corcoran"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022-present Tanner B. Corcoran"


from . import types
import sqlite3
import typing


def _compile(value, compiler: typing.Callable[[typing.Any], typing.Any]) -> typing.Any:
    return value if compiler is types.MISSING else compiler(value)


def _decompile(value, decomipler: typing.Callable[[typing.Any], typing.Any]) -> typing.Any:
    return value if decomipler is types.MISSING else decomipler(value)


class ListCompiler(types.Compiler):
    def __call__(self, value: list) -> typing.Optional[str]:
        return value and chr(130).join([f"{chr(134)}{v}{chr(135)}" for v in value])
        

class ListDecompiler(types.Decompiler):
    def __call__(self, value: str) -> list[types.T]:
        return value and [self.format(v[1:-1])[0] for v in value.split(chr(130))]


class DictCompiler(types.Compiler):
    def __call__(self, value: dict) -> typing.Optional[str]:
        return value and chr(130).join([f"{chr(134)}{k}{chr(131)}{v}{chr(135)}" for k, v in
                                        value.items()])


class DictDecompiler(types.Decompiler):
    def __call__(self, value: str) -> types.T:
        return value and dict([self.format(*(v[1:-1]).split(chr(131))) for v in
                               value.split(chr(130))])


class or_(types.Expression):
    def __init__(self, *values: types.Expression | typing.Any) -> None:
        self.value = types.MISSING if all(v is types.MISSING for v in values) else values
    
    def format(self, column: str,
               compiler: typing.Callable[[typing.Any], typing.Any]) -> tuple[str, list]:
        statements, parameters = db._build_where([db.part(column, v, compiler) for v in self.value])
        return " OR ".join(statements), list(parameters)


class and_(types.Expression):
    def __init__(self, *values: types.Expression | typing.Any) -> None:
        self.value = types.MISSING if all(v is types.MISSING for v in values) else values
    
    def format(self, column: str,
               compiler: typing.Callable[[typing.Any], typing.Any]) -> tuple[str, list]:
        statements, parameters = db._build_where([db.part(column, v, compiler) for v in self.value])
        return " AND ".join(statements), list(parameters)


class is_not(types.Expression):
    def __init__(self, value: types.Expression | typing.Any) -> None:
        """Succeeds if: column is not equal to ``value`` or if ``value``
        (expression) resolves to false.
        
        """
        self.value = value
    
    def format(self, column: str,
               compiler: typing.Callable[[typing.Any], typing.Any]) -> tuple[str, list]:
        if isinstance(self.value, types.Expression):
            stmt, params = self.value.format(column, compiler)
            return (f"NOT {stmt}", params)
        return (f"{column} IS NOT ?", [_compile(self.value, compiler)])


class is_(types.Expression):
    def __init__(self, value: typing.Any) -> None:
        """Succeeds if: column is equal to ``value``.
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[typing.Any], typing.Any]) -> tuple[str, list]:
        return (f"{column} IS ?", [_compile(self.value, compiler)])


class collate_nocase(types.Expression):
    def __init__(self, value: str) -> None:
        """Succeeds if column is equal to ``value`` (NOCASE compare).
        
        """
        self.value = value

    def format(self, column: str, compiler: typing.Callable[[str], str]) -> tuple[str, list]:
        return (f"{column} IS ? COLLATE NOCASE", [_compile(self.value, compiler)])


class collate_binary(types.Expression):
    def __init__(self, value: typing.Any) -> None:
        """Succeeds if column is equal to ``value`` (BINARY compare).
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[typing.Any], typing.Any]) -> tuple[str, list]:
        return (f"{column} IS ? COLLATE BINARY", [_compile(self.value, compiler)])


class collate_rtrim(types.Expression):
    def __init__(self, value: str) -> None:
        """Succeeds if column is equal to ``value`` (RTRIM compare).
        
        """
        self.value = value

    def format(self, column: str, compiler: typing.Callable[[str], str]) -> tuple[str, list]:
        return (f"{column} IS ? COLLATE RTRIM", [_compile(self.value, compiler)])


class substr(types.Expression):
    def __init__(self, value: str) -> None:
        """Succeeds if ``value`` is a substring of column (CASE compare).
        
        """
        self.value = value

    def format(self, column: str, compiler: typing.Callable[[str], str]) -> tuple[str, list]:
        return (f"instr({column}, ?)", [_compile(self.value, compiler)])


class nocase_substr(types.Expression):
    def __init__(self, value: str) -> None:
        """Succeeds if ``value`` is a substring of column (NOCASE compare).
        
        """
        self.value = value

    def format(self, column: str, compiler: typing.Callable[[str], str]) -> tuple[str, list]:
        return (f"{column} LIKE '%'||?||'%' ESCAPE '\\'", [_compile(self.value, compiler)])


class between(types.Expression):
    def __init__(self, a: int | float, b: int | float) -> None:
        """Succeeds if column is between ``a`` and ``b``.
        
        """
        self.value = [a, b]

    def format(self, column: str,
               compiler: typing.Callable[[int | float, int | float], list[int | float]]
                     ) -> tuple[str, list]:
        return (f"{column} BETWEEN ? AND ?", _compile(self.value, compiler))


class greater_than(types.Expression):
    def __init__(self, value: int | float) -> None:
        """Succeeds if column greater than ``value``.
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[int | float], int | float]) -> tuple[str, list]:
        return (f"{column} > ?", _compile(self.value, compiler))


class greater_than_or_equal(types.Expression):
    def __init__(self, value: int | float) -> None:
        """Succeeds if column greater than or equal to ``value``.
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[int | float], int | float]) -> tuple[str, list]:
        return (f"{column} >= ?", [_compile(self.value, compiler)])


class less_than(types.Expression):
    def __init__(self, value: int | float) -> None:
        """Succeeds if column less than ``value``.
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[int | float], int | float]) -> tuple[str, list]:
        return (f"{column} < ?", [_compile(self.value, compiler)])


class less_than_or_equal(types.Expression):
    def __init__(self, value: int | float) -> None:
        """Succeeds if column less than or equal to ``value``.
        
        """
        self.value = value

    def format(self, column: str,
               compiler: typing.Callable[[int | float], int | float]) -> tuple[str, list]:
        return (f"{column} <= ?", [_compile(self.value, compiler)])


class custom(types.Expression):
    def __init__(self, expr: str, *params: typing.Any) -> None:
        """Succeeds if ``expr`` (given ``params``) succeeds.
        
        """
        self.value = (expr, list(params))

    def format(self, column: str, compiler: None) -> tuple[str, list]:
        return self.value


class AutoSqliteConnection:
    def __init__(self, path: str) -> None:
        self._path = path
        self._conn: sqlite3.Connection = None
    
    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self._conn = sqlite3.connect(self._path)
        return self._conn, self._conn.cursor()
    
    def __exit__(self, *_) -> None:
        self._conn = self._conn.close()


class db:
    def __init__(self, db_conn: AutoSqliteConnection, table: str) -> None:
        self._db_conn = db_conn
        self.table = table

    class part:
        def __init__(self, column: str, expr: typing.Any,
                     compiler: typing.Callable = types.MISSING,
                     decompiler: typing.Callable = types.MISSING) -> None:
            self.column = column
            self.expr = expr
            self.compiler = compiler
            self.decompiler = decompiler

    @staticmethod
    def _build_where(parts: typing.Iterable[part]) -> tuple[list[str], list]:
        statements = []
        parameters = []
        for p in parts:
            if p.expr is types.MISSING:
                continue
            
            if isinstance(p.expr, types.Expression):
                if p.expr.value is types.MISSING:
                    continue
                _expr = p.expr
            else:
                _expr = is_(p.expr)

            s, p = _expr.format(p.column, p.compiler)
            statements.append(s)
            parameters.extend(p)

        return (statements, parameters)
    
    @staticmethod
    def _build_insert(parts: typing.Iterable[part]) -> tuple[list[str], list]:
        return ([p.column for p in parts if p.expr is not types.MISSING],
                [_compile(p.expr, p.compiler) for p in parts if p.expr is not types.MISSING])
    
    @staticmethod
    def _build_set(parts: typing.Iterable[part]) -> tuple[list[str], list]:
        return ([f"{p.column}=?" for p in parts if p.expr is not types.MISSING],
                [_compile(p.expr, p.compiler) for p in parts if p.expr is not types.MISSING])

    @staticmethod
    def _decompile_all(values: typing.Iterable, parts: typing.Iterable[part]) -> typing.Iterable:
        return [_decompile(v, p.decompiler) for v, p in zip(values, parts)]

    def get(self, parts: typing.Iterable[part], batchsize: int = None, matchall: bool = True,
            builder: type[types.T] = None
            ) -> types.T | list[types.T] | typing.Any | list[typing.Any] | None:
        # prepare query
        joinwith = " AND " if matchall else " OR "
        statements, parameters = self._build_where(parts)
        if parameters:
            query = f"SELECT * FROM {self.table} WHERE {joinwith.join(statements)}"
            args = (query, parameters)
        else:
            query = f"SELECT * FROM {self.table}"
            args = (query,)

        # interact with db
        with self._db_conn as (conn, cur):
            excecution = cur.execute(*args)
            if batchsize is None:
                result = excecution.fetchall()
            else:
                result = excecution.fetchmany(batchsize)

        # turn query into instances of builder (if applicable)
        if not result:
            return
        if len(result[0]) != len(parts):
            raise ValueError(f"insufficient number of parts provided; expected {len(result[0])}, "
                             f"got {len(parts)}")
        if not builder:
            final = [self._decompile_all(dataset, parts) for dataset in result]
        else:
            final = [builder(*self._decompile_all(dataset, parts)) for dataset in result]
        return final[0] if batchsize == 1 else final

    def add(self, parts: typing.Iterable[part], connection: sqlite3.Connection = None,
            return_: typing.Callable[[sqlite3.Cursor], typing.Any] = None) -> typing.Any:
        # prepare for query
        statements, parameters = self._build_insert(parts)
        placeholders = ",".join("?" for _ in statements)
        if parameters:
            query = f"INSERT INTO {self.table} ({','.join(statements)}) VALUES ({placeholders})"
            args = (query, tuple(parameters))
        else:
            query = f"INSERT INTO {self.table}"
            args = (query,)

        # interact with db
        if connection:
            cur = connection.cursor()
            result = cur.execute(*args)
            if return_:
                return return_(result)
            return

        with self._db_conn as (conn, cur):
            result = cur.execute(*args)
            if return_:
                ret = return_(result)
            else:
                ret = None
            conn.commit()
            return ret
    
    def remove(self, parts: typing.Iterable[part], matchall: bool = True,
               connection: sqlite3.Connection = None) -> None:
        # prepare query
        joinwith = " AND " if matchall else " OR "
        statements, parameters = self._build_where(parts)
        if parameters:
            query = f"DELETE FROM {self.table} WHERE {joinwith.join(statements)}"
            args = (query, parameters)
        else:
            query = f"DELETE FROM {self.table}"
            args = (query,)

        # interact with db
        if connection:
            cur = connection.cursor()
            cur.execute(*args)
            return

        with self._db_conn as (conn, cur):
            cur.execute(*args)
            conn.commit()

    def edit(self, parts: typing.Iterable[part]):
        set_statements, set_parameters = self._build_set(parts)
        if not set_parameters and not set_statements:
            raise ValueError("no changes are being made")

        def _edit(parts: typing.Iterable[db.part], matchall: bool = True,
                  connection: sqlite3.Connection = None) -> None:
            # prepare query
            where_statements, where_parameters = self._build_where(parts)
            joinwith = " AND " if matchall else " OR "
            parameters = tuple([*set_parameters, *where_parameters])
            if where_parameters:
                query = (f"UPDATE {self.table} SET {','.join(set_statements)} WHERE "
                        f"{joinwith.join(where_statements)}")
                args = (query, parameters)
            else:
                query = f"UPDATE {self.table} SET {','.join(set_statements)}"
                args = (query, tuple(set_parameters))

            # interact with db
            if connection:
                cur = connection.cursor()
                return cur.execute(*args)

            with self._db_conn as (conn, cur):
                result = cur.execute(*args)
                conn.commit()
        
        return _edit
