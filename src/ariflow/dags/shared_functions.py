import json
import logging

from airflow.sdk import BaseHook


def upsert_player_data(player_json):
    import sqlite3

    import pandas as pd

    database_conn_id = "analytics_database"
    connection = BaseHook.get_connection(database_conn_id)
    sqlite_db_path = connection.host

    if player_json:
        player_data = json.loads(player_json)

        with sqlite3.connect(sqlite_db_path) as conn:  # type: ignore
            cursor = conn.cursor()

            for player in player_data:
                try:
                    cursor.execute(
                        """
                        INSERT INTO player (
                        player_id, gsis_id, first_name, last_name,
                        position, last_changed_date
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(player_id) DO UPDATE
                        SET
                        gsis_id = excluded.gsis_id,
                        first_name = excluded.first_name,
                        last_name = excluded.last_name,
                        position = excluded.position,
                        last_changed_date = excluded.last_changed_date
                        """,
                        (
                            player["player_id"],
                            player["gsis_id"],
                            player["first_name"],
                            player["last_name"],
                            player["position"],
                            player["last_changed_date"],
                        ),
                    )
                except Exception as e:
                    logging.error(f"Failed to insert player {player['player_id']}: {e}")
                    raise
    else:
        logging.warning("No player data found.")
        raise ValueError("No player data found. Task failed due to missing data.")

    
