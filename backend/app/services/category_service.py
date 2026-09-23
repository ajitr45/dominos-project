from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate



def create_category(db: Session, category_data: CategoryCreate) -> Category:
    
    existing_category = (db.query(Category).filter(Category.name == category_data.name)).first()
    
    if existing_category:
        raise ValueError("category already exist")
    
    category = Category(
        name = category_data.name,
        description = category_data.description,
        )
    
    try:
    
        db.add(category)
        db.commit()
        db.refresh(category)
        
    except IntegrityError:
        db.rollback()
        raise ValueError("Category already exists")
    
    return category

def get_categories(db:Session, skip: int, limit: int = 20) -> list[Category]:
    
    categories = (db.query(Category)
                  .filter(Category.is_active.is_(True))
                  .order_by(Category.id)
                  .offset(skip)
                  .limit(limit).all()
                  )
    
    return categories
       


def get_category_by_id(db:Session, category_id: int,) -> Category:
    
    category = (db.query(Category).filter(Category.id == category_id, Category.is_active.is_(True)).first())
    
    return category


def update_category(
    db: Session,
    category: Category,
    category_data: CategoryUpdate,
) -> Category:

    update_data = category_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        existing_category = (
            db.query(Category)
            .filter(Category.name == update_data["name"], Category.id != category.id,)
            .first()
        )

        if existing_category:
            raise ValueError("Category already exists")

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)

    except IntegrityError:
        db.rollback()
        raise ValueError("Category already exists")

    return category
    
    
def deactivate_category(db: Session, category: Category,) -> Category:

    category.is_active = False

    db.commit()
    db.refresh(category)

    return category