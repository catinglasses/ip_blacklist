from enum import Enum


class IPStatus(str, Enum):
    PENDING = "PENDING"  # pending user verification & evaluation to blacklist
    BLACKLIST = "BLACKLISTED"
    ARCHIVED = "ARCHIVED"  # IP at TTL end, pending deletion/re-blacklisting
