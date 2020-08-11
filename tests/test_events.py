from wrestling.events import convert_event_name, Event
from wrestling.base import Mark

def test_convert_event_name():
    names = ['funtime', 'lost this one', 'wow', 'WA12A']
    for name in names:
        assert name.title().strip() == convert_event_name(name)


def test_event():
    event = Event(name='fun one here', kind=Mark('Dual Meet'))
    assert event.name
    assert event.kind in {'Tournament', 'Dual Meet'}