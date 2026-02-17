"""
CBSE Mathematics Paper Pattern Extractor
Extracts questions, topics, marks from exam papers
Output: JSON file with all patterns for ORACLE engine
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import pdfplumber


@dataclass
class Question:
    """Represents a single question from exam paper"""
    question_number: int
    question_text: str
    marks: int
    section: str  # A, B, C, D, E
    question_type: str  # MCQ, VSA, SA, LA, Case Study
    topic: str  # Identified topic
    year: int
    paper_code: str  # 30 (Standard) or 430 (Basic)
    series: str  # 1/1/1, 2/1/1, etc.


class PDFExtractor:
    """Extracts questions from CBSE PDF papers"""

    def __init__(self, pdf_folder: str):
        self.pdf_folder = Path(pdf_folder)
        self.questions: List[Question] = []

        # Topic keywords for classification
        self.topic_keywords = {
            "Real Numbers": [
                "real number", "rational", "irrational", "hcf", "lcm", "prime", "composite",
                "decimal", "fundamental theorem"
            ],
            "Polynomials": ["polynomial", "zeros", "zeroes", "quadratic polynomial", "cubic", "degree"],
            "Pair of Linear Equations": [
                "linear equation", "pair of equations", "consistent", "inconsistent",
                "substitution", "elimination"
            ],
            "Quadratic Equations": ["quadratic equation", "discriminant", "roots", "factorization", "quadratic formula"],
            "Arithmetic Progressions": ["arithmetic progression", "a.p.", "common difference", "nth term", "sum of n terms"],
            "Coordinate Geometry": ["coordinate", "distance formula", "section formula", "midpoint", "collinear"],
            "Triangles": ["triangle", "similar", "congruent", "pythagoras", "bpt", "basic proportionality"],
            "Circles": ["circle", "tangent", "chord", "arc", "sector", "segment"],
            "Trigonometry": [
                "trigonometry", "trigonometric", "sin", "cos", "tan",
                "angle of elevation", "angle of depression"
            ],
            "Mensuration": ["surface area", "volume", "cylinder", "cone", "sphere", "hemisphere", "frustum"],
            "Statistics": ["statistics", "mean", "median", "mode", "frequency", "cumulative"],
            "Probability": ["probability", "random", "dice", "coin", "card", "event"]
        }

    def parse_filename(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from filename"""
        # Examples: 30-1-1_2022_Maths_Standard.pdf, 430-1-1_2024_MATHEMATICS (BASIC).pdf

        metadata = {
            "paper_code": None,
            "series": None,
            "year": None,
            "type": None
        }

        # Extract paper code (30 or 430)
        if filename.startswith("430"):
            metadata["paper_code"] = "430"
            metadata["type"] = "Basic"
        elif filename.startswith("30"):
            metadata["paper_code"] = "30"
            metadata["type"] = "Standard"

        # Extract series (1-1-1, 2-1-1, etc.)
        series_match = re.search(r"(\d+)[_-](\d+)[_-](\d+)", filename)
        if series_match:
            metadata["series"] = f"{series_match.group(1)}/{series_match.group(2)}/{series_match.group(3)}"

        # Extract year
        year_match = re.search(r"(20\d{2})", filename)
        if year_match:
            metadata["year"] = int(year_match.group(1))

        return metadata

    def classify_topic(self, text: str) -> str:
        """Classify question topic based on keywords"""
        text_lower = text.lower()

        # Count keyword matches for each topic
        topic_scores = {}
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return "Unknown"

    def extract_questions_from_pdf(self, pdf_path: Path) -> List[Question]:
        """Extract all questions from a single PDF"""
        questions = []
        metadata = self.parse_filename(pdf_path.name)

        if not metadata["year"]:
            print(f"Skipping {pdf_path.name} - could not parse year")
            return questions

        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""

                # Extract questions (pattern: question number followed by text)
                # Matches: "1.", "21.", "Q.1", etc.
                question_pattern = r"(?:^|\n)(\d{1,2})\.?\s+(.+?)(?=\n\d{1,2}\.|\nSECTION|\n\n|$)"
                matches = re.finditer(question_pattern, full_text, re.DOTALL | re.MULTILINE)

                for match in matches:
                    q_num = int(match.group(1))
                    q_text = match.group(2).strip()

                    # Skip if too short (likely not a real question)
                    if len(q_text) < 20:
                        continue

                    # Determine marks (look for common patterns)
                    marks = self.extract_marks(q_text)

                    # Determine section and type based on question number
                    section, q_type = self.determine_section_type(q_num)

                    # Classify topic
                    topic = self.classify_topic(q_text)

                    question = Question(
                        question_number=q_num,
                        question_text=q_text[:500],
                        marks=marks,
                        section=section,
                        question_type=q_type,
                        topic=topic,
                        year=metadata["year"],
                        paper_code=metadata["paper_code"],
                        series=metadata["series"] or "Unknown"
                    )
                    questions.append(question)

        except Exception as e:
            print(f"Error processing {pdf_path.name}: {str(e)}")

        return questions

    def extract_marks(self, text: str) -> int:
        """Extract marks allocation from question text"""
        # Patterns like: [1 mark], (2 marks), 3m, etc.
        marks_pattern = r"[\[\(]?(\d)\s*marks?[\]\)]?|(\d)\s*m\b"
        match = re.search(marks_pattern, text.lower())
        if match:
            return int(match.group(1) or match.group(2))
        return 1

    def determine_section_type(self, q_num: int) -> tuple:
        """Determine section and question type based on question number"""
        if 1 <= q_num <= 20:
            return "A", "MCQ"
        if 21 <= q_num <= 25:
            return "B", "VSA"
        if 26 <= q_num <= 31:
            return "C", "SA"
        if 32 <= q_num <= 35:
            return "D", "LA"
        if 36 <= q_num <= 38:
            return "E", "Case Study"
        return "Unknown", "Unknown"

    def process_all_pdfs(self):
        """Process all PDFs in the folder"""
        pdf_files = list(self.pdf_folder.glob("*.pdf"))
        total = len(pdf_files)

        print(f"Found {total} PDF files to process\n")

        for idx, pdf_path in enumerate(pdf_files, 1):
            print(f"[{idx}/{total}] Processing: {pdf_path.name}")
            questions = self.extract_questions_from_pdf(pdf_path)
            self.questions.extend(questions)
            print(f"  Extracted {len(questions)} questions")

        print(f"Total questions extracted: {len(self.questions)}")

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze extracted questions to find patterns"""
        topic_frequency = {}
        for q in self.questions:
            topic_frequency[q.topic] = topic_frequency.get(q.topic, 0) + 1

        year_distribution = {}
        for q in self.questions:
            year_distribution[q.year] = year_distribution.get(q.year, 0) + 1

        marks_distribution = {}
        for q in self.questions:
            marks_distribution[q.marks] = marks_distribution.get(q.marks, 0) + 1

        analysis = {
            "total_questions": len(self.questions),
            "topic_frequency": dict(sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)),
            "year_distribution": dict(sorted(year_distribution.items())),
            "marks_distribution": dict(sorted(marks_distribution.items())),
            "papers_processed": len(set(q.year for q in self.questions))
        }

        return analysis

    def export_to_json(self, output_path: Path):
        """Export all data to JSON"""
        questions_data = [asdict(q) for q in self.questions]
        analysis = self.analyze_patterns()

        output = {
            "metadata": {
                "total_papers_processed": len(set((q.year, q.series) for q in self.questions)),
                "extraction_date": "2026-02-11",
                "source": "CBSE Mathematics Class X Board Papers"
            },
            "analysis": analysis,
            "questions": questions_data
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")


def main():
    """Main execution"""
    print("=" * 60)
    print("CBSE Mathematics Paper Pattern Extractor")
    print("=" * 60)

    pdf_folder = Path(__file__).parent.parent / "content" / "exam_papers" / "raw"
    output_folder = Path(__file__).parent.parent / "content" / "exam_papers" / "extracted"
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "patterns_extracted.json"

    print(f"Input folder:  {pdf_folder}")
    print(f"Output folder: {output_folder}")

    extractor = PDFExtractor(str(pdf_folder))
    extractor.process_all_pdfs()
    extractor.export_to_json(output_file)

    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Next step: copy contents of {output_file.name}")
    print("and paste into your analysis workflow")


if __name__ == "__main__":
    main()
