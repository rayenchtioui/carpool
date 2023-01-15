from operator import and_
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, aliased
from ..database import get_db
from ..routers.emailUtil import send_email
from sqlalchemy.exc import SQLAlchemyError
from ..config import settings
from app import schemas, models, oauth2
from .error import add_error

router = APIRouter(
    prefix="/review",
    tags=['Review']
)


@router.post('/', response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.Review, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # check if user exists
    db_user = db.query(models.User).filter(
        models.User.id == review.user_id).first()
    if not db_user:
        return schemas.ReviewOut(
            status=status.HTTP_404_NOT_FOUND,
            message="User not found!"
        )
    if review.user_id == current_user.id:
        return schemas.ReviewOut(
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="you can't write a review for yourself"
        )
    try:
        db_review = models.Review(reviewer_id=current_user.id, **review.dict())
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ReviewOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="There is a problem try again"
        )
    return schemas.ReviewOut(
        **db_review.__dict__,
        status=status.HTTP_201_CREATED,
        message="Review created successfully."

    )


@router.get('/get-my-reviews', response_model=schemas.ReviewsOut, status_code=status.HTTP_200_OK)
def get_reviews(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_reviews = db.query(models.Review).filter(
        models.Review.reviewer_id == current_user.id).all()
    if not db_reviews:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "No reviews were found yet!"
        }
    return schemas.ReviewsOut(
        review_list=[schemas.ReviewOut(**review.__dict__)
                     for review in db_reviews],
        message="all Reviews",
        status=status.HTTP_200_OK
    )


@router.get('/get-reviews-on-user', response_model=schemas.ReviewsOut, status_code=status.HTTP_200_OK)
def get_reviews_on_user(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    db_reviews = db.query(models.Review).filter(
        models.Review.user_id == id).all()
    if not db_reviews:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "No reviews were found yet!"
        }
    return schemas.ReviewsOut(
        review_list=[schemas.ReviewOut(**review.__dict__)
                     for review in db_reviews],
        message="all Reviews",
        status=status.HTTP_200_OK
    )


@router.patch('/{id}', response_model=schemas.ReviewOut, status_code=status.HTTP_200_OK)
def update_review(id: int, review: schemas.EditReview, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # check if review exists and belongs to the current user logged in
    review_to_update = db.query(models.Review).filter(
        and_(models.Review.id == id, models.Review.reviewer_id == current_user.id))
    db_review = review_to_update.first()
    if not db_review:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Review not found"
        }
    try:
        review_data = review.dict(exclude_unset=True)
        for key, value in review_data.items():
            setattr(db_review, key, value)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ReviewOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.ReviewOut(
        **db_review.__dict__,
        status=status.HTTP_200_OK,
        message="User updated successfully"
    )


@router.delete("/delete/{id}", response_model=schemas.ReviewOut, status_code=status.HTTP_200_OK)
def delete_review(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # query to verify that the review id exists and belongs to current user logged in
    db_review = db.query(models.Review).filter(
        and_(models.Review.id == id, models.Review.reviewer_id == current_user.id)).first()
    review_to_delete = db_review
    if not db_review:
        return schemas.ReviewOut(
            status=status.HTTP_404_NOT_FOUND,
            message="Review not found!"
        )
    try:
        db.delete(db_review)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ReviewOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong"
        )
    return schemas.CarOut(
        **review_to_delete.__dict__,
        status=status.HTTP_202_ACCEPTED,
        message="Review Deleted successfully "
    )
