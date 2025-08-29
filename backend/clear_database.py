#!/usr/bin/env python3
"""
Script to clear all quiz-related data from the database
Run this to start fresh with the new quiz history feature
"""

import asyncio
from sqlalchemy import text
from app.database import async_engine

async def clear_database():
    """Clear all quiz-related data from the database"""
    async with async_engine.begin() as conn:
        print("🗑️  Clearing database tables...")
        
        # Clear tables in the correct order (respecting foreign key constraints)
        tables_to_clear = [
            "quiz_answers",      # Clear first (references other tables)
            "quiz_submissions",  # Clear second (references quizzes)
            "quiz_questions",    # Clear third (references quizzes)
            "quizzes"           # Clear last (referenced by others)
        ]
        
        for table in tables_to_clear:
            try:
                result = await conn.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount
                print(f"✅ Cleared {count} rows from {table}")
            except Exception as e:
                print(f"❌ Error clearing {table}: {e}")
        
        print("🎉 Database cleared successfully!")
        print("📝 You can now generate new quizzes to test the history feature")

if __name__ == "__main__":
    print("🧹 Database Cleanup Tool")
    print("=" * 40)
    
    # Run the cleanup
    asyncio.run(clear_database())
