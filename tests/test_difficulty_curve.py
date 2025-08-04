import os
import sys
import builtins
import types

# Ensure modules import without user interaction or circular dependencies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
builtins.input = lambda: "1"
partner_stub = types.ModuleType("partner")
class _DummyPartner:
    pass
partner_stub.Partner = _DummyPartner
sys.modules['src.people.classes.partner'] = partner_stub

from src.people.classes.player import Player
from src.lifesim_lib.lifesim_lib import Gender

def test_difficulty_curve_scales_with_age():
    p = Player(first="Test", last="User", gender=Gender.Male)
    p.age = 0
    d0 = p.get_difficulty()
    p.age = 40
    d40 = p.get_difficulty()
    p.age = 80
    d80 = p.get_difficulty()
    assert d0 < d40 < d80

def test_event_chance_decreases_with_difficulty():
    p = Player(first="Test", last="User", gender=Gender.Male)
    base = 20
    p.age = 5
    young = p.get_event_chance(base)
    p.age = 80
    old = p.get_event_chance(base)
    assert old < young
