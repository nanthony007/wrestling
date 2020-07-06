# module for events classes


import attr
from attr.validators import in_, instance_of


def make_capital(x):
    return f"{' '.join(list(map(str.capitalize, x.split())))}"


@attr.s(kw_only=True, auto_attribs=True, slots=True)
class Event(object):
    id: str = attr.ib(validator=instance_of(str))
    name: str = attr.ib(converter=make_capital, validator=instance_of(str))
    type: str = attr.ib(validator=[instance_of(str), in_(("Tournament", "Dual"))])

    # can make more strict if want
    @id.validator
    def check_id(self, _, value):
        if len(value) < 10:
            raise ValueError("id value must be larger than 10")
