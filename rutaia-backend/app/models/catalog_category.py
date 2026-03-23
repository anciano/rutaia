from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class CatalogCategory(Base):
    """Hierarchical taxonomy for RutaIA catalog items."""
    __tablename__ = "catalog_categories"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(120), nullable=False)
    slug       = Column(String(120), unique=True, nullable=False)
    parent_id  = Column(Integer, ForeignKey("catalog_categories.id"), nullable=True)
    root_block = Column(String(60), nullable=True) # e.g. Naturaleza, Logística...
    icon       = Column(String(60), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active  = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent   = relationship("CatalogCategory", remote_side=[id], backref="children")
    items    = relationship("CatalogItem", back_populates="category")
