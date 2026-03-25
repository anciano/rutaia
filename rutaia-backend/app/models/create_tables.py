from app.models.database import Base, engine
import app.models  # Import the package to register all models

# Muy importante: la importación de 'app.models' arriba registra todas las clases en Base.metadata
Base.metadata.create_all(bind=engine)