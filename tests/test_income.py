import os
import sys
import random
import builtins
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

builtins.input = lambda: "1"

partner_stub = types.ModuleType("partner")
class _DummyPartner:
    pass
partner_stub.Partner = _DummyPartner
sys.modules['src.people.classes.partner'] = partner_stub

from src.people.classes.player import Player
from src.lifesim_lib.lifesim_lib import Gender, calculate_tax, round_stochastic


def test_player_income_respects_hours_and_tax():
    random.seed(1)
    p = Player(first="Test", last="User", gender=Gender.Male)
    p.age = 0
    p.salary = 52000
    p.has_job = True
    p.job_hours = 20
    p.money = 0
    p.years_worked = 0

    random.seed(2)
    p.random_events()

    random.seed(2)
    factor = random.uniform(0.4, 0.8)
    money = p.salary * p.job_hours / 40
    tax = calculate_tax(money)
    income = money - tax
    income *= factor
    expected = round_stochastic(income)
    assert p.money == expected
