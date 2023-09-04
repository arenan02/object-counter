import os

from counter.adapters.count_repo import (
    CountInMemoryRepo,
    CountMongoDBRepo,
    CountMySQLDBRepo,
)
from counter.adapters.object_detector import FakeObjectDetector, TFSObjectDetector
from counter.domain.actions import CountDetectedObjects, DetectObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = os.environ.get("TFS_PORT", 8501)
    mongo_host = os.environ.get("MONGO_HOST", "localhost")
    mongo_port = os.environ.get("MONGO_PORT", 27017)
    mongo_db = os.environ.get("MONGO_DB", "prod_counter")
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = os.environ.get("MYSQL_PORT", 3306)
    mysql_db = os.environ.get("MYSQL_DB", "prod_counter")
    mysql_table = os.environ.get("MYSQL_TABLE", "counter")
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "root")
    return CountDetectedObjects(
        TFSObjectDetector(tfs_host, tfs_port, "rfcn"),
        [
            CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db),
            CountMySQLDBRepo(
                host=mysql_host,
                port=mysql_port,
                database=mysql_db,
                table=mysql_table,
                user=mysql_user,
                password=mysql_password,
            ),
        ],
    )


def get_count_action() -> CountDetectedObjects:
    """Object count.

    Returns
    -------
    CountDetectedObjects
        An instance of object count.
    """
    env = os.environ.get("ENV", "dev")
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def dev_detection_action() -> DetectObjects:
    return DetectObjects(FakeObjectDetector())


def prod_detection_action() -> DetectObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = os.environ.get("TFS_PORT", 8501)
    return DetectObjects(TFSObjectDetector(tfs_host, tfs_port, "rfcn"))


def get_detection_action() -> DetectObjects:
    """Object detection.

    Returns
    -------
    DetectObjects
        An instance of object detection.
    """
    env = os.environ.get("ENV", "dev")
    detection_action_fn = f"{env}_detection_action"
    return globals()[detection_action_fn]()
