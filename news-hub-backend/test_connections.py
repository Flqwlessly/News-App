"""
Test all three service connections: News API, MongoDB, and Gemini.
Run: python test_connections.py
"""
import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import google.generativeai as genai
from config import (
    NEWS_API_KEY, NEWS_API_BASE,
    MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION,
    GEMINI_API_KEY, GEMINI_MODEL,
)

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"


async def test_news_api():
    print("\n" + "=" * 60)
    print("1. TESTING NEWS API")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=15) as client:
        # Test /top-headlines
        print("\n  [a] GET /top-headlines (country=us) ...")
        resp = await client.get(
            f"{NEWS_API_BASE}/top-headlines",
            params={"country": "us", "apiKey": NEWS_API_KEY},
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("status") == "ok":
            count = data.get("totalResults", 0)
            articles = data.get("articles", [])
            print(f"      {PASS}  Status: ok | Total results: {count}")
            if articles:
                print(f"      First headline: {articles[0].get('title', 'N/A')[:80]}")
        else:
            print(f"      {FAIL}  Status: {resp.status_code} | {data}")
            return False

        # Test /everything (Apple articles)
        print("\n  [b] GET /everything (q=Apple, sortBy=popularity) ...")
        resp2 = await client.get(
            f"{NEWS_API_BASE}/everything",
            params={
                "q": "Apple",
                "sortBy": "popularity",
                "language": "en",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            },
        )
        data2 = resp2.json()
        if resp2.status_code == 200 and data2.get("status") == "ok":
            count2 = data2.get("totalResults", 0)
            articles2 = data2.get("articles", [])
            print(f"      {PASS}  Status: ok | Total results: {count2}")
            if articles2:
                src = articles2[0].get("source", {}).get("name", "N/A")
                print(f"      Top result from: {src}")
        else:
            print(f"      {FAIL}  Status: {resp2.status_code} | {data2}")
            return False

        # Test /top-headlines/sources
        print("\n  [c] GET /top-headlines/sources ...")
        resp3 = await client.get(
            f"{NEWS_API_BASE}/top-headlines/sources",
            params={"apiKey": NEWS_API_KEY},
        )
        data3 = resp3.json()
        if resp3.status_code == 200 and data3.get("status") == "ok":
            sources = data3.get("sources", [])
            bbc = [s for s in sources if s.get("id") == "bbc-news"]
            print(f"      {PASS}  Total sources: {len(sources)}")
            if bbc:
                print(f"      BBC News found: id='bbc-news', name='{bbc[0].get('name')}'")
        else:
            print(f"      {FAIL}  Status: {resp3.status_code} | {data3}")
            return False

    return True


async def test_mongodb():
    print("\n" + "=" * 60)
    print("2. TESTING MONGODB CONNECTION")
    print("=" * 60)

    try:
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=10000)

        # Ping the server
        print("\n  [a] Pinging MongoDB Atlas ...")
        result = await client.admin.command("ping")
        print(f"      {PASS}  Ping response: {result}")

        # List databases
        print("\n  [b] Listing databases ...")
        db_names = await client.list_database_names()
        print(f"      {PASS}  Databases: {db_names}")

        # Access the newshub database and collection
        print(f"\n  [c] Accessing db='{MONGODB_DB}', collection='{MONGODB_COLLECTION}' ...")
        db = client[MONGODB_DB]
        col = db[MONGODB_COLLECTION]
        count = await col.count_documents({})
        print(f"      {PASS}  Documents in collection: {count}")

        # Test write + read + delete
        print("\n  [d] Write/Read/Delete test doc ...")
        test_doc = {"_id": "__test_connection__", "status": "ok", "source": "test_connections.py"}
        await col.update_one({"_id": test_doc["_id"]}, {"$set": test_doc}, upsert=True)
        fetched = await col.find_one({"_id": "__test_connection__"})
        await col.delete_one({"_id": "__test_connection__"})
        if fetched and fetched.get("status") == "ok":
            print(f"      {PASS}  Write/Read/Delete cycle succeeded")
        else:
            print(f"      {FAIL}  Could not verify write/read")
            return False

        client.close()
        return True

    except Exception as e:
        print(f"      {FAIL}  Error: {e}")
        return False


async def test_gemini():
    print("\n" + "=" * 60)
    print("3. TESTING GEMINI API")
    print("=" * 60)

    try:
        print("\n  [a] Configuring Gemini ...")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        print(f"      {PASS}  Model '{GEMINI_MODEL}' initialized")

        print("\n  [b] Sending test prompt ...")
        response = await model.generate_content_async(
            "Reply with exactly: CONNECTION_OK"
        )
        text = response.text.strip()
        print(f"      {PASS}  Response: {text[:100]}")

        return True

    except Exception as e:
        print(f"      {FAIL}  Error: {e}")
        return False


async def main():
    print("\n" + "#" * 60)
    print("#     NEWS HUB - CONNECTION TEST SUITE")
    print("#" * 60)

    news_ok = await test_news_api()
    mongo_ok = await test_mongodb()
    gemini_ok = await test_gemini()

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"  News API:  {PASS if news_ok else FAIL}")
    print(f"  MongoDB:   {PASS if mongo_ok else FAIL}")
    print(f"  Gemini AI: {PASS if gemini_ok else FAIL}")

    all_ok = news_ok and mongo_ok and gemini_ok
    print(f"\n  {'All connections verified!' if all_ok else 'Some connections failed.'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
