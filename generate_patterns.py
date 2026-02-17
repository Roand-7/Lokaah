"""
Pattern Factory: Generate 200+ CBSE Class 10 pattern JSON definitions.

Flow:
1. Try Gemini generation chapter-by-chapter (if configured and available).
2. Fill gaps with deterministic remix patterns to guarantee target volume.
3. Save per-chapter files plus one combined file.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


load_dotenv()


GOLDEN_TEMPLATE_PATH = Path("app/oracle/pattern_factory/golden_pattern.json")
OUTPUT_DIR = Path("app/oracle/pattern_factory/generated")

CHAPTER_SUBTOPICS: Dict[str, List[str]] = {
    "Real Numbers": [
        "Euclid Division Algorithm",
        "HCF and LCM",
        "Fundamental Theorem of Arithmetic",
        "Terminating Decimal Expansion",
    ],
    "Polynomials": [
        "Zeroes of Polynomial",
        "Relationship Between Coefficients and Roots",
        "Remainder Theorem",
        "Factor Theorem",
    ],
    "Pair of Linear Equations": [
        "Algebraic Solution",
        "Elimination Method",
        "Substitution Method",
        "Word Problems",
    ],
    "Quadratic Equations": [
        "Nature of Roots",
        "Quadratic Formula",
        "Factorization Method",
        "Word Problems",
    ],
    "Arithmetic Progressions": [
        "Nth Term",
        "Sum of N Terms",
        "Find Common Difference",
        "Daily Life Word Problems",
    ],
    "Triangles": [
        "Basic Proportionality Theorem",
        "Similarity Criteria",
        "Area Ratios",
        "Pythagoras Applications",
    ],
    "Coordinate Geometry": [
        "Distance Formula",
        "Section Formula",
        "Midpoint Formula",
        "Area of Triangle",
    ],
    "Trigonometry": [
        "Trigonometric Ratios",
        "Values at Standard Angles",
        "Identities",
        "Complementary Angles",
    ],
    "Applications of Trig": [
        "Heights and Distances",
        "Angle of Elevation",
        "Angle of Depression",
        "Two-Observation Problems",
    ],
    "Circles": [
        "Tangent Theorem",
        "Equal Tangents",
        "Radius-Perpendicular Property",
        "Chord-Tangent Relationships",
    ],
    "Constructions": [
        "Division of Line Segment",
        "Tangent from External Point",
        "Similar Triangle Construction",
        "Scale Factor Construction",
    ],
    "Areas Related to Circles": [
        "Sector Area",
        "Arc Length",
        "Segment Area",
        "Combined Figures",
    ],
    "Surface Areas & Volumes": [
        "Cone and Cylinder",
        "Sphere and Hemisphere",
        "Frustum",
        "Composite Solids",
    ],
    "Statistics": [
        "Mean from Frequency Table",
        "Median of Grouped Data",
        "Mode of Grouped Data",
        "Cumulative Frequency",
    ],
    "Probability": [
        "Theoretical Probability",
        "Cards and Dice",
        "Complementary Events",
        "At Least One Event",
    ],
}


FAMILY_BLUEPRINTS: Dict[str, List[Dict[str, Any]]] = {
    "real_numbers": [
        {
            "template": "Use Euclid division algorithm to divide {a} by {b}. Find quotient and remainder.",
            "variables": {"a": "random.randint(60, 500)", "b": "random.randint(2, 30)"},
            "solver_code": "q = a // b; r = a % b; return {'q': q, 'r': r}",
        },
        {
            "template": "For numbers {a} and {b}, compute HCF and LCM.",
            "variables": {"a": "random.randint(24, 180)", "b": "random.randint(18, 150)"},
            "solver_code": "h = math.gcd(a, b); l = (a*b)//h; return {'hcf': h, 'lcm': l}",
        },
        {
            "template": "Check whether {a} and {b} are coprime.",
            "variables": {"a": "random.randint(10, 120)", "b": "random.randint(10, 120)"},
            "solver_code": "return 'Coprime' if math.gcd(a, b) == 1 else 'Not Coprime'",
        },
    ],
    "polynomials": [
        {
            "template": "If roots of a quadratic are {r1} and {r2}, find sum and product of roots.",
            "variables": {"r1": "random.randint(-10, 10)", "r2": "random.randint(-10, 10)"},
            "solver_code": "return {'sum': r1 + r2, 'product': r1 * r2}",
        },
        {
            "template": "Evaluate polynomial P(x) = {a}x^2 + {b}x + {c} at x = {x}.",
            "variables": {
                "a": "random.randint(1, 8)",
                "b": "random.randint(-12, 12)",
                "c": "random.randint(-20, 20)",
                "x": "random.randint(-5, 5)",
            },
            "solver_code": "return a*(x**2) + b*x + c",
        },
        {
            "template": "For polynomial with coefficients a={a}, b={b}, c={c}, find discriminant.",
            "variables": {"a": "random.randint(1, 8)", "b": "random.randint(-12, 12)", "c": "random.randint(-12, 12)"},
            "solver_code": "return b**2 - 4*a*c",
        },
    ],
    "linear": [
        {
            "template": "Solve for x: {a}x + {b} = {c}.",
            "variables": {"a": "random.randint(1, 12)", "b": "random.randint(-20, 20)", "c": "random.randint(-20, 40)"},
            "solver_code": "return round((c - b) / a, 3)",
        },
        {
            "template": "Find intersection for lines a1x + b1y = c1 and a2x + b2y = c2 where a1={a1}, b1={b1}, c1={c1}, a2={a2}, b2={b2}, c2={c2}.",
            "variables": {
                "a1": "random.randint(1, 8)",
                "b1": "random.randint(1, 8)",
                "c1": "random.randint(5, 40)",
                "a2": "random.randint(1, 8)",
                "b2": "random.randint(1, 8)",
                "c2": "random.randint(5, 40)",
            },
            "solver_code": "d = a1*b2 - a2*b1; return 'No unique solution' if d == 0 else {'x': round((c1*b2 - c2*b1)/d, 3), 'y': round((a1*c2 - a2*c1)/d, 3)}",
        },
        {
            "template": "A quantity increases from {base} to {new}. Find percentage increase.",
            "variables": {"base": "random.randint(20, 200)", "new": "random.randint(201, 400)"},
            "solver_code": "return round(((new - base) / base) * 100, 2)",
        },
    ],
    "quadratic": [
        {
            "template": "Find the nature of roots for equation {a}x^2 + {b}x + {c} = 0.",
            "variables": {"a": "random.randint(1, 8)", "b": "random.randint(-15, 15)", "c": "random.randint(-10, 10)"},
            "solver_code": "D = b**2 - 4*a*c; return 'Real & Distinct' if D > 0 else ('Real & Equal' if D == 0 else 'No Real Roots')",
        },
        {
            "template": "Solve quadratic equation {a}x^2 + {b}x + {c} = 0 using formula.",
            "variables": {"a": "random.randint(1, 6)", "b": "random.randint(-12, 12)", "c": "random.randint(-12, 12)"},
            "solver_code": "D = b**2 - 4*a*c; return 'No Real Roots' if D < 0 else {'x1': round((-b + math.sqrt(D))/(2*a), 3), 'x2': round((-b - math.sqrt(D))/(2*a), 3)}",
        },
        {
            "template": "For equation x^2 - ({sum_roots})x + ({product_roots}) = 0, identify sum and product of roots.",
            "variables": {"sum_roots": "random.randint(-20, 20)", "product_roots": "random.randint(-30, 30)"},
            "solver_code": "return {'sum': sum_roots, 'product': product_roots}",
        },
    ],
    "ap": [
        {
            "template": "In an AP with first term {a} and common difference {d}, find the {n}th term.",
            "variables": {"a": "random.randint(1, 20)", "d": "random.randint(1, 10)", "n": "random.randint(5, 40)"},
            "solver_code": "return a + (n - 1)*d",
        },
        {
            "template": "Find the sum of first {n} terms of AP with first term {a} and difference {d}.",
            "variables": {"a": "random.randint(1, 20)", "d": "random.randint(1, 10)", "n": "random.randint(5, 30)"},
            "solver_code": "return round((n/2) * (2*a + (n - 1)*d), 2)",
        },
        {
            "template": "The nth term of an AP is {tn} for n={n} and first term is {a}. Find d.",
            "variables": {"tn": "random.randint(20, 200)", "n": "random.randint(4, 20)", "a": "random.randint(1, 20)"},
            "solver_code": "return round((tn - a)/(n - 1), 3)",
        },
    ],
    "geometry": [
        {
            "template": "A right triangle has legs {p} and {q}. Find hypotenuse.",
            "variables": {"p": "random.randint(3, 30)", "q": "random.randint(4, 30)"},
            "solver_code": "return round(math.sqrt(p**2 + q**2), 3)",
        },
        {
            "template": "Two similar triangles have corresponding sides in ratio {k}. Find area ratio.",
            "variables": {"k": "random.randint(2, 12)"},
            "solver_code": "return k**2",
        },
        {
            "template": "If perimeter of a square is {perimeter}, find area.",
            "variables": {"perimeter": "random.randint(16, 200)"},
            "solver_code": "side = perimeter / 4; return side**2",
        },
    ],
    "coordinate": [
        {
            "template": "Find midpoint of points ({x1}, {y1}) and ({x2}, {y2}).",
            "variables": {
                "x1": "random.randint(-15, 15)",
                "y1": "random.randint(-15, 15)",
                "x2": "random.randint(-15, 15)",
                "y2": "random.randint(-15, 15)",
            },
            "solver_code": "return {'x': (x1 + x2)/2, 'y': (y1 + y2)/2}",
        },
        {
            "template": "Find distance between points ({x1}, {y1}) and ({x2}, {y2}).",
            "variables": {
                "x1": "random.randint(-10, 10)",
                "y1": "random.randint(-10, 10)",
                "x2": "random.randint(-10, 10)",
                "y2": "random.randint(-10, 10)",
            },
            "solver_code": "return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2), 3)",
        },
        {
            "template": "Find coordinates dividing segment joining ({x1}, {y1}) and ({x2}, {y2}) in ratio {m}:{n}.",
            "variables": {
                "x1": "random.randint(-12, 12)",
                "y1": "random.randint(-12, 12)",
                "x2": "random.randint(-12, 12)",
                "y2": "random.randint(-12, 12)",
                "m": "random.randint(1, 6)",
                "n": "random.randint(1, 6)",
            },
            "solver_code": "x = (m*x2 + n*x1)/(m+n); y = (m*y2 + n*y1)/(m+n); return {'x': round(x, 3), 'y': round(y, 3)}",
        },
    ],
    "trig": [
        {
            "template": "An object is {distance} m away from a building and angle of elevation is {angle} deg. Find height.",
            "variables": {"distance": "random.randint(10, 80)", "angle": "random.choice([30, 45, 60])"},
            "solver_code": "return round(distance * math.tan(math.radians(angle)), 3)",
        },
        {
            "template": "A tower of height {height} m is observed at angle {angle} deg. Find horizontal distance.",
            "variables": {"height": "random.randint(10, 80)", "angle": "random.choice([30, 45, 60])"},
            "solver_code": "return round(height / math.tan(math.radians(angle)), 3)",
        },
        {
            "template": "Compute sin^2(theta)+cos^2(theta) for theta={angle} deg.",
            "variables": {"angle": "random.choice([0, 30, 45, 60, 90])"},
            "solver_code": "t = math.radians(angle); return round((math.sin(t)**2) + (math.cos(t)**2), 6)",
        },
    ],
    "circles": [
        {
            "template": "Find circumference and area of a circle with radius {r} cm.",
            "variables": {"r": "random.randint(2, 25)"},
            "solver_code": "return {'circumference': round(2*math.pi*r, 3), 'area': round(math.pi*(r**2), 3)}",
        },
        {
            "template": "From external point at distance {d} cm from center, radius is {r} cm. Find tangent length.",
            "variables": {"d": "random.randint(10, 40)", "r": "random.randint(2, 9)"},
            "solver_code": "return round(math.sqrt((d**2) - (r**2)), 3)",
        },
        {
            "template": "A chord subtends central angle {theta} deg in circle radius {r} cm. Find chord length.",
            "variables": {"theta": "random.choice([30, 45, 60, 90, 120])", "r": "random.randint(3, 20)"},
            "solver_code": "return round(2*r*math.sin(math.radians(theta/2)), 3)",
        },
    ],
    "mensuration": [
        {
            "template": "Find area of sector of radius {r} cm and angle {theta} deg.",
            "variables": {"r": "random.randint(4, 30)", "theta": "random.choice([30, 45, 60, 90, 120, 180])"},
            "solver_code": "return round((theta/360) * math.pi * (r**2), 3)",
        },
        {
            "template": "Find arc length for radius {r} cm and angle {theta} deg.",
            "variables": {"r": "random.randint(4, 30)", "theta": "random.choice([30, 45, 60, 90, 120, 180])"},
            "solver_code": "return round((theta/360) * 2*math.pi*r, 3)",
        },
        {
            "template": "A cylinder has radius {r} cm and height {h} cm. Find volume.",
            "variables": {"r": "random.randint(2, 20)", "h": "random.randint(5, 40)"},
            "solver_code": "return round(math.pi * (r**2) * h, 3)",
        },
    ],
    "statistics": [
        {
            "template": "For total sum {sum_x} and number of observations {n}, find mean.",
            "variables": {"sum_x": "random.randint(120, 1500)", "n": "random.randint(8, 50)"},
            "solver_code": "return round(sum_x / n, 3)",
        },
        {
            "template": "Class mark is midpoint of class {l}-{u}. Find class mark.",
            "variables": {"l": "random.randint(0, 70)", "u": "random.randint(71, 150)"},
            "solver_code": "return (l + u) / 2",
        },
        {
            "template": "In grouped data, estimated total is {total} and frequency sum is {freq}. Find mean.",
            "variables": {"total": "random.randint(300, 2500)", "freq": "random.randint(10, 80)"},
            "solver_code": "return round(total / freq, 3)",
        },
    ],
    "probability": [
        {
            "template": "If favorable outcomes are {favorable} out of total {total}, find probability.",
            "variables": {"favorable": "random.randint(1, 10)", "total": "random.randint(11, 30)"},
            "solver_code": "return round(favorable / total, 4)",
        },
        {
            "template": "Success probability in one trial is {p}. Find probability of at least one success in {n} trials.",
            "variables": {"p": "random.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])", "n": "random.randint(2, 6)"},
            "solver_code": "return round(1 - ((1 - p)**n), 4)",
        },
        {
            "template": "Probability of event A is {p}. Find probability of complement event A'.",
            "variables": {"p": "random.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75])"},
            "solver_code": "return round(1 - p, 4)",
        },
    ],
}


DIFFICULTY_CYCLE = ["Easy", "Medium", "Hard", "Medium"]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def infer_family(chapter: str, topic: str) -> str:
    text = f"{chapter} {topic}".lower()
    if "real number" in text:
        return "real_numbers"
    if "polynomial" in text:
        return "polynomials"
    if "linear equation" in text:
        return "linear"
    if "quadratic" in text:
        return "quadratic"
    if "arithmetic progression" in text:
        return "ap"
    if "coordinate" in text:
        return "coordinate"
    if "trig" in text:
        return "trig"
    if "circle" in text:
        return "circles"
    if "surface area" in text or "volume" in text or "areas related" in text:
        return "mensuration"
    if "construction" in text or "triangle" in text:
        return "geometry"
    if "statistics" in text:
        return "statistics"
    if "probability" in text:
        return "probability"
    return "geometry"


def build_fallback_pattern(chapter: str, topic: str, index: int) -> Dict[str, Any]:
    family = infer_family(chapter, topic)
    blueprints = FAMILY_BLUEPRINTS[family]
    blueprint = blueprints[index % len(blueprints)]

    pattern_id = f"cbse10_{slugify(chapter)}_{slugify(topic)}_{index + 1:03d}"
    return {
        "pattern_id": pattern_id,
        "chapter": chapter,
        "topic": topic,
        "difficulty": DIFFICULTY_CYCLE[index % len(DIFFICULTY_CYCLE)],
        "template": blueprint["template"],
        "variables": blueprint["variables"],
        "solver_code": blueprint["solver_code"],
    }


def extract_json_array(text: str) -> List[Dict[str, Any]]:
    content = text.strip()
    fenced = re.search(r"```json\s*(\[.*?\])\s*```", content, re.DOTALL)
    if fenced:
        content = fenced.group(1)

    if not content.startswith("["):
        any_array = re.search(r"(\[.*\])", content, re.DOTALL)
        if any_array:
            content = any_array.group(1)

    parsed = json.loads(content)
    if not isinstance(parsed, list):
        raise ValueError("Model output is not a JSON array")
    return parsed


def normalize_patterns(raw_patterns: List[Dict[str, Any]], chapter: str) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(raw_patterns):
        if not isinstance(item, dict):
            continue
        chapter_value = str(item.get("chapter") or chapter)
        topic_value = str(item.get("topic") or "General")
        pattern_id = str(item.get("pattern_id") or f"cbse10_{slugify(chapter_value)}_{idx + 1:03d}")
        difficulty = str(item.get("difficulty") or "Medium")
        template = str(item.get("template") or "").strip()
        variables = item.get("variables")
        solver_code = str(item.get("solver_code") or "").strip()

        if not template or not isinstance(variables, dict) or not solver_code:
            continue

        normalized.append(
            {
                "pattern_id": pattern_id,
                "chapter": chapter_value,
                "topic": topic_value,
                "difficulty": difficulty,
                "template": template,
                "variables": variables,
                "solver_code": solver_code,
            }
        )
    return normalized


def maybe_generate_with_gemini(
    chapter: str,
    topics: List[str],
    count: int,
    golden_template: Dict[str, Any],
    model_name: str,
) -> List[Dict[str, Any]]:
    try:
        from google import genai
    except Exception:
        return []

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
    except Exception:
        return []

    golden_template_json = json.dumps(golden_template, indent=2)
    topics_text = ", ".join(topics)

    prompt = (
        "I am building a procedural math engine.\n"
        f"Generate exactly {count} unique JSON patterns for CBSE Class 10 chapter '{chapter}'.\n"
        "Rules:\n"
        "1) Use this EXACT JSON structure for each item:\n"
        f"{golden_template_json}\n"
        "2) variables must contain valid Python random syntax.\n"
        "3) solver_code must be valid one-liners / short logic.\n"
        f"4) Cover these sub-topics: {topics_text}\n"
        "5) Output ONLY a valid JSON array. No extra text."
    )

    response = client.models.generate_content(model=model_name, contents=prompt)
    text = getattr(response, "text", "") or ""
    return normalize_patterns(extract_json_array(text), chapter=chapter)


def generate_chapter_patterns(
    chapter: str,
    subtopics: List[str],
    count_per_chapter: int,
    golden_template: Dict[str, Any],
    use_ai: bool,
    model_name: str,
) -> tuple[List[Dict[str, Any]], int, int]:
    chapter_patterns: List[Dict[str, Any]] = []
    ai_generated = 0

    if use_ai:
        try:
            chapter_patterns = maybe_generate_with_gemini(
                chapter=chapter,
                topics=subtopics,
                count=count_per_chapter,
                golden_template=golden_template,
                model_name=model_name,
            )
            ai_generated = len(chapter_patterns)
        except Exception:
            chapter_patterns = []
            ai_generated = 0

    if len(chapter_patterns) < count_per_chapter:
        for idx in range(len(chapter_patterns), count_per_chapter):
            topic = subtopics[idx % len(subtopics)]
            chapter_patterns.append(build_fallback_pattern(chapter, topic, idx))

    fallback_generated = count_per_chapter - ai_generated

    # Ensure stable IDs with chapter prefix and unique index.
    for idx, pattern in enumerate(chapter_patterns):
        pattern["pattern_id"] = f"cbse10_{slugify(chapter)}_{idx + 1:03d}"

    return chapter_patterns, ai_generated, fallback_generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate 200+ CBSE pattern JSON files")
    parser.add_argument("--count-per-chapter", type=int, default=16, help="Patterns per chapter")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="Gemini model name")
    parser.add_argument("--no-ai", action="store_true", help="Skip Gemini API calls")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with GOLDEN_TEMPLATE_PATH.open("r", encoding="utf-8") as file_obj:
        golden_template = json.load(file_obj)

    all_patterns: List[Dict[str, Any]] = []
    ai_total = 0
    fallback_total = 0
    for chapter, subtopics in CHAPTER_SUBTOPICS.items():
        patterns, ai_count, fallback_count = generate_chapter_patterns(
            chapter=chapter,
            subtopics=subtopics,
            count_per_chapter=args.count_per_chapter,
            golden_template=golden_template,
            use_ai=not args.no_ai,
            model_name=args.model,
        )
        ai_total += ai_count
        fallback_total += fallback_count
        all_patterns.extend(patterns)

        chapter_slug = slugify(chapter)
        chapter_file = OUTPUT_DIR / f"patterns_{chapter_slug}.json"
        with chapter_file.open("w", encoding="utf-8") as file_obj:
            json.dump(patterns, file_obj, indent=2)

    combined_file = OUTPUT_DIR / "all_patterns.json"
    with combined_file.open("w", encoding="utf-8") as file_obj:
        json.dump(all_patterns, file_obj, indent=2)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chapters": len(CHAPTER_SUBTOPICS),
        "patterns_per_chapter": args.count_per_chapter,
        "total_patterns": len(all_patterns),
        "ai_generated": ai_total,
        "fallback_generated": fallback_total,
        "output_dir": str(OUTPUT_DIR),
        "generation_mode": (
            "gemini+fallback"
            if ai_total > 0 and fallback_total > 0
            else "gemini-only"
            if ai_total > 0
            else "fallback-only"
        ),
    }
    with (OUTPUT_DIR / "manifest.json").open("w", encoding="utf-8") as file_obj:
        json.dump(manifest, file_obj, indent=2)

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
