from sqlalchemy.orm import Session

from app.models import HCP


def seed_hcps(db: Session) -> None:
    if db.query(HCP).first():
        return
    samples = [
        HCP(
            name="Dr. Maya Chen",
            specialty="Cardiology",
            institution="Riverside Heart Institute",
            npi="1003000123",
            city="Boston",
            state="MA",
        ),
        HCP(
            name="Dr. Samuel Okonkwo",
            specialty="Oncology",
            institution="Lakeview Cancer Center",
            npi="1003000456",
            city="Chicago",
            state="IL",
        ),
        HCP(
            name="Dr. Elena Vasquez",
            specialty="Endocrinology",
            institution="Summit Medical Group",
            npi="1003000789",
            city="Austin",
            state="TX",
        ),
    ]
    db.add_all(samples)
    db.commit()
