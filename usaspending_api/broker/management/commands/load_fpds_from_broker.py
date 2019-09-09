from django.core.management.base import BaseCommand
import logging
import re
import psycopg2

from usaspending_api.data_load.fpds_loader import run_fpds_load, destory_orphans
from usaspending_api.common.retrieve_file_from_uri import RetrieveFileFromUri
from usaspending_api.common.helpers.date_helper import datetime_command_line_argument_type
from usaspending_api.common.helpers.sql_helpers import get_broker_dsn_string
from usaspending_api.etl.award_helpers import (
    update_awards,
    update_contract_awards,
    update_award_categories,
    award_types,
)

logger = logging.getLogger("console")

BROKER_CONNECTION_STRING = get_broker_dsn_string()

CHUNK_SIZE = 10000  # Completely arbitrary and not backed by any testing, this can likely go higher

FPDS_FROM_DATE_QUERY = "SELECT detached_award_procurement_id FROM detached_award_procurement WHERE updated_at >= %s;"
ALL_FPDS_QUERY = "SELECT detached_award_procurement_id FROM detached_award_procurement;"


class Command(BaseCommand):
    help = "Sync USAspending DB FPDS data using Broker for new or modified records and S3 for deleted IDs"

    @staticmethod
    def get_fpds_transaction_ids_from_date(date):
        with psycopg2.connect(dsn=BROKER_CONNECTION_STRING) as connection:
            db_cursor = connection.cursor()
            db_query = FPDS_FROM_DATE_QUERY
            db_args = [date]
            db_cursor.execute(db_query, db_args)
            db_rows = [id[0] for id in db_cursor.fetchmany(CHUNK_SIZE)]

        return db_rows

    @staticmethod
    def get_all_fpds_transaction_ids():
        with psycopg2.connect(dsn=BROKER_CONNECTION_STRING) as connection:
            db_cursor = connection.cursor()
            db_query = ALL_FPDS_QUERY
            db_cursor.execute(db_query)
            db_rows = [id[0] for id in db_cursor.fetchmany(CHUNK_SIZE)]

        return db_rows

    def load_fpds_from_date(self, date):
        if date is None:
            logger.info("fetching all fpds transactions...")
            while True:
                id_list = self.get_all_fpds_transaction_ids()
                if len(id_list) == 0:
                    break
                logger.info(
                    "Loading batch from date query (size: {})...".format(len(id_list))
                )
                run_fpds_load(id_list)

        else:
            logger.info("fetching fpds transactions since {}".format(date))
            while True:
                id_list = self.get_fpds_transaction_ids_from_date(date)
                if len(id_list) == 0:
                    break
                logger.info(
                    "Loading batch from date query (size: {})...".format(len(id_list))
                )
                run_fpds_load(id_list)


    @staticmethod
    def next_file_batch_generator(file):
        while True:
            lines = file.readlines(CHUNK_SIZE)
            lines = [line.decode("utf-8") for line in lines]
            if len(lines) == 0:
                break
            yield lines

    def load_fpds_from_file(self, file_path):
        with RetrieveFileFromUri(file_path).get_file_object() as file:
            for next_batch in self.next_file_batch_generator(file):
                id_list = [int(re.search(r"\d+", x).group()) for x in next_batch]
                logger.info(
                    "Loading next batch from provided file (size: {}, ids {}-{})...".format(
                        len(id_list), id_list[0], id_list[-1]
                    )
                )
                run_fpds_load(id_list)

    def add_arguments(self, parser):
        mutually_exclusive_group = parser.add_mutually_exclusive_group()

        mutually_exclusive_group.add_argument(
            "--ids",
            nargs="+",
            type=int,
            help="(OPTIONAL) detached_award_procurement_ids of FPDS transactions to load/reload from Broker",
        )
        mutually_exclusive_group.add_argument(
            "--date",
            dest="date",
            type=datetime_command_line_argument_type(naive=True),  # Broker date/times are naive.
            help="(OPTIONAL) Date from which to start the nightly loader. Expected format: YYYY-MM-DD",
        )
        mutually_exclusive_group.add_argument(
            "--file",
            metavar="FILEPATH",
            type=str,
            help="A file containing only transaction IDs (detached_award_procurement_id) "
            "to reload, one ID per line. Nonexistent IDs will be ignored.",
        )
        mutually_exclusive_group.add_argument(
            "--reload-all",
            action="store_true",
            help="Script will reload all FPDS records in broker database",
        )

        parser.add_argument(
            "--no-award-updates",
            action="store_true",
            help="Skip any steps involving calculating derived award values. C to D linkages will still occur."
        )

    def handle(self, *args, **options):
        if options["reload_all"]:
            self.load_fpds_from_date(None)

        if options["ids"]:
            run_fpds_load(options["ids"])

        if options["file"]:
            self.load_fpds_from_file(options["file"])

        if options["date"]:
            self.load_fpds_from_date(options["date"])

        logger.info("cleaning orphaned rows")
        destory_orphans()

        logger.info("updating award values")
        if not options["no_award_updates"]:
            update_awards()
            update_contract_awards()
            update_award_categories()
