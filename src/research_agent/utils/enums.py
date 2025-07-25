from enum import Enum


class Database(str, Enum):
    pubmed = "pubmed centeral"
    semantic = "semantic scholar"

class SortOrder(str, Enum):
    relevance = "relevance"
    citation = "citation"
    date = "date"

class Task(str, Enum):
    meta = "meta"
    systematic = "systematic"

class Fetch(str, Enum):
    online = "online"
    local = "local"
