from datetime import date, datetime
from enum import EnumMeta
from functools import lru_cache, singledispatch
from typing import (
    Collection,
    Dict,
    FrozenSet,
    GenericMeta,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Set,
)

import attr

from .doc import ModelMeta


def asdict(inst):
    return {
        f.name: _raw_value(f.type)(getattr(inst, f.name))
        for f in attr.fields(inst.__class__)
    }


def _raw_primitive(value):
    return value


def _raw_date_datetime(value):
    return value.isoformat()


def _raw_enum(value):
    return value.value


def _raw_model_meta(value):
    return asdict(value)


def _raw_list(value):
    return [_raw_value(v)(v) for v in value]


def _raw_set(value):
    return {_raw_value(v)(v) for v in value}


# def _raw_tuple(value):
#     return (_raw_value(v)(v) for v in value)


def _raw_dict(value):
    return {_raw_value(k)(k): _raw_value(v)(v) for k, v in value.items()}


@lru_cache(typed=True)
@singledispatch
def _raw_value(type_):
    return _raw_primitive


@_raw_value.register(date)
@_raw_value.register(datetime)
def _raw_value_datetime(type_):
    return _raw_date_datetime


@_raw_value.register(EnumMeta)
def _raw_value_enum(type_):
    return _raw_enum


@_raw_value.register(ModelMeta)
def _raw_value_model_meta(type_):
    return _raw_model_meta


@_raw_value.register(GenericMeta)
def _raw_value_generic_meta(type_):
    if type_.__base__ in (
        List,
        Sequence,
        Collection,
        Iterable,
        MutableSequence,
    ):
        return _raw_list
    elif type_.__base__ in (Set, MutableSet, FrozenSet):
        return _raw_set
    # elif type_.__base__ == Tuple:
    #     return _raw_tuple
    elif type_.__base__ in (Dict, Mapping, MutableMapping):
        return _raw_dict
    else:
        print("utils.py")
        from IPython import embed

        embed()
        raise TypeError("This type is not supported")
