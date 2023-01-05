"""Types used by `dbutils` and `registrar`.

:copyright: (c) 2022-present Tanner B. Corcoran
:license: MIT, see LICENSE for more details.
"""

__author__ = "Tanner B. Corcoran"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022-present Tanner B. Corcoran"


import typing


T = typing.TypeVar("T")
VT = typing.TypeVar("VT")
KT = typing.TypeVar("KT")


class MISSING:
    """Represents a missing value.
    
    """


class Expression(typing.Generic[VT]):
    value: VT
    def format(self, column: str, mutator: typing.Callable[[VT], KT]) -> tuple[str, KT]: ...


class Compiler:
    def __call__(self, value: typing.Any) -> typing.Optional[str]:
        raise NotImplementedError()


class Decompiler:
    def __init__(self, *types: type[T]) -> None:
        self._types = types
    
    def format(self, *values) -> typing.Optional[T]:
        if not self._types:
            return values
        num_types = len(self._types)
        num_values = len(values)
        if num_values > num_types:
            types = list(self._types) + [self._types[-1]] * (num_values - num_types)
        else:
            types = self._types
        return [t(v) for t, v in zip(types, values)]

    
    def __call__(self, value: str) -> typing.Optional[T]:
        raise NotImplementedError()
