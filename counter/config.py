import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgreSQLRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    db_type = os.environ.get('db_type', 'mongodb')
    if db_type == "mongodb":
        mongo_host = os.environ.get('MONGO_HOST', 'localhost')
        mongo_port = os.environ.get('MONGO_PORT', 27017)
        mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
        db = CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db)
    else:
        postgres_url = os.environ.get('db_url', "NA")
        if postgres_url == "NA":
            raise Exception("please give right URL")
        else:
            db = CountPostgreSQLRepo(postgres_url)


    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                db)


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()
