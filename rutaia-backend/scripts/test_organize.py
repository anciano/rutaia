import httpx
import asyncio

async def test_organize():
    plan_id = "cc4daee7-7d96-4378-ab12-5b5c2bcc5eb4"
    url = f"http://localhost:8000/plan/{plan_id}/organize"
    print(f"POSTing to {url}")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url)
            print("Status:", r.status_code)
            print("Response:", r.text)
        except Exception as e:
            print("Exception:", str(e))

if __name__ == "__main__":
    asyncio.run(test_organize())
