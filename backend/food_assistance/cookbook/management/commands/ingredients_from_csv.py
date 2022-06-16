import logging
import os
from csv import DictReader
from logging.handlers import RotatingFileHandler

from cookbook.models import Ingredient
from django.core.management.base import BaseCommand
from food_assistance.settings import BASE_DIR

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    f'{__name__}.log',
    encoding='utf-8',
    mode='w',
)
logger.addHandler(handler)
formatter = logging.Formatter(
    '[%(asctime)s]-[%(module)s]-[%(funcName)s]-[%(levelname)s]-%(message)s'
)
handler.setFormatter(formatter)

LOG_STATUS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'error': logging.ERROR,
    'default': logging.ERROR
}


class Command(BaseCommand):
    help = 'Копирование ингредиентов из csv'
    shift_path = os.path.dirname(os.path.dirname(BASE_DIR))
    shift_path = os.path.join(shift_path, 'data')

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-log_level', type=str,
            help='Режим логгирования'
        )

    def handle(self, *args, **kwargs):
        """Основная функция выполнения команды."""
        print('start inserts')
        log_level = kwargs.get('log_level')
        print('log_level', log_level)
        if log_level and log_level.lower() in (LOG_STATUS):
            logger.setLevel(LOG_STATUS[log_level.lower()])
        else:
            logger.setLevel(LOG_STATUS['default'])
        self.insert_ingredient()
        print('stop inserts')

    def insert_ingredient(self):
        """Вставка данных в модель Ingredient."""
        logger.info('====START====')
        filename = os.path.join(self.shift_path, 'ingredients.csv')
        logger.debug('filename')
        logger.debug(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            csvdict = DictReader(f)
            for row in csvdict:
                logger.info(row)
                try:
                    Ingredient.objects.create(**row)
                    logger.info('row inserts in database')
                except Exception as err:
                    logger.error(err)
        logger.info('====STOP====')
