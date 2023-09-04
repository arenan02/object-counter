from typing import List

import mysql.connector
from pymongo import MongoClient

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


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


class CountMySQLDBRepo(ObjectCountRepo):
    def __init__(self, host, port, database, table, user, password):
        self.__host = host
        self.__port = port
        self.__database = database
        self.__table = table
        self.__user = user
        self.__password = password

    def __get_connection(self):
        connection = mysql.connector.connect(
            host=self.__host,
            port=self.__port,
            user=self.__user,
            password=self.__password,
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.__database}")
        cursor.execute(f"USE {self.__database}")
        cursor.execute(
            f"""
CREATE TABLE IF NOT EXISTS {self.__table} (
    `object_class` varchar(50) NOT NULL,
    `count` int NOT NULL,
    PRIMARY KEY (`object_class`)
)"""
        )
        return connection

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        connection = self.__get_connection()
        cursor = connection.cursor()
        query = f"""
SELECT object_class, count
FROM {self.__table}
"""
        if object_classes:
            query = f"""
SELECT object_class, count
FROM {self.__table}
WHERE object_class IN ({','.join(map(lambda x: "'" + x + "'", object_classes))})
"""
        cursor.execute(query)
        counters = cursor.fetchall()
        object_counts = [ObjectCount(counter[0], counter[1]) for counter in counters]
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        connection = self.__get_connection()
        cursor = connection.cursor()
        for value in new_values:
            cursor.execute(
                f"""
INSERT INTO {self.__table} (object_class, count)
VALUES ('{value.object_class}', {value.count})
ON DUPLICATE KEY UPDATE
count = count + {value.count}
"""
            )
        connection.commit()
