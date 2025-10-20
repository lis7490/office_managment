from django.core.exceptions import ValidationError
from .models import Desk, Reservation

class NeighborDeskValidator:
    def validate(self, reservation):
        desk = reservation.desk
        date = reservation.date
        
        # Преобразуем номер стола в число для проверки соседних столов
        try:
            desk_number = int(desk.number)
        except ValueError:
            # Если номер стола не число, пропускаем проверку
            return
        
        adjacent_desks_numbers = [desk_number - 1, desk_number + 1]
        adjacent_desks = Desk.objects.filter(number__in=[str(num) for num in adjacent_desks_numbers])
        
        for adj_desk in adjacent_desks:
            if Reservation.objects.filter(desk=adj_desk, date=date).exists():
                raise ValidationError(
                    f'Нельзя забронировать стол {desk.number} на дату {date}, '
                    f'так как соседний стол {adj_desk.number} уже забронирован'
                )