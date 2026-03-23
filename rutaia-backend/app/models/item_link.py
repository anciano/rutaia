# app/models/item_link.py

import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.database import Base


RELATION_TYPES = ("contains", "near", "requires")


class ItemLink(Base):
    """Simple relationship between two catalog items.

    Examples:
        - Glaciar Exploradores (place) —contains→ Ruta Glaciar Exploradores (route)
        - Camping Río Simpson (lodging) —near→ Reserva Nacional Coyhaique (place)
        - Escalada en roca (activity) —requires→ Transporte 4x4 (transport)
    """
    __tablename__ = "item_links"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_item_id  = Column(Integer, ForeignKey("catalog_items.id", ondelete="CASCADE"), nullable=False)
    child_item_id   = Column(Integer, ForeignKey("catalog_items.id", ondelete="CASCADE"), nullable=False)
    relation_type   = Column(
        SAEnum(*RELATION_TYPES, name="item_relation_type", create_constraint=True),
        nullable=False,
    )
    sort_order      = Column(Integer, default=0)

    # Relationships
    parent = relationship("CatalogItem", foreign_keys=[parent_item_id], back_populates="child_links")
    child  = relationship("CatalogItem", foreign_keys=[child_item_id],  back_populates="parent_links")
