import os
import anthropic
from sqlalchemy.orm import Session
from app.models.user import User

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MIN_FAVORITES = 3


def generate_style_profile(user: User, db: Session) -> str | None:
    """
    Generate and persist a style profile for the user based on their favorited brands.
    Returns None if the user has fewer than MIN_FAVORITES.
    Uses Claude Haiku to keep costs low — this runs on every 3rd+ favorite toggle.
    """
    if len(user.favorite_brands) < MIN_FAVORITES:
        return None

    brand_list = ", ".join(b.name for b in user.favorite_brands)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": (
                f"A fashion app user has favorited these brands: {brand_list}\n\n"
                "Write a 2-3 sentence style profile describing their taste. "
                "Be specific about aesthetics, cultural influences, and price point. "
                "Write in second person (\"You gravitate toward...\"). "
                "Be concise and insightful. Do not use markdown headers or bullet points — plain flowing prose only."
            ),
        }],
    )

    profile = message.content[0].text.strip()
    user.style_profile = profile
    db.commit()
    return profile
