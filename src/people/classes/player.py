import math, os, random, uuid, pickle
from random import randint, gauss

from src.lifesim_lib.const import *
from src.lifesim_lib.translation import _
from src.lifesim_lib.lifesim_lib import *
from src.lifesim_lib.goal import Goal
from src.people.classes.parent import Parent
from src.people.classes.person import Person
from src.people.classes.sibling import Sibling
from src.people.classes.partner import Partner
from src.people.classes.child import Child


class Player(Person):
	"""Base class for the player."""

	def __init__(self, first=None, last=None, gender=None):
		manual = first != None
		gender = gender or Gender.random()
		first = first or random_name(gender)
		last = last or random.choice(LAST_NAMES)
		happiness = randint(50, 100)
		health = randint(75, 100)
		smarts = randint(0, 50) + randint(0, 50)
		looks = randint(0, 65) + randint(0, 35)
		if manual and "belle" in first.lower(): #Congratulations, you discovered an easter egg!
			looks = 100
		super().__init__(first, last, 0, gender, happiness, health, smarts, looks)
		last1 = last2 = last
		if randint(1, 100) <= 40:
			newlast = random_last_name()
			if random.randint(1, 3) == 1:
				last2 = newlast  # Makes it more common to be named after the father's last name
			else:
				last1 = newlast
		self.parents = {
			"Mother": Parent(
				last1,
				min(randint(randint(18, 20), 50) for _ in range(3)),
				Gender.Female,
			),
			"Father": Parent(
				last2, min(randint(randint(18, 20), 68) for _ in range(3)), Gender.Male
			),
		}
		diff = self.parents["Father"].generosity - self.parents["Mother"].generosity
		if randint(1, 2) == 1:
			if diff > 0:
				self.parents["Mother"].generosity += randint(0, diff // 2)
			elif diff < 0:
				self.parents["Mother"].generosity -= randint(0, abs(diff) // 2)
		else:
			diff = -diff
			if diff > 0:
				self.parents["Father"].generosity += randint(0, diff // 2)
			elif diff < 0:
				self.parents["Father"].generosity -= randint(0, abs(diff) // 2)

		self.relations = [self.parents["Mother"], self.parents["Father"]]

		self.karma = randint(0, 25) + randint(0, 25) + randint(0, 25) + randint(0, 25)
		self.total_happiness = 0
		self.meditated = False
		self.worked_out = False
		self.money = 0
		self.depressed = False
		self.student_loan = 0
		self.chose_student_loan = False
		self.uv_years = 0
		self.reset_already_did()
		self.grades = None
		self.dropped_out = False
		self.times_meditated = 0
		self.salary = 0
		self.years_worked = 0
		self.has_job = False
		self.job_title = None
		self.lottery_jackpot = 0
		self.stress = 0
		self.performance = 0
		self.job_hours = 40
		self.date_options = 10
		self.times_visited_library = 0
		self.times_asked_since_last_raise = 0
		self.last_raise = 0
		self.partner = None
		self._recent_child_father = None  # Used if the player is female and got pregnant but then broke up with their partner
		self.traits = {}
		self.illnesses = []
		self.salary_years = []
		self.children = []
		self.skills = {
			"math": 0,
			"language": 0,
			"science": 0,
			"charisma": 0,
			"empathy": 0,
			"stamina": 0,
			"strength": 0,
			"creativity": 0,
			"academic": 0,
			"social": 0,
			"athletic": 0,
"leadership": 0,
}
		self.popularity = 50
		self.friendships = 0
		self.rivalries = 0
		self.romantic_interests = 0
		self.school_reputation = 50
		self.career_aspiration = None
		self.teacher_favor = 50
		self.parent_approval = 50
		self.college_prep = 0
		self.club = False
		# Track which club or sports team the player joined for more varied interactions
		self.club_name = None
		self.sports_team = False
		self.sports_team_name = None
		self.student_council = False
		self.part_time_job = False
		self.knowledge = 0
		self.attendance_years = 0
		self.achievements = set()
		self.energy = 100
		self.scholarship = False
		self.better_job = False
		self.special_event = False
		self.ID = str(uuid.uuid4())
		self.fertility = 0
		if self.gender == Gender.Female:
			self.fertility = randint(25, 100)
		self.is_pregnant = False
		self.save_path = SAVE_PATH + "/" + self.ID + ".pickle"
		self.generation = 1
		self.last_plastic_surgery = 0
		self.plastic_surgeons = [None, None]
		self.update_plastic_surgeon(0)
		self.update_plastic_surgeon(1)
		self.social_media = None
		self.goals = [
			Goal(
				_("Reach adulthood (age 18)"),
				lambda p: p.age >= 18,
				lambda p: f"{p.age}/18",
			),
			Goal(
				_("Get a job"),
				lambda p: p.has_job,
				lambda p: _("Employed") if p.has_job else _("Unemployed"),
			),
			Goal(
				_("Accumulate $100,000"),
				lambda p: p.money >= 100_000,
				lambda p: f"${p.money:,}/100,000",
			),
		]
		self.current_goal_index = 0

	def get_current_goal(self):
		if self.current_goal_index < len(self.goals):
			return self.goals[self.current_goal_index]
		return None

	def get_goal_description(self):
		goal = self.get_current_goal()
		if goal:
			return goal.description
		return _("All goals completed!")

	def get_goal_progress(self):
		goal = self.get_current_goal()
		if goal:
			prog = goal.progress(self)
			if prog is not None:
				return prog
		return ""

	def check_goals(self):
		while self.current_goal_index < len(self.goals):
			goal = self.goals[self.current_goal_index]
			if goal.is_complete(self):
				print(_("Goal complete: {goal}").format(goal=goal.description))
				self.current_goal_index += 1
				if self.current_goal_index < len(self.goals):
					next_goal = self.goals[self.current_goal_index].description
					print(_("New goal: {goal}").format(goal=next_goal))
			else:
				break

	def learn_trait(self, trait):
		if trait not in TRAITS_DICT:
			return False
		if self.has_trait(trait):
			return False
		conflicts = [
			t
			for t in self.traits.values()
			if (t.id != trait and t.conflicts_with(trait))
		]
		if conflicts:
			removal = random.choice(conflicts)
			color = None
			if removal.val > 0:
				color = "red"  # Losing a good trait is bad
			elif removal.val < 0:
				color = "green"  # Losing a bad trait is good
			print_colored(
				_("You lose the {trait!r} trait!").format(trait=removal.name), color
			)
			del self.traits[removal.id]
		else:
			data = ALL_TRAITS_DICT[trait]
			data.get_color()
			print_colored(
				_("You have gained the {trait} trait!").format(trait=data.name),
				data.get_color(),
			)
			self.traits[trait] = data
		return True
		
	def update_plastic_surgeon(self, index):
		name = random_last_name()
		reputation = randint(20, 60) + randint(0, 40)
		self.plastic_surgeons[index] = [name, reputation]

	def convert_child_to_player(self, c):  # This is here for when it's possible to continue as your child
		parent_name = self.name
		children = self.children[:]
		num = len(self.children)
		money = self.money
		gen = self.generation
		self.__init__()
		self.generation = gen + 1
		self.relations = []
		self.parents = {}
		if c.mother and type(c.mother) != Player:
			mother = Parent(c.mother.lastname, c.mother.age, Gender.Female)
			mother.health = c.mother.health
			mother.relationship = randint(90, 100) - randint(0, min(c.age, 50))
			self.relations.append(mother)
			self.parents["Mother"] = mother
		if c.father and type(c.father) != Player:
			father = Parent(c.father.lastname, c.father.age, Gender.Male)
			father.health = c.father.health
			father.relationship = randint(90, 100) - randint(0, min(c.age, 50))
			self.relations.append(father)
			self.parents["Father"] = father
		if children:
			for child in children:
				s = Sibling(
					child.lastname, child.age, child.gender, child.smarts, child.looks
				)
				s.change_relationship(round_stochastic(random.gauss(0, 8)))
				self.relations.append(s)
		if c.partner:
			self.partner = c.partner
			self.partner.change_relationship(randint(-10, 10))
			self.relations.append(c.partner)
		self.firstname = c.firstname
		self.lastname = c.lastname
		self.update_name()
		self.age = c.age
		self.gender = c.gender
		if self.gender == Gender.Female:
			self.fertility = randint(25, 100)
		self.total_happiness = c.total_happiness
		self.happiness = round_stochastic((c.relationship + c.happiness) / 2)
		self.health = c.health
		self.smarts = c.smarts
		self.looks = c.looks
		if self.age >= 6 and self.age < 17:
			self.calc_grades(randint(-10, 10))
		elif c.is_in_uv:
			self.chose_student_loan = True
			self.uv_years = c.is_in_uv
			self.calc_grades(randint(-5, 10))
		self.change_happiness(
			-randint(0, 50)
		)  # Lose some happiness as we just lost our parent
		if c.salary > 0:
			self.has_job = True
			self.salary = c.salary
			self.stress = randint(20, 50)
			if one_in(2):
				self.stress += randint(0, 25)
			self.performance = randint(40, 80)
			self.years_worked = c.years_worked
			self.salary_years = [c.salary]*c.years_worked
		self.money += c.money
		print(_("Your parent, {name}, passed away.").format(name=parent_name))
		if money > 0:
			amount = max(1, round_stochastic(money / num))
			print(_("They left behind cash assets of ${amount}.").format(amount=money))
			print(_("You inherited ${amount}.").format(amount=amount))
			self.money += amount

	def is_depressed(self):
		return "Depression" in self.illnesses

	def generate_child(self, other):
		if self.gender == Gender.Male:
			last = self.lastname
		else:
			last = other.lastname
		gender = Gender.random()
		smarts = random.gauss((self.smarts + other.smarts) / 2, 9)
		smarts = clamp(round_stochastic(smarts), 0, 100)
		looks = random.gauss((self.looks + other.looks) / 2, 7)
		looks = clamp(round_stochastic(looks), 0, 100)
		mother, father = (other, self) if self.gender == Gender.Male else (self, other)
		c = Child(random_name(gender), last, gender, smarts, looks, mother, father)
		return c

	def has_trait(self, name):
		return name in self.traits

	def was_attacked(self, damage, can_die=True):
		self.change_happiness(-damage)
		self.change_health(-damage)
		if damage >= 40:
			self.change_looks(-randint(0, (damage - 40) // 2))
		if can_die and self.health <= 0 and randint(1, 100) <= damage:
			self.die(_("You died after sustaining massive injuries in an assault."))

	def randomize_traits(self):
		self.traits.clear()
		if one_in(3):  # 1/3 chance of having no traits
			return
		trait_names = list(ALL_TRAITS_DICT.keys())
		total_traits = len(ALL_TRAITS)
		num_traits = 1
		while x_in_y(3, 8) and num_traits < randint(1, total_traits):
			num_traits += 1
		t = {}
		for i in range(num_traits):
			attempts = 50
			good = x_in_y(3, 5)
			allow_neutral = one_in(2)
			while attempts > 0:
				name = random.choice(trait_names)
				if name in t:
					attempts -= 1
					continue
				selected = ALL_TRAITS_DICT[name]
				if (selected.val == 0) ^ allow_neutral and (selected.val > 0) ^ good:
					attempts -= 1
					continue
				if not selected.roll_selection():
					continue
				if len(t) < 1 or not any(selected.conflicts_with(trait) for trait in t):
					break
				else:
					attempts -= 1
			if attempts > 0:
				t[name] = selected
		self.traits = t

	def after_trait_select(self):
		if self.has_trait("GRUMPY"):
			self.change_happiness(-12)

	def print_traits(self):
		if self.traits:
			print()
			print(_("You have the following traits:"))
			for name in self.traits:
				trait = self.traits[name]
				print_colored(f"{trait.name}: {trait.desc}", trait.get_color())

	@classmethod
	def load(cls, d):
		p = cls()
		p.__dict__.update(d)
		return p

	def change_happiness(self, amount):
		if amount != 0:
			if self.has_trait("MOODY"):
				amount = round_stochastic(amount * 1.5)
			elif self.has_trait("NON_EMOTIONAL"):
				amount = round_stochastic(amount / 2)
		super().change_happiness(amount)

	def change_jackpot(self):
		self.lottery_jackpot = round(randexpo(100000, 1000000))

	def save_game(self):
		if not os.path.exists(self.save_path):
			open(self.save_path, "x")
		data = self.__dict__.copy()
		data.pop("goals", None)
		pickle.dump(data, open(self.save_path, "wb"))

	def delete_save(self):
		if os.path.exists(self.save_path):
			os.remove(self.save_path)

	def is_in_school(self):
		return self.grades is not None

	def get_school_stage(self):
		if self.uv_years > 0:
			return "university"
		if not self.is_in_school():
			return None
		if self.age < 12:
			return "primary"
		if self.age < 14:
			return "middle"
		return "high"

	def change_skill(self, skill, amount):
		skill_map = {
			"academic": ["math", "language", "science"],
			"social": ["charisma", "empathy"],
			"athletic": ["stamina", "strength"],
			"leadership": ["charisma", "creativity"],
		}
		targets = skill_map.get(skill, [])
		if skill in self.skills:
			self.skills[skill] = clamp(self.skills[skill] + amount, 0, 100)
		for s in targets:
			if s in self.skills:
				self.skills[s] = clamp(self.skills[s] + amount, 0, 100)
	def add_illness(self, illness):
		if illness not in self.illnesses:
			self.illnesses.append(illness)

	def remove_illness(self, illness):
		if illness in self.illnesses:
			self.illnesses.remove(illness)

	def change_grades(self, amount):
		if self.is_in_school():
			self.grades = clamp(self.grades + amount, 0, 100)
			self.check_school_achievements()

	def change_karma(self, amount):
		self.karma = clamp(self.karma + amount, 0, 100)

	def change_school_reputation(self, amount):
		self.school_reputation = clamp(self.school_reputation + amount, 0, 100)

	def change_popularity(self, amount):
		self.popularity = clamp(self.popularity + amount, 0, 100)
		self.check_school_achievements()

	def change_teacher_favor(self, amount):
		self.teacher_favor = clamp(self.teacher_favor + amount, 0, 100)

	def change_parent_approval(self, amount):
		self.parent_approval = clamp(self.parent_approval + amount, 0, 100)

	def change_knowledge(self, amount):
		prev = self.knowledge
		self.knowledge = clamp(self.knowledge + amount, 0, 100)
		for m in (25, 50, 75, 100):
			if prev < m <= self.knowledge:
			        print(_("You reached a knowledge milestone of {m}!" ).format(m=m))

	def change_energy(self, amount):
		self.energy = clamp(self.energy + amount, 0, 100)

	def check_school_achievements(self):
		if self.attendance_years >= 5 and "Perfect Attendance" not in self.achievements:
			self.achievements.add("Perfect Attendance")
			self.special_event = True
			print(_("Achievement unlocked: Perfect Attendance"))
			print(_("You have been invited to a special school event!"))
		if self.grades is not None and self.grades >= 90 and "Honor Student" not in self.achievements:
			self.achievements.add("Honor Student")
			self.scholarship = True
			print(_("Achievement unlocked: Honor Student"))
			print(_("Scholarship opportunities are now available."))
		if self.popularity >= 90 and "School Celebrity" not in self.achievements:
			self.achievements.add("School Celebrity")
			self.better_job = True
			print(_("Achievement unlocked: School Celebrity"))
			print(_("Better part-time job opportunities unlocked."))

	def get_traits_str(self):
		return ", ".join(
			map(lambda t: get_colored(t.name, t.get_color()), self.traits.values())
		)

	def reset_already_did(self):
		self.meditated = False
		self.worked_out = False
		self.visited_library = False
		self.studied = False
		self.tried_to_drop_out = False
		self.played = False
		self.did_arts_and_crafts = False
		self.worked_harder = False
		self.listened_to_music = False
		self.asked_for_raise = False
		self.skipped_school = False
		w = abs(gauss(0, 16))
		if x_in_y(2, 3):
			w = -w
		else:
			w /= 3
		self.witch_doctor_health = w
		self.date_options = randint(9, 11)
		self.energy = 100
		
	def process_relation_death(self, relation, reason=None):
		if relation not in self.relations:
			return
		if reason is None:
			reason = _("died of old age")
		rel_str = relation.name_accusative()
		he_she = relation.he_she().capitalize()
		print(
			_(
				"Your {relative} died at the age of {age}.\n{he_she} {reason}."
			).format(relative=rel_str, age=relation.age, he_she=he_she, reason=reason)
		)
		inheritance = 0
		happy_remove = randint(40, 55)
		if isinstance(relation, Parent):
			if x_in_y(70, 100) and x_in_y(relation.generosity, 100):
				avg = 100000 * (relation.money / 100) ** 2
				lo = max(avg * relation.generosity / 200, 1)
				inheritance = round_stochastic(randexpo(lo, avg))
			del self.parents[relation.get_type()]
		elif isinstance(relation, Sibling):
			happy_remove = randint(25, 40)
		elif isinstance(relation, Partner):
			happy_remove = randint(65, 100)
			for c in self.children:
				if relation is c.father:
					c.father = None
				elif relation is c.mother:
					c.mother = None
			self.partner = None
		elif isinstance(relation, Child):
			happy_remove = randint(75, 100)
			self.children.remove(relation)
		self.change_happiness(-happy_remove)
		if yes_no(_("Would you like to attend the funeral?")):
			self.change_happiness(randint(3, 5))
			self.change_karma(randint(3, 5))
		else:
			self.change_karma(-randint(2, 5))
		if self.has_trait("THANATOPHOBIA"):
			self.change_happiness(-randint(30, 45))
			self.change_stress(randint(5, 10))
			display_event(_("You feel intense panic as the death of your loved one reminds you of how much you are afraid of death."))
		self.relations.remove(relation)
		if inheritance > 0:
			display_event(
				_("You inherited ${amount}").format(amount=inheritance)
			)
			self.money += inheritance
			self.change_happiness(
				round_stochastic(1.5 * math.log10(inheritance))
			)

	def age_up(self):
		oldhappy = self.happiness
		self.total_happiness += self.happiness
		super().age_up()
		if self.age >= 6:
			if self.has_trait("WELL_KEPT"): 
				self.change_looks(randint(0, 2))
			elif self.has_trait("BADLY_KEPT"):
				self.change_looks(-randint(0, 3))
		if self.has_trait("SICKLY"):
			self.change_health(-randint(0, 4))
		if self.has_trait("MOODY") and not self.is_depressed():
			self.change_happiness(randint(-6, 6))
		if self.has_trait("GRUMPY") and self.happiness > 33:
			if randint(1, 10) == 1:
				self.change_happiness(-randint(5, 8))
			else:
				self.change_happiness(-randint(1, 5))
		if self.has_trait("FAST_WORKER"):
			self.change_performance(randint(0, 3))
		elif self.has_trait("SLOW_WORKER"):
			self.change_performance(-randint(0, 3))
		if self.has_trait("LAZY"):
			self.change_performance(-randint(0, 5))
			self.change_stress(-randint(0, 4))
		if self.is_in_school():
			if not self.skipped_school:
			        self.attendance_years += 1
			self.check_school_achievements()
		self.reset_already_did()
		self.change_karma(randint(-2, 2))
		for i in range(2):
			if one_in(35):
				self.update_plastic_surgeon(i)
		for relation in self.relations:
			relation.age_up()
			if isinstance(relation, Parent):
				if self.age < 18:
					relation.change_relationship(1)
				else:
					relation.change_relationship(random.choice((-1, -1, 0)))

		print(_("Age {age}").format(age=self.age))
		if self.death_check():
			self.die(_("You died of old age."))
			return
		self.change_jackpot()
		if self.has_job:
			self.change_stress(randint(-4, 4))
			base = 60 - self.happiness * 0.3 + (self.job_hours - 40)
			base += 4 * math.sqrt(sum(1 for c in self.children if c.age < 18))
			base = clamp(base, 0, 100)
			if self.has_trait("MEDITATOR"):
				base *= 2/3
			diff = base - self.stress
			if diff > 0:
				self.change_stress(randint(0, round_stochastic(diff / 6)))
			elif diff < 0:
				factor = self.happiness / 25 + 0.5
				if self.has_trait("MEDITATOR"):
					factor += 0.5
				self.change_stress(
					-randint(0, round_stochastic(abs(diff) / 9 * factor))
				)

		if self.gender == Gender.Female:
			if self.is_pregnant:
				self.is_pregnant = False
				if not x_in_y(self.fertility, 150) and one_in(5):
					display_event(_("You suffered a miscarriage and lost the baby!"))
					self.change_happiness(-randint(30, 50))
				else:
					c = self.generate_child(self._recent_child_father)
					self._recent_child_father = None
					typ = c.get_translated_type().lower()
					print(_("You just had a baby {son_daughter}!").format(son_daughter=typ))
					him_her = c.him_her()
					while True:
						print(
							_(
								"What will you name {him_her}? (or leave blank for a random name)"
							).format(him_her=him_her)
						)
						name = input()
						if name == "":
							break
						elif len(name.strip()) > 0:
							c.firstname = name.strip()
							c.update_name()
							break
					self.change_happiness(randint(35, 50))
					self.change_stress(randint(0, 10))
					self.relations.append(c)
					self.children.append(c)
					if self.partner:
						self.partner.change_relationship(randint(3, 10))
					print(
						_(
							"You are the mother of a baby {son_daughter} named {name}."
						).format(son_daughter=typ, name=c.name)
					)
		elif self.partner and self.partner.is_pregnant:
			c = self.generate_child(self.partner)
			typ = c.get_translated_type().lower()
			self.partner.is_pregnant = False
			if not x_in_y(self.partner.fertility, 100) and one_in(5):
				display_event(_("Your {partner} suffered a miscarriage and lost the baby!").format(
					partner=self.partner.name_accusative()
				))
				self.change_happiness(-randint(30, 50))
			else:
				print(
					_("Your {partner} just had a baby {son_daughter}!").format(
						partner=self.partner.name_accusative(), son_daughter=typ
					)
				)
				him_her = c.him_her()
				while True:
					print(
						_(
							"What will you name {him_her}? (or leave blank for a random name)"
						).format(him_her=him_her)
					)
					name = input()
					if name == "":
						break
					elif len(name.strip()) > 0:
						c.firstname = name.strip()
						c.update_name()
						break
				self.change_happiness(randint(35, 50))
				self.change_stress(randint(0, 10))
				self.relations.append(c)
				self.children.append(c)
				self.partner.change_relationship(randint(8, 15))
				print(
					_("You are the father of a baby {son_daughter} named {name}.").format(
						son_daughter=typ, name=c.name
					)
				)
				display_bar(_("Smarts"), c.smarts)
				display_bar(_("Looks"), c.looks)
		if self.happiness < randint(1, 10) and not self.is_depressed():
			if not self.has_trait("NON_EMOTIONAL") or one_in(2):
				display_event(_("You are suffering from depression."))
				self.add_illness(TranslateMarker("Depression"))
				self.change_happiness(-50)
				self.change_health(-randint(4, 8))
		for relation in self.relations[:]:
			sudden_death = relation.age >= 6 and one_in(1400)
			if sudden_death or relation.death_check():
				reason = None
				if sudden_death:
					sudden_death_reasons = RELATION_SUDDEN_DEATH_REASONS[:]
					if relation.age >= 16:
						sudden_death_reasons.append(_("died after driving off a cliff while texting and driving"))
					reason = random.choice(sudden_death_reasons)
					if one_in(1000):
						reason = _("starved to death after playing this game for too many days without stopping to eat")
				self.process_relation_death(relation, reason)
				
		if self.age >= randint(12, 17) and self.has_trait("THANATOPHOBIA"):
			if one_in(10):
				thanatophobe_msgs = [
					_("You begin to worry that one day you may not be here anymore."),
					_("You begin to panic at the thought of dying."),
					_("You are afraid of dying. You feel your heart beat quickly."),
					_("You feel extremely anxious at the thought of one day not being here anyone."),
					_("You're afraid to die. You feel you must stay out of any situations that involve dying."),
					_("The thought of dying makes your heart race and you feel anxious."),
					_("You find it hard to sleep at night, afraid of even the thought of dying."),
					_("You don't even want to THINK about dying.")
				]
				self.change_happiness(-randint(4, 6))
				self.change_stress(randint(3, 8))
				self.change_health(-1)
				print(random.choice(thanatophobe_msgs))
		
		self.random_events()
		if self.partner:
			assert self.partner in self.relations
		if self.has_job:
			self.salary_years.append(self.salary)
			happy_change = (
				self.happiness - oldhappy
			)  # Large decreases in happiness can increase stress
			if happy_change > 0:
				diff = max(happy_change - 5, 0)
				diff /= 2
			else:
				diff = min(happy_change + 5, 0)
			diff = -round_stochastic(diff / 4)
			self.change_stress(diff)
			self.change_performance(
				randint(-4, 4) + round_stochastic((50 - self.stress) / 20)
			)
			if self.can_retire() and one_in(3):
				pension = self.calc_pension()
				if self.age >= 70 and one_in(3):
					display_event(_("You have been forced to retire from your position."))
					self.lose_job()
					print(_("You are now receiving a yearly pension of ${pension:,}.").format(pension=pension))
					self.salary = pension
					self.change_happiness(randint(12, 25))
				else:
					print(_("You are eligible to retire and begin receiving a yearly pension of ${pension:,}.").format(pension=pension))
					if yes_no(_("Would you like to retire?")):
						print(_("You retired and are now receiving pension."))
						self.lose_job()
						self.salary = pension
						self.change_happiness(randint(25, 50))
			elif self.performance < 15 and randint(1, self.performance + 1) == 1:
				display_event(
					_("You have been fired from your job.\nReason: Performance")
				)
				if DEBUG:
					print(
						_("Your performance was {perf}%").format(perf=self.performance)
					)
				self.lose_job()
				self.change_happiness(-randint(20, 35))
			if self.stress > 65:
				amount = randint(0, round_stochastic((self.stress - 65) / 5))
				self.change_happiness(-amount)
				critical_stress = self.stress > 85
				if critical_stress:
					self.change_health(round_stochastic((self.stress - 80) / 4))
				if amount > 0 and randint(1, 5 - critical_stress) == 1:
					if critical_stress:
						print(
							_(
								"You feel like you're on the verge of burnout from so much work!"
							)
						)
					else:
						print(_("You're feeling stressed out from all of this work."))
				if critical_stress and "High Blood Pressure" not in self.illnesses and one_in(7):
					display_event(_("You are suffering from high blood pressure."))
					self.change_health(-randint(4, 8))
					self.add_illness(TranslateMarker("High Blood Pressure"))

	def get_job(self, salary, title=None):
		if not self.has_job:
			self.has_job = True
			self.salary = salary
			self.job_title = title
			self.years_worked = 0
			self.stress = 45
			self.performance = 50
			self.job_hours = 40
			self.last_raise = self.age
			self.times_asked_since_last_raise = 0
			self.salary_years = []

	def lose_job(self):
		if self.has_job:
			self.has_job = False
			self.salary = 0
			self.job_title = None
			self.years_worked = 0
			self.stress = 0
			self.performance = 0
			self.job_hours = 0
			self.salary_years = []
	def change_stress(self, amount):
		if self.has_job:
			self.stress = clamp(self.stress + amount, 0, 100)

	def change_performance(self, amount):
		if self.has_job:
			self.performance = clamp(self.performance + amount, 0, 100)

	def calc_grades(self, offset):
		self.grades = clamp(round(10 * math.sqrt(self.smarts + offset)), 0, 100)

	def get_gender_str(self):
		return _("Male") if self.gender == Gender.Male else _("Female")

	def die(self, message):
		print(message)
		if self.age == 0:
			score = self.happiness
		else:
			avg_happy = round(self.total_happiness / self.age)
			score = self.happiness * 0.3 + avg_happy * 0.7
		print_align_bars((_("Lifetime Happiness"), score), (_("Karma"), self.karma))
		self.delete_save()
		press_enter()
		raise PlayerDied

	def display_stats(self):
		if self.happiness >= 60:
			if self.happiness >= 85:
				symbol = ":D"
			else:
				symbol = ":)"
		elif self.happiness < 40:
			if self.happiness < 15:
				symbol = ":'("
			else:
				symbol = ":("
		else:
			symbol = ":|"

		if self.looks < 15:
			looks_symbol = "🌧"
		elif self.looks < 30:
			looks_symbol = "☁"
		elif self.looks < 43:
			looks_symbol = "🌥"
		elif self.looks < 55:
			looks_symbol = "⛅"
		elif self.looks < 65:
			looks_symbol = "🌤"
		elif self.looks < 85:
			looks_symbol = "☀️"
		else:
			looks_symbol = "🔥"
		print_align_bars(
			(_("Happiness"), self.happiness, symbol),
			(_("Health"), self.health, "</3" if self.health < 20 else "<3"),
			(_("Smarts"), self.smarts),
			(_("Looks"), self.looks, looks_symbol),
			(_("Popularity"), self.popularity),
			(_("Energy"), self.energy),
			(_("Stress"), self.stress),
			show_percent=True,
		)

	def can_retire(self):
		return self.years_worked >= 10 and self.age >= 65
	
	def calc_pension(self):
		from statistics import mean
		amount = mean(sorted(self.salary_years, reverse=True)[:5])
		return round(amount * min(self.years_worked, 35) * 0.02) 
	
	@property
	def marital_status(self):
		if not self.partner:
			return 0
		return self.partner.status + 1

	def lose_partner(self):
		if self.partner in self.relations:
			self.relations.remove(self.partner)
		self.partner = None

	def divorce(self):
		amount = round(self.money * random.uniform(0.4, 0.6))
		if amount > 0:
			self.change_happiness(-randint(10, 15))
			display_event(
				_(
					"The judge has ordered you to pay {name} ${amount} to settle your divorce."
				).format(name=self.partner.name, amount=amount)
			)
			self.money -= amount
		self.lose_partner()

	def update_hours(self, hours):
		prev = self.job_hours
		self.job_hours = hours
		self.change_stress(round((self.job_hours - prev) * 0.75))

	def calculate_yearly_income(self, factor=None):
		"""Compute the amount of money earned from work this year.

		The calculation takes the player's salary, adjusts it based on the
		number of hours worked, subtracts taxes and finally applies a
		random expense factor.  The result is rounded stochastically to
		better simulate real world rounding.

		Parameters
		----------
		factor: float, optional
			Expense factor to apply to the post-tax salary.  If not
			provided a random value between 0.4 and 0.8 will be
			generated.

		Returns
		-------
		int
			The final rounded income for the year.
		"""
		money = self.salary * self.job_hours / 40
		tax = calculate_tax(money)
		income = money - tax
		if factor is None:
			factor = random.uniform(0.4, 0.8)
		income *= factor
		return round_stochastic(income)
	def get_difficulty(self):
		"""Return a difficulty modifier based on the player's age.

		The modifier follows a gentle logistic growth curve so that
		difficulty ramps up steadily without sudden spikes. Young
		players start close to 1.0 and it approaches 3.0 in later
		life, ensuring a balanced experience.
		"""
		return 1 + 2 / (1 + math.exp(-(self.age - 40) / 20))

	def get_event_chance(self, base):
		"""Scale a base ``one_in`` chance using the current difficulty.

		A higher difficulty lowers the returned denominator which in
		turn increases the frequency of the event associated with the
		chance. The value is clamped to at least 1 to avoid division
		by zero or negative probabilities.
		"""
		return max(1, round(base / self.get_difficulty()))

	def exam_mini_game(self):
		a = randint(1, 12)
		b = randint(1, 12)
		print(_("Exam time! What is {a} + {b}?" ).format(a=a, b=b))
		try:
			ans = int(input("> "))
		except ValueError:
			ans = None
		if ans == a + b:
			print(_("You passed the exam."))
			self.change_grades(randint(2, 4))
			self.change_happiness(randint(1, 3))
			return True
		else:
			print(_("You failed the exam."))
			self.change_grades(-randint(2, 4))
			self.change_happiness(-randint(1, 3))
			return False

	def school_random_events(self, forced_event=None):
		stage = self.get_school_stage()
		if not stage:
			return
		if forced_event is None:
			if not one_in(self.get_event_chance(6)):
				return
			event = random.choice(
				[
					"class_trip",
					"science_fair",
					"teacher_strike",
					"school_competition",
					"cheat_test",
					"report_cheating",
					"help_teacher",
				]
			)
		else:
			event = forced_event

		if event == "class_trip":
			cost = randint(50, 200)
			print(
				_(
					"Your class is going on a trip that costs ${cost}. Do you want to go?"
				).format(cost=cost)
			)
			choice = choice_input(_("Join the trip"), _("Stay home"))
			if choice == 1:
				if self.money >= cost:
					self.money -= cost
					self.change_happiness(randint(3, 6))
					self.change_school_reputation(randint(1, 3))
				else:
					print(_("You can't afford to go."))
		elif event == "science_fair":
			print(_("Your school is hosting a science fair. Do you want to enter?"))
			choice = choice_input(_("Enter"), _("Skip"))
			if choice == 1:
				success = self.smarts + randint(-20, 20) > 60
				if success:
					print(_("Your project was a hit!"))
					self.change_smarts(randint(1, 3))
					self.change_school_reputation(randint(2, 5))
				else:
					print(_("Your project failed to impress."))
					self.change_happiness(-randint(1, 3))
		elif event == "teacher_strike":
			print(_("Teachers are on strike. School is closed for a week."))
			self.change_happiness(randint(1, 3))
			self.change_grades(-randint(1, 3))
		elif event == "school_competition":
			comp = random.choice(["sports", "quiz"])
			print(
				_(
					"Your school is holding a {comp} competition. Do you take part?"
				).format(comp=comp)
			)
			choice = choice_input(_("Participate"), _("Skip"))
			if choice == 1:
				skill = "athletic" if comp == "sports" else "academic"
				success = self.skills[skill] + randint(0, 50) > 60
				if success:
					print(_("You won the competition!"))
					self.change_school_reputation(randint(2, 5))
					self.change_happiness(randint(2, 5))
					self.change_skill(skill, randint(1, 3))
				else:
					print(_("You lost the competition."))
					self.change_happiness(-randint(1, 3))
		elif event == "cheat_test":
			print(_("You have an important test coming up. Do you cheat?"))
			choice = choice_input(_("Cheat"), _("Take test honestly"))
			if choice == 1:
				if one_in(3):
					print(_("You were caught cheating!"))
					self.change_grades(-randint(5, 10))
					self.change_school_reputation(-randint(5, 10))
					self.change_karma(-randint(5, 10))
				else:
					print(_("You cheated and got away with it."))
					self.change_grades(randint(1, 3))
					self.change_school_reputation(-randint(1, 3))
					self.change_karma(-randint(2, 4))
			else:
				self.exam_mini_game()
		elif event == "report_cheating":
			print(_("You notice a classmate cheating on an exam. What do you do?"))
			choice = choice_input(
				_("Report to the teacher"), _("Ignore it")
			)
			if choice == 1:
				self.change_school_reputation(randint(2, 5))
				self.change_karma(randint(2, 5))
			else:
				print(_("You decided not to get involved."))
		elif event == "help_teacher":
			print(_("A teacher asks you to help organize supplies after class."))
			choice = choice_input(_("Help"), _("Decline"))
			if choice == 1:
				self.change_school_reputation(randint(2, 4))
				self.change_happiness(randint(1, 3))
				self.change_skill("leadership", randint(1, 2))
			else:
				self.change_school_reputation(-randint(1, 3))

	def random_events(self):
		if self.is_in_school():
			self.school_random_events()
		if self.age >= 5 and one_in(self.get_event_chance(5000)):
			print(_("You were struck by lightning!"))
			good_or_bad = one_in(2)
			if good_or_bad:
				self.change_happiness(100)
				self.change_health(100)
				self.change_smarts(100)
				self.change_looks(100)
			else:
				self.change_happiness(-100)
				self.change_health(-100)
				self.change_smarts(-100)
				self.change_looks(-100)
			self.display_stats()
			press_enter()
			if not good_or_bad and one_in(5):
				self.die(_("You died after being struck by lightning."))
		if self.has_job:
			self.years_worked += 1
		if self.salary > 0:
			self.money += self.calculate_yearly_income()
		if self.uv_years > 0:
			self.uv_years -= 1
			if self.uv_years == 0:
				self.grades = None
				display_event(_("You graduated from university."))
				self.change_happiness(randint(14, 20))
				self.change_smarts(randint(10, 15))
				if self.chose_student_loan:
					self.student_loan = randint(20000, 40000)
					print(_("You now have to start paying back your student loan"))
			else:
				if self.grades < randint(10, 45):
					display_event(
						_("You were expelled from university after earning bad grades.")
					)
					self.change_happiness(-randint(30, 50))
		if self.student_loan > 0:
			amount = min(randint(1000, 3000) for _ in range(3))
			amount = min(amount, self.student_loan)
			self.money -= amount
			self.student_loan -= amount
			if self.student_loan == 0:
				print(_("You've fully paid off your student loan"))
		for illness in self.illnesses[:]:
			if illness == "Depression":
				if self.happiness >= randint(20, 35):
					display_event(_("You are no longer suffering from depression"))
					self.change_happiness((100 - self.happiness) // 2)
					self.change_health(randint(4, 8))
					self.remove_illness("Depression")
				else:
					self.change_happiness(-randint(1, 2))
					self.change_health(-randint(1, 4))
			elif illness == "High Blood Pressure":
				self.change_health(-randint(1, 5))
				if self.stress > randint(80, 95) and self.health < randint(1, 15):
					if randint(1, 3) == 1:
						self.die(_("You died due to a massive heart attack."))
				elif self.stress < randint(25, 60) and one_in(2):
					display_event(
						_("You are no longer suffering from high blood pressure")
					)
					self.change_happiness(randint(4, 8))
					self.change_health(randint(4, 8))
					self.remove_illness("High Blood Pressure")
			elif illness == "Cancer":
				self.change_happiness(-randint(5, 9))
				self.change_health(-randint(10, 18))
				if self.health <= 0:
					self.die(_("You died due to complications associated with cancer."))
			elif illness in ["Common Cold", "Flu"]:
				self.remove_illness(illness)
		if self.age >= 4 and one_in(self.get_event_chance(2000)):
			display_event(_("You have been diagnosed with cancer."))
			self.add_illness(TranslateMarker("Cancer"))
			self.change_health(-randint(16, 50))
			self.change_happiness(-randint(30, 50))
		elif one_in(self.get_event_chance(20)):
			if self.age >= 3 and one_in(self.get_event_chance(6)):
				display_event(_("You are suffering from the flu."))
				self.add_illness(TranslateMarker("Flu"))
				self.change_health(-randint(2, 5))
				self.change_happiness(-randint(3, 5))
			else:
				display_event(_("You are suffering from the common cold."))
				self.add_illness(TranslateMarker("Common Cold"))
				self.change_health(-randint(1, 4))
				self.change_happiness(-randint(2, 4))
		if self.age == 2 and one_in(2):
			print(
				_("Your mother is taking to to the doctor's office to get vaccinated.")
			)
			print(_("How will you behave?"))
			choices = [
				_("Try to stay calm"), 
				_("Throw a conniption fit") if one_in(4) else _("Throw a tantrum"), 
				_("Bite her")
			]
			choice = choice_input(*choices)
			clear_screen()
			if choice == 1:
				print(_("You remained calm"))
			elif choice == 2:
				self.change_happiness(-randint(25, 35))
				self.parents["Mother"].change_relationship(-randint(6, 10))
				print(_("You threw a tantrum"))
			elif choice == 3:
				self.change_happiness(-randint(6, 10))
				self.parents["Mother"].change_relationship(-randint(25, 35))
				print(_("You bit your mother"))
		if self.is_in_school():
			self.change_grades(randint(-3, 3))
			base = round(10 * math.sqrt(self.smarts))
			if self.grades < base - 2:
				self.change_grades(randint(1, 3))
			elif self.grades > base + 2:
				self.change_grades(-randint(1, 3))
			grade_delta = (self.happiness - 50) / 10
			if grade_delta > 0:
				grade_delta /= 2
			self.change_grades(round_stochastic(grade_delta))
		if self.part_time_job and self.is_in_school():
			self.change_grades(-randint(1, 3))
			self.money += randint(500, 1500)
		if self.has_trait("GENIUS"):
			if self.age < randint(18, 25):
				self.change_smarts(randint(0, 9))
			else:
				self.change_smarts(randint(0, 4))
		if self.age == 6:
			print(_("You are starting elementary school"))
			self.change_smarts(randint(1, 2) + 2 * self.has_trait("GENIUS"))
			self.calc_grades(randint(4, 8))
		if self.age == 12:
			print(_("You are starting middle school"))
			self.change_smarts(randint(1, 3) + 3 * self.has_trait("GENIUS"))
			self.calc_grades(randint(0, 8))
		if self.age == 14:
			print(_("You are starting high school"))
			self.change_smarts(randint(1, 4) + 4 * self.has_trait("GENIUS"))
			self.calc_grades(randint(-8, 8))
		if 1 <= self.marital_status <= 2:
			if self.partner.relationship < randint(25, 35) and one_in(3):
				name = self.partner.name_accusative()
				print(
					_("Your {partner} wants to break up with you.").format(partner=name)
				)
				print(_("What will you do?"))
				him_her = self.partner.him_her()
				choice = choice_input(
					_("Wish {him_her} well").format(him_her=him_her),
					_("Beg {him_her} to stay").format(him_her=him_her),
					_("Insult {him_her} one last time").format(him_her=him_her),
				)
				self.change_happiness(-randint(15, 18))
				if choice == 1:
					print(
						_("You wished {name} the best").format(name=self.partner.name)
					)
					self.lose_partner()
				elif choice == 2:
					print(
						_("You begged {name} to stay with you.").format(
							name=self.partner.name
						)
					)
					he_she = self.partner.he_she().capitalize()
					if x_in_y(self.partner.willpower, 100):
						display_event(
							_("{he_she} dumped you anyway.").format(he_she=he_she)
						)
						self.lose_partner()
						self.change_happiness(-randint(10, 20))
					else:
						display_event(
							_("{he_she} decided to stay with you.").format(
								he_she=he_she
							)
						)
				elif choice == 3:
					self.change_karma(-4)
					he_she = self.partner.he_she()
					insult = random.choice(INSULTS)
					print(_("{name} broke up with you.").format(name=self.partner.name))
					print(
						_(
							"You called {him_her} {insult} as {he_she} was walking out the door."
						).format(him_her=him_her, insult=insult, he_she=he_she)
					)
					self.lose_partner()
		elif self.marital_status == 3:
			if self.partner.relationship <= randint(15, 30) and one_in(self.get_event_chance(6)):
				name = self.partner.name_accusative()
				print(_("Your {partner} wants a divorce.").format(partner=name))
				print(_("What will you do?"))
				him_her = self.partner.him_her()
				choices = choice_input(
					_("Wish {him_her} well").format(him_her=him_her),
					_("Beg {him_her} to stay").format(him_her=him_her),
					_("Insult {him_her} one last time").format(him_her=him_her),
				)
				self.change_happiness(-randint(15, 18))
				if choice == 1:
					print(
						_("You honored {name}'s request for a divorce.").format(
							name=self.parter.name
						)
					)
					self.divorce()
				elif choice == 2:
					print(
						_("You begged {name} to stay with you.").format(
							name=self.partner.name
						)
					)
					he_she = self.partner.he_she().capitalize()
					if x_in_y(self.partner.willpower, 100) or x_in_y(self.partner.willpower, 100):
						display_event(
							_("{he_she} insisted on getting a divorce.").format(
								he_she=he_she
							)
						)
					else:
						print(
							_("{he_she} decided to stay with you.").format(
								he_she=he_she
							)
						)
						self.change_happiness(-randint(15, 22))
						self.divorce()
				elif choice == 3:
					self.change_karma(-4)
					he_she = self.partner.he_she()
					insult = random.choice(INSULTS)
					print(_("{name} divorced you.").format(name=self.partner.name))
					print(
						_(
							"You called {him_her} {insult} as {he_she} was walking out the door."
						).format(him_her=him_her, insult=insult, he_she=he_she)
					)
					self.divorce()
		if self.partner and self.money >= 1000000 and not x_in_y(self.karma, 130) and one_in(250):
			rel = self.partner.name_accusative()
			ransom = round(self.money * random.uniform(0.2, 0.8))
			print(_("Your {partner} has been kidnapped and is being held for ${ransom} ransom!").format(partner=rel, ransom=ransom))
			print(_("The kidnappers warn you not to involve the police."))
			print(_("What will you do?"))
			self.change_happiness(-randint(30, 40))
			choice = choice_input(
				_("Pay the ransom"),
				_("Involve the police"),
				_("Do nothing")
			)
			success = False
			if choice == 1:
				success = not one_in(self.get_event_chance(6))
				self.money -= ransom
				if success:
					display_event(_("You successfully paid ${ransom} ransom in exchange for {name}'s release.").format(ransom=ransom, name=self.partner.firstname), cls=False)
				else:
					display_event(_("You paid ${ransom} ransom but they did not return {name}!").format(ransom=ransom, name=self.partner.firstname), cls=False)
			elif choice == 2:
				success = not one_in(3)
				if success:
					display_event(_("The police managed to secure {name}'s release and arrest the kidnappers!").format(name=self.partner.firstname), cls=False)
				else:
					display_event(_("The police were unable to secure {name}'s release!").format(name=self.partner.firstname), cls=False)
			else:
				display_event(_("You did absolutely nothing!"), cls=False)
				self.change_karma(-randint(8, 16))
			if success:
				self.change_happiness(randint(6, 12))
				self.partner.change_relationship(randint(30, 50))
			else:
				display_event(_("{name} and {his_her} kidnappers vanished!").format(name=self.partner.firstname, his_her=self.partner.his_her()))
				self.process_relation_death(self.partner, reason=_("is presumed dead after disappearing"))
		elif (
			self.age >= 18
			and self.age < randint(42, 70)
			and self.marital_status == 0
			and one_in(16)
		):
			partner = self.generate_partner()
			if partner.compatibility_check(self):
				string = _("A male") if partner.gender == Gender.Male else _("A female")
				print(
					_("{a_male_female} named {name} has asked you out.").format(
						a_male_female=string, name=partner.name
					)
				)
				partner.print_info()
				him_her = partner.him_her()
				option1 = _("Start dating {him_her}").format(him_her=him_her)
				option2 = _("Reject {him_her}").format(him_her=him_her)
				choice = choice_input(option1, option2)
				if choice == 1:
					self.change_happiness(randint(12, 20))
					print(_("You are now dating {name}.").format(name=partner.name))
					self.partner = partner
					self.relations.append(partner)
		if self.age == 17 and not self.dropped_out:
			self.grades = None
			print(_("You graduated from high school."))
			self.change_happiness(randint(15, 20))
			self.change_smarts(randint(6, 10))
			if self.student_council:
			        print(_("Your student council service stands out on applications."))
			        self.change_skill("leadership", randint(1, 3))
			if self.college_prep >= 50:
			        print(_("Your college prep scores earned you scholarship offers."))
			        self.money += randint(500, 2000)
			if self.scholarship:
			        print(_("Your achievements granted you a special scholarship."))
			        self.money += randint(1000, 3000)
			print()
			self.display_stats()
			print()
			print(_("Would you like to apply to university?"))
			choice = choice_input(_("Yes"), _("No"))
			clear_screen()
			if choice == 1:
				if self.smarts >= random.randint(30, 44):
					print(_("Your application to university was accepted!"))
					self.change_happiness(randint(7, 9))
					SCHOLARSHIP = _("Scholarship")
					LOAN = _("Student Loan")
					PARENTS = _("Ask parents to pay")
					choices = [SCHOLARSHIP, LOAN]
					if self.parents:
						choices.append(PARENTS)
					chosen = False
					while not chosen:
						print(_("How would you like to pay for your college tuition?"))
						choice = choice_input(*choices, return_text=True)
						clear_screen()
						if choice == SCHOLARSHIP:
							if self.smarts >= randint(randint(75, 85), 100):
								display_event(
									_("Your scholarship application has been awarded!")
								)
								self.change_happiness(
									randint(10, 15) + (10 * self.has_trait("CHEERFUL"))
								)
								chosen = True
							else:
								display_event(
									_("Your scholarship application was rejected.")
								)
								self.change_happiness(-randint(7, 9))
								choices.remove(SCHOLARSHIP)
						elif choice == PARENTS:
							total = sum(p.generosity for p in self.parents.values())
							avg = total / len(self.parents)
							chance = (avg / 100) ** 4
							if x_in_y(chance, 1.0):
								display_event(
									_(
										"Your parents agreed to pay for your university tuition!"
									)
								)
								self.change_happiness(
									randint(7, 9) + (7 * self.has_trait("CHEERFUL"))
								)
								chosen = True
							else:
								display_event(
									_(
										"Your parents refused to pay for your university tuition."
									)
								)
								self.change_happiness(-randint(7, 9))
								choices.remove(PARENTS)
						else:
							display_event(
								_(
									"You took out a student loan to pay for your university tuition."
								)
							)
							chosen = True
							self.chose_student_loan = True
					print(_("You are now enrolled in university."))
					self.uv_years = 4
					self.calc_grades(randint(-8, 10))
				else:
					display_event(_("Your application to university was rejected."))
					self.change_happiness(-randint(7, 9))
