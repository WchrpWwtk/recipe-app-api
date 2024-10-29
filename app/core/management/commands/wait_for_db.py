"""
Django command to wait for the database to be available.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """
    Django command to wait for a database.
    """

    def handle(self, *args, **options):
        """
        Entrypoint for command.
        :param args:
        :param options:
        :return:
        """
        self.stdout.write("Waiting for the database...")
        db_up = False

        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, please wait...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
