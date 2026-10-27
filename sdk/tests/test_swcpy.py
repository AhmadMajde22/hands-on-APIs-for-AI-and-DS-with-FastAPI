from io import BytesIO

import pandas as pd
import pyarrow.parquet as pq
import pytest
from swcpy import SWCClient, SWCConfig # type: ignore
from swcpy.schemas import League # type: ignore


def test_health_check():
    """Tests health check from SDK"""
    config = SWCConfig(swc_base_url="http://127.0.0.1:8000", backoff=False)
    client = SWCClient(config)
    response = client.get_health_check()
    assert response.status_code == 200
    assert response.json() == {
        "message": "This is an API health check: status successful"
    }


def test_list_leagues():
    """Tests get leagues from SDK"""
    config = SWCConfig(swc_base_url="http://127.0.0.1:8000", backoff=False)
    client = SWCClient(config)
    leagues_response = client.list_leagues()

    assert isinstance(leagues_response, list)

    for league in leagues_response:
        assert isinstance(league, League)

    assert len(leagues_response) == 5


def test_bulk_player_file_parquet():
    """Tests bulk player download through SDK - Parquet"""
    config = SWCConfig(
        swc_base_url="http://127.0.0.1:8000",
        bulk_file_format="parquet",
    )
    client = SWCClient(config)
    player_file_parquet = client.get_bulk_player_file()
    # Assert the file has the correct number of records (including header)
    player_table = pq.read_table(BytesIO(player_file_parquet))
    player_df = player_table.to_pandas()
    assert len(player_df) == 1018
