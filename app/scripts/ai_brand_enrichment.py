import os
import sys
import json
import time
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import anthropic

load_dotenv()

from app.database import SessionLocal
from app.models.brand import Brand
from app.models.brand_article import BrandArticle  # noqa: required for SQLAlchemy relationships
from app.models.user import User  # noqa: required for SQLAlchemy relationships

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
LOGO_DEV_TOKEN = os.getenv("LOGO_DEV_TOKEN")

VALID_CATEGORIES = {"streetwear", "luxury", "outdoor", "workwear", "athletic", "contemporary", "avant-garde"}
VALID_REGIONS = {"north-america", "europe", "asia", "other"}

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ── Prompts ───────────────────────────────────────────────────────────────────

ENRICH_PROMPT = """You are a fashion industry expert with deep knowledge of global fashion brands.

For the brand "{name}", provide the following information as valid JSON:

{{
  "description": "2-3 sentences describing the brand's aesthetic, design philosophy, and what they are known for",
  "category": "one of: streetwear, luxury, outdoor, workwear, athletic, contemporary, avant-garde",
  "region": "one of: north-america, europe, asia, other",
  "country": "country of origin (e.g. Japan, France, USA)",
  "tags": ["5 to 8 lowercase style tags relevant to the brand"]
}}

Rules:
- Only respond with the raw JSON object, no markdown or explanation
- If you are not confident about a field, use null
- Tags should be specific and useful (e.g. "minimalist", "japanese", "technical", "streetwear", "luxury")"""

ADD_NEW_PROMPT = """You are a fashion industry expert. Generate a list of {count} notable fashion brands in the "{category}" category that are NOT in this list:

{existing}

For each brand return a JSON array of objects with these fields:
{{
  "name": "exact brand name",
  "description": "2-3 sentences on their aesthetic and design philosophy",
  "category": "{category}",
  "region": "one of: north-america, europe, asia, other",
  "country": "country of origin",
  "website": "official website URL (e.g. https://www.nike.com)",
  "tags": ["5 to 8 lowercase style tags"]
}}

Rules:
- Only respond with a raw JSON array, no markdown or explanation
- Include well-known and emerging brands
- Prioritise brands with a strong distinct identity
- Include accurate official website URLs"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def fetch_logo(website: str | None, brand_name: str) -> str | None:
    if not LOGO_DEV_TOKEN:
        return None

    domains = []

    if website:
        parsed = urlparse(website)
        domain = parsed.netloc.lstrip("www.")
        if domain:
            domains.append(domain)

    # Also try guessing from name
    slug = (
        brand_name.lower()
        .replace(" ", "").replace("-", "").replace("'", "")
        .replace("®", "").replace("™", "").replace("*", "")
        .replace(".", "").replace("/", "").replace("°", "")
    )
    domains.append(f"{slug}.com")

    for domain in domains:
        url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_TOKEN}&size=200&format=png"
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200 and len(res.content) > 500:
                return f"logodev:{domain}"
        except Exception:
            continue

    return None


# ── Enrich existing brands ────────────────────────────────────────────────────

def enrich_brand_with_ai(brand_name: str) -> dict | None:
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": ENRICH_PROMPT.format(name=brand_name)}],
        )
        return parse_json(response.content[0].text)
    except Exception as e:
        print(f"    [AI error] {e}")
        return None


def enrich_brand(brand: Brand, overwrite: bool) -> bool:
    needs_enrichment = (
        overwrite
        or not brand.description
        or not brand.tags
        or not brand.category
        or not brand.region
    )

    if not needs_enrichment:
        print(f"  — skipping (already enriched)")
        return False

    data = enrich_brand_with_ai(brand.name)
    if not data:
        print(f"  ✗ No data returned")
        return False

    changed = False

    if (not brand.description or overwrite) and data.get("description"):
        brand.description = data["description"]
        print(f"  ✓ Description: {data['description'][:70]}...")
        changed = True

    if (not brand.category or overwrite) and data.get("category") in VALID_CATEGORIES:
        brand.category = data["category"]
        print(f"  ✓ Category: {data['category']}")
        changed = True

    if (not brand.region or overwrite) and data.get("region") in VALID_REGIONS:
        brand.region = data["region"]
        print(f"  ✓ Region: {data['region']}")
        changed = True

    if (not brand.country or overwrite) and data.get("country"):
        brand.country = data["country"]
        print(f"  ✓ Country: {data['country']}")
        changed = True

    if (not brand.tags or overwrite) and data.get("tags"):
        tags = [t.lower().strip() for t in data["tags"] if isinstance(t, str)]
        if tags:
            brand.tags = tags
            print(f"  ✓ Tags: {tags}")
            changed = True

    return changed


# ── Add new brands ────────────────────────────────────────────────────────────

def generate_new_brands(category: str, existing_names: set[str], count: int) -> list[dict]:
    existing_list = "\n".join(sorted(existing_names)) if existing_names else "(none yet)"
    prompt = ADD_NEW_PROMPT.format(
        count=count,
        category=category,
        existing=existing_list,
    )
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        result = parse_json(response.content[0].text)
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"  [AI error] {e}")
        return []


def add_new_brands(db, per_category: int = 15):
    existing = {b.name.lower() for b in db.query(Brand.name).all()}
    total_added = 0

    for category in VALID_CATEGORIES:
        print(f"\n── Generating {per_category} new {category} brands ──────────────")
        brands_data = generate_new_brands(category, existing, per_category)

        for data in brands_data:
            name = data.get("name", "").strip()
            if not name or name.lower() in existing:
                print(f"  — skipping '{name}' (already exists)")
                continue

            logo_url = fetch_logo(data.get("website"), name)

            brand = Brand(
                name=name,
                description=data.get("description"),
                category=data.get("category") if data.get("category") in VALID_CATEGORIES else category,
                region=data.get("region") if data.get("region") in VALID_REGIONS else None,
                country=data.get("country"),
                website=data.get("website"),
                tags=[t.lower().strip() for t in data.get("tags", []) if isinstance(t, str)],
                logo_url=logo_url,
            )
            db.add(brand)
            existing.add(name.lower())
            total_added += 1
            logo_status = "✓ logo" if logo_url else "✗ no logo"
            print(f"  + {name} ({logo_status})")

        db.commit()
        time.sleep(0.5)

    print(f"\n✓ Added {total_added} new brands.")


# ── Entry point ───────────────────────────────────────────────────────────────

def run(overwrite: bool = False, single_brand: str | None = None, add_new: bool = False, per_category: int = 15):
    db = SessionLocal()

    if add_new:
        add_new_brands(db, per_category=per_category)
        db.close()
        return

    if single_brand:
        brands = db.query(Brand).filter(Brand.name.ilike(f"%{single_brand}%")).all()
        if not brands:
            print(f"No brand found matching '{single_brand}'")
            db.close()
            return
    else:
        brands = db.query(Brand).all()

    print(f"── Enriching {len(brands)} brand(s) ──────────────────────────\n")

    enriched = 0
    for i, brand in enumerate(brands):
        print(f"[{i+1}/{len(brands)}] {brand.name}")
        changed = enrich_brand(brand, overwrite)
        if changed:
            db.commit()
            enriched += 1
        time.sleep(0.3)

    db.close()
    print(f"\n✓ Done. Enriched {enriched}/{len(brands)} brands.")


if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    add_new = "--add-new" in sys.argv

    per_category = 15
    if "--per-category" in sys.argv:
        idx = sys.argv.index("--per-category")
        if idx + 1 < len(sys.argv):
            per_category = int(sys.argv[idx + 1])

    single = None
    if "--brand" in sys.argv:
        idx = sys.argv.index("--brand")
        if idx + 1 < len(sys.argv):
            single = sys.argv[idx + 1]

    run(overwrite=overwrite, single_brand=single, add_new=add_new, per_category=per_category)
