from enum import Enum


class CodeStatus(str, Enum):
    pending = "pending"
    used = "used"
