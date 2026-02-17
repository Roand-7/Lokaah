"""
DYNAMIC PATTERN MANAGEMENT SYSTEM
Eliminates tech debt by storing patterns as JSON configs
Auto-generates new patterns using AI
Version-controlled syllabus updates
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import random
import math

from app.oracle.secure_sandbox import SafeMathSandbox, SandboxError


@dataclass
class PatternTemplate:
    """Lightweight pattern definition - no code required"""
    pattern_id: str
    topic: str
    marks: int
    difficulty: float
    template_text: str  # "Find the nature of roots of x² - {b}x + {c} = 0"
    variables: Dict[str, Dict]  # Variable definitions with ranges
    solution_template: List[str]  # Step-by-step template
    answer_template: str  # "{nature_of_roots} (D={discriminant})"
    socratic_hints: List[Dict]
    validation_rules: List[str]  # Python expressions for validation
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


class PatternManager:
    """
    Central pattern registry - manages all 60+ patterns as JSON
    No more hardcoded Python generators!
    """
    
    def __init__(self, patterns_dir: str = "app/oracle/patterns"):
        self.patterns_dir = Path(patterns_dir)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, PatternTemplate] = {}
        self.sandbox = SafeMathSandbox()
        self._load_all_patterns()
    
    def _load_all_patterns(self):
        """Load all pattern JSON files"""
        for file_path in self.patterns_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Remove non-dataclass fields
                    data.pop('_note', None)
                    pattern = PatternTemplate(**data)
                    self._cache[pattern.pattern_id] = pattern
            except Exception as e:
                print(f"[WARN] Failed to load {file_path}: {e}")

        print(f"[OK] Loaded {len(self._cache)} patterns from {self.patterns_dir}")
    
    def get_pattern(self, pattern_id: str) -> Optional[PatternTemplate]:
        """Get pattern by ID"""
        return self._cache.get(pattern_id)
    
    def find_patterns(self, topic: str = None, marks: int = None) -> List[PatternTemplate]:
        """Find patterns by criteria"""
        results = []
        for pattern in self._cache.values():
            if topic and pattern.topic != topic:
                continue
            if marks and pattern.marks != marks:
                continue
            results.append(pattern)
        return results
    
    def generate_question(self, pattern_id: str) -> Dict:
        """
        Generate question from pattern template
        NO HARDCODED PYTHON - pure template rendering
        """
        pattern = self._cache.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_id}")
        
        # Generate random variables
        variables = self._generate_variables(pattern.variables)
        
        # Build context for expression rendering.
        context = {**variables, 'math': math}
        
        # Render template
        question_text = self._render_template(pattern.template_text, context)
        
        # Render solution steps
        solution_steps = []
        for step in pattern.solution_template:
            try:
                rendered = self._render_template(step, context)
                solution_steps.append(rendered)
            except:
                solution_steps.append(step)
        
        # Render answer
        try:
            final_answer = self._render_template(pattern.answer_template, context)
        except:
            final_answer = pattern.answer_template
        
        # Validate
        is_valid = self._validate(variables, pattern.validation_rules, context)
        if not is_valid:
            # Retry with new variables
            return self.generate_question(pattern_id)
        
        return {
            "question_id": f"PAT_{pattern_id}_{random.randint(1000,9999)}",
            "pattern_id": pattern_id,
            "topic": pattern.topic,
            "question_text": question_text,
            "solution_steps": solution_steps,
            "final_answer": final_answer,
            "marks": pattern.marks,
            "difficulty": pattern.difficulty,
            "variables": variables,
            "socratic_hints": pattern.socratic_hints,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_variables(self, var_specs: Dict) -> Dict:
        """Generate random variables based on specs"""
        variables = {}
        pending_calculated = {}
        for var_name, spec in var_specs.items():
            var_type = spec.get('type', 'int')
            
            if var_type == 'int':
                min_val = spec.get('min', 1)
                max_val = spec.get('max', 100)
                variables[var_name] = random.randint(min_val, max_val)
            
            elif var_type == 'float':
                min_val = spec.get('min', 1.0)
                max_val = spec.get('max', 100.0)
                decimals = spec.get('decimals', 2)
                variables[var_name] = round(random.uniform(min_val, max_val), decimals)
            
            elif var_type == 'choice':
                choices = spec.get('choices', [1, 2, 3])
                variables[var_name] = random.choice(choices)
            
            elif var_type == 'calculated':
                # Variable depends on others
                formula = spec.get('formula', '{a} + {b}')
                pending_calculated[var_name] = formula
        
        # Resolve dependent variables in multiple passes.
        for _ in range(max(1, len(pending_calculated))):
            resolved_in_pass = False
            for var_name in list(pending_calculated.keys()):
                formula = pending_calculated[var_name]
                try:
                    rendered = formula.format(**variables)
                except KeyError:
                    continue

                variables[var_name] = self.sandbox.evaluate_expression(
                    rendered, context=variables
                )
                del pending_calculated[var_name]
                resolved_in_pass = True

            if not pending_calculated:
                break
            if not resolved_in_pass:
                unresolved = ", ".join(sorted(pending_calculated.keys()))
                raise ValueError(f"Unresolved calculated variables: {unresolved}")
        
        return variables
    
    def _validate(self, variables: Dict, rules: List[str], context: Dict) -> bool:
        """Validate generated variables against rules"""
        for rule in rules:
            try:
                rendered_rule = rule.format(**variables)
                if not self.sandbox.evaluate_boolean(
                    rendered_rule, context={**context, **variables}
                ):
                    return False
            except (SandboxError, KeyError, ValueError):
                return False
        return True

    def _render_template(self, text: str, context: Dict[str, Any]) -> str:
        """Render placeholders; supports inline expressions inside {...}."""
        def replace(match: re.Match) -> str:
            expression = match.group(1).strip()
            try:
                value = self.sandbox.evaluate_expression(expression, context=context)
                return str(value)
            except Exception:
                if expression in context:
                    return str(context[expression])
                return match.group(0)

        return re.sub(r"{([^{}]+)}", replace, text)
    
    def add_pattern(self, pattern: PatternTemplate) -> bool:
        """Add new pattern (JSON only, no Python code!)"""
        file_path = self.patterns_dir / f"{pattern.pattern_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(pattern), f, indent=2, ensure_ascii=False)
        
        self._cache[pattern.pattern_id] = pattern
        print(f"✅ Added pattern: {pattern.pattern_id}")
        return True
    
    def update_pattern(self, pattern_id: str, updates: Dict) -> bool:
        """Update existing pattern"""
        if pattern_id not in self._cache:
            return False
        
        pattern = self._cache[pattern_id]
        
        for key, value in updates.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)
        
        pattern.updated_at = datetime.now().isoformat()
        
        # Save
        file_path = self.patterns_dir / f"{pattern_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(pattern), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated pattern: {pattern_id}")
        return True
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Soft delete by archiving"""
        if pattern_id not in self._cache:
            return False
        
        # Move to archive
        archive_dir = self.patterns_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        src = self.patterns_dir / f"{pattern_id}.json"
        dst = archive_dir / f"{pattern_id}_{datetime.now().strftime('%Y%m%d')}.json"
        
        src.rename(dst)
        del self._cache[pattern_id]
        
        print(f"✅ Archived pattern: {pattern_id}")
        return True
    
    def get_stats(self) -> Dict:
        """Pattern statistics"""
        topics = {}
        for p in self._cache.values():
            topics[p.topic] = topics.get(p.topic, 0) + 1
        
        return {
            "total_patterns": len(self._cache),
            "topics": topics,
            "last_updated": max(p.updated_at for p in self._cache.values()) if self._cache else None
        }


# ==========================================
# AUTO-GENERATION: AI creates patterns from examples
# ==========================================

class PatternAutoGenerator:
    """
    Uses AI to convert example questions into pattern templates
    Reduces pattern creation time from hours to minutes
    """
    
    def __init__(self):
        try:
            from google import genai
            gemini_key = os.getenv("GEMINI_API_KEY")
            self.gemini = genai.Client(api_key=gemini_key) if gemini_key else None
        except Exception as exc:
            print(f"Warning: Gemini initialization failed in PatternAutoGenerator: {exc}")
            self.gemini = None
    
    def create_pattern_from_example(self, example_question: str, topic: str, marks: int) -> PatternTemplate:
        """
        AI analyzes example and creates pattern template
        Example: "Find nature of roots of x² - 4x + 4 = 0" → PatternTemplate
        """
        
        prompt = f"""Analyze this CBSE Class 10 question and create a pattern template.

EXAMPLE QUESTION:
{example_question}

TOPIC: {topic}
MARKS: {marks}

Create a JSON pattern template with:
1. Variable definitions (what numbers can change)
2. Template text with {{placeholders}}
3. Solution steps
4. Validation rules

OUTPUT FORMAT (strict JSON):
{{
    "template_text": "Find the nature of roots of x² - {{b}}x + {{c}} = 0",
    "variables": {{
        "b": {{"type": "int", "min": 2, "max": 20}},
        "c": {{"type": "int", "min": 1, "max": 100}}
    }},
    "solution_template": [
        "Given equation: x² - {{b}}x + {{c}} = 0",
        "Compare with ax² + bx + c = 0: a=1, b={{b}}, c={{c}}",
        "Discriminant D = b² - 4ac = {{b}}² - 4(1)({{c}})",
        "D = {{discriminant}}",
        "Since D {{comparison}}, roots are {{nature}}"
    ],
    "answer_template": "{{nature_of_roots}} (D={{discriminant}})",
    "validation_rules": [
        "{{discriminant}} >= 0"  # Ensure real roots
    ],
    "socratic_hints": [
        {{"level": 1, "hint": "What is the discriminant formula?", "nudge": "D = b² - 4ac"}},
        {{"level": 2, "hint": "Calculate D first", "nudge": "Substitute values in D = b² - 4ac"}},
        {{"level": 3, "hint": "Check D value", "nudge": "D>0: distinct, D=0: equal, D<0: imaginary"}}
    ]
}}"""
        
        if not self.gemini:
            raise ValueError("Gemini not available for auto-generation")
        
        try:
            response = self.gemini.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt,
                config={'temperature': 0.3, 'max_output_tokens': 2000}
            )
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                pattern_id = f"{topic.lower().replace(' ', '_')}_{marks}m_{random.randint(100,999)}"
                
                return PatternTemplate(
                    pattern_id=pattern_id,
                    topic=topic,
                    marks=marks,
                    difficulty=0.5,
                    **data
                )
        except Exception as e:
            print(f"⚠️ Auto-generation failed: {e}")
            raise


# ==========================================
# EXAMPLE PATTERN JSON FILES
# ==========================================

EXAMPLE_PATTERNS = {
    "quadratic_nature_of_roots.json": {
        "pattern_id": "quadratic_nature_of_roots",
        "topic": "Quadratic Equations",
        "marks": 2,
        "difficulty": 0.5,
        "template_text": "Find the nature of roots of the quadratic equation x² - {b}x + {c} = 0.",
        "variables": {
            "b": {"type": "int", "min": 2, "max": 20},
            "c": {"type": "int", "min": 1, "max": 50},
            "discriminant": {"type": "calculated", "formula": "{b}**2 - 4*{c}"},
            "nature": {"type": "calculated", "formula": "'equal' if {discriminant} == 0 else ('distinct real' if {discriminant} > 0 else 'imaginary')"}
        },
        "solution_template": [
            "Given equation: x² - {b}x + {c} = 0",
            "Comparing with ax² + bx + c = 0: a = 1, b = -{b}, c = {c}",
            "Discriminant D = b² - 4ac",
            "D = (-{b})² - 4(1)({c})",
            "D = {b**2} - {4*c}",
            "D = {discriminant}",
            "Since D {'> 0' if {discriminant} > 0 else '= 0' if {discriminant} == 0 else '< 0'}, the roots are {nature}."
        ],
        "answer_template": "The roots are {nature} (D = {discriminant})",
        "validation_rules": [
            "{discriminant} >= 0"  # Only real roots for Class 10
        ],
        "socratic_hints": [
            {"level": 1, "hint": "What is the discriminant formula?", "nudge": "D = b² - 4ac"},
            {"level": 2, "hint": "Calculate the value of D", "nudge": "Substitute a=1, b={b}, c={c}"},
            {"level": 3, "hint": "Check the value of D", "nudge": "D > 0: distinct, D = 0: equal, D < 0: imaginary"}
        ]
    }
}


# Initialize patterns directory with examples
def init_patterns_directory():
    """Create initial pattern files"""
    patterns_dir = Path("app/oracle/patterns")
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, data in EXAMPLE_PATTERNS.items():
        file_path = patterns_dir / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Created: {filename}")


# Test
if __name__ == "__main__":
    init_patterns_directory()
    
    pm = PatternManager()
    
    # Generate a question
    result = pm.generate_question("quadratic_nature_of_roots")
    
    print("\n" + "="*60)
    print("DYNAMIC PATTERN GENERATION")
    print("="*60)
    print(f"\nQuestion: {result['question_text']}")
    print(f"\nSolution:")
    for step in result['solution_steps']:
        print(f"  → {step}")
    print(f"\nAnswer: {result['final_answer']}")
    print(f"\nStats: {pm.get_stats()}")
