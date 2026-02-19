import google.generativeai as genai
from django.conf import settings
import json
from loguru import logger

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"}
        )

    async def analyze_social_presence(self, data: dict, language: str = "uz") -> dict:
        prompt = f"""
        Role: SMM Strategist (2026).
        Task: Analyze social data and output STRICT JSON.
        Language: {language}
        
        Data: {json.dumps(data, ensure_ascii=False)}
        
        Required JSON Schema:
        {{
          "quick_audit": ["string"],
          "positioning_analysis": {{"details": "string"}},
          "content_pillars": ["string"],
          "hooks_strategy": ["string"],
          "30_day_plan": [{{"day": 1, "topic": "string", "format": "string"}}],
          "kpi_targets": {{"details": "string"}},
          "risks": ["string"],
          "next_7_days_action_plan": ["string"],
          "growth_hypotheses": ["string (Why followers growing/dropping?)"],
          "visual_style_analysis": ["string (Colors, Editing style, Vibe)"]
        }}
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"AI Error: {e}")
            raise e

    async def generate_post_idea(self, audit_report: dict, language: str = "uz") -> dict:
        """Generates a specific post idea based on the audit findings"""
        prompt = f"""
        Role: SMM Specialist.
        Task: Create a High-Converting Social Media Post based on the audit results.
        Language: {language}
        
        Audit Context:
        - Pillars: {audit_report.get('content_pillars', [])}
        - 7 Day Plan: {audit_report.get('next_7_days_action_plan', [])}
        
        Required JSON Schema:
        {{
            "topic": "string (Catchy Title)",
            "format": "string (Reel / Carousel / Post)",
            "caption": "string (Full engaging caption with emojis)",
            "hashtags": ["string"],
            "image_prompt": "string (Detailed prompt for Midjourney/DALL-E to generate visual)"
        }}
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"AI Post Gen Error: {e}")
            return {"topic": "Error", "caption": "Xatolik yuz berdi."}
