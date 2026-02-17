"""
Populate CBSE Class 10 Math Topic Hierarchy
Creates all 60 topics in the database with proper structure
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db


# CBSE Class 10 Math Topic Hierarchy (60 topics total)
# Based on NCERT syllabus and official CBSE exam pattern

CBSE_CLASS_10_MATH_TOPICS = [
    # UNIT 1: NUMBER SYSTEMS (6 marks)
    {
        "code": "REAL_NUMBERS",
        "name": "Real Numbers",
        "parent_topic_id": None,
        "sequence_order": 1,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 1,
        "difficulty_avg": 0.4,
        "description": "Euclid's division lemma, HCF, LCM, fundamental theorem of arithmetic",
        "learning_objectives": [
            "Apply Euclid's division algorithm to find HCF",
            "Prove irrationality of numbers",
            "Understand fundamental theorem of arithmetic"
        ]
    },
    {
        "code": "EUCLIDS_DIVISION_LEMMA",
        "name": "Euclid's Division Lemma",
        "parent_topic_id": "REAL_NUMBERS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "FUNDAMENTAL_THEOREM_ARITHMETIC",
        "name": "Fundamental Theorem of Arithmetic",
        "parent_topic_id": "REAL_NUMBERS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "IRRATIONAL_NUMBERS",
        "name": "Irrational Numbers",
        "parent_topic_id": "REAL_NUMBERS",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },

    # UNIT 2: ALGEBRA (20 marks)
    # Chapter 2: Polynomials
    {
        "code": "POLYNOMIALS",
        "name": "Polynomials",
        "parent_topic_id": None,
        "sequence_order": 2,
        "depth_level": 0,
        "weightage_marks": 4,
        "ncert_chapter_number": 2,
        "difficulty_avg": 0.5,
        "description": "Zeros of polynomial, relationship between zeros and coefficients, division algorithm",
        "learning_objectives": [
            "Find zeros of quadratic polynomials",
            "Verify relationship between zeros and coefficients",
            "Apply division algorithm for polynomials"
        ]
    },
    {
        "code": "ZEROS_OF_POLYNOMIAL",
        "name": "Zeros of Polynomial",
        "parent_topic_id": "POLYNOMIALS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "RELATIONSHIP_ZEROS_COEFFICIENTS",
        "name": "Relationship between Zeros and Coefficients",
        "parent_topic_id": "POLYNOMIALS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },

    # Chapter 3: Linear Equations in Two Variables
    {
        "code": "LINEAR_EQUATIONS_TWO_VARIABLES",
        "name": "Pair of Linear Equations in Two Variables",
        "parent_topic_id": None,
        "sequence_order": 3,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 3,
        "difficulty_avg": 0.5,
        "description": "Graphical and algebraic solutions, consistency of equations",
        "learning_objectives": [
            "Solve pairs of equations graphically and algebraically",
            "Understand consistency and inconsistency",
            "Apply to real-life problems"
        ]
    },
    {
        "code": "GRAPHICAL_SOLUTION",
        "name": "Graphical Method",
        "parent_topic_id": "LINEAR_EQUATIONS_TWO_VARIABLES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "ALGEBRAIC_METHODS",
        "name": "Algebraic Methods (Substitution, Elimination, Cross Multiplication)",
        "parent_topic_id": "LINEAR_EQUATIONS_TWO_VARIABLES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.5
    },
    {
        "code": "CONSISTENCY_OF_EQUATIONS",
        "name": "Consistency of Equations",
        "parent_topic_id": "LINEAR_EQUATIONS_TWO_VARIABLES",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 1,
        "difficulty_avg": 0.6
    },

    # Chapter 4: Quadratic Equations
    {
        "code": "QUADRATIC_EQUATIONS",
        "name": "Quadratic Equations",
        "parent_topic_id": None,
        "sequence_order": 4,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 4,
        "difficulty_avg": 0.6,
        "description": "Standard form, solutions by factorization, completing the square, quadratic formula, discriminant",
        "learning_objectives": [
            "Solve quadratic equations by different methods",
            "Determine nature of roots using discriminant",
            "Apply to word problems"
        ]
    },
    {
        "code": "QUADRATIC_STANDARD_FORM",
        "name": "Standard Form of Quadratic Equation",
        "parent_topic_id": "QUADRATIC_EQUATIONS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 1,
        "difficulty_avg": 0.3
    },
    {
        "code": "QUADRATIC_FACTORIZATION",
        "name": "Solution by Factorization",
        "parent_topic_id": "QUADRATIC_EQUATIONS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "QUADRATIC_FORMULA",
        "name": "Quadratic Formula",
        "parent_topic_id": "QUADRATIC_EQUATIONS",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },
    {
        "code": "NATURE_OF_ROOTS",
        "name": "Nature of Roots (Discriminant)",
        "parent_topic_id": "QUADRATIC_EQUATIONS",
        "sequence_order": 4,
        "depth_level": 1,
        "weightage_marks": 1,
        "difficulty_avg": 0.5
    },

    # Chapter 5: Arithmetic Progressions
    {
        "code": "ARITHMETIC_PROGRESSIONS",
        "name": "Arithmetic Progressions",
        "parent_topic_id": None,
        "sequence_order": 5,
        "depth_level": 0,
        "weightage_marks": 4,
        "ncert_chapter_number": 5,
        "difficulty_avg": 0.5,
        "description": "nth term, sum of first n terms, applications",
        "learning_objectives": [
            "Find nth term of an AP",
            "Calculate sum of first n terms",
            "Solve real-world AP problems"
        ]
    },
    {
        "code": "AP_NTH_TERM",
        "name": "nth Term of AP",
        "parent_topic_id": "ARITHMETIC_PROGRESSIONS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "AP_SUM_N_TERMS",
        "name": "Sum of First n Terms",
        "parent_topic_id": "ARITHMETIC_PROGRESSIONS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },

    # UNIT 3: COORDINATE GEOMETRY (6 marks)
    {
        "code": "COORDINATE_GEOMETRY",
        "name": "Coordinate Geometry",
        "parent_topic_id": None,
        "sequence_order": 6,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 7,
        "difficulty_avg": 0.5,
        "description": "Distance formula, section formula, area of triangle",
        "learning_objectives": [
            "Apply distance formula",
            "Use section formula to find coordinates",
            "Calculate area of triangle using coordinates"
        ]
    },
    {
        "code": "DISTANCE_FORMULA",
        "name": "Distance Formula",
        "parent_topic_id": "COORDINATE_GEOMETRY",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "SECTION_FORMULA",
        "name": "Section Formula",
        "parent_topic_id": "COORDINATE_GEOMETRY",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },
    {
        "code": "AREA_OF_TRIANGLE",
        "name": "Area of Triangle",
        "parent_topic_id": "COORDINATE_GEOMETRY",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },

    # UNIT 4: GEOMETRY (15 marks)
    # Chapter 6: Triangles
    {
        "code": "TRIANGLES",
        "name": "Triangles",
        "parent_topic_id": None,
        "sequence_order": 7,
        "depth_level": 0,
        "weightage_marks": 8,
        "ncert_chapter_number": 6,
        "difficulty_avg": 0.6,
        "description": "Similarity, BPT, Pythagoras theorem, areas of similar triangles",
        "learning_objectives": [
            "Prove and apply Basic Proportionality Theorem",
            "Establish similarity criteria",
            "Apply Pythagoras theorem"
        ]
    },
    {
        "code": "SIMILAR_TRIANGLES",
        "name": "Similar Triangles",
        "parent_topic_id": "TRIANGLES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.6
    },
    {
        "code": "BPT_THEOREM",
        "name": "Basic Proportionality Theorem",
        "parent_topic_id": "TRIANGLES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.7
    },
    {
        "code": "PYTHAGORAS_THEOREM",
        "name": "Pythagoras Theorem",
        "parent_topic_id": "TRIANGLES",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.5
    },

    # Chapter 10: Circles
    {
        "code": "CIRCLES",
        "name": "Circles",
        "parent_topic_id": None,
        "sequence_order": 8,
        "depth_level": 0,
        "weightage_marks": 7,
        "ncert_chapter_number": 10,
        "difficulty_avg": 0.6,
        "description": "Tangent to circle, number of tangents from a point",
        "learning_objectives": [
            "Prove tangent perpendicular to radius",
            "Find length of tangent from external point",
            "Apply tangent properties to solve problems"
        ]
    },
    {
        "code": "TANGENT_PROPERTIES",
        "name": "Tangent Properties",
        "parent_topic_id": "CIRCLES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.5
    },
    {
        "code": "TANGENT_FROM_EXTERNAL_POINT",
        "name": "Tangents from External Point",
        "parent_topic_id": "CIRCLES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 4,
        "difficulty_avg": 0.7
    },

    # UNIT 5: TRIGONOMETRY (12 marks)
    {
        "code": "INTRODUCTION_TO_TRIGONOMETRY",
        "name": "Introduction to Trigonometry",
        "parent_topic_id": None,
        "sequence_order": 9,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 8,
        "difficulty_avg": 0.5,
        "description": "Trigonometric ratios, identities, standard angles",
        "learning_objectives": [
            "Define and calculate trigonometric ratios",
            "Prove and apply trigonometric identities",
            "Use standard angle values"
        ]
    },
    {
        "code": "TRIG_RATIOS",
        "name": "Trigonometric Ratios",
        "parent_topic_id": "INTRODUCTION_TO_TRIGONOMETRY",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "TRIG_IDENTITIES",
        "name": "Trigonometric Identities",
        "parent_topic_id": "INTRODUCTION_TO_TRIGONOMETRY",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },
    {
        "code": "TRIG_STANDARD_ANGLES",
        "name": "Trigonometric Ratios of Standard Angles",
        "parent_topic_id": "INTRODUCTION_TO_TRIGONOMETRY",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },

    {
        "code": "HEIGHTS_AND_DISTANCES",
        "name": "Some Applications of Trigonometry (Heights and Distances)",
        "parent_topic_id": None,
        "sequence_order": 10,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 9,
        "difficulty_avg": 0.6,
        "description": "Angle of elevation, angle of depression, applications",
        "learning_objectives": [
            "Identify angles of elevation and depression",
            "Apply trigonometry to real-world problems",
            "Solve height and distance problems"
        ]
    },
    {
        "code": "ANGLE_ELEVATION_DEPRESSION",
        "name": "Angles of Elevation and Depression",
        "parent_topic_id": "HEIGHTS_AND_DISTANCES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "HEIGHT_DISTANCE_APPLICATIONS",
        "name": "Height and Distance Applications",
        "parent_topic_id": "HEIGHTS_AND_DISTANCES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 4,
        "difficulty_avg": 0.7
    },

    # UNIT 6: MENSURATION (10 marks)
    {
        "code": "AREAS_RELATED_TO_CIRCLES",
        "name": "Areas Related to Circles",
        "parent_topic_id": None,
        "sequence_order": 11,
        "depth_level": 0,
        "weightage_marks": 4,
        "ncert_chapter_number": 12,
        "difficulty_avg": 0.5,
        "description": "Area of circle, sector, segment, combinations of plane figures",
        "learning_objectives": [
            "Calculate areas of sectors and segments",
            "Find areas of combinations of plane figures",
            "Solve real-world mensuration problems"
        ]
    },
    {
        "code": "CIRCLE_SECTOR_SEGMENT",
        "name": "Area of Sector and Segment",
        "parent_topic_id": "AREAS_RELATED_TO_CIRCLES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "COMBINATION_PLANE_FIGURES",
        "name": "Combinations of Plane Figures",
        "parent_topic_id": "AREAS_RELATED_TO_CIRCLES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },

    {
        "code": "SURFACE_AREAS_VOLUMES",
        "name": "Surface Areas and Volumes",
        "parent_topic_id": None,
        "sequence_order": 12,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 13,
        "difficulty_avg": 0.6,
        "description": "Surface areas and volumes of combinations of solids, conversion of solid from one shape to another",
        "learning_objectives": [
            "Calculate surface areas and volumes of combined solids",
            "Solve problems on conversion of solids",
            "Apply concepts to practical situations"
        ]
    },
    {
        "code": "COMBINATION_SOLIDS",
        "name": "Combination of Solids",
        "parent_topic_id": "SURFACE_AREAS_VOLUMES",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.6
    },
    {
        "code": "CONVERSION_OF_SOLIDS",
        "name": "Conversion of Solid from One Shape to Another",
        "parent_topic_id": "SURFACE_AREAS_VOLUMES",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 3,
        "difficulty_avg": 0.7
    },

    # UNIT 7: STATISTICS AND PROBABILITY (11 marks)
    {
        "code": "STATISTICS",
        "name": "Statistics",
        "parent_topic_id": None,
        "sequence_order": 13,
        "depth_level": 0,
        "weightage_marks": 6,
        "ncert_chapter_number": 14,
        "difficulty_avg": 0.5,
        "description": "Mean, median, mode of grouped data, cumulative frequency graph",
        "learning_objectives": [
            "Calculate mean, median, mode for grouped data",
            "Draw and interpret cumulative frequency graphs",
            "Analyze statistical data"
        ]
    },
    {
        "code": "MEAN_GROUPED_DATA",
        "name": "Mean of Grouped Data",
        "parent_topic_id": "STATISTICS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "MEDIAN_MODE_GROUPED_DATA",
        "name": "Median and Mode of Grouped Data",
        "parent_topic_id": "STATISTICS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.6
    },
    {
        "code": "CUMULATIVE_FREQUENCY",
        "name": "Cumulative Frequency Graph (Ogive)",
        "parent_topic_id": "STATISTICS",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },

    {
        "code": "PROBABILITY",
        "name": "Probability",
        "parent_topic_id": None,
        "sequence_order": 14,
        "depth_level": 0,
        "weightage_marks": 5,
        "ncert_chapter_number": 15,
        "difficulty_avg": 0.5,
        "description": "Classical probability, complementary events, simple problems",
        "learning_objectives": [
            "Calculate probability of events",
            "Apply probability to real situations",
            "Understand complementary events"
        ]
    },
    {
        "code": "CLASSICAL_PROBABILITY",
        "name": "Classical Probability",
        "parent_topic_id": "PROBABILITY",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.4
    },
    {
        "code": "COMPLEMENTARY_EVENTS",
        "name": "Complementary Events",
        "parent_topic_id": "PROBABILITY",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 2,
        "difficulty_avg": 0.5
    },
    {
        "code": "PROBABILITY_APPLICATIONS",
        "name": "Applications of Probability",
        "parent_topic_id": "PROBABILITY",
        "sequence_order": 3,
        "depth_level": 1,
        "weightage_marks": 1,
        "difficulty_avg": 0.6
    },

    # CONSTRUCTIONS (not in marks breakdown but part of syllabus)
    {
        "code": "CONSTRUCTIONS",
        "name": "Constructions",
        "parent_topic_id": None,
        "sequence_order": 15,
        "depth_level": 0,
        "weightage_marks": 0,
        "ncert_chapter_number": 11,
        "difficulty_avg": 0.6,
        "description": "Division of line segment, construction of tangents, similar triangles",
        "learning_objectives": [
            "Divide line segment in given ratio",
            "Construct tangents to circle",
            "Construct similar triangles"
        ]
    },
    {
        "code": "CONSTRUCTION_LINE_SEGMENT",
        "name": "Division of Line Segment",
        "parent_topic_id": "CONSTRUCTIONS",
        "sequence_order": 1,
        "depth_level": 1,
        "weightage_marks": 0,
        "difficulty_avg": 0.5
    },
    {
        "code": "CONSTRUCTION_TANGENTS",
        "name": "Construction of Tangents",
        "parent_topic_id": "CONSTRUCTIONS",
        "sequence_order": 2,
        "depth_level": 1,
        "weightage_marks": 0,
        "difficulty_avg": 0.7
    },
]


def populate_topics(curriculum_id: str):
    """Populate topics for CBSE Class 10 Math curriculum"""
    db = get_db()

    print("\n" + "="*60)
    print(f"POPULATING CBSE CLASS 10 MATH TOPICS")
    print("="*60)
    print(f"Curriculum ID: {curriculum_id}")
    print(f"Total topics to insert: {len(CBSE_CLASS_10_MATH_TOPICS)}")
    print("="*60 + "\n")

    # Store topic IDs for parent-child relationships
    topic_id_map = {}
    inserted_count = 0
    failed_count = 0

    for topic_data in CBSE_CLASS_10_MATH_TOPICS:
        try:
            # Prepare topic data
            topic = {
                "curriculum_id": curriculum_id,
                "code": topic_data["code"],
                "name": topic_data["name"],
                "display_names": {"en": topic_data["name"]},  # Start with English only
                "parent_topic_id": None,  # Will be set later if needed
                "sequence_order": topic_data["sequence_order"],
                "depth_level": topic_data["depth_level"],
                "weightage_marks": topic_data["weightage_marks"],
                "ncert_chapter_number": topic_data.get("ncert_chapter_number"),
                "difficulty_avg": topic_data["difficulty_avg"],
                "description": topic_data.get("description"),
                "learning_objectives": topic_data.get("learning_objectives", []),
                "prerequisites": topic_data.get("prerequisites", []),
                "is_active": True
            }

            # Resolve parent topic ID
            if topic_data.get("parent_topic_id"):
                parent_code = topic_data["parent_topic_id"]
                if parent_code in topic_id_map:
                    topic["parent_topic_id"] = topic_id_map[parent_code]
                else:
                    print(f"  [WARN] Parent topic {parent_code} not found for {topic_data['code']}")

            # Insert topic
            result = db.table('topics').insert(topic).execute()

            if result.data:
                topic_id = result.data[0]['id']
                topic_id_map[topic_data["code"]] = topic_id
                print(f"  [OK] {topic_data['code']}: {topic_data['name']}")
                inserted_count += 1
            else:
                print(f"  [FAIL] {topic_data['code']}: No data returned")
                failed_count += 1

        except Exception as e:
            print(f"  [ERROR] {topic_data['code']}: {e}")
            failed_count += 1

    print("\n" + "="*60)
    print("POPULATION COMPLETE")
    print("="*60)
    print(f"  Success: {inserted_count}")
    print(f"  Failed:  {failed_count}")
    print(f"  Total:   {len(CBSE_CLASS_10_MATH_TOPICS)}")
    print("="*60)


if __name__ == "__main__":
    # Get CBSE Class 10 Math curriculum ID from database
    # You can pass it as argument or fetch from database
    import sys

    if len(sys.argv) > 1:
        curriculum_id = sys.argv[1]
    else:
        print("Usage: python populate_cbse_topics.py <curriculum_id>")
        print("\nOR")
        print("Let me fetch the curriculum ID from database...")

        try:
            from app.curriculum import get_curriculum_manager
            from app.core.database import get_db

            db = get_db()
            cm = get_curriculum_manager(db)

            # This will work after running migration 002
            # For now, we'll use a placeholder
            curriculum_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

            print(f"\nUsing curriculum ID: {curriculum_id}")
            print("(Update this after running database migrations)")

        except Exception as e:
            print(f"\nError: {e}")
            print("\nPlease provide curriculum ID as argument:")
            print("  python populate_cbse_topics.py <curriculum_id>")
            sys.exit(1)

    populate_topics(curriculum_id)
