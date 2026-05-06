"""
AI Engine Service
Handles AI-powered analysis using OpenAI
"""
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
    
    async def generate_analysis(self, seo_data: dict, security_data: dict, url: str) -> dict:
        """Generate AI analysis using OpenAI"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            
            prompt = self._create_prompt(seo_data, security_data, url)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a website analysis expert. Provide clear, actionable insights."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
            
        except ImportError:
            logger.warning("OpenAI package not installed")
            return None
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _create_prompt(self, seo_data: dict, security_data: dict, url: str) -> str:
        """Create analysis prompt"""
        return f"""Analyze {url}:

SEO Score: {seo_data.get('score', 'N/A')}/100
Security Score: {security_data.get('score', 'N/A')}/100

Provide:
1. Brief summary (2-3 sentences)
2. 3-5 actionable suggestions
3. Priority issues

Format:
SUMMARY: [text]
SUGGESTIONS:
- [suggestion]
- [suggestion]
PRIORITY: [comma-separated issues]"""
    
    def _parse_response(self, content: str) -> dict:
        """Parse AI response"""
        summary = ""
        suggestions = []
        priority = []
        
        current = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("SUGGESTIONS:"):
                current = "suggestions"
            elif line.startswith("PRIORITY:"):
                priority_text = line.replace("PRIORITY:", "").strip()
                priority = [p.strip() for p in priority_text.split(',')]
                current = None
            elif current == "suggestions" and line.startswith("-"):
                suggestions.append(line[1:].strip())
        
        return {
            "summary": summary,
            "suggestions": suggestions,
            "priority_issues": priority
        }