#!/usr/bin/env python3
"""Test script: starts real uvicorn server, tests endpoints, shuts down."""
import asyncio
import httpx
import multiprocessing
import time
import sys
import os

def run_server():
    import uvicorn
    os.environ["PYTHONPATH"] = "."
    uvicorn.run(
        "services.api.main:app",
        host="127.0.0.1",
        port=18768,
        log_level="error",
        lifespan="off",
    )

async def main():
    # Start server in subprocess
    ctx = multiprocessing.get_context("spawn")
    proc = ctx.Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(3)

    if proc.exitcode is not None:
        print(f"Server failed to start: exitcode={proc.exitcode}")
        sys.exit(1)

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:18768", follow_redirects=True, timeout=10) as client:
            # Health
            r = await client.get("/health")
            print(f"GET /health -> {r.status_code} | {r.text[:100]}")

            # Businesses list (should be empty)
            r = await client.get("/api/v1/businesses")
            print(f"GET /api/v1/businesses -> {r.status_code}")

            # Create a business
            r = await client.post("/api/v1/businesses", json={"name": "Test Dispensary", "business_type": "retail"})
            print(f"POST /api/v1/businesses -> {r.status_code} | {r.text[:200]}")

            if r.status_code == 201:
                biz_id = r.json()["id"]
                r2 = await client.get(f"/api/v1/businesses/{biz_id}")
                print(f"GET /api/v1/businesses/{biz_id} -> {r2.status_code}")

                # Create website
                site_payload = {"business_id": biz_id, "url": "https://test.example.com"}
                r3 = await client.post("/api/v1/websites", json=site_payload)
                print(f"POST /api/v1/websites -> {r3.status_code}")
                if r3.status_code == 201:
                    site_id = r3.json()["id"]
                    # Create crawl
                    r4 = await client.post("/api/v1/crawls", json={"website_id": site_id, "crawl_depth": 2})
                    print(f"POST /api/v1/crawls -> {r4.status_code} | {r4.text[:200]}")
    finally:
        proc.terminate()
        proc.join(timeout=5)

if __name__ == "__main__":
    asyncio.run(main())
