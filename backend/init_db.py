#!/usr/bin/env python3
"""
Database initialization script for AI Quiz Generator
Run this script to set up the database and create initial tables
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.config import settings
from app.database import close_db, init_db


async def main():
    """Initialize the database"""
    print("🚀 Initializing AI Quiz Generator Database...")
    print(f"📊 Database URL: {'***' if settings.DATABASE_URL else 'None'}")

    try:
        # Initialize database (create tables)
        await init_db()
        print("✅ Database initialized successfully!")
        print("📋 Tables created:")
        print("   - quizzes")
        print("   - quiz_questions")
        print("   - quiz_submissions")
        print("   - quiz_answers")
        print("   - chat_sessions")
        print("   - chat_messages")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check your DATABASE_URL in .env file")
        print("   3. Verify database credentials")
        print("   4. Ensure database 'ai_quiz_db' exists")
        sys.exit(1)

    finally:
        # Close database connections
        await close_db()
        print("🔌 Database connections closed")


if __name__ == "__main__":
    asyncio.run(main())
