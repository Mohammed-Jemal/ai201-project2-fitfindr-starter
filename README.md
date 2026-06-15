# FitFindr — Short README (Beginner Friendly)

This project finds secondhand listings and suggests outfits using a local mock dataset. Run, test, and extend the tools step-by-step.

Quick start
-----------

Install deps:
```bash
pip install -r requirements.txt
```

Test tools only before integrating the tools:
```bash
python test_tools.py
```

Tools and their purpose:
-----------------------

- `search_listings(description: str, size: str|None = None, max_price: float|None = None) -> list[dict]`
	- Purpose: find and rank listings from `data/listings.json` by keywords, optional size and max price.

- `suggest_outfit(new_item: dict, wardrobe: dict) -> str`
	- Purpose: pick 0–2 wardrobe pieces that match the new item by style tags, colors, and complementary categories; return a short suggestion string.

- `create_fit_card(outfit: str, new_item: dict) -> str`
	- Purpose: produce a 3-line fit card with title/price, the outfit sentence, and a short "why it works" line.

- `run_agent(query: str, wardrobe: dict) -> dict` (planning loop) and `handle_query(user_query: str, wardrobe_choice: str) -> (listing_text, outfit, fit_card)`.

How the planning loop works 
----------------------------------------

1. Parse `query` into `description`, `size`, and `max_price` (regex for `$N` and `size`).
2. Call `search_listings(description, size, max_price)`.
	 - If search errors → stop and return an error message.
	 - If no results → return a friendly message suggesting relaxing filters.
3. Pick the top search result as `selected_item`.
4. Call `suggest_outfit(selected_item, wardrobe)`.
5. Call `create_fit_card(outfit, selected_item)`.
6. Return a `session` dict that contains `selected_item`, `outfit_suggestion`, `fit_card`, and `error`.

State management 
----------------------------------------

- `session` dict holds everything for one interaction: `query`, `parsed`, `search_results`, `selected_item`, `wardrobe`, `outfit_suggestion`, `fit_card`, `error`.
- Each tool writes its output into `session` (or returns values used to populate `session`) so the next step reads from it.

Error handling 
------------------------------

- `search_listings`: returns empty list if nothing matches. Example: a too-strict query like "designer ballgown size XXS under $5" results in no matches; the agent returns: "No listings found. Try removing the size filter, increasing max price, or using fewer keywords.".
- `suggest_outfit`: never raises for normal inputs; if wardrobe is empty it returns helpful guidance instead of failing.
- `create_fit_card`: returns a fallback string "Couldn't create fit card — missing item or outfit info." if outfit input is empty.


AI usage 
-----------------------

1. I asked the assistant for a scoring recipe for `search_listings` (title > tags > body, tie-break by price). I implemented and tuned the weights after testing.
2. I asked for `suggest_outfit` phrasing and fallback behavior; the assistant suggested examples and an algorithm. I implemented a deterministic version and adjusted wording.

Next steps 
------------------------

- Run the UI: `python app.py` and try with different example queries.



