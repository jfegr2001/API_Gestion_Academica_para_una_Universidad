from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Base
from models.academic import Semester, Subject, Schedule, Enrollment, Grade
from models.user import User, UserRole

target_metadata = Base.metadata

def get_url():
    MYSQL_USER = os.getenv("MYSQL_USER", "user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
    MYSQL_DB = os.getenv("MYSQL_DATABASE", "APIGestionAcademica-DB")
    return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online'."""
    try:
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = get_url()
    
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )
            
            with context.begin_transaction():
                # Eliminar tabla alembic_version si existe
                from sqlalchemy import text
                connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
                
                # Ejecutar migraciones
                context.run_migrations()

    except Exception as e:
        print(f"Error durante la migración: {e}")
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()