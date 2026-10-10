from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.logging import get_logger
from app.features.admin.schema import UserListResponse
from app.features.admin.service import list_users

logger = get_logger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/users",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all registered users (Admin only)",
    description=("Returns a paginated list of all registered users in the database."),
)
def get_users(
    skip: int = Query(0, ge=0, description="Records to skip for pagination."),
    limit: int = Query(100, ge=1, le=500, description="Max records to return."),
    db: Session = Depends(get_db),
) -> UserListResponse:
    return list_users(db, skip=skip, limit=limit)
