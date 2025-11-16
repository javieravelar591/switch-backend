from app.database import SessionLocal, engine
from app.scrapers import brand_scraper
from app.models.brand import Brand

def import_brands():
    db = SessionLocal()
    brands = brand_scraper.scrape_hbx_brands()

    for b in brands:
        exists = db.query(Brand).filter(Brand.name == b["name"]).first()
        if not exists:
            new_brand = Brand(
                name=b["name"],
                description=None,
                category=None,
                logo_url=None,
                website=b["url"],
                # official_site=b["official_site"]
                tags=b["letter"]
            )
            db.add(new_brand)
    

    db.commit()
    db.close()
    print(f"Imported {len(brands)} brands")


if __name__ == "__main__":
    import_brands()