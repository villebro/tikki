"""
Module containing all SQL Alchemy table classes that are used by the platform.
"""
import json
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as sao
from typing import Any, Dict
from sqlalchemy_utils import UUIDType, JSONType


class TikkiBase(object):
    """
    JSON serializable Base table class.
    """
    @property
    def json_dict(self) -> Dict[str, Any]:
        """
        A dict representation of the object that can be serialized to json.

        :return: a dict mapping column names to values
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """
        A json-representation of the object.

        :return: a string-based json representation of the object
        """
        return json.dumps(self.json_dict)


Base = declarative_base(cls=TikkiBase)  # type: Any


class Category(Base):
    """
    Table containing record categories
    """
    __tablename__ = 'dim_category'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                }


class UserType(Base):
    """
    Table containing user types
    """
    __tablename__ = 'dim_user_type'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                }


class RecordType(Base):
    """
    Table containing record types
    """
    __tablename__ = 'dim_record_type'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    schema = sa.Column(JSONType, nullable=False)
    category_id = sa.Column(sa.Integer, sa.ForeignKey('dim_category.id'),
                            nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                'schema': self.schema,
                'category_id': self.category_id,
                }


class User(Base):
    """
    Table containing user details
    """
    __tablename__ = 'fact_user'
    id = sa.Column(UUIDType, primary_key=True)
    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('dim_user_type.id'), nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    payload = sa.Column(JSONType, nullable=False)

    @property
    def json_dict(self) -> Dict[str, Any]:
        return {'id': str(self.id),
                'type_id': self.type_id,
                'username': self.username,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'payload': self.payload,
                }


class Record(Base):
    """
    Table containing activity and other records, such as executed tests and
    answers to questionnaires.
    """
    __tablename__ = 'fact_record'
    id = sa.Column(UUIDType, primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    user_id = sa.Column(UUIDType, sa.ForeignKey('fact_user.id'), nullable=False)
    created_user_id = sa.Column(UUIDType, nullable=False)
    event_id = sa.Column(UUIDType, sa.ForeignKey('fact_event.id'), nullable=False)
    parent_record_id = sa.Column(UUIDType, nullable=True)
    type_id = sa.Column(sa.Integer, nullable=False, default=0)
    validated_user_id = sa.Column(UUIDType, nullable=True)
    validated_at = sa.Column(sa.DateTime, nullable=True)
    payload = sa.Column(JSONType, nullable=False)

    @property
    def json_dict(self):
        val = {'id': str(self.id),
               'created_at': self.created_at.isoformat(),
               'updated_at': self.updated_at.isoformat(),
               'user_id': str(self.user_id),
               'created_user_id': str(self.created_user_id),
               'type_id': self.type_id,
               'payload': self.payload,
               }
        if self.event_id is not None:
            val['event_id'] = self.event_id
        if self.validated_at:
            val['validated_at'] = self.validated_at.isoformat()
        if self.validated_user_id:
            val['validated_user_id'] = self.validated_user_id
        if self.parent_record_id:
            val['parent_record_id'] = self.parent_record_id
        return val


class Event(Base):
    """
    Table containing Events where activities can be executed.
    """
    __tablename__ = 'fact_event'
    id = sa.Column(UUIDType, primary_key=True)
    organization_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    event_at = sa.Column(sa.DateTime, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    user_id = sa.Column(UUIDType, sa.ForeignKey('fact_user.id'), nullable=True)
    address = sa.Column(sa.String, nullable=True)
    postal_code = sa.Column(sa.String, nullable=True)
    longitude = sa.Column(sa.Numeric, nullable=True)
    latitude = sa.Column(sa.Numeric, nullable=True)
    payload = sa.Column(JSONType, nullable=False)
    participants = sao.relationship('UserEventLink', lazy='joined')

    @property
    def json_dict(self):
        val = {'id': str(self.id),
               'organization_id': self.organization_id,
               'event_at': self.event_at.isoformat(),
               'created_at': self.created_at.isoformat(),
               'updated_at': self.updated_at.isoformat(),
               'name': self.name,
               'description': self.description,
               'address': self.address,
               'postal_code': self.postal_code,
               'longitude': self.longitude,
               'latitude': self.latitude,
               'user_id': str(self.user_id),
               'participants': list(),
               'payload': self.payload,
               }
        for participant in self.participants:
            val['participants'].append(str(participant.user_id))
        return val


class UserEventLink(Base):
    """
    Table containing links between users and events.
    """
    __tablename__ = 'fact_user_event_link'
    user_id = sa.Column(UUIDType, sa.ForeignKey('fact_user.id'), primary_key=True)
    event_id = sa.Column(UUIDType, sa.ForeignKey('fact_event.id'), primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    payload = sa.Column(JSONType, nullable=False)

    @property
    def json_dict(self):
        return {'user_id': str(self.user_id),
                'event_id': str(self.event_id),
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'payload': self.payload,
                }


class MilitaryStatus(Base):
    """
    Table containing military statuses (soldier, civilian, conscript)
    """
    __tablename__ = 'dim_military_status'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                }


class Gender(Base):
    """
    Table containing genders
    """
    __tablename__ = 'dim_gender'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                }


class Performance(Base):
    """
    Table containing test performance categories
    """
    __tablename__ = 'dim_performance'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    @property
    def json_dict(self):
        return {'id': self.id,
                'name': self.name,
                }


class TestLimit(Base):
    """
    Table containing test limits
    """
    __tablename__ = 'dim_test_limit'
    record_type_id = sa.Column(sa.Integer, primary_key=True)
    military_status_id = sa.Column(sa.Integer, sa.ForeignKey('dim_military_status.id'),
                                   primary_key=True)
    gender_id = sa.Column(sa.Integer, sa.ForeignKey('dim_gender.id'), primary_key=True)
    age_lower_limit = sa.Column(sa.Integer, nullable=False)
    age_upper_limit = sa.Column(sa.Integer, nullable=False)
    lower_limit = sa.Column(sa.Float, nullable=False)
    upper_limit = sa.Column(sa.Float, nullable=False)
    performance_id = sa.Column(sa.Integer, sa.ForeignKey('dim_performance.id'),
                               nullable=False)
    score = sa.Column(sa.Float, nullable=False)

    @property
    def json_dict(self):
        return {'record_type_id': self.record_type_id,
                'military_status_id': self.military_status_id,
                'gender_id': self.gender_id,
                'age_lower_limit': self.age_lower_limit,
                'age_upper_limit': self.age_upper_limit,
                'lower_limit': self.lower_limit,
                'upper_limit': self.upper_limit,
                'performance_id': self.performance_id,
                'score': self.score
                }
