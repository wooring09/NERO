import asyncio
from Database.connection import Settings

async def main():
    settings = Settings()
    await settings.initiate_database()

if __name__ == "__main__":
    print(1)
    asyncio.run(main())