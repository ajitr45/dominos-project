from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Size
from app.schemas import SizeCreate, SizeUpdate


def create_size(db: Session, size_data: SizeCreate) -> Size:
    
    existing_size = (db.query(Size).filter(Size.name == size_data.name).first())
    
    if existing_size:
        raise ValueError("Size already exists")
    
    size = Size(name = size_data.name)
    
    try:
        db.add(size)
        db.commit()
        db.refresh()
        
    except IntegrityError:
        db.rollback()
        raise ValueError("Size already exists")
    
    return size


def get_sizes(db: Session, skip: int=0, limit= 20) -> list[Size]:
    
    sizes = (db.query(Size).filter(Size.is_active.is_(True)).order_by(Size.id).offset(skip).limit(limit).all())
    
    return sizes


def get_size_by_id(db: Session, size_id: int) -> Size:
    
    size = (db.query(Size).filter(Size.id == size_id, Size.is_active.is_(True)).first())
    
    return size

def get_size_for_admin(db: Session, size_id: int) -> Size | None:

    size = (db.query(Size).filter(Size.id == size_id).first())

    return size


def update_size(db: Session, size: Size, size_data: SizeUpdate) -> Size:
    
    update_data = size_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        
        existing_size = (db.query(Size).filter(Size.name == update_data["name"], Size.id != Size.id, Size.is_active.is_(True))).first()
        
        if existing_size:
            raise ValueError("Size already exists")
        
        for field, value in update_data.items():
            setattr(size, field, value)
            
        try:
            db.commit()
            db.refresh(size)
            
        except IntegrityError:
            db.rollback()
            raise ValueError("Size could not be updated")
        
        return size
    
def deactivate_size(db: Session, size: Size) -> Size:

    size.is_active = False

    db.commit()
    db.refresh(size)

    return size

def activate_size(db: Session, size: Size,) -> Size:

    size.is_active = True

    try:
        db.commit()
        db.refresh(size)

    except IntegrityError:
        db.rollback()
        raise ValueError("Size could not be activated")

    return size