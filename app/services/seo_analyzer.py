"""
SEO Analyzer Service
Performs basic SEO analysis on websites
"""
import logging
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl
import socket
import time
import re

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.timeout = 10
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
    
    async def analyze(self, url: str) -> dict:
        """Analyze SEO aspects of a website"""
        try:
            start_time = time.time()
            
            # Fetch the page
            html_content = self._fetch_page(url)
            load_time = round(time.time() - start_time, 2)
            
            if not html_content:
                return self._get_default_seo_data()
            
            # Parse HTML content
            seo_data = {
                "score": 100,
                "title_tag": self._analyze_title(html_content),
                "meta_description": self._analyze_meta_description(html_content),
                "headings": self._analyze_headings(html_content),
                "images": self._analyze_images(html_content, url),
                "links": self._analyze_links(html_content, url),
                "mobile_friendly": self._check_mobile_friendly(html_content),
                "load_time": load_time,
                "ssl_certificate": self._check_ssl(url)
            }
            
            # Calculate score
            seo_data["score"] = self._calculate_score(seo_data)
            
            return seo_data
            
        except Exception as e:
            logger.error(f"SEO analysis failed for {url}: {e}")
            return self._get_default_seo_data()
    
    def _fetch_page(self, url: str) -> str:
        """Fetch webpage content"""
        try:
            req = Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response = urlopen(req, timeout=self.timeout, context=self.ctx)
            return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to fetch page: {e}")
            return ""
    
    def _analyze_title(self, html: str) -> dict:
        """Analyze title tag"""
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title_text = title_match.group(1).strip() if title_match else ""
        
        issues = []
        if not title_text:
            issues.append("Missing title tag")
        elif len(title_text) < 30:
            issues.append("Title is too short (less than 30 characters)")
        elif len(title_text) > 60:
            issues.append("Title is too long (more than 60 characters)")
        
        return {
            "exists": bool(title_text),
            "content": title_text,
            "length": len(title_text),
            "issues": issues
        }
    
    def _analyze_meta_description(self, html: str) -> dict:
        """Analyze meta description"""
        meta_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        content = meta_match.group(1) if meta_match else ""
        
        issues = []
        if not content:
            issues.append("Missing meta description")
        elif len(content) < 120:
            issues.append("Meta description is too short")
        elif len(content) > 160:
            issues.append("Meta description is too long")
        
        return {
            "exists": bool(content),
            "content": content[:200],
            "length": len(content) if content else 0,
            "issues": issues
        }
    
    def _analyze_headings(self, html: str) -> dict:
        """Analyze heading structure"""
        h1_count = len(re.findall(r'<h1[^>]*>', html, re.IGNORECASE))
        h2_count = len(re.findall(r'<h2[^>]*>', html, re.IGNORECASE))
        h3_count = len(re.findall(r'<h3[^>]*>', html, re.IGNORECASE))
        
        issues = []
        structure_valid = True
        
        if h1_count == 0:
            issues.append("Missing H1 tag")
            structure_valid = False
        elif h1_count > 1:
            issues.append("Multiple H1 tags found")
            structure_valid = False
        
        if h1_count > 0 and h2_count == 0:
            issues.append("No H2 tags found for content structure")
        
        return {
            "h1": h1_count,
            "h2": h2_count,
            "h3": h3_count,
            "structure_valid": structure_valid,
            "issues": issues
        }
    
    def _analyze_images(self, html: str, base_url: str) -> dict:
        """Analyze image tags"""
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        total = len(images)
        without_alt = len([img for img in images if 'alt=' not in img.lower()])
        
        issues = []
        if total > 0 and without_alt > 0:
            issues.append(f"{without_alt} images missing alt text")
        
        return {
            "total": total,
            "without_alt": without_alt,
            "without_dimensions": 0,
            "issues": issues
        }
    
    def _analyze_links(self, html: str, base_url: str) -> dict:
        """Analyze link structure"""
        links = re.findall(r'<a[^>]*href=["\'](.*?)["\']', html, re.IGNORECASE)
        domain = urlparse(base_url).netloc
        
        internal = 0
        external = 0
        
        for link in links:
            if link.startswith('http'):
                if domain in link:
                    internal += 1
                else:
                    external += 1
            else:
                internal += 1
        
        issues = []
        if internal == 0:
            issues.append("No internal links found")
        
        return {
            "total": len(links),
            "internal": internal,
            "external": external,
            "issues": issues
        }
    
    def _check_mobile_friendly(self, html: str) -> bool:
        """Check for viewport meta tag"""
        return bool(re.search(r'<meta[^>]*viewport', html, re.IGNORECASE))
    
    def _check_ssl(self, url: str) -> dict:
        """Check SSL certificate"""
        domain = urlparse(url).netloc
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        "valid": True,
                        "expires": cert.get('notAfter', 'Unknown'),
                        "issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "issues": []
                    }
        except Exception as e:
            return {
                "valid": False,
                "expires": "",
                "issuer": {},
                "issues": [f"SSL issue: {str(e)[:100]}"]
            }
    
    def _calculate_score(self, data: dict) -> int:
        """Calculate overall SEO score"""
        score = 100
        
        # Title checks
        if not data["title_tag"]["exists"]:
            score -= 20
        elif data["title_tag"]["issues"]:
            score -= 10
        
        # Meta description checks
        if not data["meta_description"]["exists"]:
            score -= 15
        
        # Heading checks
        if not data["headings"]["structure_valid"]:
            score -= 15
        
        # Image checks
        if data["images"]["total"] > 0 and data["images"]["without_alt"] > 0:
            score -= min(15, data["images"]["without_alt"] * 5)
        
        # Mobile check
        if not data["mobile_friendly"]:
            score -= 15
        
        # Load time
        if data["load_time"] > 3:
            score -= 10
        
        return max(0, min(100, score))
    
    def _get_default_seo_data(self) -> dict:
        """Return default SEO data when analysis fails"""
        return {
            "score": 0,
            "title_tag": {"exists": False, "content": "", "length": 0, "issues": ["Could not analyze"]},
            "meta_description": {"exists": False, "content": "", "length": 0, "issues": []},
            "headings": {"h1": 0, "h2": 0, "h3": 0, "structure_valid": False, "issues": ["Could not analyze"]},
            "images": {"total": 0, "without_alt": 0, "without_dimensions": 0, "issues": []},
            "links": {"total": 0, "internal": 0, "external": 0, "issues": []},
            "mobile_friendly": False,
            "load_time": 0,
            "ssl_certificate": {"valid": False, "expires": "", "issuer": {}, "issues": ["Could not check"]},
            "error": "Website could not be analyzed"
        }
    
    async def close(self):
        """Cleanup resources"""
        pass