# backend/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Company:
    id: int
    name: str
    created_at: datetime
    
    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(id=data[0], name=data[1], created_at=data[2])

@dataclass
class Board:
    id: int
    company_id: int
    name: str
    description: str
    created_at: datetime
    
    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(
            id=data[0], 
            company_id=data[1], 
            name=data[2], 
            description=data[3], 
            created_at=data[4]
        )

@dataclass
class Note:
    id: int
    board_id: int
    topic: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    last_modified_by: str
    priority: int
    is_archived: bool
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            board_id=data['board_id'],
            topic=data['topic'],
            title=data['title'],
            content=data['content'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            created_by=data['created_by'],
            last_modified_by=data['last_modified_by'],
            priority=data['priority'],
            is_archived=bool(data['is_archived'])
        )