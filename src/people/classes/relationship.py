from random import randint

from src.lifesim_lib.lifesim_lib import clamp, Gender
from src.people.classes.person import Person
from src.lifesim_lib.translation import _


class Relationship(Person):
    """Base class for relationships."""

    def __init__(
        self, first, last, age, gender, happiness, health, smarts, looks, relationship
    ):
        super().__init__(first, last, age, gender, happiness, health, smarts, looks)
        self.relationship = relationship
        self.spent_time = False
        self.had_conversation = False
        self.was_complimented = False

    def is_male(self):
        """Return True if this relation is male."""
        return self.gender == Gender.Male

    def is_female(self):
        """Return True if this relation is female."""
        return self.gender == Gender.Female

    def change_relationship(self, amount):
        self.relationship = clamp(self.relationship + amount, 0, 100)

    def get_gender_word(self, wordmale, wordfemale):
        return wordmale if self.gender == Gender.Male else wordfemale

    def he_she(self):
        return self.get_gender_word(_("he"), _("she"))

    def his_her(self):
        return self.get_gender_word(_("his"), _("her"))

    def him_her(self):
        return self.get_gender_word(_("him"), _("her"))

    def hes_shes(self):
        return self.get_gender_word(_("he's"), _("she's"))

    def get_type(self):
        return "Unknown Relation"

    def name_accusative(self):
        return _("relationship")

    def age_up(self):
        super().age_up()
        self.change_relationship(randint(-4, 4))
        self.spent_time = False
        self.had_conversation = False
        self.was_complimented = False
