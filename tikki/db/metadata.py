"""
Module containing type ids and their schenas that are used throughout the application.
These are currently regenerated at the end of the migration process, but will be moved
to a dedicated migration step once wording and schemas are finalized.
"""
from enum import IntEnum
from typing import Any, Dict

from tikki.db.tables import Category, RecordType


class TestPerformanceEnum(IntEnum):
    EXCELLENT = 6
    VERY_GOOD = 5
    GOOD = 4
    SATISFACTORY = 3
    SUFFICIENT = 2
    POOR = 1
    INSUFFICIENT = 0


class MilitaryStatusEnum(IntEnum):
    UNKNOWN = 0
    CIVILIAN = 1
    SOLDIER = 2
    CONSCRIPT = 3


class GenderEnum(IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class CategoryEnum(IntEnum):
    UNKNOWN = 0
    TEST = 1
    QUESTIONNAIRE = 2


class RecordTypeEnum(IntEnum):
    COOPERS_TEST = 1
    PUSH_UP_60_TEST = 2
    SIT_UPS = 3
    STANDING_JUMP = 4
    ACTIVITY_STATUS = 6
    EDUCATION_DURATION = 7
    CURRENT_FITNESS = 8
    WORKING_ABILITY = 9
    HIGH_BLOOD_PRESSURE = 10
    DIABETES = 11
    ALCOHOL = 12
    SMOKING = 13
    FAMILY_STATUS = 14
    DEPRESSION = 15
    SICK_LEAVE = 16


# Category types

categories: Dict[int, Category] = {}


def _append_category(id_: int, name: str):
    """
    Append new record type to global category dict
    """
    global categories
    categories[id_] = Category(id=id_, name=name)


_append_category(0, 'Unknown')
_append_category(1, 'Test')
_append_category(2, 'Questionnaire')


# Record types

record_types: Dict[int, RecordType] = {}


def _append_record_type(id_: int, category_id: int, name: str, schema: Dict[str, Any]):
    """
    Append new record type to global record type dict
    """
    global record_types
    record_types[id_] = RecordType(id=id_, name=name, schema=schema,
                                   category_id=category_id)


_append_record_type(0, 0, 'Unknown', {})
_append_record_type(1, 2, "Cooper's test", {'distance': 'float'})
_append_record_type(2, 1, 'Push-up 60 sec test', {'pushups': 'integer'})
_append_record_type(3, 1, 'Sit-up test', {'situps': 'integer'})
_append_record_type(4, 1, 'Standing jump', {'standingjump': 'integer'})
_append_record_type(6, 2, 'Activity level', {
    'single': {
        'question':
            'Ajattele kolmea viime kuukautta ja ota huomioon kaikki sellainen vapaa-ajan '
            'fyysinen rasitus, joka on kestänyt kerrallaan vähintään 20 minuuttia. '
            'Liikunta on ripeää ja reipasta, kun se aiheuttaa ainakin jonkin verran '
            'hikoilua ja hengityksen kiihtymistä.',
        'options': {
            '1': 'Ei juuri mitään liikuntaa joka viikko',
            '2': 'Verkkaista tai rauhallista liikuntaa yhtenä tai useampana päivänä '
                 'viikossa',
            '3': 'Ripeää ja reipasta liikuntaa noin kerran viikossa',
            '4': 'Ripeää ja reipasta liikuntaa kaksi kertaa viikossa',
            '5': 'Ripeää ja reipasta liikuntaa kolme kertaa viikossa',
            '6': 'Ripeää ja reipasta liikuntaa ainakin neljä kertaa viikossa'}}})
_append_record_type(7, 2, 'Education duration', {
    'question':
        'Kuinka monta vuotta olette yhteensä käynyt koulua ja opiskellut päätoimisesti '
        '(kansakoulu tai peruskoulu lasketaan mukaan)',
    'format': 'integer'})
_append_record_type(8, 2, 'Current fitness', {
    'single': {
        'question': 'Mitä mieltä olette nykyisestä terveydentilastanne?',
        'options': {
            '1': 'Erittäin hyvä',
            '2': 'Melko hyvä',
            '3': 'Keskitasoinen',
            '4': 'Melko huono',
            '5': 'Erittäin huono'}}})
_append_record_type(9, 2, 'Working ability', {
    'single': {
        'question': 'Työkyky kuvastaa kykyäsi selviytyä työtehtävistäsi. Miten arvioit '
                    'tämänhetkistä työkykyäsi?',
        'options': {
            '1': 'Erittäin hyvä',
            '2': 'Melko hyvä',
            '3': 'Keskitasoinen',
            '4': 'Melko huono',
            '5': 'Erittäin huono'
        }}})
_append_record_type(10, 2, 'High blood pressure', {
    'single': {
        'question': 'Onko teillä koskaan todettu korkea tai kohonnut verenpaine?',
        'options': {
            '1': 'Kyllä',
            '2': 'Ei'}}})
_append_record_type(11, 2, 'Diabetes', {
    'single': {
        'question': 'Onko teillä koskaan todettu diabetes, eli sokeritauti?',
        'options': {
            '1': 'Kyllä',
            '2': 'Ei'}}})
_append_record_type(12, 2, 'Alcohol', {
    'single': {
        'question': 'Kuinka usein juot alkoholia kerralla kuusi annosta tai enemmän? '
                    '(alkoholiannos käsittää pullon olutta tai vastaavaa, lasin viiniä '
                    'tai ravintola-annoksen väkevää alkoholijuomaa)',
        'options': {
            '1': 'En koskaan',
            '2': 'Harvemmin kuin kerran kuukaudessa',
            '3': 'Kerran kuukaudessa',
            '4': 'Kerran viikossa',
            '5': 'Päivittäin tai lähes päivittäin'}}})
_append_record_type(13, 2, 'Alcohol', {
    'single': {
        'question': 'Kuinka usein juot alkoholia kerralla kuusi annosta tai enemmän? '
                    '(alkoholiannos käsittää pullon olutta tai vastaavaa, lasin viiniä '
                    'tai ravintola-annoksen väkevää alkoholijuomaa)',
        'options': {
            '1': 'En koskaan',
            '2': 'Harvemmin kuin kerran kuukaudessa',
            '3': 'Kerran kuukaudessa',
            '4': 'Kerran viikossa',
            '5': 'Päivittäin tai lähes päivittäin'}}})
_append_record_type(14, 2, 'Family status', {
    'single': {
        'question': 'Mikä on elämäntilanteesi parisuhteen ja perheen suhteen?',
        'options': {
            '1': 'Asun yksin',
            '2': 'Asun parisuhteessa',
            '3': 'Asun yksin lapsen/lasten kanssa',
            '4': 'Asun parisuhteessa lapsen/lasten kanssa'}}})
_append_record_type(15, 2, 'Depression', {
    'single': {
        'question': 'Onko teillä viimeisen 12 kuukauden aikana ollut vähintään kahden '
                    'viikon jaksoa, jolloin olette suurimman osan aikaa ollut mieli '
                    'maassa, alakuloinen tai masentunut?',
        'options': {
            '1': 'Ei',
            '2': 'Kyllä'}}})
_append_record_type(16, 2, 'Sick leave', {
    'single': {
        'question': 'Kuinka monta päivää olet ollut sairaslomalla viimeisen '
                    'vuoden aikana?',
        'options': {
            '1': 'En lainkaan',
            '2': '1-3 päivää',
            '3': '4-7 päivää',
            '4': '8-14 päivää',
            '5': '15-30 päivää',
            '6': '31-60',
            '7': '61-120',
            '8': 'yli 120 päivää'}}})
