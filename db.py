import os
import sqlalchemy as sa
import sqlalchemy.orm as sao
from sqlalchemy.ext.declarative import declarative_base
import datetime
from typing import List, Dict, TypeVar, Any, Type
import util

# Initialisation
Base = declarative_base()
engine = None
Session = None
T = TypeVar('T')

# Exceptions

class NoRecordsException(Exception):
    pass


class TooManyRecordsException(Exception):
    pass


# JSON-serializable base classes

class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.String, primary_key=True)
    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    type_id = sa.Column(sa.Integer, nullable=False, default=1)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    payload = sa.Column(sa.JSON, nullable=False)

    @property
    def jsondict(self):
        return {'id': str(self.id), 'type_id': self.type_id, 'username': self.username,
                'created_at': self.created_at.isoformat(), 'updated_at': self.updated_at.isoformat(),
                'payload': self.payload}

    def __repr__(self):
        return util.jsonify(self.jsondict)


class RecordType(Base):
    __tablename__ = 'record_type'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=True)
    schema = sa.Column(sa.JSON, nullable=False)
    category_id = sa.Column(sa.Integer, nullable=False)

    @property
    def jsondict(self):
        val = {'id': str(self.id), 'name': self.name,
               'schema': self.schema, 'category_id': self.category_id}
        return val

    def __repr__(self):
        return util.jsonify(self.jsondict)


class RequestLog(Base):
    __tablename__ = 'request_log'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=True)
    schema = sa.Column(sa.JSON, nullable=False)
    category_id = sa.Column(sa.Integer, nullable=False)

    @property
    def jsondict(self):
        val = {'id': str(self.id), 'name': self.name,
               'schema': self.schema, 'category_id': self.category_id}
        return val

    def __repr__(self):
        return util.jsonify(self.jsondict)


class Record(Base):
    __tablename__ = 'record'
    id = sa.Column(sa.String, primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    user_id = sa.Column(sa.String, sa.ForeignKey('user.id'), nullable=True)
    created_user_id = sa.Column(sa.String, nullable=True)
    event_id = sa.Column(sa.String, sa.ForeignKey('event.id'), nullable=True)
    parent_record_id = sa.Column(sa.String, nullable=True)
    type_id = sa.Column(sa.Integer, nullable=False, default=0)
    validated_user_id = sa.Column(sa.String, nullable=True)
    validated_at = sa.Column(sa.DateTime, nullable=True)
    payload = sa.Column(sa.JSON, nullable=False)

    @property
    def jsondict(self):
        val = {'id': str(self.id), 'created_at': self.created_at.isoformat(),
               'updated_at': self.updated_at.isoformat(), 'user_id': str(self.user_id),
               'created_user_id': str(self.created_user_id), 'type_id': self.type_id,
               'payload': self.payload}
        if self.event_id is not None:
            val['event_id'] = self.event_id
        if self.validated_at is not None:
            val['validated_at'] = self.validated_at.isoformat()
        if self.validated_user_id is not None:
            val['validated_user_id'] = self.validated_user_id
        if self.parent_record_id is not None:
            val['parent_record_id'] = self.parent_record_id
        return val

    def __repr__(self):
        return util.jsonify(self.jsondict)


class Event(Base):
    __tablename__ = 'event'
    id = sa.Column(sa.String, primary_key=True)
    organization_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    event_at = sa.Column(sa.DateTime, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    user_id = sa.Column(sa.String, sa.ForeignKey('user.id'), nullable=True)
    address = sa.Column(sa.String, nullable=True)
    postal_code = sa.Column(sa.String, nullable=True)
    longitude = sa.Column(sa.Numeric, nullable=True)
    latitude = sa.Column(sa.Numeric, nullable=True)
    payload = sa.Column(sa.JSON, nullable=False)
    participants = sao.relationship('UserEventLink', lazy='joined')

    @property
    def jsondict(self):
        val = {'id': str(self.id), 'organization_id': self.organization_id,
               'event_at': self.event_at.isoformat(), 'created_at': self.created_at.isoformat(),
               'updated_at': self.updated_at.isoformat(),
               'name': self.name, 'description': self.description,
               'address': self.address, 'postal_code': self.postal_code,
               'longitude': self.longitude, 'latitude': self.latitude,
               'user_id': str(self.user_id), 'participants': list(),
               'payload': self.payload}
        for participant in self.participants:
            val['participants'].append(str(participant.user_id))
        return val

    def __repr__(self):
        return util.jsonify(self.jsondict)


class UserEventLink(Base):
    __tablename__ = 'user_event_link'
    user_id = sa.Column(sa.String, sa.ForeignKey(User.id), primary_key=True)
    event_id = sa.Column(sa.String, sa.ForeignKey(Event.id), primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now())
    payload = sa.Column(sa.JSON, nullable=False)

    @property
    def jsondict(self):
        val = {'user_id': str(self.user_id), 'event_id': str(self.event_id),
               'created_at': self.created_at.isoformat(), 'updated_at': self.updated_at.isoformat(),
               'payload': self.payload}
        return val

    def __repr__(self):
        return util.jsonify(self.jsondict)


def init(app):
    """Function for initializing the database connection.

    Requires that the Flask app config has been initialized with the following variables:
     - DB_USERNAME
     - DB_PASSWORD
     - DB_HOSTNAME
     - DB_DATABASE

    :param app: Flask app object.
    """
    global engine, Session

    engine = sa.create_engine("postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
        app.config['DB_USERNAME'],
        app.config['DB_PASSWORD'],
        app.config['DB_HOSTNAME'],
        app.config['DB_DATABASE']))
    Session = sao.sessionmaker(bind=engine)


def get_rows(t: Type[T], filter_by: Dict[str, Any]) -> List[T]:
    global Session
    session = Session()
    rows = session.query(t).filter_by(**filter_by).all()
    session.close()
    return rows


def get_row(t: Type[T], filter_by: Dict[str, Any]) -> T:
    global Session
    session = Session()
    row = session.query(t).filter_by(**filter_by).first()
    session.close()
    return row


def get_and_update_row(t: Type[T], filter_by: Dict[str, Any], new_params: Dict[str, Any]) -> T:
    global Session
    session = Session()
    row = session.query(t).filter_by(**filter_by).first()
    for key, value in new_params.items():
        setattr(row, key, value)
    session.close()
    return row


def add_row(t: Type[T], params: Dict[str, Any]) -> T:
    """Function for adding a row into the database.

    :param t: SQL Alchemy object type to be created.
    :param params: Parameters of the object to be created.
    """
    global Session
    session = Session()
    row = t(**params)
    session.add(row)
    session.commit()
    return row


def delete_row(t: Type[T], filter_by: Dict[str, Any]) -> None:
    """Function for deleting a single row in the database.

    :param t: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    :raises TooManyRecordsException: If more than one row would be deleted given the criteria in filter_by.
    """
    global Session
    session = Session()
    rows_affected = session.query(t).filter_by(**filter_by).delete()
    if rows_affected == 0:
        raise NoRecordsException
    elif rows_affected > 1:
        session.rollback()
        raise TooManyRecordsException
    session.commit()


def delete_rows(t, filter_by: Dict[str, Any]):
    """Function for deleting a one or many rows in the database.

    :param t: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    """
    global Session
    session = Session()
    rows_affected = session.query(t).filter_by(**filter_by).delete()
    if rows_affected == 0:
        raise NoRecordsException
    session.commit()


def update_row(t, filter_by: Dict[str, Any], params: Dict[str, Any]):
    """Function for updating a single row in the database.

    :param t: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    :raises TooManyRecordsException: If more than one row would be deleted given the criteria in filter_by.
    """
    global Session
    session = Session()
    try:
        rows = session.query(t).filter_by(**filter_by).all()
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


def update_rows(t, filter_by: Dict[str, Any], params: Dict[str, Any]) -> List:
    """Function for updating one or many rows in the database.

    :param t: SQL Alchemy object type.
    :param filter_by: Filters specifying which rows should be affected
    :raises NoRecordsException: If no records matched the criteria in filter_by.
    """
    global Session
    session = Session()
    try:
        rows = session.query(t).filter_by(**filter_by).all()
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
