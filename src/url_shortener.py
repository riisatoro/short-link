from uuid import uuid4
import hashlib


def make_short_url(length: int = 10) -> str:
    return hashlib.md5(str(uuid4()).encode()).hexdigest()[:length]
