from src.people.classes.player import Player


def test_exam_mini_game_success(monkeypatch):
    p = Player()
    p.grades = 50
    p.happiness = 50
    values = iter([2, 3, 2, 2])  # a, b, grade delta, happiness delta
    monkeypatch.setattr("src.people.classes.player.randint", lambda a, b: next(values))
    monkeypatch.setattr("builtins.input", lambda prompt='': "5")
    result = p.exam_mini_game()
    assert result is True
    assert p.grades == 52
    assert p.happiness == 52


def test_help_teacher_event(monkeypatch):
    p = Player()
    p.grades = 50
    p.happiness = 50
    p.school_reputation = 50
    p.skills["leadership"] = 0
    monkeypatch.setattr("src.people.classes.player.choice_input", lambda *args, **kwargs: 1)
    values = iter([3, 2, 1])  # reputation, happiness, skill gains
    monkeypatch.setattr("src.people.classes.player.randint", lambda a, b: next(values))
    p.school_random_events(forced_event="help_teacher")
    assert p.school_reputation == 53
    assert p.happiness == 52
    assert p.skills["leadership"] == 1
