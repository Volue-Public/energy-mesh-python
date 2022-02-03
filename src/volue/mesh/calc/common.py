""""
Common classes/enums/etc for calculation functions
"""

from enum import Enum

class Timezone(Enum):
    """
    Timezone parameter
    """
    LOCAL    = 0
    STANDARD = 1
    UTC      = 2
