from django.core.exceptions import ValidationError
from food_assistance.settings import MINIMUM_COOKING_TIME


def validate_cooking_time(value):
    if value < MINIMUM_COOKING_TIME:
        raise ValidationError(
            f'Время приготовления не может быть меньше {MINIMUM_COOKING_TIME}!'
        )
