from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/validation-info")
async def get_office_validation_info():
    """
    Получить информацию о правилах офиса
    """
    return {
        "office_rules": {
            "desk_validation": "Автоматическая проверка соседних столов",
            "position_restrictions": "Разработчики и тестировщики не могут сидеть рядом",
            "reservation_system": "Бронирование столов по датам"
        }
    }