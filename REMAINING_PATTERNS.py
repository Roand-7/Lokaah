"""
REMAINING ORACLE PATTERNS TO ADD
================================
Copy these 11 patterns (8 Probability + 3 Constructions) 
and insert them BEFORE the _gcd method in oracle_engine.py (around line 3157)
"""

# ============================================================
# PROBABILITY PATTERNS (8 patterns - 5 marks)
# ============================================================

def _gen_probability_single_card(self, pattern, topic):
    """
    Pattern: Probability of drawing single card
    Frequency: 9/11 papers (Very High)
    Source: 2023 Q1, 2024 Q3, 2025 Q1
    """
    # Variables - different card types
    card_scenarios = [
        {"type": "red card", "favorable": 26, "total": 52},
        {"type": "black card", "favorable": 26, "total": 52},
        {"type": "face card", "favorable": 12, "total": 52},
        {"type": "ace", "favorable": 4, "total": 52},
        {"type": "king", "favorable": 4, "total": 52},
        {"type": "heart", "favorable": 13, "total": 52},
        {"type": "spade", "favorable": 13, "total": 52},
        {"type": "diamond", "favorable": 13, "total": 52},
        {"type": "club", "favorable": 13, "total": 52},
    ]
    
    chosen = random.choice(card_scenarios)
    card_type = chosen["type"]
    favorable = chosen["favorable"]
    total = chosen["total"]
    
    # Simplify fraction
    from math import gcd
    g = gcd(favorable, total)
    numerator = favorable // g
    denominator = total // g
    
    question_text = (
        f"A card is drawn at random from a well-shuffled deck of {total} playing cards. "
        f"Find the probability of getting {card_type}."
    )
    
    solution_steps = [
        f"Total number of cards = {total}",
        f"Number of {card_type}s = {favorable}",
        f"Probability P(E) = Favorable outcomes / Total outcomes",
        f"P({card_type}) = {favorable}/{total}",
        f"P({card_type}) = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "What is the formula for probability?",
            "nudge": "P(E) = Favorable outcomes / Total outcomes"
        },
        {
            "level": 2,
            "hint": f"How many {card_type}s are in a standard deck?",
            "nudge": f"There are {favorable} {card_type}s"
        },
        {
            "level": 3,
            "hint": f"Calculate {favorable}/{total} and simplify",
            "nudge": f"= {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_single_card",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 1,
        "difficulty": 0.2,
        "estimated_time_minutes": 2,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_two_dice(self, pattern, topic):
    """
    Pattern: Two dice - sum or product
    Frequency: 7/11 papers (High)
    Source: 2023 Q21, 2024 Q19, 2025 Q20
    """
    # Variables - different conditions
    dice_conditions = [
        {"condition": "sum is 7", "favorable": 6},  # (1,6), (2,5), (3,4), (4,3), (5,2), (6,1)
        {"condition": "sum is 10", "favorable": 3}, # (4,6), (5,5), (6,4)
        {"condition": "sum is 5", "favorable": 4},  # (1,4), (2,3), (3,2), (4,1)
        {"condition": "product is 12", "favorable": 4}, # (2,6), (3,4), (4,3), (6,2)
        {"condition": "both numbers same", "favorable": 6}, # (1,1), (2,2), ..., (6,6)
    ]
    
    chosen = random.choice(dice_conditions)
    condition = chosen["condition"]
    favorable = chosen["favorable"]
    total = 36  # 6×6
    
    # Simplify fraction
    from math import gcd
    g = gcd(favorable, total)
    numerator = favorable // g
    denominator = total // g
    
    question_text = (
        f"Two dice are thrown simultaneously. "
        f"Find the probability that the {condition}."
    )
    
    solution_steps = [
        "Total outcomes when two dice are thrown = 6 × 6 = 36",
        f"Favorable outcomes (where {condition}):",
        f"Number of favorable outcomes = {favorable}",
        f"Probability P(E) = {favorable}/36",
        f"P(E) = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "How many total outcomes when throwing two dice?",
            "nudge": "6 × 6 = 36"
        },
        {
            "level": 2,
            "hint": f"List or count all pairs where {condition}",
            "nudge": f"There are {favorable} such outcomes"
        },
        {
            "level": 3,
            "hint": f"Calculate probability: {favorable}/36",
            "nudge": f"Simplified: {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_two_dice",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 2,
        "difficulty": 0.4,
        "estimated_time_minutes": 3,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_balls_without_replacement(self, pattern, topic):
    """
    Pattern: Balls drawn without replacement
    Frequency: 6/11 papers (Medium-High)
    Source: 2024 Q21, 2023 Q22, 2019 Q5
    """
    # Variables
    red_balls = random.choice([3, 4, 5])
    blue_balls = random.choice([4, 5, 6])
    total_balls = red_balls + blue_balls
    
    # Probability of drawing 2 red balls without replacement
    prob_first_red = red_balls / total_balls
    prob_second_red = (red_balls - 1) / (total_balls - 1)
    prob_both_red = prob_first_red * prob_second_red
    
    # Simplify
    from math import gcd
    numerator = red_balls * (red_balls - 1)
    denominator = total_balls * (total_balls - 1)
    g = gcd(numerator, denominator)
    num_simplified = numerator // g
    den_simplified = denominator // g
    
    question_text = (
        f"A bag contains {red_balls} red balls and {blue_balls} blue balls. "
        f"Two balls are drawn at random one after another without replacement. "
        f"Find the probability that both balls are red."
    )
    
    solution_steps = [
        f"Total balls = {red_balls} + {blue_balls} = {total_balls}",
        "Event: Both balls are red",
        f"P(first ball red) = {red_balls}/{total_balls}",
        f"After drawing one red ball: Remaining = {red_balls-1} red, {blue_balls} blue",
        f"P(second ball red | first red) = {red_balls-1}/{total_balls-1}",
        "P(both red) = P(first red) × P(second red | first red)",
        f"P(both red) = ({red_balls}/{total_balls}) × ({red_balls-1}/{total_balls-1})",
        f"P(both red) = {numerator}/{denominator}",
        f"P(both red) = {num_simplified}/{den_simplified}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "What changes after the first ball is drawn?",
            "nudge": "Total balls and red balls both decrease by 1"
        },
        {
            "level": 2,
            "hint": "How do you find probability of two dependent events?",
            "nudge": "Multiply: P(A) × P(B|A)"
        },
        {
            "level": 3,
            "hint": f"Calculate: ({red_balls}/{total_balls}) × ({red_balls-1}/{total_balls-1})",
            "nudge": f"= {num_simplified}/{den_simplified}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_balls_without_replacement",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {num_simplified}/{den_simplified}",
        "marks": 3,
        "difficulty": 0.6,
        "estimated_time_minutes": 5,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_complementary_event(self, pattern, topic):
    """
    Pattern: Complementary event P(not E) = 1 - P(E)
    Frequency: 8/11 papers (High)
    Source: 2023 Q12, 2024 Q14, 2025 Q12
    """
    # Variables
    prob_events = [
        {"event": "winning a game", "prob": "3/5", "prob_decimal": 0.6},
        {"event": "raining tomorrow", "prob": "2/7", "prob_decimal": 2/7},
        {"event": "getting a defective item", "prob": "1/8", "prob_decimal": 0.125},
    ]
    
    chosen = random.choice(prob_events)
    event = chosen["event"]
    prob_str = chosen["prob"]
    prob_val = chosen["prob_decimal"]
    
    # Calculate complement
    comp_val = 1 - prob_val
    
    # Express as fraction
    from fractions import Fraction
    frac = Fraction(prob_str)
    comp_frac = 1 - frac
    
    question_text = (
        f"The probability of {event} is {prob_str}. "
        f"Find the probability of not {event}."
    )
    
    solution_steps = [
        f"Given: P({event}) = {prob_str}",
        f"Let E = event of {event}",
        "Complementary event: not E",
        "Formula: P(not E) = 1 - P(E)",
        f"P(not {event}) = 1 - {prob_str}",
        f"P(not {event}) = {comp_frac}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "What is the relationship between an event and its complement?",
            "nudge": "P(E) + P(not E) = 1"
        },
        {
            "level": 2,
            "hint": "How do you find P(not E) if you know P(E)?",
            "nudge": "P(not E) = 1 - P(E)"
        },
        {
            "level": 3,
            "hint": f"Subtract: 1 - {prob_str}",
            "nudge": f"= {comp_frac}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_complementary_event",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"P(not {event}) = {comp_frac}",
        "marks": 1,
        "difficulty": 0.3,
        "estimated_time_minutes": 2,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_pack_of_cards_advanced(self, pattern, topic):
    """
    Pattern: Advanced card probability (two cards)
    Frequency: 8/11 papers (High)
    Source: 2023 Q24, 2024 Q23, 2025 Q22
    """
    # Variables - two card scenarios
    scenarios = [
        {"condition": "both are aces", "favorable": 4*3},
        {"condition": "both are face cards", "favorable": 12*11},
        {"condition": "both are red", "favorable": 26*25},
    ]
    
    chosen = random.choice(scenarios)
    condition = chosen["condition"]
    favorable = chosen["favorable"]
    total = 52 * 51  # Two cards without replacement
    
    # Simplify
    from math import gcd
    g = gcd(favorable, total)
    numerator = favorable // g
    denominator = total // g
    
    question_text = (
        f"Two cards are drawn at random from a deck of 52 cards without replacement. "
        f"Find the probability that {condition}."
    )
    
    solution_steps = [
        "Total ways to draw 2 cards = 52 × 51 (without replacement)",
        f"For {condition}:",
        f"Favorable outcomes = {favorable}",
        f"Probability = {favorable}/{total}",
        f"Probability = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "How many ways can you draw 2 cards from 52?",
            "nudge": "52 × 51 (order matters, without replacement)"
        },
        {
            "level": 2,
            "hint": f"Count favorable outcomes for {condition}",
            "nudge": f"There are {favorable} such outcomes"
        },
        {
            "level": 3,
            "hint": f"Calculate and simplify: {favorable}/{total}",
            "nudge": f"= {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_pack_of_cards_advanced",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 2,
        "difficulty": 0.5,
        "estimated_time_minutes": 4,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_at_least_one(self, pattern, topic):
    """
    Pattern: At least one success
    Frequency: 6/11 papers (Medium-High)
    Source: 2024 Q25, 2022 Q6, 2019 Q4
    """
    # Coin toss scenario
    num_tosses = random.choice([2, 3])
    
    if num_tosses == 2:
        total_outcomes = 4  # HH, HT, TH, TT
        at_least_one_head = 3  # HH, HT, TH
        none_head = 1  # TT
    else:  # 3 tosses
        total_outcomes = 8
        at_least_one_head = 7
        none_head = 1  # TTT
    
    # Simplify
    from math import gcd
    g = gcd(at_least_one_head, total_outcomes)
    numerator = at_least_one_head // g
    denominator = total_outcomes // g
    
    question_text = (
        f"A coin is tossed {num_tosses} times. "
        f"Find the probability of getting at least one head."
    )
    
    solution_steps = [
        f"Total outcomes when tossing {num_tosses} times = 2^{num_tosses} = {total_outcomes}",
        "Method 1: Direct counting",
        f"At least one head = all cases except all tails",
        f"Favorable outcomes = {total_outcomes} - {none_head} = {at_least_one_head}",
        f"P(at least one head) = {at_least_one_head}/{total_outcomes}",
        "",
        "Method 2: Using complement",
        f"P(no head) = P(all tails) = {none_head}/{total_outcomes}",
        f"P(at least one head) = 1 - P(no head)",
        f"P(at least one head) = 1 - {none_head}/{total_outcomes} = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "What is the complement of 'at least one head'?",
            "nudge": "'No heads' or 'all tails'"
        },
        {
            "level": 2,
            "hint": "Use: P(at least one) = 1 - P(none)",
            "nudge": f"P(all tails) = {none_head}/{total_outcomes}"
        },
        {
            "level": 3,
            "hint": f"Calculate: 1 - {none_head}/{total_outcomes}",
            "nudge": f"= {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_at_least_one",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 2,
        "difficulty": 0.6,
        "estimated_time_minutes": 4,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_spinner(self, pattern, topic):
    """
    Pattern: Spinner/wheel probability
    Frequency: 5/11 papers (Medium)
    Source: 2025 Q18, 2021 Q3
    """
    # Variables
    total_sections = random.choice([8, 10, 12])
    winning_sections = random.choice([2, 3, 4])
    
    # Simplify
    from math import gcd
    g = gcd(winning_sections, total_sections)
    numerator = winning_sections // g
    denominator = total_sections // g
    
    question_text = (
        f"A spinner is divided into {total_sections} equal sections numbered 1 to {total_sections}. "
        f"Sections {', '.join(str(i) for i in range(1, winning_sections+1))} are colored red. "
        f"If the spinner is spun once, find the probability that it lands on a red section."
    )
    
    solution_steps = [
        f"Total sections = {total_sections}",
        f"Red sections = {winning_sections}",
        "All sections are equally likely",
        f"P(red section) = Number of red sections / Total sections",
        f"P(red section) = {winning_sections}/{total_sections}",
        f"P(red section) = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "Are all sections equally likely?",
            "nudge": "Yes, so use classical probability"
        },
        {
            "level": 2,
            "hint": f"How many red sections out of {total_sections}?",
            "nudge": f"{winning_sections} red sections"
        },
        {
            "level": 3,
            "hint": f"Calculate: {winning_sections}/{total_sections}",
            "nudge": f"Simplified: {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_spinner",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 1,
        "difficulty": 0.3,
        "estimated_time_minutes": 2,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_probability_random_number(self, pattern, topic):
    """
    Pattern: Random number selection
    Frequency: 6/11 papers (Medium-High)
    Source: 2023 Q15, 2024 Q16, 2022 Q5
    """
    # Variables
    min_num = 1
    max_num = random.choice([20, 30, 50, 100])
    
    conditions = [
        {"type": "multiple of 5", "count": max_num // 5},
        {"type": "multiple of 10", "count": max_num // 10},
    ]
    
    chosen = random.choice([c for c in conditions if c["count"] is not None])
    condition_type = chosen["type"]
    favorable = chosen["count"]
    
    # Simplify
    from math import gcd
    g = gcd(favorable, max_num)
    numerator = favorable // g
    denominator = max_num // g
    
    question_text = (
        f"A number is selected at random from the numbers {min_num} to {max_num}. "
        f"Find the probability that the selected number is a {condition_type}."
    )
    
    solution_steps = [
        f"Total numbers from {min_num} to {max_num} = {max_num}",
        f"Numbers that are {condition_type}: {favorable}",
        f"P({condition_type}) = {favorable}/{max_num}",
        f"P({condition_type}) = {numerator}/{denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": f"How many numbers are there from {min_num} to {max_num}?",
            "nudge": f"{max_num} numbers"
        },
        {
            "level": 2,
            "hint": f"Count how many are {condition_type}",
            "nudge": f"{favorable} such numbers"
        },
        {
            "level": 3,
            "hint": f"Calculate and simplify: {favorable}/{max_num}",
            "nudge": f"= {numerator}/{denominator}"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "probability_random_number",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Probability = {numerator}/{denominator}",
        "marks": 2,
        "difficulty": 0.4,
        "estimated_time_minutes": 3,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


# ============================================================
# CONSTRUCTIONS PATTERNS (3 patterns - 3 marks)
# ============================================================

def _gen_construction_divide_line_segment(self, pattern, topic):
    """
    Pattern: Divide line segment in given ratio
    Frequency: 6/11 papers (Medium-High)
    Source: 2023 Q37, 2024 Q37, 2022 Q12
    """
    # Variables
    ratio_m = random.choice([2, 3, 4])
    ratio_n = random.choice([3, 4, 5])
    
    # Ensure m < n for internal division
    if ratio_m >= ratio_n:
        ratio_m, ratio_n = ratio_n, ratio_m
    
    question_text = (
        f"Draw a line segment AB of length 8 cm. "
        f"Divide it internally in the ratio {ratio_m}:{ratio_n}. "
        f"Write the steps of construction."
    )
    
    solution_steps = [
        "Steps of Construction:",
        "1. Draw a line segment AB = 8 cm",
        f"2. Draw any ray AX making an acute angle with AB",
        f"3. Mark {ratio_m + ratio_n} equal points A₁, A₂, ..., A_{ratio_m + ratio_n} on AX",
        f"4. Join BA_{ratio_m + ratio_n}",
        f"5. From A_{ratio_m}, draw A_{ratio_m}P || BA_{ratio_m + ratio_n} (using corresponding angles)",
        "6. P divides AB in the ratio {ratio_m}:{ratio_n}",
        "",
        "Justification:",
        f"By Basic Proportionality Theorem: AP/PB = AA_{ratio_m}/A_{ratio_m}A_{ratio_m + ratio_n} = {ratio_m}/{ratio_n}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "How many equal divisions do you need on the ray?",
            "nudge": f"m + n = {ratio_m} + {ratio_n} = {ratio_m + ratio_n} divisions"
        },
        {
            "level": 2,
            "hint": f"From which point do you draw a line parallel to BA_{ratio_m + ratio_n}?",
            "nudge": f"From the {ratio_m}th point (A_{ratio_m})"
        },
        {
            "level": 3,
            "hint": "Which theorem justifies this construction?",
            "nudge": "Basic Proportionality Theorem (Thales' theorem)"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "construction_divide_line_segment",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Line segment divided in ratio {ratio_m}:{ratio_n}",
        "marks": 2,
        "difficulty": 0.5,
        "estimated_time_minutes": 5,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_construction_tangent_from_external_point(self, pattern, topic):
    """
    Pattern: Construct tangents from external point
    Frequency: 5/11 papers (Medium)
    Source: 2023 Q38, 2024 Q39, 2021 Q13
    """
    # Variables
    radius = random.choice([3, 4, 5])
    distance = random.choice([7, 8, 9, 10])
    
    question_text = (
        f"Draw a circle of radius {radius} cm. "
        f"From a point P at a distance of {distance} cm from the center, "
        f"construct two tangents to the circle. "
        f"Write the steps of construction."
    )
    
    solution_steps = [
        "Steps of Construction:",
        f"1. Draw a circle with center O and radius {radius} cm",
        f"2. Mark a point P at distance {distance} cm from O",
        "3. Join OP",
        "4. Draw perpendicular bisector of OP, meeting OP at M (midpoint)",
        "5. With M as center and MO (or MP) as radius, draw a circle",
        "6. This circle intersects the given circle at points T₁ and T₂",
        "7. Join PT₁ and PT₂",
        "8. PT₁ and PT₂ are the required tangents",
        "",
        "Justification:",
        "∠OT₁P = 90° (angle in semicircle)",
        "OT₁ ⊥ PT₁, so PT₁ is tangent to circle at T₁",
        "Similarly, PT₂ is tangent at T₂"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": "What geometric property do tangents from an external point have?",
            "nudge": "They are equal in length and perpendicular to radius at point of contact"
        },
        {
            "level": 2,
            "hint": "How can you ensure the angle at T is 90°?",
            "nudge": "Use angle in semicircle property"
        },
        {
            "level": 3,
            "hint": "Which circle passes through O, T, and P?",
            "nudge": "Circle with diameter OP (constructed using midpoint M)"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "construction_tangent_from_external_point",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": "Two tangents constructed from external point",
        "marks": 3,
        "difficulty": 0.7,
        "estimated_time_minutes": 7,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }


def _gen_construction_similar_triangle(self, pattern, topic):
    """
    Pattern: Construct triangle similar to given triangle
    Frequency: 4/11 papers (Medium)
    Source: 2024 Q38, 2022 Q13, 2019 Q12
    """
    # Variables
    scale_numerator = random.choice([2, 3, 4, 5])
    scale_denominator = random.choice([3, 4, 5, 6, 7])
    
    # Ensure proper fraction
    if scale_numerator >= scale_denominator:
        scale_numerator, scale_denominator = scale_denominator - 1, scale_denominator
    
    question_text = (
        f"Construct a triangle ABC with sides AB = 6 cm, BC = 7 cm, and AC = 5 cm. "
        f"Then construct another triangle similar to triangle ABC "
        f"with scale factor {scale_numerator}/{scale_denominator}. "
        f"Write the steps of construction."
    )
    
    solution_steps = [
        "Steps of Construction:",
        "1. Construct △ABC with AB = 6 cm, BC = 7 cm, AC = 5 cm",
        f"2. Draw any ray BX making acute angle with BC",
        f"3. Mark {scale_denominator} equal points B₁, B₂, ..., B_{scale_denominator} on BX",
        f"4. Join B_{scale_denominator}C",
        f"5. From B_{scale_numerator}, draw B_{scale_numerator}C' || B_{scale_denominator}C",
        "6. From C', draw C'A' || CA",
        "7. △A'BC' is the required triangle",
        "",
        "Justification:",
        f"By construction, BC'/BC = {scale_numerator}/{scale_denominator}",
        "Since C'A' || CA, △A'BC' ~ △ABC",
        f"Scale factor = {scale_numerator}/{scale_denominator}"
    ]
    
    socratic_hints = [
        {
            "level": 1,
            "hint": f"How many points do you mark on ray BX?",
            "nudge": f"The denominator: {scale_denominator} points"
        },
        {
            "level": 2,
            "hint": f"From which point do you draw the parallel line?",
            "nudge": f"From B_{scale_numerator} (the numerator)"
        },
        {
            "level": 3,
            "hint": "Which similarity criterion proves the triangles are similar?",
            "nudge": "AA criterion (two pairs of corresponding angles equal)"
        }
    ]
    
    return {
        "question_id": self._generate_id(),
        "pattern_id": "construction_similar_triangle",
        "topic": topic,
        "question_text": question_text,
        "solution_steps": solution_steps,
        "final_answer": f"Triangle similar with scale factor {scale_numerator}/{scale_denominator}",
        "marks": 3,
        "difficulty": 0.7,
        "estimated_time_minutes": 8,
        "socratic_hints": socratic_hints,
        "generated_at": datetime.now().isoformat(),
        "unique_hash": self._compute_hash(question_text)
    }
