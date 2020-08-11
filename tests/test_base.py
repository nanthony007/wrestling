from wrestling.base import Result, Mark, CollegeLabel, HSLabel
import enum

def test_result():
    results_set = {
        "Loss Fall", "Loss Tech", "Loss Major", "Loss Dec",
        "Win Fall", "Win Tech", "Win Major", "Win Dec",
        "No Contest",
    }
    for result in Result:
        assert isinstance(result.value, int)
        assert result.text in results_set
        assert isinstance(result.win, bool)
        assert isinstance(result.bonus, bool)
        assert isinstance(result.pin, bool)
        assert isinstance(result.team_points, int)
        assert result.team_points in {0, 3, 4, 5, 6}


def test_mark():
    mark1 = Mark(12)
    mark2 = Mark('15')
    mark3 = Mark('hello')
    
    for mark in [mark1, mark2, mark3]:
        assert isinstance(mark.tag, (str, int))


def test_college_label():
    label = CollegeLabel('R01')
    assert isinstance(label.tag, (str, int))
    assert label.point_value in range(5)


def test_college_label():
    label = CollegeLabel('N3')
    assert isinstance(label.tag, (str, int))
    assert label.point_value in range(5)