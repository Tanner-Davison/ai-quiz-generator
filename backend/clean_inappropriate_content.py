#!/usr/bin/env python3
"""
Clean up inappropriate content from the database
"""
import asyncio
from sqlalchemy import text
from app.database import async_engine

async def clean_inappropriate_content():
    async with async_engine.begin() as conn:
        print("🧹 Cleaning up inappropriate content...")
        
        # List of inappropriate topics to remove
        inappropriate_topics = [
            "vagina", "nipple", "sphincter", "feces"
        ]
        
        # Remove quizzes with inappropriate topics
        for topic in inappropriate_topics:
            try:
                # First, get the quiz IDs to remove related data
                quiz_result = await conn.execute(
                    text("SELECT id FROM quizzes WHERE LOWER(topic) = LOWER(:topic)")
                )
                quiz_ids = [row[0] for row in quiz_result.fetchall()]
                
                if quiz_ids:
                    print(f"🗑️  Removing quiz: '{topic}' (ID: {quiz_ids[0]})")
                    
                    # Remove in correct order due to foreign key constraints
                    await conn.execute(
                        text("DELETE FROM quiz_answers WHERE quiz_submission_id IN (SELECT id FROM quiz_submissions WHERE quiz_id = :quiz_id)"),
                        {"quiz_id": quiz_ids[0]}
                    )
                    
                    await conn.execute(
                        text("DELETE FROM quiz_submissions WHERE quiz_id = :quiz_id"),
                        {"quiz_id": quiz_ids[0]}
                    )
                    
                    await conn.execute(
                        text("DELETE FROM quiz_questions WHERE quiz_id = :quiz_id"),
                        {"quiz_id": quiz_ids[0]}
                    )
                    
                    await conn.execute(
                        text("DELETE FROM quizzes WHERE id = :quiz_id"),
                        {"quiz_id": quiz_ids[0]}
                    )
                    
                    print(f"✅ Removed quiz: '{topic}' and all related data")
                else:
                    print(f"ℹ️  No quiz found for topic: '{topic}'")
                    
            except Exception as e:
                print(f"❌ Error removing '{topic}': {e}")
        
        print("🎉 Database cleanup completed!")

if __name__ == "__main__":
    asyncio.run(clean_inappropriate_content())
