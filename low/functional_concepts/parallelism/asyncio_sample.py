import asyncio

async def fetch_data():
    print("Start fetching")
    await asyncio.sleep(5)  # Simulates network call
    print("Done fetching")
    return 42

async def main():
    result = await fetch_data()
    print("Result:", result)

asyncio.run(main())
# await will let the other piece of code to be executed, but sleep will sort of block it
