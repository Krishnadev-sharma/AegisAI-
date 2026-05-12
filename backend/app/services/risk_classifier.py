"""
Risk classification service for EU AI Act compliance.
"""
import logging
from typing import List, Tuple, Dict, Any

from app.schemas.ai_system import (
    RiskClassificationRequest,
    RiskClassificationResponse,
)
from app.models.ai_system import RiskLevel

logger = logging.getLogger(__name__)


class RiskClassifier:
    """Service for classifying AI systems based on EU AI Act criteria."""

    def classify(
        self, data: RiskClassificationRequest
    ) -> RiskClassificationResponse:
        """
        Classify the risk level of an AI system based on EU AI Act criteria.

        Args:
            data: Risk classification questionnaire response

        Returns:
            RiskClassificationResponse with risk level, confidence, and requirements

        Raises:
            ValueError: If classification data is invalid
        """
        reasons: List[str] = []
        requirements: List[str] = []
        next_steps: List[str] = []

        risk_level = RiskLevel.MINIMAL
        confidence = 0.9

        high_risk_indicators: List[str] = []

        # Check high-risk indicators
        high_risk_indicators, high_risk_reasons, high_risk_reqs = (
            self._check_high_risk_indicators(data)
        )

        reasons.extend(high_risk_reasons)
        requirements.extend(high_risk_reqs)

        # If any high-risk indicator found, classify as HIGH
        if high_risk_indicators:
            risk_level = RiskLevel.HIGH
            logger.info(
                f"System classified as HIGH risk. Indicators: {high_risk_indicators}"
            )
        else:
            # Check limited-risk indicators
            limited_risk_found, limited_risk_reasons, limited_risk_reqs = (
                self._check_limited_risk_indicators(data)
            )

            if limited_risk_found:
                risk_level = RiskLevel.LIMITED
                reasons.extend(limited_risk_reasons)
                requirements.extend(limited_risk_reqs)
                logger.info("System classified as LIMITED risk")
            else:
                reasons.append(
                    "System does not fall into high-risk "
                    "or limited-risk categories."
                )
                requirements.append("Voluntary codes of conduct encouraged.")
                logger.info("System classified as MINIMAL risk")

        # Determine next steps based on risk level
        next_steps = self._get_next_steps(risk_level)

        return RiskClassificationResponse(
            risk_level=risk_level,
            confidence=confidence,
            reasons=reasons,
            requirements=requirements,
            next_steps=next_steps,
        )

    def _check_high_risk_indicators(
        self, data: RiskClassificationRequest
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Check for high-risk indicators from Article 6 of EU AI Act.

        Args:
            data: Risk classification questionnaire response

        Returns:
            Tuple of (indicators, reasons, requirements)
        """
        indicators: List[str] = []
        reasons: List[str] = []
        requirements: List[str] = []

        # HR recruitment/management
        if data.hr_recruitment_screening or data.hr_promotion_termination:
            indicators.append("HR recruitment/management AI system")
            reasons.append(
                "AI systems used for recruitment or employment decisions are HIGH risk."
            )
            requirements.extend(
                [
                    "Implement risk management system",
                    "Ensure data governance and quality",
                    "Maintain technical documentation",
                    "Enable record-keeping/logging",
                    "Provide transparency to users",
                    "Enable human oversight",
                    "Ensure accuracy and robustness",
                ]
            )

        # Credit and insurance
        if data.credit_worthiness or data.insurance_risk_assessment:
            indicators.append("Credit/insurance assessment AI")
            reasons.append(
                "AI for creditworthiness or insurance assessment is HIGH risk."
            )
            requirements.extend(
                [
                    "Implement risk management system",
                    "Ensure data quality and governance",
                    "Provide decision transparency",
                    "Enable human review mechanisms",
                ]
            )

        # Safety components
        if data.is_safety_component:
            indicators.append("Safety component of a product")
            reasons.append(
                "AI used as a safety component requires HIGH risk compliance."
            )
            requirements.extend(
                [
                    "Conduct thorough risk assessments",
                    "Implement safety validation procedures",
                    "Maintain detailed technical documentation",
                ]
            )

        # Fundamental rights
        if data.affects_fundamental_rights:
            indicators.append("Affects fundamental rights")
            reasons.append("System impacts fundamental rights.")
            requirements.extend(
                [
                    "Ensure non-discrimination measures",
                    "Implement fairness assessments",
                    "Enable audit and logging",
                ]
            )

        # Law enforcement and justice
        if data.law_enforcement or data.border_control or data.justice_system:
            indicators.append("Law enforcement/justice system use")
            reasons.append("Use in law enforcement or justice is HIGH risk.")
            requirements.extend(
                [
                    "Strict human oversight requirements",
                    "Log all system operations",
                    "Regular bias and accuracy testing",
                    "Transparency to affected individuals",
                ]
            )

        # Biometric data
        if data.uses_biometric_data:
            indicators.append("Biometric data processing")
            reasons.append(
                "Systems processing biometric data for identification are HIGH risk."
            )
            requirements.extend(
                [
                    "Implement strict data protection",
                    "Enable user consent mechanisms",
                    "Provide audit trails",
                ]
            )

        return indicators, reasons, requirements

    def _check_limited_risk_indicators(
        self, data: RiskClassificationRequest
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Check for limited-risk indicators from Article 52 of EU AI Act.

        Args:
            data: Risk classification questionnaire response

        Returns:
            Tuple of (found, reasons, requirements)
        """
        reasons: List[str] = []
        requirements: List[str] = []

        if (
            data.interacts_with_humans
            or data.emotion_recognition
            or data.generates_synthetic_content
            or data.biometric_categorization
        ):

            if data.interacts_with_humans:
                reasons.append("System interacts directly with humans.")
                requirements.append(
                    "Inform users they are interacting with AI."
                )

            if data.emotion_recognition:
                reasons.append("System uses emotion recognition.")
                requirements.append(
                    "Inform subjects about emotion recognition."
                )

            if data.generates_synthetic_content:
                reasons.append("System generates synthetic content.")
                requirements.append("Label AI-generated content appropriately.")

            if data.biometric_categorization:
                reasons.append("System performs biometric categorization.")
                requirements.append(
                    "Disclose biometric categorization to users."
                )

            return True, reasons, requirements

        return False, [], []

    def _get_next_steps(self, risk_level: RiskLevel) -> List[str]:
        """
        Get recommended next steps based on risk level.

        Args:
            risk_level: The determined risk level

        Returns:
            List of recommended next steps
        """
        if risk_level == RiskLevel.HIGH:
            return [
                "Complete risk assessment questionnaire",
                "Document technical specifications",
                "Implement risk management system",
                "Establish governance procedures",
                "Set up human oversight mechanisms",
                "Schedule compliance review",
            ]

        elif risk_level == RiskLevel.LIMITED:
            return [
                "Implement transparency notices",
                "Document disclosure mechanisms",
                "Review user interaction points",
                "Plan transparency implementation",
            ]

        else:  # MINIMAL
            return [
                "Consider voluntary compliance measures",
                "Monitor regulatory updates",
                "Document governance practices",
            ]

    def compute_assessment_scores(
        self, data: RiskClassificationRequest, risk_level: RiskLevel
    ) -> Dict[str, int]:
        """
        Compute detailed compliance scores based on questionnaire responses.

        Args:
            data: Risk classification questionnaire response
            risk_level: The determined risk level

        Returns:
            Dictionary with various compliance scores (0-100)
        """
        # Base overall score based on risk level
        overall_score_map = {
            RiskLevel.MINIMAL: 80,
            RiskLevel.LIMITED: 50,
            RiskLevel.HIGH: 20,
            RiskLevel.UNACCEPTABLE: 0,
        }
        overall_score = overall_score_map.get(risk_level, 0)

        # Data governance score (0-100)
        data_governance_score = 60
        if data.uses_biometric_data:
            data_governance_score -= 20
        if data.makes_automated_decisions:
            data_governance_score -= 10

        # Transparency score (0-100)
        transparency_score = 70
        if not data.interacts_with_humans:
            transparency_score -= 20
        if data.emotion_recognition or data.generates_synthetic_content:
            transparency_score -= 15

        # Human oversight score (0-100)
        human_oversight_score = 75
        if data.law_enforcement or data.justice_system or data.credit_worthiness:
            human_oversight_score -= 30

        # Robustness score (0-100)
        robustness_score = 65
        if data.is_safety_component:
            robustness_score -= 25
        if data.affects_fundamental_rights:
            robustness_score -= 15

        return {
            "overall_score": overall_score,
            "data_governance_score": data_governance_score,
            "transparency_score": transparency_score,
            "human_oversight_score": human_oversight_score,
            "robustness_score": robustness_score,
        }
