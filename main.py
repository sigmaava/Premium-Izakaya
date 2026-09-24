import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Premium Izakaya Menu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"

try:
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        menu_data = json.load(f)
except FileNotFoundError:
    raise RuntimeError("menu.json was not found.")
except json.JSONDecodeError:
    raise RuntimeError("menu.json contains invalid JSON.")

@app.get("/")
def home():
    return {
        "message": "Welcome to Premium Izakaya",
        "endpoints": [
            "/categories",
            "/categories/{category}",
            "/dish?query=salmon"
        ]
    }

@app.get("/categories")
def get_categories():

    return list(menu_data["categories"].keys())


@app.get("/categories/{category}")
def get_category_items(category: str):

    category_lower = category.strip().lower()

    categories = menu_data["categories"]

    for category_name, items in categories.items():

        if category_name.lower() == category_lower:
            return items

    raise HTTPException(
        status_code=404,
        detail=f"Category '{category}' not found."
    )

@app.get("/dish")
def search_dish(
    query: str = Query(
        ...,
        min_length=1,
        description="Search keyword for dishes"
    )
):

    clean_query = query.strip().lower()

    if not clean_query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    if not menu_data or "categories" not in menu_data:
        raise HTTPException(
            status_code=500,
            detail="Menu database is empty or not loaded."
        )

    categories = menu_data["categories"]

    results = []

    for category_name, items in categories.items():

        if not isinstance(items, list):
            continue

        for item in items:

            name = str(
                item.get("name") or ""
            ).lower()

            ingredient = str(
                item.get("ingredient") or ""
            ).lower()

            description = str(
                item.get("description") or ""
            ).lower()

            category_lower = str(
                category_name or ""
            ).lower()

            if (
                clean_query in name
                or clean_query in ingredient
                or clean_query in description
                or clean_query in category_lower
            ):

                results.append(
                    {
                        "category": category_name,
                        "name": item.get("name"),
                        "ingredient": item.get(
                            "ingredient",
                            ""
                        ),
                        "description": item.get(
                            "description",
                            ""
                        ),
                        "price": item.get("price"),
                    }
                )


    if not results:

        raise HTTPException(
            status_code=404,
            detail=f"No matching dishes found for '{query}'."
        )

    return results