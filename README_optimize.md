1. Parallel Processing
Concurrent Generation: Caption and image generation now happen simultaneously using asyncio.gather()
Increased Concurrency: Raised from 5 to 10 concurrent requests
Batch Processing: Process posts in batches of 20 for better memory management

2. Database Optimization
Reduced DB Calls: Single transaction for post updates instead of multiple commits
Eliminated Intermediate States: Removed unnecessary status updates (generating_caption, generating_image)
Batch Updates: More efficient database operations