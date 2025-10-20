from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from workplace.schemas import Desk, DeskCreate, DeskUpdate, Reservation, ReservationCreate
from core.dependencies import get_db_session

router = APIRouter()

@router.get("/desks/", response_model=List[Desk])
async def get_desks(
    skip: int = Query(0, description="Пропустить записи"),
    limit: int = Query(100, description="Лимит записей"),
    is_available: Optional[bool] = Query(None, description="Фильтр по доступности"),
    db_session = Depends(get_db_session)
):
    """
    Получить список всех рабочих столов
    """
    from employee.models import Desk as DeskModel
    
    queryset = DeskModel.objects.all()
    
    if is_available is not None:
        queryset = queryset.filter(is_available=is_available)
    
    desks = list(queryset[skip:skip + limit])
    return [Desk.model_validate(desk) for desk in desks]

@router.post("/desks/", response_model=Desk)
async def create_desk(desk: DeskCreate, db_session = Depends(get_db_session)):
    """
    Создать новый рабочий стол
    """
    from employee.models import Desk as DeskModel
    
    try:
        db_desk = DeskModel.objects.create(**desk.model_dump())
        return Desk.model_validate(db_desk)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/desks/{desk_id}", response_model=Desk)
async def get_desk(desk_id: int, db_session = Depends(get_db_session)):
    """
    Получить стол по ID
    """
    from employee.models import Desk as DeskModel
    
    try:
        desk = DeskModel.objects.get(id=desk_id)
        return Desk.model_validate(desk)
    except DeskModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Desk not found")

@router.put("/desks/{desk_id}", response_model=Desk)
async def update_desk(desk_id: int, desk_data: DeskUpdate, db_session = Depends(get_db_session)):
    """
    Обновить рабочий стол
    """
    from employee.models import Desk as DeskModel
    
    try:
        desk = DeskModel.objects.get(id=desk_id)
        
        update_data = desk_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(desk, field, value)
        
        desk.save()
        return Desk.model_validate(desk)
        
    except DeskModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Desk not found")

# Эндпоинты для бронирования
@router.get("/reservations/", response_model=List[Reservation])
async def get_reservations(
    desk_id: Optional[int] = Query(None, description="Фильтр по столу"),
    date: Optional[str] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
    db_session = Depends(get_db_session)
):
    """
    Получить список бронирований
    """
    from employee.models import Reservation as ReservationModel
    
    queryset = ReservationModel.objects.all().select_related('user', 'desk')
    
    if desk_id:
        queryset = queryset.filter(desk_id=desk_id)
    
    if date:
        queryset = queryset.filter(date=date)
    
    reservations = list(queryset)
    
    result = []
    for res in reservations:
        res_data = Reservation.model_validate(res)
        # Добавляем базовую информацию о пользователе
        res_data.user = {
            "id": res.user.id,
            "username": res.user.username,
            "email": getattr(res.user, 'email', '')
        }
        result.append(res_data)
    
    return result

@router.post("/reservations/", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate, db_session = Depends(get_db_session)):
    """
    Создать бронирование стола
    """
    from employee.models import Reservation as ReservationModel, Desk as DeskModel
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        # Проверяем существование стола и пользователя
        desk = DeskModel.objects.get(id=reservation.desk_id)
        user = User.objects.get(id=reservation.user_id)
        
        # Проверяем доступность стола на эту дату
        existing_reservation = ReservationModel.objects.filter(
            desk=desk, date=reservation.date
        ).first()
        
        if existing_reservation:
            raise HTTPException(status_code=400, detail="Desk already reserved for this date")
        
        # Создаем бронирование
        db_reservation = ReservationModel.objects.create(
            user=user,
            desk=desk,
            date=reservation.date
        )
        
        result = Reservation.model_validate(db_reservation)
        result.user = {
            "id": user.id,
            "username": user.username,
            "email": getattr(user, 'email', '')
        }
        return result
        
    except DeskModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Desk not found")
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/validation/rules")
async def get_validation_rules():
    """
    Получить правила валидации расстановки сотрудников
    """
    return {
        "validation_rules": {
            "developer_tester_separation": True,
            "description": "Тестировщики и разработчики не могут работать за соседними столами"
        },
        "position_codes": {
            "backend": "Бекенд-разработчик",
            "frontend": "Фронтенд-разработчик", 
            "tester": "Тестировщик",
            "manager": "Менеджер",
            "designer": "Дизайнер"
        }
    }