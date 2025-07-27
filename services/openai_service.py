import openai
import asyncio
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_caption(self, campaign_data: Dict) -> str:
        prompt = f"""
        Create an engaging Instagram caption for:
        Brand: {campaign_data['brand_name']}
        Topic: {campaign_data.get('topic', 'General')}
        Tone: {campaign_data['tone']}
        Target Audience: {campaign_data.get('target_audience', 'General audience')}
        Brief: {campaign_data.get('brief', '')}
        
        Requirements:
        - Match the {campaign_data['tone']} tone
        - Include 5-8 relevant hashtags
        - Add appropriate emojis
        - Keep under 2000 characters
        - Include call-to-action
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Caption generation failed: {str(e)}")
    
    async def generate_image(self, campaign_data: Dict) -> str:
        image_prompt = f"""
        Professional Instagram post image for {campaign_data['brand_name']}.
        Topic: {campaign_data.get('topic', 'Brand content')}
        Style: {campaign_data['tone']} and appealing
        Brief: {campaign_data.get('brief', '')}
        High quality, 1:1 aspect ratio, vibrant colors, no text overlay.
        """
        
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

# Global instance
openai_service = OpenAIService()