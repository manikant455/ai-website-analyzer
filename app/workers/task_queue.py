from celery import Celery
from app.core.config import settings
from app.services.seo_analyzer import SEOAnalyzer
from app.services.security_checker import SecurityChecker
from app.services.ai_engine import AIEngine
from app.core.database import db
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'website_analyzer',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
)

@celery_app.task(bind=True, max_retries=3)
def analyze_website_task(self, scan_id: str, url: str, scan_type: str = "full"):
    """Background task to analyze website"""
    try:
        # Update status to processing
        db.db.scans.update_one(
            {"_id": scan_id},
            {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
        )
        
        # Run analyses based on scan type
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        seo_results = None
        security_results = None
        
        if scan_type in ["full", "seo"]:
            seo_analyzer = SEOAnalyzer()
            seo_results = loop.run_until_complete(seo_analyzer.analyze(url))
            loop.run_until_complete(seo_analyzer.close())
        
        if scan_type in ["full", "security"]:
            security_checker = SecurityChecker()
            security_results = loop.run_until_complete(security_checker.analyze(url))
            loop.run_until_complete(security_checker.close())
        
        # Generate AI analysis
        if seo_results and security_results:
            ai_engine = AIEngine()
            ai_analysis = loop.run_until_complete(
                ai_engine.generate_analysis(seo_results, security_results, url)
            )
        else:
            ai_analysis = {
                "summary": "Partial analysis completed",
                "suggestions": ["Complete full scan for AI recommendations"],
                "priority_issues": []
            }
        
        loop.close()
        
        # Update scan with results
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if seo_results:
            update_data["seo_score"] = seo_results
        if security_results:
            update_data["security_score"] = security_results
        if ai_analysis:
            update_data["ai_summary"] = ai_analysis.get("summary")
            update_data["ai_suggestions"] = ai_analysis.get("suggestions")
            update_data["priority_issues"] = ai_analysis.get("priority_issues")
        
        db.db.scans.update_one(
            {"_id": scan_id},
            {"$set": update_data}
        )
        
        # Cache results in Redis for 1 hour
        db.redis.setex(
            f"scan:{scan_id}",
            3600,
            str(update_data)
        )
        
        return {"status": "success", "scan_id": scan_id}
        
    except Exception as e:
        logger.error(f"Task failed for scan {scan_id}: {e}")
        
        # Update scan as failed
        db.db.scans.update_one(
            {"_id": scan_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))