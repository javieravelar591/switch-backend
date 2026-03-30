import os
import anthropic
from sqlalchemy.orm import Session
from app.models.user import User

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MIN_FAVORITES = 3


def generate_style_profile_from_quiz(
    aesthetics: list[str],
    budget: str,
    values: list[str],
    user: User,
    db: Session,
) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": (
                f"A fashion app user answered a style quiz:\n"
                f"- Aesthetics they love: {', '.join(aesthetics)}\n"
                f"- Typical budget per piece: {budget}\n"
                f"- What they value in a brand: {', '.join(values)}\n\n"
                "Write a 2-3 sentence style profile describing their taste. "
                "Be specific about aesthetics, cultural influences, and price point. "
                "Write in second person (\"You gravitate toward...\"). "
                "Be concise and insightful. No markdown headers or bullet points."
            ),
        }],
    )
    profile = message.content[0].text.strip()
    user.style_profile = profile
    db.commit()
    return profile


def generate_style_profile(user: User, db: Session) -> str | None:
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
                "Write in second person (\"You gravitate toward...\"). Be concise and insightful."
            ),
        }],
    )

    profile = message.content[0].text.strip()
    user.style_profile = profile
    db.commit()
    return profile
