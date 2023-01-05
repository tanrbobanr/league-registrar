"""A system for programatically keeping track of league data.

:copyright: (c) 2022 Tanner B. Corcoran
:license: MIT, see LICENSE for more details.
"""

__title__ = "league-registrar"
__author__ = "Tanner B. Corcoran"
__email__ = "tannerbcorcoran@gmail.com"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022 Tanner B. Corcoran"
__version__ = "0.0.1"
__description__ = "A system for programatically keeping track of league data"
# __url__ = "https://github.com/tanrbobanr/pychasing"
# __download_url__ = "https://pypi.org/project/pychasing/"

from .dbutils import (
    or_,
    and_,
    is_not,
    is_,
    collate_nocase,
    collate_binary,
    collate_rtrim,
    substr,
    nocase_substr,
    between,
    greater_than,
    greater_than_or_equal,
    less_than,
    less_than_or_equal,
    custom
)
from . import models
from .registrar import Registrar

__all__ = (
    "or_",
    "and_",
    "is_not",
    "is_",
    "collate_nocase",
    "collate_binary",
    "collate_rtrim",
    "substr",
    "nocase_substr",
    "between",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "custom",
    "models",
    "Registrar"
)
