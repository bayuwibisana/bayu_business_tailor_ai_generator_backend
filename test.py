from services.openai_service import OpenAIService

async def test_openai():
    openai_service = OpenAIService()
    
    test_data = {
        'brand_name': 'Test Brand',
        'topic': 'Product Launch',
        'tone': 'friendly',
        'brief': 'Testing our new product'
    }
    
    caption = await openai_service.generate_caption(test_data)
    print("Generated Caption:", caption)
    
    image_url = await openai_service.generate_image(test_data)
    print("Generated Image URL:", image_url)

# Run: python -c "import asyncio; asyncio.run(test_openai())"