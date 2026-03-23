# app/models/__init__.py

# Stage 3 Models (Dependencies)
from .day             import PlanDay
from .plan_item       import PlanItem

from .user            import User
from .user_plan       import UserPlan
from .ciudad          import Ciudad
from .categoria       import Categoria
from .preferencia     import Preferencia

# Catálogos
from .lugar           import Lugar
from .hospedaje       import Hospedaje
from .actividad       import Actividad
from .transporte      import Transporte

# Detalles de plan
from .plan_lugares    import PlanLugar
from .plan_hospedaje  import PlanHospedaje
from .plan_actividades import PlanActividad
from .plan_transporte import PlanTransporte
from .plan_segment    import PlanSegment

# Detalle jerárquico (V2/Stage 3 legacy)
from .plan_detail import (
    PlaceItem,
    ActivityItem,
    TransportSegment,
    LodgingItem,
    TravelLog
)

# Bitácora
from .historia_viaje  import HistoriaViaje

# Stage 9 — Unified Catalog
from .catalog_category import CatalogCategory
from .catalog_item     import CatalogItem
from .item_link        import ItemLink
from .catalog_transport_segment import CatalogTransportSegment
from .catalog_event      import CatalogEvent
from .destination_profile import DestinationProfile