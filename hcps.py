from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HCP
from app.schemas import HCPOut

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=list[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).order_by(HCP.name).all()
