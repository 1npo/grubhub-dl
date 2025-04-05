"""Exports EmailMessage objects to various different formats.
"""

import os
import json
import logging

import pandas as pd

from grubhub_dl import models

logger = logging.getLogger(__name__)


def grubhub_data_to_table(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_json(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_json_file(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_csv_file(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_sqlite(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_postgres(params: models.Parameters, grubhub_data):
    pass


def grubhub_data_to_dataframe(params: models.Parameters, grubhub_data) -> pd.DataFrame:
    pass
