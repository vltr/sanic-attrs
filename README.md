# Sanic with attrs towards Swagger 2.0 / OpenAPI support

Supercharge your [Sanic](https://github.com/channelcat/sanic>) app with:

- [attrs](http://www.attrs.org/)
- [Swagger](https://swagger.io/docs/specification/2-0/basic-structure/)

**Note**: This is a fork of Sanic OpenAPI implementation from [@channelcat](https://github.com/channelcat), which I like a lot but it lacks some of the functionality I wanted (and I also went sideways by using a third-party lib ([`attrs`](http://www.attrs.org/)) as default for modeling input / output model classes).

[![PyPI](https://img.shields.io/pypi/v/sanic-attrs.svg)](https://pypi.python.org/pypi/sanic-attrs/)
[![PyPI](https://img.shields.io/pypi/pyversions/sanic-attrs.svg)](https://pypi.python.org/pypi/sanic-attrs/)

## Super quick introduction

Give your Sanic API an UI and OpenAPI documentation, all for the price of free!

![Example Swagger UI](https://github.com/vltr/sanic-attrs/blob/master/images/code-to-ui.png?raw=true "Swagger UI")

## Installation

**Attention**: since this fork came from a necessity of mine, a lot of features I want to implement are still not available, hence the status of `pre-alpha` to this library! Also, _don't try the examples folder_, it was not converted (yet)! Shame on me ...

```shell
pip install sanic-attrs
```

Add OpenAPI and Swagger UI:

```python
from sanic_attrs import swagger_blueprint, openapi_blueprint

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
```

You'll now have a Swagger UI at the URL `/swagger`. Your routes will be automatically categorized by their blueprints. This is the default usage, but more advanced usage can be seen. Keep reading!

_Note_: the `swagger_blueprint` is awesome but sometimes you don't want it open-wide for whatever reason you have (security, etc), so you can make it available only if running with `debug=True`, for example. That's how I actually use it :smile:

## [typing](https://docs.python.org/3/library/typing.html)

Since `sanic-attrs` is, of course, based on `attrs` and the Python target version is 3.5+, most of the typing definitions for your model will be made entirely using Python types, either global ones or from the `typing` library. Also, `enums` are supported as well! :sparkles:

### Supported types

#### "Primitives"

- `int`
- `float`
- `str`
- `bool`
- `date`
- `datetime`
- `bytes`

### Enums

Probably all enums will be transparently supported by `sanic-attrs`.

### `typing` to array / list

- `typing.List`
- `typing.Collection`
- `typing.Sequence`
- `typing.MutableSequence`
- `typing.Iterable`

### `typing` to dictionaries

- `typing.Dict`
- `typing.MutableMapping`
- `typing.Mapping`

### `typing` to sets

- `typing.Set`
- `typing.MutableSet`
- `typing.FrozenSet`

### Other `typing` members

- `typing.Any`
- `typing.Optional`
- `typing.Union`

**A note on `list` and `dict`**: Please, use `typing.List` and `typing.Dict` for this.

## Usage

### Use simple decorators to document routes

```python
from sanic_attrs import doc

@app.get("/user/<user_id:int>")
@doc.summary("Fetches a user by ID")
@doc.produces(SomeOutputModel)
async def get_user(request, user_id):
    ...

@app.post("/user")
@doc.summary("Creates a user")
@doc.consumes(SomeInputModel, location="body")
async def create_user(request):
    ...
```

### Model your input/output

Yes, in this version you **need** to be descriptive :wink:

```python
import typing

from sanic_attrs import doc


class Car(doc.Model):
    make: str = doc.field(description="Who made the car")
    model: str = doc.field(description="Type of car. This will vary by make")
    year: int = doc.field(description="4-digit year of the car", required=False)


class Garage(doc.Model):
    spaces: int = doc.field(description="How many cars can fit in the garage")
    cars: typing.List[Car] = doc.field(description="All cars in the garage")


@app.get("/garage")
@doc.summary("Gets the whole garage")
@doc.produces(Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"make": "Nissan", "model": "370Z"}]
    })

```

### Advanced usage

Since `doc.Model` and `doc.field` are nothing more as syntatic sugar for the `@attr.s` decorator and `attr.ib` function, you can express your models using these provided classes and methods or use vanilla `attrs` in your models. Here's a complex example that shows a mixed model:

```python
from enum import Enum, IntEnum
from typing import (Any, Collection, Dict, Iterable, List, Mapping, Optional,
                    Sequence, Set, Union)

import attr

from sanic_attrs import doc


class PlatformEnum(str, Enum):
    XBOX1 = "XBOX1"
    PLAYSTATION4 = "PLAYSTATION4"
    PC = "PC"


class LanguageEnum(IntEnum):
    ENGLISH = 1
    JAPANESE = 2
    SPANISH = 3
    GERMAN = 4
    PORTUGUESE = 5


class Something(doc.Model):
    some_name: str = doc.field(description="Something name")


@attr.s
class AnotherSomething:
    another_name: str = attr.ib(metadata={"description": "Another field"})


class Game(doc.Model):
    name: str = doc.field(description="The name of the game")
    platform: PlatformEnum = doc.field(description="Which platform it runs on")
    score: float = doc.field(description="The average score of the game")
    resolution_tested: str = doc.field(description="The resolution which the game was tested")
    genre: List[str] = doc.field(description="One or more genres this game is part of")
    genre_extra: Sequence[str] = doc.field(description="One or more genres this game is part of")
    rating: Dict[str, float] = doc.field(description="Ratings given on each country")
    rating_outside: Mapping[str, float] = doc.field(description="Ratings given on each country")
    screenshots: Set[bytes] = doc.field(description="Screenshots of the game")
    screenshots_extra: Collection[bytes] = doc.field(description="Screenshots of the game")
    players: Iterable[str] = doc.field(description="Some of the notorious players of this game")
    review_link: Optional[str] = doc.field(description="The link of the game review (if exists)")
    junk: Union[str, bytes] = doc.field(description="This should be strange")
    more_junk: Any = doc.field(description="The more junk field")
    language: LanguageEnum = doc.field(description="The language of the game")
    something: List[Something] = doc.field(description="Something to go along the game")
    another: AnotherSomething = doc.field(description="Another something to go along the game")
```

### A note on typing hints or `type` argument

You may have noticed that in the example above, all variables have been created using typing hints. While this is somewhat interesting, you may also want to use the `type` argument as provided from the `attr` package, and `sanic-attrs` is absolutely fine with that. So, our `Game` class would rather looks like:

```python
class Game(doc.Model):
    name = doc.field(type=str, description="The name of the game")
    platform = doc.field(type=PlatformEnum, description="Which platform it runs on")
    score = doc.field(type=float, description="The average score of the game")
    resolution_tested = doc.field(type=str, description="The resolution which the game was tested")
    genre = doc.field(type=List[str], description="One or more genres this game is part of")
    genre_extra = doc.field(type=Sequence[str], description="One or more genres this game is part of")
    rating = doc.field(type=Dict[str, float], description="Ratings given on each country")
    rating_outside = doc.field(type=Mapping[str, float], description="Ratings given on each country")
    screenshots = doc.field(type=Set[bytes], description="Screenshots of the game")
    screenshots_extra = doc.field(type=Collection[bytes], description="Screenshots of the game")
    players = doc.field(type=Iterable[str], description="Some of the notorious players of this game")
    review_link = doc.field(type=Optional[str], description="The link of the game review (if exists)")
    junk = doc.field(type=Union[str, bytes], description="This should be strange")
    more_junk = doc.field(type=Any, description="The more junk field")
    language = doc.field(type=LanguageEnum, description="The language of the game")
    something = doc.field(type=List[Something], description="Something to go along the game")
    another = doc.field(type=AnotherSomething, description="Another something to go along the game")
```

### A note on a lot of features of `attrs`

There are a lot of features in `attrs` that can be handy while declaring a model, such as validators, factories and etc. For this release, some syntatic sugar is planned regarding validators (since most of the rules can be provided to `doc.field`). Other features, like `factories`, are not encourage at this time (or for the lifetime of this project, undecided) while declaring models since there wasn't enough time to actually test them (so far) :confused:

## On-the-fly input model parsing

There are a few surprises inside `sanic-attrs`. Let's say you have already declared your model, your endpoint and you still have to take the `request.json` and load it as your model? That doesn't seems right ... Fortunatelly, a small middleware was written to handle these cases :wink:

To enable on-the-fly input model parsing, all you need to do is add a `blueprint` to your Sanic app and access the object using the `input_obj` keyword directly from the request:

```python
from sanic_attrs import parser_blueprint

# ...

app.blueprint(parser_blueprint)

# ...

@app.post("/game", strict_slashes=True)
@doc.summary("Inserts the game data into the database")
@doc.response("200", "Game inserted successfuly", model=SuccessOutput)
@doc.response("403", "The user couldn't insert game to application", model=ErrorOutput)
@doc.consumes(Game, location="body", content_type="application/json")
@doc.produces(SuccessOutput)
async def insert_game(request):
    my_object = request["input_obj"]
    assert isinstance(my_object, Game)
    # your logic here
```

**Note**: there are no validations to deal with (really) broken data. If an exception occurs while populating your model, you will find that your `input_obj` keyword will be `None`, along with another key, `input_exc`, that will contain the exception given (if any). If you want to further customize this behavior so you won't need to check for `None` in every request, you can add your own `middleware` **after** adding the `parser_blueprint` to the `app` instance, like the following:

```python
from sanic.response import json
from sanic_attrs import parser_blueprint

# ...

app.blueprint(parser_blueprint)

# ...

@app.middleware("request")
async def check_if_input_is_none(request):
    if "input_obj" in request:
        if request["input_obj"] is None:
            # error handling here
            return json({"error": request["input_exc"].args[0]}, 500)
```

## On-the-fly output model serialization

To keep things simple, it is also possible to handle the direct return of `attrs` objects, instead of having to create a dictionary and then serialize or call `sanic.responses.json`, although this is exactly what's running under the hood:

```python
from sanic_attrs import response

# ...

@app.get("/game", strict_slashes=True)
@doc.summary("Gets the most played game in our database")
@doc.response("200", "Game data", model=Game)
@doc.response("403", "The user can't access this endpoint", model=ErrorOutput)
@doc.produces(Game)
async def get_game(request):
    game = Game(
        name="Cities: Skylines",
        platform="PC",
        score=9.0,
        resolution_tested="1920x1080",
        genre=["Simulators", "City Building"],
        rating={
            "IGN": 8.5,
            "Gamespot": 8.0,
            "Steam": 4.5
        },
        players=["Flux", "strictoaster"],
        language=1
    )
    return response.model(game)  # <--- the game instance, to be further serialized
```

**Note**: remember to create models that can have all its values serializable to JSON :+1:

### Configure everything else

```python
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Car API'
app.config.API_DESCRIPTION = 'Car API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'channelcat@gmail.com'
```

### Types not *yet* avaiable

These are the types not available from [`typing`](https://docs.python.org/3/library/typing.html) in the current version (with some notes so I can remember what to do later (if necessary)):

- `AbstractSet` - would be like set?
- `AnyStr` - this is mostly like Optional[str] or just str?
- `AsyncContextManager` - not a variable I think
- `AsyncGenerator` - not a variable I think
- `AsyncIterable` - not a variable I think
- `AsyncIterator` - not a variable I think
- `Awaitable` - not a variable I think
- `BinaryIO` - hmmm, I don't know ... Bytes maybe?
- `ByteString` - could be like bytes, for openapi is `{"type":"string", "format": "byte"}`
- `CT_co` - I don't even know what this is ...
- `Callable` - not a variable
- `CallableMeta` - not a variable
- `ChainMap` - not a variable (?)
- `ClassVar` - generic ...
- `Container` - generic
- `ContextManager` - not a variable
- `Coroutine` - not a variable
- `Counter` - not a variable
- `DefaultDict` - perhaps like dict?
- `Deque` - like List ?
- `Generator` - not a variable
- `Generic` - no way - or Any?
- `Hashable` - a hashmap?
- `IO` - hmmm, from docs: "Generic base class for TextIO and BinaryIO.", so ...
- `ItemsView` - what is an Item? it inherits from AbstractSet ... from docs: "A set is a finite, iterable container."
- `Iterator` - not a variable
- `KT` - generics
- `KeysView` - dict "readonly" ?
- `MappingView` - dict "readonly" ?
- `Match` - generic (I think)
- `MethodDescriptorType` - not a variable
- `MethodWrapperType` - not a variable
- `NamedTuple` - what to do here? NamedTuple is just an object with variables that can be *anything* I guess ...
- `NamedTupleMeta` - baseclass of NamedTuple
- `NewType` - not a variable / generic ?
- `NoReturn` - not a variable
- `Pattern` - generic
- `Reversible` - generic (Iterable)
- `Sized` - generic
- `SupportsAbs` - not a variable
- `SupportsBytes` - not a variable
- `SupportsComplex` - not a variable
- `SupportsFloat` - not a variable
- `SupportsInt` - not a variable
- `SupportsRound` - not a variable
- `T` - generic
- `TYPE_CHECKING` - ???
- `T_co` - ???
- `T_contra` - ???
- `Text` - returns a str object if created, so I'll stick with str or map it too?
- `TextIO` - buffer, like bytes ... map it?
- `Tuple` - well ... Tuple like lists or Tuple like Tuple[int, str, float] ?
- `TupleMeta` - baseclass of Tuple
- `Type` - generics
- `TypeVar` - generics
- `TypingMeta` - generics

If there's anything missing or required, please fill in a issue or contribute with a PR. PR's are most welcome :smiley:

## TODO

- [ ] Property deal with `required` fields (in OpenAPI `object` schema)
- [ ] Use type hinting to document the return of a function (as output schema / model)
- [ ] Provide JSON schemas?
- [ ] Be microservice-friendly (merging several endpoints definitions into one Swagger UI)
- [ ] Proper testing
- [ ] Increase use cases
- [ ] Find out if I can get the request model without calling the router
- [ ] Documentation

## License

MIT, the same as [`sanic-openapi`](https://github.com/channelcat/sanic-openapi/blob/ffe8a5c7443810f1dfe65ad7dd1991e776931dc1/LICENSE).
