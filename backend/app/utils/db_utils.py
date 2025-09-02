import logging
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_database_connection(db: AsyncSession) -> bool:
    """Check if database connection is working"""
    try:
        result = await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def get_database_info(db: AsyncSession) -> Optional[Dict[str, Any]]:
    """Get basic database information"""
    try:
        # Get PostgreSQL version
        version_result = await db.execute(text("SELECT version()"))
        version = version_result.scalar()

        # Get current database name
        db_name_result = await db.execute(text("SELECT current_database()"))
        db_name = db_name_result.scalar()

        # Get current user
        user_result = await db.execute(text("SELECT current_user"))
        user = user_result.scalar()

        return {
            "version": version,
            "database": db_name,
            "user": user,
            "status": "connected",
        }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return None


async def execute_raw_sql(
    db: AsyncSession, sql: str, params: Optional[Dict[str, Any]] = None
) -> Any:
    """Execute raw SQL with optional parameters"""
    try:
        result = await db.execute(text(sql), params or {})
        return result
    except Exception as e:
        logger.error(f"Raw SQL execution failed: {e}")
        raise


async def health_check_database(db: AsyncSession) -> Dict[str, Any]:
    """Perform a comprehensive database health check"""
    try:
        # Check connection
        connection_ok = await check_database_connection(db)

        # Get database info
        db_info = await get_database_info(db)

        # Check if tables exist
        tables_result = await db.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
            )
        )
        tables = [row[0] for row in tables_result.fetchall()]

        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "connection": connection_ok,
            "database_info": db_info,
            "tables": tables,
            "timestamp": "now()",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "error": str(e), "timestamp": "now()"}
