""" Module for handling database interactions """
import sqlalchemy as sa
import sqlalchemy.orm as sao
from typing import List, Dict, Any, Type
from tikki import utils
from tikki.db.tables import (
    Base, Category, Gender, RecordType, TestPerformance
)
from tikki.db import metadata, views
from tikki.exceptions import NoRecordsException, TooManyRecordsException

# Initialisation
SESSION = None  # type: Any


def init(app):
    """Function for initializing the database connection.

    Requires that the Flask app config has been initialized with the following variables:
     - SQLA_DB_URI

    :param app: Flask app object.
    """
    global SESSION

    engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    SESSION = sao.sessionmaker(bind=engine)


def get_rows(base_class: Type[Base], filter_by: Dict[str, Any]) -> List[Base]:
    """Function for retrieving rows from the database.

    :param base_class: SQL Alchemy object type to be retrieved.
    :param filter_by: Filters specifying which rows should be retrieved.
    :return: list of SQL Alchemy objects
    """
    global SESSION
    session = SESSION()
    rows = session.query(base_class).filter_by(**filter_by).all()
    session.close()
    return rows


def get_row(base_class: Type[Base], filter_by: Dict[str, Any]) -> Base:
    """Function for retrieving a row from the database.

    :param base_class: SQL Alchemy object type to be retrieved.
    :param filter_by: Filters specifying which rows should be retrieved.
    :return: SQL Alchemy object
    """
    global SESSION
    session = SESSION()
    row = session.query(base_class).filter_by(**filter_by).first()
    session.close()
    return row


def add_row(base_class: Type[Base], params: Dict[str, Any]) -> Base:
    """Function for adding a row into the database.

    :param base_class: SQL Alchemy object type to be created.
    :param params: Parameters of the object to be created.
    :return: SQL Alchemy object
    """
    global SESSION
    session = SESSION()
    row = base_class(**params)
    session.add(row)
    session.commit()
    return row


def delete_row(base_class: Type[Base], filter_by: Dict[str, Any]) -> None:
    """Function for deleting a single row in the database.

    :param base_class: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    :raises TooManyRecordsException: If more than one row would be deleted given
    the criteria in filter_by.
    """
    global SESSION
    session = SESSION()
    rows_affected = session.query(base_class).filter_by(**filter_by).delete()
    if rows_affected == 0:
        raise NoRecordsException
    elif rows_affected > 1:
        session.rollback()
        raise TooManyRecordsException
    session.commit()


def delete_rows(base_class: Type[Base], filter_by: Dict[str, Any]):
    """Function for deleting a one or many rows in the database.

    :param base_class: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    """
    global SESSION
    session = SESSION()
    rows_affected = session.query(base_class).filter_by(**filter_by).delete()
    if rows_affected == 0:
        raise NoRecordsException
    session.commit()


def update_row(base_class: Type[Base], filter_by: Dict[str, Any],
               params: Dict[str, Any]) -> Base:
    """Function for updating and retrieving a single row in the database.

    :param base_class: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :param params: Parameters of the object to be updated.
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    :raises TooManyRecordsException: If more than one row would be deleted given the
    criteria in filter_by.
    :return: SQL Alchemy object
    """
    global SESSION
    session = SESSION()
    try:
        rows = session.query(base_class).filter_by(**filter_by).all()
        if rows is None or len(rows) == 0:
            session.close()
            raise NoRecordsException
        elif len(rows) > 1:
            session.rollback()
            raise TooManyRecordsException
    except Exception:
        session.close()
        raise NoRecordsException

    row = rows[0]
    for key, value in params.items():
        setattr(row, key, value)
    session.commit()
    return row


def update_rows(base_class: Type[Base], filter_by: Dict[str, Any],
                params: Dict[str, Any]) -> List[Base]:
    """Function for updating and retrieving one or many rows in the database.

    :param base_class: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :param params: Attributes to update
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    :return: List of SQL Alchemy objects
    """
    global SESSION
    session = SESSION()
    try:
        rows = session.query(base_class).filter_by(**filter_by).all()
        if rows is None or len(rows) == 0:
            session.close()
            raise NoRecordsException
    except Exception:
        session.close()
        raise NoRecordsException

    for row in rows:
        for key, value in params.items():
            setattr(row, key, value)
        session.commit()
    return rows


def regenerate_metadata():
    """Rebuild dimension tables and views.
    """
    global SESSION
    session = SESSION()
    logger = utils.get_logger()
    try:
        logger.info('Regenerate dim_category_type data in database')
        session.query(Category).delete()
        for category_type in metadata.category_types.values():
            session.add(category_type)

        logger.info('Regenerate dim_record_type data in database')
        session.query(RecordType).delete()
        for record_type in metadata.record_types.values():
            session.add(record_type)

        logger.info('Regenerate views')
        for view in views.views.values():
            session.execute(view)

        test_performances = [
            TestPerformance(6, 'Excellent'),  # Erinomainen
            TestPerformance(5, 'Very Good'),  # Kiitettävä
            TestPerformance(4, 'Good'),  # Hyvä
            TestPerformance(3, 'Satisfactory'),  # Tyydyttävä
            TestPerformance(2, 'Sufficient'),  # Välttävä
            TestPerformance(1, 'Poor'),  # Heikko
            TestPerformance(0, 'Inadequate'),  # Riittämätön
        ]
        for test_performance in test_performances:
            session.add(test_performance)

        genders = [
            Gender(0, 'Unknown'),
            Gender(1, 'Male'),
            Gender(2, 'Female'),
        ]
        for gender in genders:
            session.add(gender)

        session.commit()
    except Exception as ex:
        print(ex)
        logger.exception(ex)
        session.rollback()


def drop_metadata():
    """Rebuild dimension tables and views.
    """
    global SESSION
    session = SESSION()
    logger = utils.get_logger()
    try:
        logger.info('Drop views')
        for view in sorted(views.views.values(), reverse=True):
            print(view)
            session.execute(view)
        session.commit()
    except Exception as ex:
        print(ex)
        logger.exception(ex)
        session.rollback()
