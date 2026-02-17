"""
Bayesian Knowledge Tracing - Scientific mastery tracking

Replaces simple percentage-based mastery with probabilistic modeling.
Based on Bayesian Knowledge Tracing (Corbett & Anderson, 1994).

Each concept has a probability of mastery that updates after every student interaction.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BKTParameters:
    """Bayesian Knowledge Tracing model parameters"""
    p_learn: float = 0.15  # Probability of learning per opportunity
    p_guess: float = 0.25  # Probability of guessing correctly without knowing
    p_slip: float = 0.10   # Probability of slip (knowing but getting wrong)
    p_init: float = 0.30   # Initial probability of mastery


class BayesianKnowledgeTracer:
    """
    Tracks per-student, per-concept mastery using Bayesian updates.

    Instead of simple "% correct", this models the probability that a student
    has truly mastered a concept, accounting for guessing and slipping.

    Example:
        tracer = BayesianKnowledgeTracer()
        mastery = tracer.update_mastery(
            concept="quadratic_equations",
            prior_mastery=0.4,
            is_correct=True
        )
        # Returns updated probability (e.g., 0.52)
    """

    def __init__(self, params: Optional[BKTParameters] = None):
        self.params = params or BKTParameters()

    def update_mastery(
        self,
        concept: str,
        prior_mastery: float,
        is_correct: bool
    ) -> float:
        """
        Update mastery probability using Bayesian inference.

        Args:
            concept: Concept ID (e.g., "quadratic_equations")
            prior_mastery: Prior probability of mastery (0.0 to 1.0)
            is_correct: Whether the student answered correctly

        Returns:
            Updated mastery probability (0.0 to 1.0)
        """
        if is_correct:
            # P(mastery | correct answer)
            p_correct_if_mastered = 1 - self.params.p_slip
            p_correct_if_not = self.params.p_guess

            # P(correct) = P(mastered) * P(correct|mastered) + P(not) * P(correct|not)
            p_correct = (
                prior_mastery * p_correct_if_mastered +
                (1 - prior_mastery) * p_correct_if_not
            )

            # Bayes' theorem: P(mastered|correct) = P(mastered) * P(correct|mastered) / P(correct)
            posterior = (prior_mastery * p_correct_if_mastered) / p_correct if p_correct > 0 else prior_mastery
        else:
            # P(mastery | incorrect answer)
            p_wrong_if_mastered = self.params.p_slip
            p_wrong_if_not = 1 - self.params.p_guess

            p_wrong = (
                prior_mastery * p_wrong_if_mastered +
                (1 - prior_mastery) * p_wrong_if_not
            )

            posterior = (prior_mastery * p_wrong_if_mastered) / p_wrong if p_wrong > 0 else prior_mastery

        # Learning transition: P(mastered_next) = P(mastered_now) + P(not_mastered) * P(learn)
        updated_mastery = posterior + (1 - posterior) * self.params.p_learn

        # Bound to [0, 1]
        updated_mastery = max(0.0, min(1.0, updated_mastery))

        logger.debug(
            f"BKT update: {concept} | prior={prior_mastery:.3f} | "
            f"correct={is_correct} | posterior={updated_mastery:.3f}"
        )

        return updated_mastery

    def get_initial_mastery(self) -> float:
        """Get initial mastery probability for new concepts"""
        return self.params.p_init

    def predict_performance(self, mastery: float) -> float:
        """
        Predict probability of correct answer given current mastery.

        P(correct) = P(mastered) * P(correct|mastered) + P(not) * P(correct|not)
        """
        return mastery * (1 - self.params.p_slip) + (1 - mastery) * self.params.p_guess


# Global singleton instance
_tracer: Optional[BayesianKnowledgeTracer] = None


def get_knowledge_tracer() -> BayesianKnowledgeTracer:
    """Get global knowledge tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = BayesianKnowledgeTracer()
    return _tracer
