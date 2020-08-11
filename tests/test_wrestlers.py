from wrestling.wrestlers import convert_to_title, Wrestler
from wrestling.base import Mark, YEARS


def test_convert_to_title():
    names = ['Nsnfk Afansjfsa', ' fs fasfsa ', 'NFASKJFAFA']
    for name in names:
        assert name.title().strip() == convert_to_title(name)


wrestler = Wrestler(name='Nick Anthony', team='Eagles', grade=Mark('Fr.'))

class TestWrestler:
    def test_grade(self):
        assert wrestler.grade in YEARS


