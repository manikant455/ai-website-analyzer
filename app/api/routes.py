from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import asyncio
import logging

from app.services.seo_analyzer import SEOAnalyzer
from app.services.security_checker import SecurityChecker
from app.services.ai_engine import AIEngine
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage (for now, until MongoDB is connected)
scans_db = {}

def generate_fallback_analysis(url: str, seo_data: Optional[Dict] = None, security_data: Optional[Dict] = None) -> Dict:
    """Generate rule-based fallback analysis when AI API is not available"""
    
    issues = []
    suggestions = []
    priority = []
    
    # Analyze SEO data if available
    if seo_data:
        # Title analysis
        if seo_data.get("title_tag", {}).get("issues"):
            for issue in seo_data["title_tag"]["issues"]:
                issues.append(f"SEO: {issue}")
                suggestions.append(f"Fix title tag: {issue}")
                if "Missing" in issue:
                    priority.append("Critical: Missing title tag")
                    
        # Meta description analysis
        if seo_data.get("meta_description", {}).get("issues"):
            for issue in seo_data["meta_description"]["issues"]:
                issues.append(f"SEO: {issue}")
                suggestions.append(f"Fix meta description: {issue}")
        
        # Image analysis
        if seo_data.get("images", {}).get("without_alt", 0) > 0:
            count = seo_data["images"]["without_alt"]
            issues.append(f"SEO: {count} images missing alt text")
            suggestions.append(f"Add descriptive alt text to {count} images for better accessibility and SEO")
            if count > 5:
                priority.append("High: Many images missing alt text")
        
        # Load time
        load_time = seo_data.get("load_time", 0)
        if load_time > 3:
            issues.append(f"Performance: Slow page load time ({load_time}s)")
            suggestions.append(f"Optimize page load time (currently {load_time}s) by compressing images and minifying resources")
            if load_time > 5:
                priority.append("Critical: Very slow page load time")
        
        # Mobile friendly
        if not seo_data.get("mobile_friendly", True):
            issues.append("Mobile: Website is not mobile-friendly")
            suggestions.append("Add responsive design and viewport meta tag for mobile optimization")
            priority.append("High: Website not mobile-friendly")
    
    # Analyze Security data if available
    if security_data:
        # SSL
        if not security_data.get("ssl_valid", True):
            issues.append("Security: Invalid or missing SSL certificate")
            suggestions.append("Install a valid SSL certificate to enable HTTPS")
            priority.append("Critical: Missing SSL certificate")
        
        # Security headers
        missing_headers = security_data.get("http_headers", {}).get("missing", [])
        if missing_headers:
            headers_str = ", ".join(missing_headers)
            issues.append(f"Security: Missing headers - {headers_str}")
            suggestions.append(f"Add missing security headers: {headers_str}")
            if "Content-Security-Policy" in missing_headers:
                priority.append("High: Missing Content-Security-Policy header")
        
        # Vulnerabilities
        vulnerabilities = security_data.get("vulnerabilities", [])
        if vulnerabilities:
            for vuln in vulnerabilities:
                issues.append(f"Security: {vuln}")
                suggestions.append(f"Fix security issue: {vuln}")
                if "Missing security header" in vuln:
                    priority.append(f"High: {vuln}")
        
        # Open ports
        open_ports = security_data.get("open_ports", [])
        dangerous_ports = set(open_ports) - {80, 443}
        if dangerous_ports:
            ports_str = ", ".join(map(str, dangerous_ports))
            issues.append(f"Security: Unusual open ports - {ports_str}")
            suggestions.append(f"Close unnecessary ports: {ports_str}")
            priority.append(f"Medium: Unusual open ports detected")
    
    # Generate summary
    if issues:
        summary = f"Analysis of {url} revealed {len(issues)} issues. "
        if priority:
            summary += f"Critical concerns include: {', '.join(priority[:2])}. "
        summary += "This is an automated fallback analysis as AI-powered analysis is not available."
    else:
        summary = f"No major issues found on {url}. This is an automated fallback analysis."
    
    # Ensure we have at least some suggestions
    if not suggestions:
        suggestions = [
            "Regularly update your website content for better SEO",
            "Implement HTTPS if not already using it",
            "Add security headers like Content-Security-Policy",
            "Optimize images and minify CSS/JS for better performance",
            "Ensure your website is mobile-responsive"
        ]
    
    if not priority:
        priority = ["Review security headers", "Check page load speed", "Verify mobile responsiveness"]
    
    return {
        "summary": summary,
        "suggestions": suggestions[:5],  # Top 5 suggestions
        "priority_issues": priority[:3],  # Top 3 priorities
        "is_ai_generated": False,
        "note": "⚠️ This is a fallback rule-based analysis. AI-powered analysis is not available. Set OPENAI_API_KEY in .env for AI-generated insights."
    }

@router.post("/scan")
async def create_scan(scan_request: Dict):
    """Initiate a new website scan with real analysis"""
    try:
        scan_id = str(uuid.uuid4())
        url = scan_request.get("url")
        scan_type = scan_request.get("scan_type", "full")
        
        logger.info(f"Starting scan {scan_id} for {url}")
        
        # Initialize results
        seo_data = None
        security_data = None
        ai_analysis = None
        
        # Run SEO analysis
        if scan_type in ["full", "seo"]:
            try:
                logger.info(f"Running SEO analysis for {url}")
                seo_analyzer = SEOAnalyzer()
                seo_data = await seo_analyzer.analyze(url)
                await seo_analyzer.close()
                logger.info(f"SEO analysis completed. Score: {seo_data.get('score')}")
            except Exception as e:
                logger.error(f"SEO analysis failed: {e}")
                seo_data = {
                    "score": 0,
                    "error": str(e),
                    "title_tag": {"exists": False, "content": "", "length": 0, "issues": ["Could not analyze - website may be unreachable"]},
                    "meta_description": {"exists": False, "content": "", "length": 0, "issues": []},
                    "headings": {"h1": 0, "h2": 0, "h3": 0, "structure_valid": False, "issues": []},
                    "images": {"total": 0, "without_alt": 0, "without_dimensions": 0, "issues": []},
                    "links": {"total": 0, "internal": 0, "external": 0, "issues": []},
                    "mobile_friendly": False,
                    "load_time": 0,
                    "ssl_certificate": {"valid": False, "expires": "", "issuer": {}, "issues": ["Could not verify SSL"]}
                }
        
        # Run Security analysis
        if scan_type in ["full", "security"]:
            try:
                logger.info(f"Running security analysis for {url}")
                security_checker = SecurityChecker()
                security_data = await security_checker.analyze(url)
                await security_checker.close()
                logger.info(f"Security analysis completed. Score: {security_data.get('score')}")
            except Exception as e:
                logger.error(f"Security analysis failed: {e}")
                security_data = {
                    "score": 0,
                    "error": str(e),
                    "ssl_valid": False,
                    "http_headers": {"headers": {}, "missing": ["Could not retrieve headers"], "score": 0},
                    "cookies": {"total": 0, "secure": 0, "http_only": 0, "issues": ["Could not analyze cookies"]},
                    "open_ports": [],
                    "vulnerabilities": ["Could not complete security scan"]
                }
        
        # Try AI analysis first, fallback if not available
        try:
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
                logger.info("OpenAI API key found, generating AI analysis...")
                ai_engine = AIEngine()
                ai_analysis = await ai_engine.generate_analysis(seo_data, security_data, url)
                ai_analysis["is_ai_generated"] = True
                ai_analysis["note"] = "✅ AI-powered analysis using OpenAI GPT"
                logger.info("AI analysis completed successfully")
            else:
                logger.warning("No valid OpenAI API key found, using fallback analysis")
                ai_analysis = generate_fallback_analysis(url, seo_data, security_data)
        except Exception as e:
            logger.error(f"AI analysis failed, using fallback: {e}")
            ai_analysis = generate_fallback_analysis(url, seo_data, security_data)
            ai_analysis["note"] += f" (AI attempt failed: {str(e)[:100]})"
        
        # Create complete scan record
        scan_record = {
            "id": scan_id,
            "url": url,
            "status": "completed",
            "scan_type": scan_type,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "seo_score": seo_data,
            "security_score": security_data,
            "ai_summary": ai_analysis.get("summary", ""),
            "ai_suggestions": ai_analysis.get("suggestions", []),
            "priority_issues": ai_analysis.get("priority_issues", []),
            "ai_analysis_metadata": {
                "is_ai_generated": ai_analysis.get("is_ai_generated", False),
                "note": ai_analysis.get("note", "Fallback analysis")
            }
        }
        
        # Store in memory
        scans_db[scan_id] = scan_record
        
        logger.info(f"Scan {scan_id} completed successfully")
        return scan_record
        
    except Exception as e:
        logger.error(f"Scan failed completely: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@router.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    scan = scans_db.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scans/recent")
async def get_recent_scans(limit: int = 10):
    """Get recent scans"""
    scans = list(scans_db.values())
    scans.sort(key=lambda x: x["created_at"], reverse=True)
    return scans[:limit]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    ai_status = "available" if (settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here") else "unavailable (using fallback)"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "scans_count": len(scans_db),
        "ai_service": ai_status,
        "features": {
            "seo_analysis": True,
            "security_scanning": True,
            "ai_powered": settings.OPENAI_API_KEY != "",
            "fallback_analysis": True
        }
    }