"""
TRUE AI ORACLE - 50% of Hybrid System
Generates infinite unique questions with verified math + JSXGraph visuals
"""

import os
import json
import logging
from google import genai
import math
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.oracle.secure_sandbox import SafeMathSandbox, SandboxError
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AIQuestionResult:
    """Structured output from AI Oracle"""
    question_text: str
    solution_steps: List[str]
    final_answer: str
    variables: Dict
    jsxgraph_code: Optional[str]
    difficulty: float
    marks: int
    concept_tags: List[str]


class TrueAIOracle:
    """
    AI Assessment Agent - Infinite Question Generation
    Uses Gemini for scenarios, Python for calculations
    """
    
    def __init__(self):
        self.sandbox = SafeMathSandbox()
        
        # Initialize Gemini using API key or default credentials.
        gemini_key = settings.GEMINI_API_KEY
        try:
            if gemini_key:
                self.gemini = genai.Client(api_key=gemini_key)
                logger.info("TrueAIOracle Gemini client initialized via API key.")
            elif settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_CLOUD_PROJECT:
                os.environ.setdefault(
                    "GOOGLE_APPLICATION_CREDENTIALS",
                    settings.GOOGLE_APPLICATION_CREDENTIALS,
                )
                self.gemini = genai.Client(
                    vertexai=True,
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location=settings.GOOGLE_CLOUD_LOCATION,
                )
                logger.info("TrueAIOracle Gemini client initialized via Vertex AI credentials.")
            else:
                raise ValueError("Missing Gemini auth configuration.")
            self.gemini_available = True
        except Exception as e:
            logger.warning("TrueAIOracle Gemini initialization failed: %s", e)
            self.gemini = None
            self.gemini_available = False
             
        # Cost tracking
        self.generation_count = 0
        self.api_cost_estimate = 0.0
    
    def generate_question(
        self,
        concept: str,
        marks: int,
        difficulty: float,
        student_context: Optional[Dict] = None
    ) -> AIQuestionResult:
        """
        Main generation pipeline: AI scenario â†’ Python calculation â†’ JSXGraph visual
        """
        self.generation_count += 1
        
        # Step 1: AI generates scenario + raw parameters
        scenario = self._ai_generate_scenario(concept, marks, difficulty, student_context)
        
        # Step 2: Python calculates (deterministic, 100% accurate)
        calculation = self._calculate_answer(scenario, concept)
        
        # Step 3: AI generates JSXGraph if geometry concept
        jsxgraph = None
        if self._needs_visual(concept):
            jsxgraph = self._ai_generate_jsxgraph(scenario, calculation, concept)
        
        # Step 4: Compile final result
        result = AIQuestionResult(
            question_text=scenario["question_text"],
            solution_steps=calculation["steps"],
            final_answer=calculation["final_answer"],
            variables=scenario["variables"],
            jsxgraph_code=jsxgraph,
            difficulty=difficulty,
            marks=marks,
            concept_tags=[concept]
        )
        
        return result
    
    def _ai_generate_scenario(
        self, 
        concept: str, 
        marks: int, 
        difficulty: float,
        context: Optional[Dict]
    ) -> Dict:
        """
        AI creates unique scenario + parameters (never calculates)
        """
        
        # Define required variables for each concept
        concept_variables = {
            "trigonometry_heights": {
                "required": ["hypotenuse", "angle_degrees"],
                "example": '{"hypotenuse": 50, "angle_degrees": 60}'
            },
            "trigonometry_distances": {
                "required": ["height", "angle_degrees"],
                "example": '{"height": 30, "angle_degrees": 45}'
            },
            "coordinate_geometry_distance": {
                "required": ["x1", "y1", "x2", "y2"],
                "example": '{"x1": 2, "y1": 3, "x2": 5, "y2": 7}'
            },
            "quadratic_roots": {
                "required": ["a", "b", "c"],
                "example": '{"a": 1, "b": -5, "c": 6}'
            }
        }
        
        var_spec = concept_variables.get(concept, {
            "required": ["value1", "value2"],
            "example": '{"value1": 10, "value2": 20}'
        })
        
        # Build constraint-aware prompt
        prompt = f"""You are a CBSE Class 10 Mathematics question creator.

TASK: Create a UNIQUE question scenario for:
- Concept: {concept}
- Marks: {marks}
- Difficulty: {difficulty}/1.0
- Student level: {"Needs simpler numbers" if difficulty < 0.4 else "Standard" if difficulty < 0.7 else "Advanced"}

CRITICAL RULES:
1. Create INDIAN context (Delhi Metro, cricket, Qutub Minar, kite flying, etc.)
2. Use Indian names (Rahul, Priya, Amit, Neha)
3. NEVER calculate the answer - only provide raw variables
4. Make scenario UNIQUE (not from any textbook)
5. Include "show your work" for 3+ marks
6. MUST use EXACT variable names: {var_spec["required"]}
7. USE ACTUAL NUMBERS in question text, NOT placeholders like [hypotenuse] or 'angle_degrees'
8. NEVER output variable names like 'angle_degrees' or 'hypotenuse' - only the actual values

OUTPUT FORMAT (Strict JSON):
{{
    "question_text": "Complete CBSE-style question text...",
    "variables": {var_spec["example"]},
    "unknown": "what_to_find",
    "formula_hint": "which_formula_to_use",
    "scenario_type": "real_world_context"
}}

Example for "trigonometry_heights":
{{
    "question_text": "Rahul is flying a kite at India Gate. The string is 50m long and makes 60° with the ground. Find the height of the kite. (Use √3 = 1.73)",
    "variables": {{
        "hypotenuse": 50,
        "angle_degrees": 60
    }},
    "unknown": "height_of_kite",
    "formula_hint": "sin(theta) = opposite/hypotenuse",
    "scenario_type": "kite_flying_monument"
}}

Generate for concept: {concept}"""
        
        # Use Gemini only
        if not self.gemini:
            raise ValueError(
                "Gemini not available. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS."
            )
        
        try:
            response = self.gemini.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={
                    'temperature': 0.9,
                    'max_output_tokens': 4096
                }
            )
            
            # Get full text from response
            if hasattr(response, 'text'):
                text = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                text = response.candidates[0].content.parts[0].text.strip()
            else:
                raise ValueError(f"Unable to extract text from Gemini response: {response}")
            
            self.api_cost_estimate += 0.0005  # Gemini cost
        except Exception as e:
            raise ValueError(f"Gemini generation failed: {e}")
        
        return self._extract_json(text)
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from AI response with multiple fallback strategies"""
        import json
        import re
        
        if not text or not text.strip():
            return self._fallback_question()
        
        text = text.strip()
        
        # Strategy 1: Find JSON in markdown code blocks
        patterns = [
            r'```json\s*(.*?)\s*```',  # JSON block
            r'```\s*(\{.*?\})\s*```',   # Any code block with JSON
            r'(\{.*?\})',               # Raw JSON object (greedy)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Clean up common AI errors
                    cleaned = match.strip()
                    cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas
                    cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas in arrays
                    cleaned = cleaned.replace("'", '"')  # Replace single quotes
                    return json.loads(cleaned)
                except:
                    continue
        
        # Strategy 2: Try to extract anything between first { and last }
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
                # Aggressive cleaning
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Remove control chars
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # Remove trailing commas
                json_str = json_str.replace('\\', '\\\\')  # Fix escaping
                return json.loads(json_str)
        except Exception as e:
            print(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Return fallback
        print("Warning: JSON parsing failed. Using fallback.")
        print(f"Raw response preview: {text[:300]}...")
        return self._fallback_question()

    def _fallback_question(self) -> dict:
        """Return a safe fallback question if AI fails"""
        return {
            "question_text": "A student is standing 20m away from a building and looks up at a 60Â° angle to see the top. Find the height of the building.",
            "variables": {
                "base_distance": 20.0,
                "angle_degrees": 60.0,
                "hypotenuse": None,
                "opposite": None
            },
            "solution_steps": [
                "Identify: tan(Î¸) = opposite/adjacent",
                "tan(60Â°) = height/20",
                "height = 20 Ã— tan(60Â°)",
                "height = 20 Ã— 1.732 = 34.64m"
            ],
            "correct_answer": {
                "value": 34.64,
                "tolerance": 0.01,
                "unit": "meters"
            },
            "jsxgraph_code": "// Basic triangle visualization\nvar board = JXG.JSXGraph.initBoard('jxgbox', {boundingbox: [-5, 40, 25, -5], axis: true});\nvar A = board.create('point', [0, 0], {name: 'A', fixed: true});\nvar B = board.create('point', [20, 0], {name: 'B', fixed: true});\nvar C = board.create('point', [20, 34.64], {name: 'C', fixed: false, size: 5, color: 'red'});\nboard.create('polygon', [A, B, C], {fillColor: 'lightblue', fillOpacity: 0.3});\nboard.create('angle', [A, B, C], {name: '60Â°'});"
        }

    def _calculate_answer(self, scenario: Dict, concept: str) -> Dict:
        """
        PYTHON calculates - AI never does math (guaranteed accuracy)
        """
        vars = scenario["variables"]

        # If scenario includes dynamic solver code, run it in restricted sandbox.
        solver_code = scenario.get("solver_code")
        if solver_code:
            logger.info(
                "oracle_solver_execution concept=%s mode=sandbox vars=%s",
                concept,
                ",".join(sorted(vars.keys())[:20]),
            )
            try:
                value = self.sandbox.execute_solver(solver_code, context=dict(vars))
                logger.info("oracle_solver_execution success concept=%s result=%r", concept, value)
                return {
                    "steps": [
                        "Executed solver logic inside restricted sandbox.",
                        f"Computed value: {value}",
                    ],
                    "final_answer": str(value),
                    "numeric_answer": value,
                }
            except (SandboxError, ValueError) as exc:
                logger.warning("oracle_solver_execution failed concept=%s error=%s", concept, exc)
                raise ValueError(f"Sandbox solver execution failed: {exc}") from exc
        
        # Route to appropriate calculator
        calculators = {
            "trigonometry_heights": self._calc_trig_heights,
            "trigonometry_distances": self._calc_trig_heights,
            "quadratic_roots": self._calc_quadratic,
            "quadratic_nature": self._calc_quadratic_nature,
            "linear_equations": self._calc_linear,
            "arithmetic_progression": self._calc_ap,
            "circles_tangent": self._calc_circle_tangent,
            "coordinate_distance": self._calc_coord_distance,
            "coordinate_section": self._calc_coord_section,
            "triangles_similarity": self._calc_triangle_similarity,
            "mensuration_sector": self._calc_mensuration,
            "probability_basic": self._calc_probability,
            "statistics_mean": self._calc_statistics_mean,
        }
        
        calculator = calculators.get(concept, self._calc_generic)
        return calculator(vars)
    
    def _calc_trig_heights(self, vars: Dict) -> Dict:
        """Deterministic trigonometry calculator"""
        if "hypotenuse" in vars or "string_length" in vars:
            # Height scenario (given hypotenuse and angle, find height)
            hyp = vars.get("hypotenuse") or vars.get("string_length")
            angle = vars["angle_degrees"]
            angle_rad = math.radians(angle)
            
            height = hyp * math.sin(angle_rad)
            
            return {
                "steps": [
                    f"Given: String length (hypotenuse) = {hyp}m",
                    f"Angle with ground = {angle}Â°",
                    f"We need to find height (opposite side)",
                    f"Using sin Î¸ = opposite/hypotenuse",
                    f"sin {angle}Â° = height / {hyp}",
                    f"height = {hyp} Ã— sin({angle}Â°)",
                    f"height = {hyp} Ã— {math.sin(angle_rad):.4f}",
                    f"height = {height:.2f}m"
                ],
                "final_answer": f"{height:.2f}m",
                "numeric_answer": round(height, 2)
            }
        else:
            # Distance scenario (given height and angle, find distance)
            height = vars["height"]
            angle = vars["angle_degrees"]
            angle_rad = math.radians(angle)
            
            distance = height / math.tan(angle_rad)
            
            return {
                "steps": [
                    f"Given: Height = {height}m, Angle = {angle}Â°",
                    f"Using tan Î¸ = opposite/adjacent",
                    f"tan {angle}Â° = {height} / distance",
                    f"distance = {height} / tan({angle}Â°)",
                    f"distance = {height} / {math.tan(angle_rad):.4f}",
                    f"distance = {distance:.2f}m"
                ],
                "final_answer": f"{distance:.2f}m",
                "numeric_answer": round(distance, 2)
            }
    
    def _calc_quadratic(self, vars: Dict) -> Dict:
        """Solve axÂ² + bx + c = 0"""
        a = vars.get("a", 1)
        b = vars.get("b", 0)
        c = vars.get("c", 0)
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return {
                "steps": [
                    f"Equation: {a}xÂ² + {b}x + {c} = 0",
                    f"Discriminant D = bÂ² - 4ac",
                    f"D = {b}Â² - 4({a})({c})",
                    f"D = {discriminant}",
                    "Since D < 0, roots are imaginary (no real roots)"
                ],
                "final_answer": "No real roots",
                "numeric_answer": None
            }
        
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        
        return {
            "steps": [
                f"Equation: {a}xÂ² + {b}x + {c} = 0",
                f"a = {a}, b = {b}, c = {c}",
                f"Discriminant D = {b}Â² - 4({a})({c}) = {discriminant}",
                f"Using quadratic formula: x = [-b Â± âˆšD] / 2a",
                f"x = [{-b} Â± âˆš{discriminant}] / {2*a}",
                f"x = ({-b} + {math.sqrt(discriminant):.2f}) / {2*a} = {root1:.2f}",
                f"x = ({-b} - {math.sqrt(discriminant):.2f}) / {2*a} = {root2:.2f}"
            ],
            "final_answer": f"x = {root1:.2f} or x = {root2:.2f}",
            "numeric_answer": [round(root1, 2), round(root2, 2)]
        }
    
    def _calc_linear(self, vars: Dict) -> Dict:
        """Solve system of linear equations"""
        a1, b1, c1 = vars["a1"], vars["b1"], vars["c1"]
        a2, b2, c2 = vars["a2"], vars["b2"], vars["c2"]
        
        # Using cross-multiplication
        x = (b1*c2 - b2*c1) / (a1*b2 - a2*b1)
        y = (c1*a2 - c2*a1) / (a1*b2 - a2*b1)
        
        return {
            "steps": [
                f"Equations: {a1}x + {b1}y = {c1} and {a2}x + {b2}y = {c2}",
                f"Using cross-multiplication:",
                f"x / (b1Â·c2 - b2Â·c1) = y / (c1Â·a2 - c2Â·a1) = 1 / (a1Â·b2 - a2Â·b1)",
                f"x / ({b1*c2} - {b2*c1}) = y / ({c1*a2} - {c2*a1}) = 1 / ({a1*b2} - {a2*b1})",
                f"x / {b1*c2 - b2*c1} = y / {c1*a2 - c2*a1} = 1 / {a1*b2 - a2*b1}",
                f"x = {x:.2f}, y = {y:.2f}"
            ],
            "final_answer": f"x = {x:.2f}, y = {y:.2f}",
            "numeric_answer": {"x": round(x, 2), "y": round(y, 2)}
        }
    
    def _calc_ap(self, vars: Dict) -> Dict:
        """Arithmetic Progression calculations"""
        a = vars["first_term"]
        d = vars["common_difference"]
        n = vars["n"]
        
        # nth term
        nth_term = a + (n-1)*d
        
        # Sum of n terms
        sum_n = (n/2) * (2*a + (n-1)*d)
        
        return {
            "steps": [
                f"Given: First term a = {a}, d = {d}, n = {n}",
                f"nth term: a_n = a + (n-1)d",
                f"a_{n} = {a} + ({n}-1)Ã—{d}",
                f"a_{n} = {a} + {(n-1)*d} = {nth_term}",
                f"Sum: S_n = (n/2)[2a + (n-1)d]",
                f"S_{n} = ({n}/2)[2Ã—{a} + ({n}-1)Ã—{d}]",
                f"S_{n} = {sum_n}"
            ],
            "final_answer": f"a_{n} = {nth_term}, S_{n} = {int(sum_n)}",
            "numeric_answer": {"nth_term": nth_term, "sum": sum_n}
        }
    
    def _calc_generic(self, vars: Dict) -> Dict:
        """Fallback - summarizes given values in plain language instead of dumping raw dict"""
        given_parts = [f"{k} = {v}" for k, v in vars.items() if v is not None]
        given_text = ", ".join(given_parts) if given_parts else "the given values"
        return {
            "steps": [
                f"Given: {given_text}",
                "Apply the relevant formula from the chapter",
                "Substitute values and simplify step by step"
            ],
            "final_answer": "Solve using the steps above",
            "numeric_answer": None
        }

    def _calc_circle_tangent(self, vars: Dict) -> Dict:
        """Circle tangent properties"""
        radius = vars.get("radius", vars.get("r", 5))
        distance = vars.get("distance", vars.get("d", 13))
        tangent_length = math.sqrt(distance**2 - radius**2)
        return {
            "steps": [
                f"Given: Radius = {radius}, Distance from centre to external point = {distance}",
                "Tangent is perpendicular to radius at point of contact",
                f"By Pythagoras: tangent^2 = distance^2 - radius^2",
                f"tangent^2 = {distance}^2 - {radius}^2 = {distance**2 - radius**2}",
                f"tangent = {tangent_length:.2f}"
            ],
            "final_answer": f"{tangent_length:.2f}",
            "numeric_answer": round(tangent_length, 2)
        }

    def _calc_coord_distance(self, vars: Dict) -> Dict:
        """Distance between two points"""
        x1 = vars.get("x1", 0)
        y1 = vars.get("y1", 0)
        x2 = vars.get("x2", 3)
        y2 = vars.get("y2", 4)
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return {
            "steps": [
                f"Points: ({x1}, {y1}) and ({x2}, {y2})",
                f"Distance = sqrt[({x2}-{x1})^2 + ({y2}-{y1})^2]",
                f"= sqrt[{(x2-x1)**2} + {(y2-y1)**2}]",
                f"= sqrt[{(x2-x1)**2 + (y2-y1)**2}]",
                f"= {dist:.2f} units"
            ],
            "final_answer": f"{dist:.2f} units",
            "numeric_answer": round(dist, 2)
        }

    def _calc_coord_section(self, vars: Dict) -> Dict:
        """Section formula"""
        x1, y1 = vars.get("x1", 0), vars.get("y1", 0)
        x2, y2 = vars.get("x2", 6), vars.get("y2", 8)
        m, n = vars.get("m", 1), vars.get("n", 1)
        px = (m * x2 + n * x1) / (m + n)
        py = (m * y2 + n * y1) / (m + n)
        return {
            "steps": [
                f"Points: ({x1}, {y1}) and ({x2}, {y2}), ratio {m}:{n}",
                f"x = (m*x2 + n*x1)/(m+n) = ({m}*{x2} + {n}*{x1})/({m}+{n}) = {px:.2f}",
                f"y = (m*y2 + n*y1)/(m+n) = ({m}*{y2} + {n}*{y1})/({m}+{n}) = {py:.2f}",
                f"Point = ({px:.2f}, {py:.2f})"
            ],
            "final_answer": f"({px:.2f}, {py:.2f})",
            "numeric_answer": {"x": round(px, 2), "y": round(py, 2)}
        }

    def _calc_triangle_similarity(self, vars: Dict) -> Dict:
        """Similar triangles - find unknown side"""
        a1 = vars.get("side_a1", vars.get("a1", 3))
        b1 = vars.get("side_b1", vars.get("b1", 4))
        a2 = vars.get("side_a2", vars.get("a2", 6))
        b2 = a2 * b1 / a1
        return {
            "steps": [
                f"By similarity, corresponding sides are proportional",
                f"{a1}/{a2} = {b1}/x",
                f"x = {a2} * {b1} / {a1}",
                f"x = {b2:.2f}"
            ],
            "final_answer": f"{b2:.2f}",
            "numeric_answer": round(b2, 2)
        }

    def _calc_mensuration(self, vars: Dict) -> Dict:
        """Sector area and arc length"""
        r = vars.get("radius", vars.get("r", 7))
        theta = vars.get("angle", vars.get("theta", 60))
        area = (theta / 360) * math.pi * r**2
        arc = (theta / 360) * 2 * math.pi * r
        return {
            "steps": [
                f"Given: radius = {r}, angle = {theta} deg",
                f"Area of sector = (theta/360) * pi * r^2",
                f"= ({theta}/360) * pi * {r}^2",
                f"= {area:.2f} sq units",
                f"Arc length = (theta/360) * 2*pi*r = {arc:.2f} units"
            ],
            "final_answer": f"Area = {area:.2f} sq units, Arc = {arc:.2f} units",
            "numeric_answer": {"area": round(area, 2), "arc": round(arc, 2)}
        }

    def _calc_probability(self, vars: Dict) -> Dict:
        """Basic probability"""
        favorable = vars.get("favorable", vars.get("f", 4))
        total = vars.get("total", vars.get("n", 52))
        prob = favorable / total
        return {
            "steps": [
                f"Favorable outcomes = {favorable}",
                f"Total outcomes = {total}",
                f"P(E) = favorable/total = {favorable}/{total}",
                f"P(E) = {prob:.4f}" if prob != int(prob) else f"P(E) = {favorable}/{total}"
            ],
            "final_answer": f"{favorable}/{total}" if favorable != total else "1",
            "numeric_answer": round(prob, 4)
        }

    def _calc_statistics_mean(self, vars: Dict) -> Dict:
        """Mean from frequency table"""
        values = vars.get("values", vars.get("xi", [10, 20, 30]))
        freqs = vars.get("frequencies", vars.get("fi", [5, 8, 7]))
        if not isinstance(values, list):
            return self._calc_generic(vars)
        total_fi = sum(freqs)
        total_fixi = sum(v * f for v, f in zip(values, freqs))
        mean = total_fixi / total_fi
        return {
            "steps": [
                f"Sum of fi = {total_fi}",
                f"Sum of fi*xi = {total_fixi}",
                f"Mean = Sum(fi*xi) / Sum(fi) = {total_fixi}/{total_fi}",
                f"Mean = {mean:.2f}"
            ],
            "final_answer": f"{mean:.2f}",
            "numeric_answer": round(mean, 2)
        }

    _calc_quadratic_nature = _calc_quadratic
    
    def _ai_generate_jsxgraph(self, scenario: Dict, calculation: Dict, concept: str) -> str:
        """
        AI generates interactive JSXGraph visualization
        """
        vars = scenario["variables"]
        
        # Build prompt for visual
        prompt = f"""Create JSXGraph JavaScript code for an interactive diagram.

CONCEPT: {concept}
QUESTION: {scenario["question_text"]}
VARIABLES: {json.dumps(vars)}
ANSWER: {calculation["final_answer"]}

REQUIREMENTS:
1. Create a DIV with id="jxgbox" and class="jxgbox"
2. Use JXG.JSXGraph.initBoard to create board
3. Draw the geometric scenario accurately
4. Show given values as labels
5. Make it interactive (student can drag points if applicable)
6. Include the calculated answer visually
7. Use proper mathematical notation

Return ONLY the complete HTML/JS code that can be embedded directly.
Example structure:
<div id="jxgbox" class="jxgbox" style="width:400px; height:400px;"></div>
<script type="text/javascript">
    var board = JXG.JSXGraph.initBoard('jxgbox', {{boundingbox: [-5, 10, 10, -5], axis:true}});
    // ... drawing code ...
</script>"""
        
        try:
            if self.gemini:
                response = self.gemini.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config={
                        'temperature': 0.8,
                        'max_output_tokens': 1500
                    }
                )
                return response.text.strip()
            else:
                raise ValueError("Gemini not available for JSXGraph generation")
        except Exception as e:
            print(f"JSXGraph generation failed: {e}")
            return None
    
    def _needs_visual(self, concept: str) -> bool:
        """Check if concept benefits from diagram"""
        visual_concepts = [
            "trigonometry", "geometry", "circles", "triangles", 
            "coordinate", "mensuration", "construction"
        ]
        return any(v in concept.lower() for v in visual_concepts)
    
    def get_stats(self) -> Dict:
        """Return generation statistics"""
        return {
            "questions_generated": self.generation_count,
            "estimated_api_cost_usd": round(self.api_cost_estimate, 4),
            "gemini_available": self.gemini is not None
        }


# Test function
if __name__ == "__main__":
    oracle = TrueAIOracle()
    
    # Test generation
    result = oracle.generate_question(
        concept="trigonometry_heights",
        marks=3,
        difficulty=0.6
    )
    
    print("\n" + "="*60)
    print("TRUE AI ORACLE TEST")
    print("="*60)
    print(f"\nQuestion: {result.question_text}")
    print(f"\nSolution: {' -> '.join(result.solution_steps)}")
    print(f"\nAnswer: {result.final_answer}")
    print(f"\nVisual: {'âœ“ Generated' if result.jsxgraph_code else 'âœ— Not needed'}")
    print(f"\nStats: {oracle.get_stats()}")


