import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("database.initial_data_started")
    init()
    logger.info("database.initial_data_completed")


if __name__ == "__main__":
    main()
