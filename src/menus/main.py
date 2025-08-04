import random
from random import randint

from src.lifesim_lib.const import *
from src.countries import *
from src.lifesim_lib.translation import _
from src.lifesim_lib.lifesim_lib import *
from src.people.classes.parent import Parent
from src.people.classes.person import Person
from src.people.classes.sibling import Sibling
from src.people.classes.partner import Partner
from src.people.classes.child import Child
from src.menus.activities import activities_menu

# Available school clubs and sports teams with optional skill requirements
# Each entry is (name, {skill: minimum_value}, skill_reward)
CLUB_OPTIONS = [
	("Science Club", {"science": 20}, "academic"),
	("Art Club", {"creativity": 20}, "social"),
	("Drama Club", {"charisma": 20}, "social"),
	("Math Club", {"math": 20}, "academic"),
	("Literature Club", {"language": 20}, "academic"),
]

SPORT_OPTIONS = [
	("Soccer", {"athletic": 15, "stamina": 10}),
	("Basketball", {"athletic": 20, "strength": 10}),
	("Swimming", {"athletic": 18, "stamina": 15}),
	("Football", {"athletic": 25, "strength": 15}),
	("Baseball", {"athletic": 15, "strength": 10}),
	("Tennis", {"athletic": 18, "stamina": 12}),
	("Volleyball", {"athletic": 17, "strength": 12}),
	("Track and Field", {"athletic": 22, "stamina": 18}),
	("Cheerleading", {"athletic": 16, "charisma": 12}),
]

PROJECT_OPTIONS = [
	("science fair project", "You built a baking soda volcano.", "science"),
	("art project", "You created a colorful painting.", "creativity"),
	("history presentation", "You presented about ancient Rome.", "language"),
]

# Middle school career aspirations which influence high-school options
CAREER_OPTIONS = ["Science", "Arts", "Sports", "Business"]

# Mapping of career aspirations to specialized high-school courses
ADVANCED_COURSES = {
	"Science": ("advanced science program", "science"),
	"Arts": ("advanced arts program", "creativity"),
	"Sports": ("elite athletic training", "athletic"),
	"Business": ("advanced business program", "language"),
}

# Tasks that parents or teachers may request from the player
PARENT_TASKS = [
	(_("study extra"), lambda p: (p.change_grades(randint(1, 3)), p.change_energy(-5))),
	(_("do chores"), lambda p: p.change_happiness(-randint(1, 3))),
	(_("improve your behavior"), lambda p: p.change_karma(randint(1, 3))),
]

TEACHER_TASKS = [
	(_("complete an extra credit assignment"), lambda p: (p.change_grades(randint(1, 3)), p.change_knowledge(randint(1, 3)))),
	(_("stay after class to help"), lambda p: (p.change_happiness(-randint(1, 2)), p.change_school_reputation(randint(1, 3)))),
	(_("behave better in class"), lambda p: p.change_school_reputation(randint(1, 3))),
]

def main_menu(player):
	player.check_goals()
	print()
	display_data(_("Your name"), player.name)
	t = player.get_traits_str() if player.traits else "None"
	display_data(_("Traits"), t)
	display_data(_("Gender"), player.get_gender_str())
	display_data(_("Money"), f"${player.money:,}")
	if player.has_job:
		display_data(_("Job Title"), player.job_title)
		display_data(_("Salary"), f"${player.salary:,}")
	if player.generation > 1:
		display_data(_("Generation"), player.generation)
	current_goal = player.get_current_goal()
	if current_goal:
		display_data(_("Current Goal"), current_goal.description)
		progress = player.get_goal_progress()
		if progress:
			display_data(_("Progress"), progress)
	player.display_stats()
	print()
	choices = [_("Age +1"), _("Relationships"), _("Activities")]
	if player.is_in_school():
		choices.append(_("School"))
	elif player.age >= 18:
		if player.has_job:
			choices.append(_("Job Menu"))
		else:
			choices.append(_("Find a Job"))
	choices.append(_("View Saved Games"))
	if DEBUG:
		choices.append(_("Debug Menu"))
	choice = choice_input(*choices, return_text=True)
	clear_screen()
	if choice == _("Age +1"):
		print()
		player.age_up()
	if choice == _("Relationships"):
		relations = player.relations
		print(_("Relationships: "))
		for num, relation in enumerate(relations):
			print(f"{num+1}. {relation.name} ({relation.get_translated_type()})")
		back = _("Back")
		print(f"{len(relations)+1}. {back}")
		choice = int_input_range(1, len(relations) + 1)
		clear_screen()
		if choice <= len(player.relations):
			relation = relations[choice - 1]
			print(
				_("Name")
				+ ": "
				+ relation.name
				+ f" ({relation.get_translated_type()})"
			)
			print(_("Age") + f": {relation.age}")
			bars = [(_("Relationship"), relation.relationship)]
			if isinstance(relation, Parent):
				bars.append((_("Generosity"), relation.generosity))
				bars.append((_("Money"), relation.money))
			elif isinstance(relation, (Sibling, Partner, Child)):
				bars.append((_("Smarts"), relation.smarts))
				bars.append((_("Looks"), relation.looks))
				if isinstance(relation, Sibling):
					bars.append((_("Petulance"), relation.petulance))
				elif isinstance(relation, Partner):
					bars.append((_("Craziness"), relation.craziness))
			print_align_bars(*bars)
			choices = [_("Back")]
			if relation.age >= 5:
				if player.age >= 5:
					choices.append(_("Spend time"))
				if player.age >= 3:
					choices.append(_("Have a conversation"))
				if player.age >= 6:
					choices.append(_("Compliment"))
					choices.append(_("Insult"))
				if isinstance(relation, Partner):
					choices.append(_("Have a baby"))
					if relation.status < 2:
						choices.append(_("Break up"))
					else:
						choices.append(_("Divorce"))
						choices.append(_("Renew Vows"))
					if relation.status == 0:
						choices.append(_("Propose"))
					elif relation.status == 1:
						choices.append(_("Plan the wedding"))
						choices.append(_("Call off the engagement"))
				elif player.age >= 6 and isinstance(relation, Parent):
					choices.append(_("Ask for money"))
			choice = choice_input(*choices, return_text=True)
			clear_screen()
			if choice == _("Spend time"):
				if relation.relationship < 15:
					print(_("Your {relation} refused to see you.").format(relation=relation.name_accusative()))
					player.change_happiness(-4)
				else:
					enjoyment1 = max(randint(0, 70), randint(0, 70)) + randint(0, 30)
					if player.has_trait("CHEERFUL"):
						enjoyment1 = max(enjoyment1, randint(0, 100))
					elif player.has_trait("GRUMPY"):
						enjoyment1 = min(enjoyment1, randint(0, 100))
					enjoyment2 = round(random.triangular(0, 100, relation.relationship))
					if isinstance(relation, Child):
						enjoyment1 += round_stochastic((100 - enjoyment1)*max(0, 18 - relation.age)/randint(36, 100))
						enjoyment2 += round_stochastic((100 - enjoyment2)*max(0, 13 - relation.age)/randint(26, 39))
					print(_("You took your {relation} {place}.").format(relation=relation.name_accusative(), place=random.choice(SPEND_TIME_PLACES)))
					print_align_bars(
						(_("Your Enjoyment"), enjoyment1),
						(
							_("{his_her} Enjoyment").format(
								his_her=relation.his_her().capitalize()
							),
							enjoyment2,
						),
					)
					if not relation.spent_time:
						player.change_happiness(round_stochastic(enjoyment1 / 12))
						relation.change_relationship(round_stochastic(enjoyment2 / 12))
						if player.has_trait("CHEERFUL"):
							player.change_happiness(3)
						relation.spent_time = True
			elif choice == _("Have a conversation"):
				if relation.relationship < 25:
					display_event(
						_(
							"Your {relation} isn't interested in having a conversation with you."
						).format(relation=relation.name_accusative())
					)
					player.change_happiness(-4)
				else:
					agreement = random.triangular(0, 100, 70)
					agreement += randint(0, max(0, (relation.relationship - 50) // 3))
					if isinstance(relation, Sibling) and one_in(2):
						agreement -= randint(0, relation.petulance // 3)
					if player.age < 6:
						v = (6 - player.age) * 8
						agreement += randint(v // 4, v)
					agreement = clamp(
						round(agreement), randint(0, 10), randint(90, 100)
					)
					if player.age < 13:
						chat = random.choice(CHATS_CHILD)
					else:
						chat = random.choice(CHATS)
					discussion = random.choice(DISCUSSIONS)
					talk = random.choice(TALKS)
					heart_to_heart = random.choice(HEART_TO_HEARTS)
					sayings = [
						_("You and your {relation} had a chat about {chat}.").format(
							relation=relation.name_accusative(),
							chat=chat
						),
						_("You and your {relation} discussed {discussion}.").format(
							relation=relation.name_accusative(),
							discussion=discussion
						),
						_("You and your {relation} talked about {talk}.").format(
							relation=relation.name_accusative(),
							talk=talk
						),
						_(
							"You and your {relation} had a heart-to-heart about {heart_to_heart}."
						).format(relation=relation.name_accusative(), heart_to_heart=heart_to_heart),
					]
					print(random.choice(sayings))
					display_bar(_("Agreement"), agreement)
					if not relation.had_conversation:
						player.change_happiness(
							8 if player.has_trait("CHEERFUL") else 4
						)
						relation.change_relationship(round_stochastic(agreement / 12))
						relation.had_conversation = True
					if agreement < 15:
						relation.change_relationship(-randint(2, 8))
						player.change_happiness(-4)
						print(
							_(
								"You and your {relation} got into an argument. What will you do?"
							).format(relation=relation.name_accusative())
						)
						choice = choice_input(
							_("Apologize"),
							_("Agree to disagree"),
							_("Insult {him_her}").format(him_her=relation.him_her()),
						)
						if choice == 1:
							player.change_karma(randint(1, 3))
							player.change_happiness(-randint(2, 4))
							print(
								_("You apologized to your {relation}").format(
									relation=relation.name_accusative()
								)
							)
							relation.change_relationship(randint(2, 4))
						elif choice == 2:
							print(_("You agreed to disagree"))
						elif choice == 3:
							player.change_karma(-randint(2, 6))
							insult = random.choice(INSULTS)
							print(
								_("You called your {relation} {insult}.").format(
									relation=relation.name_accusative(), insult=insult
								)
							)
							relation.change_relationship(-randint(4, 7))
			elif choice == _("Ask for money"):
				typ = relation.name_accusative()
				if relation.asked_for_money >= 3:
					print(_("Your {parent} told you to stop asking for money.").format(parent=typ))
					if relation.relationship < 25:
						insult = random.choice(INSULTS)
						print(_("{he_she} called you {insult}.").format(he_she=relation.he_she().capitalize(), insult=insult))
					relation.change_relationship(-randint(5, 10))
				else:
					if relation.asked_for_money == 0 and x_in_y(relation.generosity, 35):
						amount = 5 ** (relation.money/22) * (relation.generosity/100)**2 * math.sqrt(player.age)
						amount = max(randint(1, 5), round_stochastic(amount * random.uniform(0.6, 1.4)))
						print(_("Your {parent} gave you ${amount}.").format(parent=typ, amount=amount))
						player.money += amount
						relation.change_relationship(-randint(0, 8))
						relation.ask_money_cd = 3
					else:
						print(_("Your {parent} refused to give you any money.").format(parent=typ))
						relation.change_relationship(-randint(4, 8))
					relation.asked_for_money += 1
			elif choice == _("Compliment"):
				gen_appreciation = lambda: randint(0, 50) + randint(0, 50)
				appreciation = gen_appreciation()
				relationship = relation.relationship
				if relationship >= randint(51, 100):
					appreciation = max(appreciation, gen_appreciation())
					if relationship >= randint(75, 120):
						appreciation = max(
							appreciation, gen_appreciation()
						)
				elif relationship <= randint(0, 49):
					appreciation = min(appreciation, gen_appreciation())
					if relationship <= randint(0, 25):
						appreciation = min(
							appreciation, gen_appreciation()
						)
				compliments = COMPLIMENTS[:]
				if relation.gender == Gender.Male:
					compliments.extend([
						_("an alpha male"),
						_("handsome")
					])
				else:
					compliments.extend([
						_("an alpha female"),
						_("beautiful")
					])
				compliment = random.choice(COMPLIMENTS)
				print(
					_("You told your {relation} that {hes_shes} {compliment}.").format(
						relation=relation.name_accusative(),
						hes_shes=relation.hes_shes(),
						compliment=compliment,
					)
				)
				display_bar(
					_("{his_her} Appreciation").format(
						his_her=relation.his_her().capitalize()
					),
					appreciation,
				)
				press_enter()
				if not relation.was_complimented:
					player.change_karma(randint(0, 2))
					relation.change_relationship(round_stochastic(appreciation / 6))
					roll = randint(1, 300)
					cmp = round_stochastic(
						appreciation * relation.relationship / 50
					)
					if roll <= cmp:
						compliment = random.choice(COMPLIMENTS)
						display_event(
							_(
								"Your {relation} told you that you're {compliment}!"
							).format(
								relation=relation.name_accusative(),
								compliment=compliment,
							)
						)
						player.change_happiness(
							randint(6, 10) - (3 * (player.has_trait("GRUMPY")))
						)
						if player.has_trait("CHEERFUL"):
							player.change_happiness(4)
						if roll <= min(15, cmp//2): 
							relation.change_relationship(randint(25, 40))
					relation.was_complimented = True
			elif choice == _("Insult"):
				rel = relation.name_accusative()
				if yes_no(
					_("Are you sure you want to insult your {relation}?").format(
						relation=rel
					)
				):
					insult = random.choice(INSULTS)
					display_event(
						_("You called your {rel} {insult}.").format(
							rel=rel, insult=insult
						)
					)
					relation.change_relationship(-randint(4, 8))
					player.change_karma(-randint(2, 4))
					if isinstance(relation, Sibling):
						chance = 50 * (relation.petulance / 100) ** 1.5
					else:
						chance = (100 - relation.relationship) / 4
					attack_chance = 0
					if isinstance(relation, Sibling):
						attack_chance = 30 * (relation.petulance/100)**1.5
					elif isinstance(relation, Partner):
						attack_chance = 45 * (relation.craziness/100)**2
					if x_in_y(attack_chance, 100):
						display_event(_("Your {rel} attacked you!").format(rel=rel))
						player.was_attacked(randint(4, 10), False)
						relation.change_relationship(-randint(4, 8))
					elif x_in_y(chance, 100):
						insult = random.choice(INSULTS)
						display_event(
							_("Your {rel} called you {insult}!").format(
								rel=rel, insult=insult
							)
						)
						player.change_happiness(-randint(2, 6))
			elif choice == _("Have a baby"):
				already_pregnant = player.partner.is_pregnant if player.gender == Gender.Male else player.is_pregnant
				if already_pregnant:
					rel = player.partner.name_accusative()
					if player.gender == Gender.Male:
						print(_("Your {partner} is already pregnant!").format(partner=rel))
					else:
						print(_("You are already pregnant!"))
				elif relation.relationship >= randint(45, 75) and player.partner.years_together >= randint(1, 2):
					rel = player.partner.name_accusative()
					display_event(_("You and your {partner} tried for a baby.").format(partner=rel), cls=False)
					fertility = player.partner.fertility if player.gender == Gender.Male else player.fertility
					if x_in_y(fertility, 100):
						if player.gender == Gender.Male:
							print(_("Your {partner} is pregnant with your baby!").format(partner=rel))
						else:
							print(_("You are pregnant with {name}'s baby!").format(name=player.partner.firstname))
						print(_("What will you do"))
						choice = choice_input(
							_("Keep the baby"),
							_("Get an abortion")
						)
						overrule_chance = 10 * (player.partner.craziness/100)**2
						if player.partner.gender == Gender.Female:
							if choice == 1:
								overrule_chance /= 2
						elif choice == 2:
							overrule_chance /= 2
						is_pregnant = True
						if choice == 1:
							if x_in_y(overrule_chance, 100):
								is_pregnant = False
								if player.partner.gender == Gender.Female:
									msg = _("Your {partner} got an abortion anyway!")
								else:
									msg = _("Your {partner} forced you to get an abortion!")
								display_event(msg.format(partner=rel))
								player.change_happiness(-randint(10, 15))
						else:
							if x_in_y(overrule_chance, 100):
								if player.partner.gender == Gender.Female:
									msg = _("Your {partner} refused to get an abortion!")
								else:
									msg = _("Your {partner} forced you to keep the baby!")
								display_event(msg.format(partner=rel))
								player.change_happiness(-randint(8, 15))
							else:
								is_pregnant = False
								if player.gender == Gender.Male:
									msg = _("You made your {partner} get an abortion!")
								else:
									msg = _("You got an abortion!")
								display_event(msg.format(partner=rel))
						
						if is_pregnant:
							if player.gender == Gender.Male:
								player.partner.is_pregnant = True
							else:
								player.is_pregnant = True
								player._recent_child_father = player.partner
					else:
						msg = _("You failed to get your {partner} pregnant.").format(partner=player.partner.name_accusative()) if player.gender == Gender.Male else _("You failed to get pregnant.")
						print(msg)
				else:
					print(_("Your {partner} doesn't want to have a baby with you.").format(partner=player.partner.name_accusative()))
					player.partner.change_relationship(-randint(4, 8))
			elif choice == _("Break up"):
				partner = player.partner.name_accusative()
				if yes_no(
					_("Are you sure you want to break up with your {partner}?").format(
						partner=partner
					)
				):
					print(
						_("You broke up with your {partner}.").format(partner=partner)
					)
					player.lose_partner()
			elif choice == _("Propose"):
				partner = player.partner
				name = partner.name_accusative()
				if (
					partner.years_together >= randint(3, 8 - partner.craziness // 20)
					and not partner.was_proposed_to
					and partner.relationship >= randint(50, 60) + randint(0, 40)
				):
					print(
						_("Your {partner} accepted your proposal!").format(partner=name)
					)
					partner.status = 1
					partner.change_relationship(randint(20, 50))
				else:
					print(
						_("Your {partner} rejected your proposal.").format(partner=name)
					)
					if not partner.was_proposed_to:
						player.change_happiness(-randint(3, 8))
						partner.change_relationship(-randint(4, 9))
						partner.was_proposed_to = True
			elif choice == _("Call off the engagement"):
				partner = player.partner.name_accusative()
				if yes_no(
					_("Are you sure you want to call off your engagement with your {partner}?").format(
						partner=partner
					)
				):
					print(
						_("You called off your engagement with your {partner}.").format(partner=partner)
					)
					player.partner.status = 0
					player.partner.change_relationship(-15)
			elif choice == _("Plan the wedding"):
				locations = {
					TranslateMarker("golf course"): 15300,
					TranslateMarker("vineyard"): 15300,
					TranslateMarker("family member's house"): 255,
					TranslateMarker("courthouse"): 51,
					TranslateMarker("restaurant"): 5100,
					TranslateMarker("drive-thru wedding chapel"): 255,
					TranslateMarker("country club"): 15300
				}
				places = list(locations.keys())
				choices = random.sample(places, 4)
				while True:
					print(_("Choose a location:"))
					choice = choice_input(*(list(map(lambda a: str(a).capitalize(), choices)) + ["Cancel"]))
					if choice <= len(choices):
						location = choices[choice - 1]
						price = locations[location]
						print(_("You have chosen to marry {name} at a {place}.\nCost: ${price}").format(name=relation.name, place=location, price=price))
						choice = choice_input(_("Do it"), _("Edit the plan"), _("Actually, never mind"))
						if choice == 1:
							if player.money < price:
								print(_("You don't have enough money for this wedding plan."))
							else:
								player.money -= price
								print(_("You married {name} at a {place}.").format(name=relation.name, place=location))
								player.change_happiness(randint(10, 16))
								relation.change_relationship(randint(30, 50))
								relation.status = 2
								relation.last_renew_vows = player.age
							break
						elif choice == 3:
							break
					else:
						break
			elif choice == _("Divorce"):
				partner = player.partner.name_accusative()
				if yes_no(_("Are you sure you want to divorce your {partner}?").format(partner=partner)):
					print(
						_("You divorced your {partner}.").format(partner=partner)
					)
					player.divorce()
			elif choice == _("Renew Vows"):
				partner = relation.name_accusative()
				if relation.asked_renew_vows or player.age - relation.last_renew_vows < 10 or relation.relationship < randint(40, 70):
					print(_("Your {partner} doesn't want to renew your wedding vows.").format(partner=partner))
					relation.change_relationship(-randint(4, 8))
					relation.asked_renew_vows = True
				else:
					print(_("You and your {partner} renewed your wedding vows.").format(partner=partner))
					relation.change_relationship(randint(15, 20))
					player.change_happiness(randint(10, 16))
					relation.last_renew_vows = player.age
			print()
	if choice == _("Activities"):	
		activities_menu(player)			
	
	if choice == _("School"):
		print(_("School Menu"))
		print()
		display_bar(_("Grades"), player.grades)
		display_bar(_("Knowledge"), player.knowledge)
		display_bar(_("Popularity"), player.popularity)
		display_bar(_("Parent Approval"), player.parent_approval)
		display_bar(_("Teacher Favor"), player.teacher_favor)
		display_data(_("Friends"), player.friendships)
		display_data(_("Rivals"), player.rivalries)
		display_data(_("Romantic interests"), player.romantic_interests)
		stage = player.get_school_stage()
		base_options = [
			_("Back"),
			_("Study harder"),
			_("Drop out"),
			_("Skip school"),
			_("Hang out"),
			_("Study together"),
			_("Gossip"),
		]
		base_options.append(_("Parent meeting"))
		parent_meeting_idx = len(base_options)
		base_options.append(_("Meet teacher"))
		teacher_meeting_idx = len(base_options)
		attend_party_idx = None
		if stage != "primary":
			base_options.append(_("Attend party"))
			attend_party_idx = len(base_options)
		train_idx = None
		if player.sports_team:
			base_options.append(_("Train sport"))
			train_idx = len(base_options)
		if stage == "primary":
			extra = [_("Join a club"), _("Start a project"), _("Ask a question in class"), _("Help a classmate"), _("Join a sports team")]
		elif stage == "middle":
			extra = [_("Set career aspiration"), _("Choose elective"), _("Join sports team"), _("Study group"), _("Student council"), _("Deal with bullying")]
		elif stage == "high":
			extra = [_("Advanced course options"), _("Extracurricular leadership"), _("Prom"), _("Part-time job"), _("College prep tests")]
		else:
			extra = []
		base_len = len(base_options)
		choice = choice_input(*(base_options + extra))
		clear_screen()
		if train_idx and choice == train_idx:
			if player.energy < 10:
				print(_("You're too tired to train."))
			else:
				print(
					_("You trained with the {sport} team.").format(
						sport=player.sports_team_name.lower()
					)
				)
				gain = randint(1, 3)
				player.change_skill("athletic", gain)
				player.change_health(randint(1, 3))
				player.change_happiness(randint(1, 3))
				player.change_energy(-10)
		elif attend_party_idx and choice == attend_party_idx:
			if player.energy < 15:
				print(_("You're too tired to party."))
			else:
				print(_("You attended a party."))
				player.change_happiness(randint(4, 8))
				player.change_popularity(randint(3, 6))
				player.change_stress(randint(0, 5))
				player.change_grades(-randint(1, 3))
				player.change_energy(-15)
				if one_in(3):
					player.romantic_interests += 1
				for parent in player.parents.values():
					parent.change_relationship(-randint(1, 4))
		elif choice == 2:
			print(_("You began studying harder"))
			if player.energy < 10:
				print(_("You're too tired to study."))
			elif not player.studied:
				player.change_grades(randint(5, 7 + (100 - player.grades) // 5))
				player.change_smarts(randint(0, 2) + (player.has_trait("NERD")))
				player.change_knowledge(randint(5, 10))
				player.change_energy(-10)
				if x_in_y(player.smarts, 2000):
					player.learn_trait("NERD")
				player.studied = True
		elif choice == 3:
			can_drop_out = player.smarts < randint(8, 12) + randint(0, 13)
			can_drop_out &= not player.tried_to_drop_out
			if (
				player.age >= 18
				or player.uv_years > 0
				or (player.age >= randint(15, 16) and can_drop_out)
			):
				player.dropped_out = True
				player.grades = None
				print(_("You dropped out of school."))
				if player.uv_years > 0:
					player.uv_years = 0
			else:
				player.tried_to_drop_out = True
				print(_("Your parents won't let you drop out of school."))
		elif choice == 4:
			place = random.choice(SPEND_TIME_PLACES)
			display_event(_("You skipped school and went {place} instead.").format(place=place), cls=False)
			player.change_smarts(-2)
			player.change_grades(-randint(4, 8))
			if player.uv_years == 0 and one_in(5):
					display_event(_("You were caught skipping school!\nYou were sent to the principal's office and got detention."))
					player.change_happiness(-randint(15, 25))
					player.change_karma(-randint(1, 6))
			elif not player.skipped_school:
				player.change_happiness(randint(3, 7))
				player.change_karma(-randint(1, 6))
			player.skipped_school = True
		elif choice == 5:
			if player.energy < 5:
				print(_("You're too tired to hang out."))
			else:
				hangouts = [
					_("You went to the movies with friends."),
					_("You played video games at a friend's house."),
					_("You hung out at the park."),
					_("You spent the afternoon at the mall."),
					_("You went to the movies with friends and laughed so hard popcorn flew everywhere."),
					_("You played video games at a friend's house and pulled off an epic comeback win."),
					_("You hung out at the park, chasing frisbees and dodging squirrels."),
					_("You spent the afternoon at the mall, trying on ridiculous outfits and striking poses."),
					_("You had a picnic in the backyard, complete with ant invasions and silly stories."),
					_("You biked around the neighborhood, racing each other like pros."),
					_("You built a massive blanket fort and declared it your new kingdom."),
					_("You tried baking cookies together, ending up with more dough on your faces than in the oven."),
					_("You stargazed on the roof, making up constellations like 'The Giant Pizza'."),
					_("You had a water balloon fight that turned the yard into a splash zone."),
					_("You explored a local museum, pretending to be time travelers."),
					_("You jammed out to music in the garage, forming a fake band called 'The Homework Rebels'."),
					_("You went thrift shopping and found the weirdest treasures imaginable."),
					_("You played board games all night, with dramatic accusations of cheating."),
					_("You hiked a nearby trail, spotting wildlife and sharing ghost stories."),
					_("You organized a talent show in the living room, with hilariously bad impressions."),
					_("You tried street food from a food truck, rating each bite like food critics."),
					_("You had a photo scavenger hunt around town, capturing goofy moments."),
					_("You chilled at the beach, building sandcastles that rivaled real architecture."),
					_("You hosted a movie marathon with themed snacks and endless commentary."),
					_("You went roller skating, falling more times than you could count but loving it."),
					_("You planted a mini garden together, naming each plant after a celebrity."),
					_("You had a karaoke session, belting out tunes off-key but full of heart."),
					_("You explored an arcade, competing for the high score on every machine."),
					_("You crafted DIY friendship bracelets, getting tangled in yarn and laughter."),
					_("You went on a library adventure, recommending the weirdest books to each other."),
					_("You had a pillow fight that escalated into an all-out feather frenzy."),
					_("You tried yoga in the park, ending up in a pile of giggles instead of zen."),
					_("You shared secrets and dreams under a tree, strengthening your bonds."),
					_("You invented a new game combining tag and hide-and-seek with silly rules."),
				]
				print(random.choice(hangouts))
				player.friendships += 1
				player.change_popularity(randint(1, 3))
				player.change_happiness(randint(2, 5))
				player.change_stress(-randint(0, 3))
				player.change_energy(-5)
		elif choice == 6:
			if player.energy < 7:
				print(_("You're too tired to study with classmates."))
			else:
				study_events = [
					_("You and your friends reviewed math problems at the library."),
					_("You studied history together at a cafe."),
					_("You quizzed each other for the science test."),
					_("You formed a virtual study group online."),
					_("You and your friends reviewed math problems at the library, turning equations into a game of 'solve or snack'."),
						_("You studied history together at a cafe, reenacting battles with sugar packets and straws."),
						_("You quizzed each other for the science test, making up goofy mnemonics that had everyone in stitches."),
					_("You formed a virtual study group online, with everyone accidentally leaving their mics on during snack breaks."),
					_("You tackled literature notes in the park, dramatically reading passages like Shakespearean actors."),
					_("You crammed for biology at a friend's house, drawing cell diagrams in chalk on the driveway."),
					_("You worked on chemistry problems in the school lab, pretending to be mad scientists with wild hair."),
					_("You studied foreign language vocab at a diner, shouting phrases over milkshakes and fries."),
					_("You reviewed physics concepts at the skate park, comparing ramps to projectile motion."),
					_("You group-studied for English, writing absurd short stories to test grammar rules."),
					_("You dove into computer science at a tech shop, debugging code while surrounded by gadget chaos."),
					_("You practiced debate skills in the library, arguing silly topics like 'cats vs. dogs' for fun."),
					_("You studied geography by mapping out a fictional world on a giant poster board."),
					_("You tackled algebra together in a treehouse, solving equations while munching on candy."),
					_("You prepped for a history exam at the museum, whispering facts in front of ancient artifacts."),
					_("You worked on art history in a gallery, sketching replicas of famous paintings with crayons."),
					_("You studied music theory in a garage, banging on pots and pans to understand rhythm."),
					_("You reviewed economics at the mall, analyzing fake budgets for a dream shopping spree."),
					_("You quizzed each other on psychology terms, diagnosing your study group's 'procrastination syndrome'."),
					_("You studied environmental science by the lake, debating solutions while skipping rocks."),
					_("You tackled trigonometry in a backyard, using a protractor to measure angles of a swing set."),
					_("You formed a flashcards frenzy at a pizza place, tossing cards like confetti for correct answers."),
					_("You studied astronomy under the stars, pointing out constellations with a laser pointer."),
					_("You worked on group projects in a basement, turning research into a podcast recording session."),
					_("You reviewed philosophy in a coffee shop, debating life's big questions over lattes."),
				]
				print(random.choice(study_events))
				player.friendships += 1
				player.change_grades(randint(1, 3))
				player.change_skill("academic", 1)
				player.change_popularity(randint(0, 2))
				player.change_stress(-randint(0, 2))
				player.change_knowledge(randint(2, 4))
				player.change_energy(-7)
		elif choice == 7:
			if player.energy < 3:
				print(_("You're too tired to gossip."))
			else:
				gossip_events = [
					_("You spread a rumor about a classmate."),
					_("You talked about the latest drama in school."),
					_("You whispered secrets with a friend."),
					_("You accidentally gossiped about the wrong person!"),
					_("You spread a juicy rumor about a classmate's secret talent for yodeling in the shower."),
					_("You dished about the latest school drama over lunch, complete with wild theories about who started it."),
					_("You whispered secrets with a friend behind the bleachers, giggling so hard you almost got caught."),
					_("You accidentally gossiped about the wrong person and now everyone's talking about your mix-up!"),
					_("You overheard a wild story about the principal's secret karaoke nights and shared it with the squad."),
					_("You speculated about who left a love note in the library, creating a school-wide mystery."),
					_("You traded gossip about the cafeteria’s mystery meat recipe, swearing it’s alien food."),
					_("You and your bestie debated whether the new kid is secretly a movie star in disguise."),
					_("You passed on a rumor that the math teacher’s chalkboard doodles are coded messages."),
					_("You shared a hot tip about a secret party happening in the old gym this weekend."),
					_("You got the scoop on why the school mascot costume smells like tacos and told everyone."),
					_("You whispered about a classmate’s epic prank that turned the fountain bright pink."),
					_("You spread a tale about a haunted locker that only opens at midnight."),
					_("You gossiped about who’s been sneaking extra cookies from the bake sale table."),
					_("You shared a wild guess about the gym teacher’s secret life as a roller derby champ."),
					_("You and your crew debated who’s behind the anonymous advice column in the school paper."),
					_("You let slip a rumor about a teacher’s pet parrot that swears in three languages."),
					_("You traded stories about a classmate’s legendary dance moves at the talent show."),
					_("You whispered about a secret club that meets in the janitor’s closet after hours."),
					_("You speculated on who keeps leaving glitter bombs in the hallways for fun."),
					_("You shared a theory that the school’s Wi-Fi outages are caused by a rogue hacker clique."),
					_("You giggled over gossip about a classmate’s bizarre collection of vintage lunchboxes."),
					_("You passed on a rumor that the science lab skeleton is actually a retired pirate’s bones."),
					_("You dished about a teacher’s coffee addiction, claiming they hide espresso in their water bottle."),
					_("You spread word of a secret handshake that only the cool kids know—now everyone’s trying it."),
				]
				print(random.choice(gossip_events))
				player.change_popularity(randint(1, 4))
				player.rivalries += 1
				player.change_stress(randint(1, 4))
				player.change_school_reputation(-randint(1, 3))
				player.change_energy(-3)
		elif choice == parent_meeting_idx:
			task, action = random.choice(PARENT_TASKS)
			print(_("Your parents ask you to {task}. Do you comply?").format(task=task))
			if choice_input(_("Yes"), _("No")) == 1:
				action(player)
				player.change_parent_approval(randint(4, 8))
				print(_("Your parents are pleased."))
			else:
				player.change_parent_approval(-randint(4, 8))
				print(_("Your parents are disappointed."))
		elif choice == teacher_meeting_idx:
			task, action = random.choice(TEACHER_TASKS)
			print(_("Your teacher asks you to {task}. Do you comply?").format(task=task))
			if choice_input(_("Yes"), _("No")) == 1:
				action(player)
				player.change_teacher_favor(randint(4, 8))
				print(_("Your teacher appreciates your effort."))
			else:
				player.change_teacher_favor(-randint(4, 8))
				print(_("You declined the request."))
		else:
			idx = choice - base_len
			if stage == "primary":
				if idx == 1:
					if player.energy < 5:
						print(_("You're too tired."))
					elif not player.club:
						club_names = [_(c[0]) for c in CLUB_OPTIONS]
						cchoice = choice_input(*club_names)
						cname, reqs, reward = CLUB_OPTIONS[cchoice - 1]
						print(_("Requirements for {club}:").format(club=cname))
						for skill, val in reqs.items():
							pval = player.skills.get(skill, 0)
							print(f" - {skill.capitalize()}: {pval}/{val}")
						meets = all(
							player.skills.get(skill, 0) >= val
							for skill, val in reqs.items()
						)
						if meets:
							print(
								_("You joined the {club}.").format(
									club=cname.lower()
								)
							)
							player.change_happiness(randint(5, 10))
							player.change_skill(reward, randint(1, 3))
							player.change_energy(-5)
							player.club = True
							player.club_name = cname
						else:
							print(
								_("You don't meet the requirements for the {club}.").format(
									club=cname.lower()
								)
							)
					else:
						print(_("You are already in a club."))
				elif idx == 2:
					if player.energy < 7:
						print(_("You're too tired to start a project."))
					else:
						project_names = [_(p[0]) for p in PROJECT_OPTIONS]
						pchoice = choice_input(*project_names)
						pname, msg, skill = PROJECT_OPTIONS[pchoice - 1]
						print(_(msg))
						player.change_skill(skill, randint(1, 3))
						player.change_skill("academic", randint(1, 3))
						player.change_grades(randint(1, 3))
						player.change_knowledge(randint(2, 4))
						player.change_energy(-7)
				elif idx == 3:
					if player.energy < 2:
						print(_("You're too tired to ask questions."))
					else:
						subject = max(
							["math", "language", "science"],
							key=lambda s: player.skills.get(s, 0),
						)
						smart = (
							player.smarts + player.skills.get(subject, 0) >= 120
						)
						smart_questions = {
							"math": [
								_("You asked how to apply calculus to physics."),
								_("You wondered about solving quadratic equations."),
							],
							"language": [
								_("You asked about the use of metaphors."),
								_("You discussed nuances of grammar."),
							],
							"science": [
								_("You asked about quantum mechanics."),
								_("You questioned how photosynthesis works."),
							],
						}
						dumb_questions = {
							"math": [
								_("You asked if 1+1 always equals 2."),
								_("You wondered why we need numbers."),
							],
							"language": [
								_("You asked if 'cat' is a verb."),
								_("You questioned why spelling matters."),
							],
							"science": [
								_("You asked if the sun is made of fire."),
								_("You wondered why water is wet."),
							],
						}
						question_bank = smart_questions if smart else dumb_questions
						print(random.choice(question_bank[subject]))
						player.change_skill("academic", 1 + smart)
						player.change_grades(randint(0, 2) + smart)
						player.change_knowledge(1 + smart)
						player.change_energy(-2)
				elif idx == 4:
					if player.energy < 3:
						print(_("You're too tired to help."))
					else:
						help_events = [
							_("You helped a classmate with homework."),
							_("You defended a classmate from a bully."),
							_("You shared your notes with a classmate."),
							_("You helped carry books for a classmate."),
						]
						print(random.choice(help_events))
						player.change_happiness(randint(2,5))
						player.change_karma(randint(1,3))
						player.change_skill("social", 1)
						player.change_energy(-3)
				elif idx == 5:
					if player.energy < 10:
						print(_("You're too tired for sports."))
					elif not player.sports_team:
						sport_names = [_(s[0]) for s in SPORT_OPTIONS]
						schoice = choice_input(*sport_names)
						sname, reqs = SPORT_OPTIONS[schoice - 1]
						print(_("Requirements for {sport} team:").format(sport=sname))
						for skill, val in reqs.items():
							pval = player.skills.get(skill, 0)
							print(f" - {skill.capitalize()}: {pval}/{val}")
						meets = True
						if stage != "primary":
							meets = all(
								player.skills.get(skill, 0) >= val
								for skill, val in reqs.items()
							)
						if meets:
							print(
								_("You joined the {sport} team.").format(
									sport=sname.lower()
								)
							)
							player.sports_team = True
							player.sports_team_name = sname
							player.change_skill("athletic", randint(1,3))
							player.change_health(randint(1,4))
							player.change_energy(-10)
						else:
							print(
								_("You don't meet the requirements for the {sport} team.").format(
									sport=sname.lower()
								)
							)
					else:
						print(_("You are already on a sports team."))
			elif stage == "middle":
				if idx == 1:
					if player.career_aspiration:
						print(_("You already chose a career aspiration: {asp}." ).format(asp=player.career_aspiration))
					else:
						opts = [_(o) for o in CAREER_OPTIONS]
						cchoice = choice_input(*opts)
						player.career_aspiration = CAREER_OPTIONS[cchoice - 1]
						print(_("You now aspire to a career in {asp}." ).format(asp=player.career_aspiration.lower()))
						player.change_happiness(randint(1,3))
				elif idx == 2:
					if player.energy < 4:
						print(_("You're too tired to pick an elective."))
					else:
						print(_("Which elective will you choose?"))
						echoice = choice_input(_("Art"), _("Music"), _("Computer"), _("Foreign language"))
						elective_map = {1:("social",2),2:("social",2),3:("academic",3),4:("academic",2)}
						skill, amt = elective_map.get(echoice, ("academic",1))
						player.change_skill(skill, amt)
						player.change_happiness(randint(1,3))
						player.change_knowledge(2)
						player.change_energy(-4)
				elif idx == 3:
					if player.energy < 10:
						print(_("You're too tired for sports."))
					elif not player.sports_team:
						sport_names = [_(s[0]) for s in SPORT_OPTIONS]
						schoice = choice_input(*sport_names)
						sname, reqs = SPORT_OPTIONS[schoice - 1]
						print(_("Requirements for {sport} team:").format(sport=sname))
						for skill, val in reqs.items():
							pval = player.skills.get(skill, 0)
							print(f" - {skill.capitalize()}: {pval}/{val}")
						meets = all(
							player.skills.get(skill, 0) >= val
							for skill, val in reqs.items()
						)
						if meets:
							print(
								_("You joined the {sport} team.").format(
									sport=sname.lower()
								)
							)
							player.sports_team = True
							player.sports_team_name = sname
							player.change_skill("athletic", randint(1,3))
							player.change_health(randint(1,4))
							player.change_energy(-10)
						else:
							print(
								_("You don't meet the requirements for the {sport} team.").format(
									sport=sname.lower()
								)
							)
					else:
						print(_("You are already on a sports team."))
				elif idx == 4:
					if player.energy < 3:
						print(_("You're too tired for study group."))
					else:
						print(_("You participated in a study group."))
						player.change_skill("academic",2)
						player.change_grades(randint(1,3))
						player.change_happiness(randint(1,3))
						player.change_energy(-3)
				elif idx == 5:
					if player.energy < 5:
						print(_("You're too tired for student council."))
					elif not player.student_council:
						print(_("You joined the student council."))
						player.student_council = True
						player.change_skill("leadership",2)
						player.change_happiness(randint(2,4))
						player.change_energy(-5)
					else:
						print(_("You are already on the student council."))
				elif idx == 6:
					if player.energy < 4:
						print(_("You're too tired to deal with this."))
					else:
						print(_("A bully confronts you. How do you respond?"))
						bchoice = choice_input(_("Report to teacher"), _("Stand up"), _("Ignore"))
						player.change_energy(-4)
						if bchoice == 1:
							player.change_karma(randint(1,3))
							player.change_happiness(-randint(1,3))
						elif bchoice == 2:
							if one_in(2):
								print(_("You stood up to the bully successfully."))
								player.change_happiness(randint(2,5))
							else:
								print(_("The bully intimidated you."))
								player.change_happiness(-randint(2,5))
						else:
							player.change_happiness(-randint(1,3))
			elif stage == "high":
				if idx == 1:
					if player.career_aspiration is None:
						print(_("You need to set a career aspiration before enrolling in advanced courses."))
					elif player.energy < 8:
						print(_("You're too tired for advanced courses."))
					else:
						cname, skill = ADVANCED_COURSES.get(player.career_aspiration, ("advanced courses", "academic"))
						print(_("You enrolled in the {course}.").format(course=cname))
						player.change_grades(randint(1,4))
						player.change_skill(skill,3)
						player.change_skill("academic",3)
						player.change_knowledge(randint(3,5))
						player.change_energy(-8)
				elif idx == 2:
					if player.energy < 6:
						print(_("You're too tired for leadership roles."))
					elif not player.student_council:
						print(_("You took on an extracurricular leadership role."))
						player.student_council = True
						player.change_skill("leadership",3)
						player.change_happiness(randint(2,5))
						player.change_energy(-6)
					else:
						print(_("You are already a student leader."))
				elif idx == 3:
					if player.energy < 10:
						print(_("You're too tired to go to prom."))
					else:
						print(_("You went to prom."))
						player.change_happiness(randint(8,15))
						player.change_skill("social",2)
						player.change_energy(-10)
				elif idx == 4:
					if player.part_time_job:
						print(_("You quit your part-time job to study more."))
						player.part_time_job = False
						player.change_grades(randint(3,5))
					else:
						if player.energy < 10:
							print(_("You're too tired to start working."))
						else:
							print(_("You started a part-time job."))
							player.part_time_job = True
							player.change_grades(-randint(3,5))
							gain = randint(200, 400)
							if player.better_job:
								gain = randint(300, 600)
							player.money += gain
							player.change_energy(-10)
				elif idx == 5:
					if player.energy < 8:
						print(_("You're too tired for tests."))
					else:
						print(_("You took college prep tests."))
						player.college_prep = clamp(player.college_prep + randint(5,10), 0, 100)
						player.change_skill("academic",3)
						player.change_grades(randint(1,3))
						player.change_knowledge(randint(3,5))
						player.change_energy(-8)
				
	if choice == _("Debug Menu"):
		choice = choice_input(_("Back"), _("Stats"), _("Identity"))
		if choice == 2:
			while True:
				clear_screen()
				print(_("Your stats"))
				display_data(_("Happiness"), player.happiness)
				display_data(_("Health"), player.health)
				display_data(_("Smarts"), player.smarts)
				display_data(_("Looks"), player.looks)
				display_data(_("Karma"), player.karma)
				print()
				print(_("The below stats only matter if you have a job:"))
				display_data(_("Stress"), player.stress)
				display_data(_("Performance"), player.performance)
				print()
				choice = choice_input(
					_("Back"),
					_("Modify Happiness"),
					_("Modify Health"),
					_("Modify Smarts"),
					_("Modify Looks"),
					_("Modify Karma"),
					_("Modify Stress"),
					_("Modify Performance"),
				)
				if choice == 1:
					break
				elif choice == 2:
					print(_("What would you like to set Happiness to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.happiness = val
				elif choice == 3:
					print(_("What would you like to set Health to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.health = val
				elif choice == 4:
					print(_("What would you like to set Smarts to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.smarts = val
				elif choice == 5:
					print(_("What would you like to set Looks to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.looks = val
				elif choice == 6:
					print(_("What would you like to set Karma to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.karma = val
				elif choice == 7:
					print(_("What would you like to set Stress to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.stress = val
				elif choice == 8:
					print(_("What would you like to set Performance to? (0-100)"))
					val = int_input_range_optional(0, 100)
					if val is not None:
						player.performance = val
		elif choice == 3:
			while True:
				clear_screen()
				display_data(_("First name"), player.firstname)
				display_data(_("Last name"), player.lastname)
				display_data(_("Gender"), player.get_gender_str())
				choice = choice_input(
					_("Back"),
					_("Change first name"),
					_("Change last name"),
					_("Change gender"),
				)
				if choice == 1:
					break
				elif choice == 2:
					name = input(_("Enter first name: ")).strip()
					if name:
						player.firstname = name
				elif choice == 3:
					name = input(_("Enter last name: ")).strip()
					if name:
						player.lastname = name
				elif choice == 4:
					if player.gender == Gender.Male:
						player.gender = Gender.Female
					else:
						player.gender = Gender.Male
	if choice == _("Find a Job"):
		offers = random.sample(JOB_TYPES, min(3, len(JOB_TYPES)))
		jobs = []
		options = [_("Back")]
		for title, lo, avg in offers:
			salary = round_stochastic(randexpo(lo, avg))
			jobs.append((title, salary))
			options.append(f"{title} (${salary:,})")
		job_choice = choice_input(*options)
		if job_choice != 1:
			title, salary = jobs[job_choice - 2]
			if yes_no(
				_(
					"You found a job as a {title} with a salary of ${salary:,}. Would you like to apply?"
				).format(title=title, salary=salary)
			):
				m = 100 + round_stochastic((salary - 40000) / 300)
				mod = 50 - player.smarts
				if randint(1, 3) == 1:
					mod += round((50 - player.karma) / 2)
				roll = randint(1, m)
				if mod > 0:
					roll += randint(0, mod)
				elif mod < 0:
					roll -= randint(0, abs(mod))
				if roll <= 100:
					print(_("You got the job!"))
					player.change_happiness(4)
					player.get_job(salary, title)
				else:
					print(_("You didn't get an interview."))
					player.change_happiness(-randint(1, 4))
			else:
				clear_screen()
	elif choice == _("Job Menu"):
		print(_("Your job"))
		print()
		display_data(_("Job Title"), player.job_title)
		display_data(_("Salary"), f"${player.salary:,}")
		print_align_bars(
			(_("Stress"), player.stress), (_("Performance"), player.performance)
		)
		display_data(_("Hours"), player.job_hours)
		can_retire = player.years_worked >= 10 and player.age >= 65
		choice = choice_input(
			_("Back"),
			_("Work Harder"),
			_("Retire") if can_retire else _("Quit Job"),
			_("Adjust Hours"),
			_("Request a Raise")
		)
		if choice == 2:
			print("You worked harder.")
			if not player.worked_harder:
				player.change_performance(randint(1, 10))
				player.change_stress(4)
				if player.has_trait("LAZY"):
					player.change_stress(6)
				player.worked_harder = True
		elif choice == 3:
			if can_retire:
				pension = player.calc_pension()
				if yes_no(
					_(
						"Do you want to retire? You will receive a yearly pension of ${pension}"
					).format(pension=pension)
				):
					player.lose_job()
					player.salary = pension
					player.change_happiness(randint(25, 50))
					print(
						_(
							"You retired and are now receiving pension of ${pension}."
						).format(pension=pension)
					)
			elif yes_no(_("Are you sure you want to quit your job?")):
				player.lose_job()
				print(_("You quit your job."))
		elif choice == 4:
			print(_("What would you like to set your hours to? (38 - 70)"))
			player.update_hours(int_input_range(38, 70))
		elif choice == 5:
			if player.age - player.last_raise >= 10 and not player.asked_for_raise and player.performance >= randint(40, 120):
				print(_("Your request for a raise has been approved."))
				perc = round(randint(20, 85) / 10, 2)
				player.salary += round(player.salary * perc/100)
				display_event(_("You got a raise of {perc}%").format(perc=perc))
				player.times_asked_since_last_raise = 0
				player.last_raise = player.age
			else:
				display_event(_("Your request for a raise has been rejected."))
				if player.times_asked_since_last_raise >= 2 and randint(1, 9) == 1:
					display_event(_("Your boss fired you for asking for a raise."))
					player.lose_job()
					player.change_happiness(-randint(25, 35))
				player.times_asked_since_last_raise += 1
			player.asked_for_raise = True
	elif choice == _("View Saved Games"):
		players = list(filter(lambda p: p["ID"] != player.ID, get_saves()))
		if not players:
			print(_("No previously saved games"))
		else:
			print(_("Previously saved games:"))
			choices = list(map(lambda p: p["name"], players))
			choices.append(_("Back"))
			choice = choice_input(*choices)
			clear_screen()
			if choice < len(choices):
				d = players[choice - 1]
				print(d["name"] + "\n")
				choice = choice_input(_("Back"), _("Load Save"), _("Delete Save"))
				if choice == 2:
					if yes_no(_("Would you like to load this save?")):
						player.save_game()
						player.__init__()  # Re-initialize in preparation for loading a save
						player.__dict__.update(d)
						clear_screen()
				elif choice == 3:
					if yes_no(_("Are you sure you want to delete this save?")):
						os.remove(d["save_path"])
