"""
Security Checker Service
Performs basic security analysis on websites
"""
import logging
import socket
import ssl
from urllib.parse import urlparse
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

class SecurityChecker:
    def __init__(self):
        self.timeout = 5
        self.common_ports = [80, 443, 8080, 8443, 21, 22, 25, 3306]
    
    async def analyze(self, url: str) -> dict:
        """Analyze security aspects of a website"""
        try:
            domain = urlparse(url).netloc
            
            security_data = {
                "score": 100,
                "ssl_valid": self._check_ssl(domain),
                "http_headers": self._check_headers(url),
                "cookies": {"total": 0, "secure": 0, "http_only": 0, "issues": []},
                "open_ports": self._scan_ports(domain),
                "vulnerabilities": []
            }
            
            # Check vulnerabilities
            security_data["vulnerabilities"] = self._check_vulnerabilities(security_data)
            
            # Calculate score
            security_data["score"] = self._calculate_score(security_data)
            
            return security_data
            
        except Exception as e:
            logger.error(f"Security analysis failed for {url}: {e}")
            return {
                "score": 0,
                "ssl_valid": False,
                "http_headers": {"headers": {}, "missing": ["Could not analyze"], "score": 0},
                "cookies": {"total": 0, "secure": 0, "http_only": 0, "issues": ["Could not analyze"]},
                "open_ports": [],
                "vulnerabilities": [f"Analysis failed: {str(e)[:100]}"],
                "error": str(e)
            }
    
    def _check_ssl(self, domain: str) -> bool:
        """Check SSL certificate"""
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    return True
        except:
            return False
    
    def _check_headers(self, url: str) -> dict:
        """Check security headers"""
        security_headers = {
            "Strict-Transport-Security": "Missing",
            "Content-Security-Policy": "Missing",
            "X-Frame-Options": "Missing",
            "X-Content-Type-Options": "Missing",
            "X-XSS-Protection": "Missing",
            "Referrer-Policy": "Missing"
        }
        
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req, timeout=self.timeout, context=ctx)
            
            for header in security_headers.keys():
                if header in response.headers:
                    security_headers[header] = response.headers[header]
        except:
            pass
        
        missing = [k for k, v in security_headers.items() if v == "Missing"]
        
        return {
            "headers": security_headers,
            "missing": missing,
            "score": max(0, 100 - (len(missing) * 16))
        }
    
    def _scan_ports(self, domain: str) -> list:
        """Scan common ports"""
        open_ports = []
        for port in [80, 443]:  # Only check essential ports
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((domain, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                continue
        return open_ports
    
    def _check_vulnerabilities(self, data: dict) -> list:
        """Check for common vulnerabilities"""
        vulnerabilities = []
        
        if not data["ssl_valid"]:
            vulnerabilities.append("Invalid or missing SSL certificate")
        
        if data["http_headers"]["missing"]:
            vulnerabilities.append(f"Missing security headers: {', '.join(data['http_headers']['missing'][:3])}")
        
        return vulnerabilities
    
    def _calculate_score(self, data: dict) -> int:
        """Calculate security score"""
        score = 100
        
        if not data["ssl_valid"]:
            score -= 30
        
        score -= len(data["http_headers"]["missing"]) * 10
        score -= len(data["vulnerabilities"]) * 15
        
        return max(0, min(100, score))
    
    async def close(self):
        """Cleanup resources"""
        pass