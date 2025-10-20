from django.db import models


# Create your models here.
class Workplace(models.Model):

    TableNumber = models.CharField(max_length=20, verbose_name="Номер стола")
    Information = models.CharField(
        max_length=250, verbose_name="Дополнительная информация"
    )

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"

    def __str__(self):
        return self.TableNumber
