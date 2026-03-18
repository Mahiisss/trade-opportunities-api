from fastapi import HTTPException


def validate_sector(sector: str):
    if not sector or len(sector.strip()) < 3:
        raise HTTPException(status_code=400, detail="Sector name too short")

    cleaned = sector.strip().lower()

    if not all(c.isalpha() or c in [" ", "-"] for c in cleaned):
        raise HTTPException(
            status_code=400,
            detail="Sector must contain only letters, spaces, or hyphens"
        )

    if len(cleaned) > 50:
        raise HTTPException(status_code=400, detail="Sector name too long")

    return cleaned