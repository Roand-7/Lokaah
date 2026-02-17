"""
Manim Animation Generator Service
Generates stunning visual explanations using Manim Community Edition

Prerequisites:
    pip install manim

Requires system dependencies:
    - ffmpeg (video rendering)
    - LaTeX (math formulas)

For production:
    - Pre-render common concepts
    - Use background tasks for on-demand rendering
    - Store videos in CDN (S3, Cloudflare R2, etc.)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class AnimationResult:
    """Result of animation generation"""
    success: bool
    video_path: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    concept: Optional[str] = None


class ManimGenerator:
    """
    Generates Manim animations for mathematical concepts

    Features:
    - Template library for common concepts (quadratic, trigonometry, etc.)
    - Caching to avoid re-rendering same concepts
    - Async rendering (doesn't block main thread)
    - Configurable quality (low/medium/high)
    """

    # Pre-defined Manim templates for common CBSE Class 10 concepts
    CONCEPT_TEMPLATES = {
        "quadratic_formula": """
from manim import *

class QuadraticFormula(Scene):
    def construct(self):
        # Title
        title = Text("Quadratic Formula", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.to_edge(UP))

        # General form
        eq_general = MathTex(r"ax^2 + bx + c = 0", font_size=42)
        self.play(Write(eq_general))
        self.wait(1)

        # Arrow to solution
        arrow = Arrow(start=DOWN, end=UP).next_to(eq_general, DOWN)
        self.play(GrowArrow(arrow))

        # Quadratic formula
        formula = MathTex(
            r"x = \\\\frac{-b \\\\pm \\\\sqrt{b^2 - 4ac}}{2a}",
            font_size=42,
            color=YELLOW
        ).next_to(arrow, DOWN)
        self.play(Write(formula))
        self.wait(1)

        # Discriminant highlight
        discriminant = MathTex(r"b^2 - 4ac", font_size=36, color=RED)
        disc_label = Text("Discriminant", font_size=24, color=RED)
        disc_group = VGroup(discriminant, disc_label.next_to(discriminant, DOWN))
        disc_group.to_edge(LEFT)

        self.play(FadeIn(disc_group))
        self.wait(1)

        # Interpretation
        cases = VGroup(
            Text("• > 0: Two real roots", font_size=24),
            Text("• = 0: One real root", font_size=24),
            Text("• < 0: No real roots", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(disc_group, DOWN)

        self.play(Write(cases))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))
""",
        "pythagoras_theorem": """
from manim import *

class PythagorasTheorem(Scene):
    def construct(self):
        # Title
        title = Text("Pythagoras Theorem", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.scale(0.6).to_edge(UP))

        # Right triangle
        A = np.array([-2, -1, 0])
        B = np.array([2, -1, 0])
        C = np.array([2, 2, 0])

        triangle = Polygon(A, B, C, color=WHITE, fill_opacity=0.2)
        self.play(Create(triangle))

        # Labels
        a_label = MathTex("a", color=RED).next_to(Line(B, C), RIGHT)
        b_label = MathTex("b", color=GREEN).next_to(Line(A, B), DOWN)
        c_label = MathTex("c", color=YELLOW).next_to(Line(A, C), LEFT)

        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(1)

        # Right angle marker
        right_angle = RightAngle(Line(A, B), Line(B, C), length=0.3)
        self.play(Create(right_angle))
        self.wait(1)

        # Formula
        formula = MathTex(
            "c^2", "=", "a^2", "+", "b^2",
            font_size=48,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(formula))
        self.wait(1)

        # Highlight each term
        self.play(Indicate(c_label), Indicate(formula[0]))
        self.wait(0.5)
        self.play(Indicate(a_label), Indicate(formula[2]))
        self.wait(0.5)
        self.play(Indicate(b_label), Indicate(formula[4]))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))
""",
        "linear_equation": """
from manim import *

class LinearEquation(Scene):
    def construct(self):
        # Title
        title = Text("Linear Equation: y = mx + c", font_size=44, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.scale(0.7).to_edge(UP))

        # Axes
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": True}
        ).shift(LEFT * 2)

        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))

        # Slope m = 2, intercept c = 1
        line = axes.plot(lambda x: 2*x + 1, color=YELLOW, x_range=[-2, 2])
        line_label = MathTex("y = 2x + 1", color=YELLOW, font_size=36).next_to(line, RIGHT, buff=0.5)

        self.play(Create(line), Write(line_label))
        self.wait(1)

        # Annotate slope
        slope_line = Line(
            axes.c2p(0, 1),
            axes.c2p(1, 3),
            color=RED
        )
        slope_label = MathTex("\\\\text{slope} = m = 2", color=RED, font_size=32).to_edge(RIGHT)

        self.play(Create(slope_line), Write(slope_label))
        self.wait(1)

        # Annotate y-intercept
        intercept_dot = Dot(axes.c2p(0, 1), color=GREEN)
        intercept_label = MathTex("c = 1", color=GREEN, font_size=32).next_to(slope_label, DOWN)

        self.play(Create(intercept_dot), Write(intercept_label))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))
""",
        "area_of_circle": """
from manim import *

class AreaOfCircle(Scene):
    def construct(self):
        # Title
        title = Text("Area of a Circle", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.scale(0.7).to_edge(UP))

        # Circle
        circle = Circle(radius=2, color=YELLOW, fill_opacity=0.3)
        self.play(Create(circle))

        # Radius
        radius_line = Line(ORIGIN, circle.point_at_angle(PI/4), color=RED)
        radius_label = MathTex("r", color=RED, font_size=36).next_to(radius_line, UP)

        self.play(Create(radius_line), Write(radius_label))
        self.wait(1)

        # Formula
        formula = MathTex(
            "A", "=", "\\\\pi", "r^2",
            font_size=48,
            color=YELLOW
        ).to_edge(DOWN)

        self.play(Write(formula))
        self.wait(1)

        # Highlight pi
        pi_value = MathTex("\\\\pi \\\\approx 3.14", font_size=32, color=GREEN).next_to(formula, DOWN)
        self.play(Write(pi_value))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))
"""
    }

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        quality: str = "medium_quality",  # low_quality, medium_quality, high_quality
        cache_enabled: bool = True
    ):
        """
        Initialize Manim generator

        Args:
            output_dir: Directory to store generated videos (defaults to temp)
            quality: Rendering quality (affects resolution and frame rate)
            cache_enabled: Whether to cache rendered videos
        """
        self.output_dir = output_dir or Path(tempfile.gettempdir()) / "lokaah_manim"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.quality = quality
        self.cache_enabled = cache_enabled

        # Quality settings
        self.quality_flags = {
            "low_quality": "-ql",      # 480p, 15fps
            "medium_quality": "-qm",   # 720p, 30fps
            "high_quality": "-qh"      # 1080p, 60fps
        }

        logger.info(f"ManimGenerator initialized: output_dir={self.output_dir}, quality={quality}")

    async def generate_animation(
        self,
        concept: str,
        custom_code: Optional[str] = None,
        background_color: str = "#1e1e1e"
    ) -> AnimationResult:
        """
        Generate Manim animation for a concept

        Args:
            concept: Concept name (must match CONCEPT_TEMPLATES key or provide custom_code)
            custom_code: Optional custom Manim scene code
            background_color: Background color (hex or color name)

        Returns:
            AnimationResult with video path or error
        """
        try:
            # Use template or custom code
            if custom_code:
                scene_code = custom_code
                cache_key = hashlib.md5(custom_code.encode()).hexdigest()
            elif concept in self.CONCEPT_TEMPLATES:
                scene_code = self.CONCEPT_TEMPLATES[concept]
                cache_key = f"template_{concept}"
            else:
                return AnimationResult(
                    success=False,
                    error=f"No template found for concept '{concept}'. Available: {list(self.CONCEPT_TEMPLATES.keys())}"
                )

            # Check cache
            if self.cache_enabled:
                cached_path = self.output_dir / f"{cache_key}.mp4"
                if cached_path.exists():
                    logger.info(f"Cache hit for concept '{concept}'")
                    return AnimationResult(
                        success=True,
                        video_path=str(cached_path),
                        concept=concept
                    )

            # Create temporary Python file
            temp_scene_file = self.output_dir / f"{cache_key}.py"
            with open(temp_scene_file, "w") as f:
                f.write(scene_code)

            # Extract scene class name (assumes first class definition)
            scene_class = self._extract_scene_class(scene_code)
            if not scene_class:
                return AnimationResult(
                    success=False,
                    error="Could not find Scene class in provided code"
                )

            # Render with Manim
            quality_flag = self.quality_flags.get(self.quality, "-qm")

            # Run Manim command asynchronously
            cmd = [
                "manim",
                quality_flag,
                "-o", f"{cache_key}.mp4",
                str(temp_scene_file),
                scene_class,
                "--disable_caching",
                "-c", background_color
            ]

            logger.info(f"Rendering animation: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.output_dir)
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown Manim error"
                logger.error(f"Manim rendering failed: {error_msg}")
                return AnimationResult(
                    success=False,
                    error=f"Manim rendering failed: {error_msg}"
                )

            # Find generated video (Manim outputs to media/videos/<quality>/)
            video_path = None
            media_dir = self.output_dir / "media" / "videos" / temp_scene_file.stem / self.quality.split("_")[0]

            if media_dir.exists():
                for video_file in media_dir.glob("*.mp4"):
                    video_path = video_file
                    break

            if not video_path or not video_path.exists():
                return AnimationResult(
                    success=False,
                    error="Manim rendered successfully but video file not found"
                )

            # Move to cache location
            final_path = self.output_dir / f"{cache_key}.mp4"
            video_path.rename(final_path)

            logger.info(f"Animation generated successfully: {final_path}")

            return AnimationResult(
                success=True,
                video_path=str(final_path),
                concept=concept
            )

        except FileNotFoundError:
            return AnimationResult(
                success=False,
                error="Manim not installed. Install with: pip install manim"
            )
        except Exception as exc:
            logger.exception(f"Error generating animation: {exc}")
            return AnimationResult(
                success=False,
                error=f"Error generating animation: {str(exc)}"
            )

    def _extract_scene_class(self, code: str) -> Optional[str]:
        """Extract scene class name from Manim code"""
        import re
        match = re.search(r'class\s+(\w+)\s*\(Scene\)', code)
        if match:
            return match.group(1)
        return None

    def list_available_concepts(self) -> list[str]:
        """List all pre-defined concept templates"""
        return list(self.CONCEPT_TEMPLATES.keys())

    def get_template(self, concept: str) -> Optional[str]:
        """Get template code for a concept"""
        return self.CONCEPT_TEMPLATES.get(concept)


# Singleton instance
_manim_generator: Optional[ManimGenerator] = None


def get_manim_generator(
    output_dir: Optional[Path] = None,
    quality: str = "medium_quality"
) -> ManimGenerator:
    """Get or create ManimGenerator singleton"""
    global _manim_generator
    if _manim_generator is None:
        _manim_generator = ManimGenerator(output_dir=output_dir, quality=quality)
    return _manim_generator
