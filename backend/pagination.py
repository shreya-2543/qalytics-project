"""
Common pagination and filtering utilities for API endpoints
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page")
    offset: int = Field(default=0, ge=0, description="Items to skip")


class PaginatedResponse(BaseModel):
    """Standard paginated response wrapper"""
    items: List = Field(description="Array of items")
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Items skipped")
    
    @property
    def pages(self) -> int:
        """Calculate total pages"""
        return (self.total + self.limit - 1) // self.limit
    
    @property
    def current_page(self) -> int:
        """Calculate current page number"""
        return (self.offset // self.limit) + 1


def paginate(query, limit: int = 50, offset: int = 0):
    """
    Apply pagination to SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        limit: Items per page (max 1000)
        offset: Items to skip
        
    Returns:
        Limited query object
    """
    limit = min(limit, 1000)  # Cap at 1000
    return query.limit(limit).offset(offset)
