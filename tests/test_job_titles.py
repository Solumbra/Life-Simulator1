from src.people.classes.player import Player
from src.lifesim_lib.lifesim_lib import Gender

def test_get_job_sets_title_and_resets():
    p = Player(first="Test", last="User", gender=Gender.Male)
    p.get_job(50000, "Teacher")
    assert p.has_job
    assert p.salary == 50000
    assert p.job_title == "Teacher"
    p.lose_job()
    assert not p.has_job
    assert p.job_title is None
