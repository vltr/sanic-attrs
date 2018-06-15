from datetime import date, datetime
from enum import EnumMeta
from functools import partial, singledispatch
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
from dateutil.parser import parse


def model_converter(model_cls, value):
    if isinstance(value, model_cls):
        return value
    return model_cls(**value)


def _iterable_converter(value_converter, is_set, value):
    res = [value_converter(v) for v in value]
    return res if not is_set else set(res)


def _dict_converter(key_converter, value_converter, value):
    return {key_converter(k): value_converter(v) for k, v in value.items()}


def _date_converter(value):
    if isinstance(value, str):
        return parse(value).date()
    elif isinstance(value, (tuple, list, set)) and len(value) > 2:
        return date(*value[:3])
    elif isinstance(value, (int, float)):
        return date.fromtimestamp(value)
    raise TypeError(
        'the value "{}" given can\'t be converted to date'.format(value)
    )


def _datetime_converter(value):
    if isinstance(value, str):
        return parse(value)
    elif isinstance(value, (tuple, list, set)) and len(value) > 2:
        return datetime(*value)
    elif isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    raise TypeError(
        'the value "{}" given can\'t be converted to datetime'.format(value)
    )


@singledispatch
def converter(type_):
    if type_ in (int, float, str, bool):
        return type_
    elif type_ == date:
        return _date_converter
    elif type_ == datetime:
        return _datetime_converter
    elif attr.has(type_):
        return partial(model_converter, type_)
    else:
        raise TypeError("SEE ME!")


@converter.register(EnumMeta)
def _converter_enum(type_):
    return type_


@converter.register(GenericMeta)
def _converter_generic_meta(type_):
    if type_.__base__ in (
        List,
        Set,
        MutableSet,
        Sequence,
        Collection,
        Iterable,
        MutableSequence,
        FrozenSet,
    ):
        if type_.__args__:
            return partial(
                _iterable_converter,
                converter(type_.__args__[0]),
                type_.__base__ == Set,
            )
    elif type_.__base__ in (Dict, Mapping, MutableMapping):
        if type_.__args__:
            return partial(
                _dict_converter,
                converter(type_.__args__[0]),
                converter(type_.__args__[1]),
            )
    else:
        print("converters.py")
        from IPython import embed

        embed()
        raise TypeError("This type is not supported")


# List, MutableSequence, Sequence, Collection, Iterable
# Dict, MutableMapping, Mapping
# MutableSet, Set, FrozenSet
# NamedTuple, NamedTupleMeta  <<<
# Tuple
# Any, Optional, Union <<<
