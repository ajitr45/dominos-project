from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin_or_manager
from app.schemas import DashboardResponse
from app.services.admin_service import get_dashboard_data


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_admin_dashboard(db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    
    dashboard_data = get_dashboard_data(db)

    return dashboard_data