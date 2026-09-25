from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin
from app.schemas import SizeCreate, SizeUpdate, SizeResponse
from app.services.size_service import create_size, get_size_for_admin, get_sizes, get_size_by_id, update_size, deactivate_size, activate_size


router = APIRouter(prefix="/sizes", tags=["Sizes"])


@router.post("/", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
def create_size_api(size_data: SizeCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        size = create_size(db, size_data)
        return size
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/", response_model=list[SizeResponse])
def get_sizes_api(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    sizes = get_sizes(db, skip, limit)
    return sizes


@router.get("/{size_id}", response_model=SizeResponse)
def get_size_api(size_id: int, db: Session = Depends(get_db)):
    size = get_size_by_id(db, size_id)

    if not size:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")

    return size


@router.patch("/{size_id}", response_model=SizeResponse)
def update_size_api(size_id: int, size_data: SizeUpdate = None, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if size_data is None:
        size_data = SizeUpdate()

    try:
        size = update_size(db, size_id, size_data)
        if not size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")
        return size
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{size_id}", response_model=SizeResponse)
def deactivate_size_api(size_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    size = deactivate_size(db, size_id)

    if not size:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size not found")

    return size


@router.patch(
    "/{size_id}/activate",
    response_model=SizeResponse,
)
def activate_size_api(
    size_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    size = get_size_for_admin(db, size_id)

    if not size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Size not found",
        )

    if size.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Size is already active",
        )

    try:
        activated_size = activate_size(db, size)

        return activated_size

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    