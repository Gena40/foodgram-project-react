from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 0:
        print('value < 0')
        raise ValidationError(
            'Время приготовления не может быть отрицательной величиной!'
        )
    if value == 0:
        raise ValidationError(
            'Невозможно приготовить что-либо так быстро!'
        )
