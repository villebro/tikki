""" Module for handling database interactions """
import re

import pandas as pd

import sqlalchemy as sa
import sqlalchemy.orm as sao

from typing import List, Dict, Any, Type, Tuple

from tikki import utils
from tikki.db.tables import (
    Base, Category, Gender, MilitaryStatus, Performance, RecordType, TestLimit
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


def regenerate_dimensions():
    """Rebuild dimension tables and views.
    """
    global SESSION
    session = SESSION()
    logger = utils.get_logger()
    try:
        logger.info('Regenerate dim_category data in database')
        session.query(Category).delete()
        for category in metadata.categories.values():
            session.add(category)

        logger.info('Regenerate dim_record_type data in database')
        session.query(RecordType).delete()
        for record_type in metadata.record_types.values():
            session.add(record_type)

        logger.info('Regenerate dim_performance data in database')
        session.query(Performance).delete()
        for performance in metadata.performances.values():
            session.add(performance)

        logger.info('Regenerate dim_gender data in database')
        session.query(Gender).delete()
        for gender in metadata.genders.values():
            session.add(gender)

        logger.info('Regenerate dim_military_status data in database')
        session.query(MilitaryStatus).delete()
        for military_status in metadata.military_statuses.values():
            session.add(military_status)

        session.commit()
    except Exception as ex:
        print(ex)
        logger.exception(ex)
        session.rollback()


def regenerate_views():
    global SESSION
    session = SESSION()
    logger = utils.get_logger()
    logger.info('Regenerate views')
    try:
        for view in views.views.values():
            session.execute(view)
        session.commit()
    except Exception as ex:
        print(ex)
        logger.exception(ex)
        session.rollback()


def get_rows_from_file(filename: str) -> List[TestLimit]:
    ret_list: List[TestLimit] = []
    gender_map = {
        'm': int(metadata.GenderEnum.MALE),
        'f': int(metadata.GenderEnum.FEMALE),
    }
    military_status_map = {
        's': int(metadata.MilitaryStatusEnum.SOLDIER),
        'c': int(metadata.MilitaryStatusEnum.CIVILIAN),
        'x': int(metadata.MilitaryStatusEnum.CONSCRIPT),
    }
    file_map = {
        'coopers.tsv': int(metadata.RecordTypeEnum.COOPERS_TEST),
        'standingjump.tsv': int(metadata.RecordTypeEnum.STANDING_JUMP),
        'situp.tsv': int(metadata.RecordTypeEnum.SIT_UPS),
        'pushup.tsv': int(metadata.RecordTypeEnum.PUSH_UP_60_TEST),
    }
    record_type_id = file_map[filename]
    regex = re.compile(r'([scx])([mf])(\d{1,2})-(\d{2,3})')

    data = pd.read_csv('tikki/data/' + filename, header=0, sep='\t')
    limit_cols = {}
    for col in list(data):
        match = regex.match(col)
        if match:
            military_status_id = int(military_status_map[match[1]])
            gender_id = int(gender_map[match.group(2)])
            age_lower_limit = int(match.group(3))
            age_upper_limit = int(match.group(4))
            limit_cols[col] = (military_status_id, gender_id, age_lower_limit, age_upper_limit)  # noqa

    lag_upper_limit: Dict[str, Tuple[int, int, int, int]] = {}
    for _, row in data.sort_values('score', ascending=False).iterrows():
        for col, ids in limit_cols.items():
            upper_limit = lag_upper_limit.get(col, 10 * row[col])
            lower_limit = row[col]
            ret_list.append(TestLimit(record_type_id=record_type_id,
                                      military_status_id=ids[0],
                                      gender_id=ids[1],
                                      age_lower_limit=ids[2],
                                      age_upper_limit=ids[3],
                                      upper_limit=upper_limit,
                                      lower_limit=lower_limit,
                                      performance_id=row['performance_id'],
                                      score=row['score'],
                                      ))
            lag_upper_limit[col] = lower_limit

    return ret_list


def regenerate_limits():
    limits: List[TestLimit] = []
    limits.extend(get_rows_from_file('coopers.tsv'))
    limits.extend(get_rows_from_file('pushup.tsv'))
    limits.extend(get_rows_from_file('standingjump.tsv'))
    limits.extend(get_rows_from_file('situp.tsv'))

    global SESSION
    session = SESSION()
    logger = utils.get_logger()
    try:
        logger.info('Regenerate dim_test_limit data in database')
        session.query(TestLimit).delete()
        for limit in limits:
            session.add(limit)
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
