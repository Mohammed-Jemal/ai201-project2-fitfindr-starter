"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    # normalize inputs
    desc = (description or "").lower().strip()
    tokens = [t for t in re.split(r"\W+", desc) if t]
    size_norm = (size or "").lower().strip() or None

    scored: list[tuple[int, float, dict]] = []

    for l in listings:
        title = (l.get("title") or "").lower()
        body = (l.get("description") or "").lower()
        tags = " ".join([t.lower() for t in l.get("style_tags", [])])

        # price handling
        raw_price = l.get("price")
        try:
            price_val = float(raw_price) if raw_price is not None else float("inf")
        except Exception:
            price_val = float("inf")

        # size filter 
        listing_size = (l.get("size") or "").lower()
        if size_norm and size_norm not in listing_size:
            continue

        # price filter
        if max_price is not None:
            try:
                if price_val > float(max_price):
                    continue
            except Exception:
                pass

        # relevance scoring by token overlap
        if tokens:
            relevance = 0
            for t in tokens:
                if t in title:
                    relevance += 3
                if t in tags:
                    relevance += 2
                if t in body:
                    relevance += 1
        else:
            relevance = 1

        # drop listings with zero relevance
        if relevance <= 0:
            continue

        scored.append((relevance, price_val, l))

    # sort by relevance (desc) then price (asc)
    scored.sort(key=lambda x: (-x[0], x[1]))

    return [item for (_score, _price, item) in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    items = wardrobe.get("items", []) if wardrobe else []

    # If the user has no wardrobe items, return friendly guidance
    if not items:
        return (
            "Your wardrobe is empty — add basics like jeans, a neutral jacket, and "
            "sneakers so I can suggest specific outfits. For now, try pairing this "
            f"item ({new_item.get('title')}) with high-waist jeans and white sneakers."
        )

    new_tags = {t.lower() for t in new_item.get("style_tags", [])}
    new_colors = {c.lower() for c in new_item.get("colors", [])}
    new_cat = (new_item.get("category") or "").lower()

    def score_piece(p: dict) -> int:
        score = 0
        p_tags = {t.lower() for t in p.get("style_tags", [])}
        p_colors = {c.lower() for c in p.get("colors", [])}

        # style tag overlap is the strongest signal
        score += 3 * len(new_tags & p_tags)
        # color matches are useful secondary signals
        score += 2 * len(new_colors & p_colors)

        # prefer complementary categories (e.g., bottoms for a top)
        p_cat = (p.get("category") or "").lower()
        if new_cat == "tops" and p_cat == "bottoms":
            score += 2
        if new_cat == "bottoms" and p_cat == "tops":
            score += 2
        if p_cat == "outerwear":
            score += 1

        return score

    scored = []
    for p in items:
        s = score_piece(p)
        if s > 0:
            scored.append((s, p))

    # If no wardrobe pieces scored (no overlaps), return a gentle fallback
    if not scored:
        return (
            f"I couldn't find close matches in your wardrobe for {new_item.get('title')}. "
            "Try pairing it with neutral basics like jeans, a denim jacket, or simple sneakers."
        )

    # sort by score descending
    scored.sort(key=lambda x: -x[0])

    # Select up to two complementary pieces, preferring different categories
    selected = []
    seen_cats = set()
    for _s, p in scored:
        cat = (p.get("category") or "").lower()
        if cat in seen_cats:
            continue
        selected.append(p)
        seen_cats.add(cat)
        if len(selected) >= 2:
            break

    # build human-friendly suggestion text
    pieces_text = ", ".join(f"{p['name']} ({p.get('category')})" for p in selected)

    # explain why these pieces work together
    reasons = []
    # shared style tags
    shared_tags = set()
    for p in selected:
        shared_tags |= new_tags & {t.lower() for t in p.get("style_tags", [])}
    if shared_tags:
        reasons.append("style: " + ", ".join(sorted(shared_tags)))
    # shared colors
    shared_colors = set()
    for p in selected:
        shared_colors |= new_colors & {c.lower() for c in p.get("colors", [])}
    if shared_colors:
        reasons.append("colors: " + ", ".join(sorted(shared_colors)))

    reason_text = ("; ".join(reasons)) if reasons else "they complement each other"

    return f"Pair the {new_item.get('title')} with {pieces_text}. Reason: {reason_text}."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Guard against empty outfit input
    if not outfit or not str(outfit).strip():
        return "Couldn't create fit card — missing item or outfit info."

    title = new_item.get("title", "Item")
    price = new_item.get("price")
    try:
        price_str = f"${float(price):.2f}" if price is not None else "Price unknown"
    except Exception:
        price_str = str(price)
    platform = new_item.get("platform") or "unknown"

    # Short metadata
    category = (new_item.get("category") or "").capitalize()
    tags = new_item.get("style_tags") or []
    colors = new_item.get("colors") or []

    # Build a concise, human-friendly fit card (3 lines)
    lines = []
    lines.append(f"{title} — {price_str} on {platform}")
    # Outfit suggestion (use as-is; it's already a friendly sentence)
    lines.append(outfit)

    # Why it works: combine category, a couple of tags, and colors
    reasons = []
    if category:
        reasons.append(category)
    if tags:
        reasons.append("vibe: " + ", ".join(tags[:3]))
    if colors:
        reasons.append("colors: " + ", ".join(colors[:3]))

    reason_text = "; ".join(reasons) if reasons else "they complement each other"
    lines.append(f"Why it works: {reason_text}.")

    return "\n".join(lines)

