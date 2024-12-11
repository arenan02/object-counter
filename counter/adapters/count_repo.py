import os
from typing import List
from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient

import psycopg2
from psycopg2.extras import Json

class CountInMemoryRepo(ObjectCountRepo):
    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(
                    key, stored_object_count.count + new_object_count.count
                )
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):
    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter["object_class"], counter["count"]))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one(
                {"object_class": value.object_class},
                {"$inc": {"count": value.count}},
                upsert=True,
            )

class CountSQLDBRepo(ObjectCountRepo):
    def __init__(self, host: str, port: int, database: str):
        """
        Initialize the database connection.
        """
        self.__host = host
        self.__port = port
        self.__database = database
        self.conn = psycopg2.connect(
            dbname=self.__database,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=self.__host,
            port=self.__port,
        )

    def update_values(self, new_values: List[ObjectCount]):
        """
        Update object counts in the database.

        :param new_values: A list of ObjectCount objects to update.
        """
        try:
            with self.conn.cursor() as cursor:
                query = """
                INSERT INTO object_counts (image_id, object_counts)
                VALUES (%s, %s)
                ON CONFLICT (image_id) DO UPDATE
                SET object_counts = EXCLUDED.object_counts;
                """
                for obj in new_values:
                    cursor.execute(query, (obj.image_id, Json(obj.counts)))
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Database error: {e}")

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """
        Retrieve object detection results filtered by object classes.

        :param object_classes: Optional list of object classes to filter results.
        :return: A list of ObjectCount objects.
        """
        try:
            with self.conn.cursor() as cursor:
                if object_classes:
                    query = """
                    SELECT image_id, object_counts
                    FROM object_counts
                    WHERE object_classes && %s;
                    """
                    cursor.execute(query, (object_classes,))
                else:
                    query = "SELECT image_id, object_counts FROM object_counts;"
                    cursor.execute(query)

                results = cursor.fetchall()
                return [ObjectCount(image_id=row[0], counts=row[1]) for row in results]
        except psycopg2.Error as e:
            raise RuntimeError(f"Database error: {e}")

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
