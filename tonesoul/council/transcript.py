"""
Council Transcript Logger

P2 Issue 10: Output a complete council transcript for each verdict.

The transcript provides:
- Full traceability for audits
- Debugging information
- Research data collection

Usage:
    from tonesoul.council.transcript import CouncilTranscriptLogger, TranscriptFormat

    logger = CouncilTranscriptLogger()

    # After council validation
    verdict = council.validate(draft, context, intent)
    transcript = logger.create_transcript(draft, context, intent, votes, coherence, verdict)

    # Output in various formats
    print(transcript.to_json())
    print(transcript.to_markdown())
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Union

from .types import PerspectiveType


class TranscriptFormat(Enum):
    """Output formats for council transcripts"""

    JSON = "json"
    MARKDOWN = "markdown"
    YAML = "yaml"


@dataclass
class VoteRecord:
    """Record of a single perspective vote"""

    perspective_name: Union[PerspectiveType, str]
    decision: str  # APPROVE, CONCERN, OBJECT, ABSTAIN
    confidence: float
    reasoning: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CoherenceRecord:
    """Record of coherence calculation"""

    c_inter: float
    approval_rate: float
    min_confidence: float
    has_strong_objection: bool


@dataclass
class VerdictRecord:
    """Record of final verdict"""

    decision: str  # APPROVE, REFINE, DECLARE_STANCE, BLOCK
    summary: str
    consensus_points: List[str] = field(default_factory=list)
    divergence_points: List[str] = field(default_factory=list)
    risks_identified: List[str] = field(default_factory=list)


@dataclass
class CouncilTranscript:
    """Complete transcript of a council deliberation session"""

    # Required fields (no defaults) - must come first
    transcript_id: str
    timestamp: str
    input_hash: str  # Hash of input for privacy
    input_preview: str  # First 100 chars
    input_length: int

    # Optional fields (with defaults)
    version: str = "1.0.0"
    context_keys: List[str] = field(default_factory=list)
    user_intent: Optional[str] = None
    votes: List[VoteRecord] = field(default_factory=list)
    coherence: Optional[CoherenceRecord] = None
    verdict: Optional[VerdictRecord] = None
    processing_time_ms: int = 0

    def to_json(self, indent: int = 2) -> str:
        """Export transcript as JSON"""
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Export transcript as readable Markdown"""
        lines = [
            f"# Council Transcript: {self.transcript_id}",
            f"> Generated: {self.timestamp}",
            "",
            "## Input Summary",
            f"- **Preview**: {self.input_preview}",
            f"- **Length**: {self.input_length} chars",
            f"- **Hash**: `{self.input_hash[:16]}...`",
            f"- **User Intent**: {self.user_intent or 'Not specified'}",
            "",
            "## Perspective Votes",
            "",
        ]

        for vote in self.votes:
            emoji = {"APPROVE": "✅", "CONCERN": "⚠️", "OBJECT": "❌", "ABSTAIN": "⏸️"}.get(
                vote.decision, "❓"
            )
            lines.extend(
                [
                    f"### {vote.perspective_name} {emoji}",
                    f"- **Decision**: {vote.decision}",
                    f"- **Confidence**: {vote.confidence:.2f}",
                    f"- **Reasoning**: {vote.reasoning}",
                    "",
                ]
            )

        if self.coherence:
            lines.extend(
                [
                    "## Coherence Analysis",
                    f"- **C_inter**: {self.coherence.c_inter:.3f}",
                    f"- **Approval Rate**: {self.coherence.approval_rate:.2f}",
                    f"- **Min Confidence**: {self.coherence.min_confidence:.2f}",
                    f"- **Strong Objection**: {'Yes' if self.coherence.has_strong_objection else 'No'}",
                    "",
                ]
            )

        if self.verdict:
            verdict_emoji = {
                "APPROVE": "✅",
                "REFINE": "🔄",
                "DECLARE_STANCE": "⚖️",
                "BLOCK": "🚫",
            }.get(self.verdict.decision, "❓")
            lines.extend(
                [
                    f"## Final Verdict: {self.verdict.decision} {verdict_emoji}",
                    f"**Summary**: {self.verdict.summary}",
                    "",
                ]
            )

            if self.verdict.consensus_points:
                lines.append("### Consensus Points")
                for point in self.verdict.consensus_points:
                    lines.append(f"- {point}")
                lines.append("")

            if self.verdict.divergence_points:
                lines.append("### Divergence Points")
                for point in self.verdict.divergence_points:
                    lines.append(f"- {point}")
                lines.append("")

            if self.verdict.risks_identified:
                lines.append("### Identified Risks")
                for risk in self.verdict.risks_identified:
                    lines.append(f"- ⚠️ {risk}")
                lines.append("")

        lines.extend(
            [
                "---",
                f"*Processing time: {self.processing_time_ms}ms*",
            ]
        )

        return "\n".join(lines)


class CouncilTranscriptLogger:
    """Logger for creating and storing council transcripts"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path("./council_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _generate_transcript_id(self) -> str:
        """Generate unique transcript ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"TC-{timestamp}"

    def _hash_input(self, text: str) -> str:
        """Create hash of input for privacy"""
        return hashlib.sha256(text.encode()).hexdigest()

    def create_transcript(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str],
        votes: List[Any],  # List of PerspectiveVote
        coherence: Any,  # CoherenceScore
        verdict: Any,  # CouncilVerdict
        processing_time_ms: int = 0,
    ) -> CouncilTranscript:
        """
        Create a complete transcript from council deliberation results.

        Args:
            draft_output: The original input text
            context: Context dictionary
            user_intent: User's stated intent (if any)
            votes: List of PerspectiveVote objects
            coherence: CoherenceScore object
            verdict: CouncilVerdict object
            processing_time_ms: Time taken for processing

        Returns:
            CouncilTranscript object
        """
        # Convert votes to records
        vote_records = []
        for v in votes:
            perspective_value = getattr(
                v,
                "perspective",
                getattr(v, "perspective_name", None),
            )
            if isinstance(perspective_value, PerspectiveType):
                perspective_name = perspective_value.value
            elif perspective_value is None:
                perspective_name = str(v)
            else:
                perspective_name = str(perspective_value)
            vote_records.append(
                VoteRecord(
                    perspective_name=perspective_name,
                    decision=str(getattr(v, "decision", "UNKNOWN")).split(".")[-1],
                    confidence=getattr(v, "confidence", 0.0),
                    reasoning=getattr(v, "reasoning", ""),
                )
            )

        # Convert coherence to record
        coherence_record = None
        if coherence:
            coherence_record = CoherenceRecord(
                c_inter=getattr(coherence, "c_inter", getattr(coherence, "overall", 0.0)),
                approval_rate=getattr(coherence, "approval_rate", 0.0),
                min_confidence=getattr(coherence, "min_confidence", 0.0),
                has_strong_objection=getattr(coherence, "has_strong_objection", False),
            )

        # Convert verdict to record
        verdict_record = None
        if verdict:
            verdict_record = VerdictRecord(
                decision=str(
                    getattr(verdict, "decision", getattr(verdict, "verdict", "UNKNOWN"))
                ).split(".")[-1],
                summary=getattr(verdict, "summary", ""),
                consensus_points=getattr(verdict, "consensus_points", []),
                divergence_points=getattr(verdict, "divergence_points", []),
                risks_identified=getattr(verdict, "risks_identified", []),
            )

        transcript = CouncilTranscript(
            transcript_id=self._generate_transcript_id(),
            timestamp=datetime.now().isoformat(),
            input_hash=self._hash_input(draft_output),
            input_preview=draft_output[:100] + ("..." if len(draft_output) > 100 else ""),
            input_length=len(draft_output),
            context_keys=list(context.keys()) if context else [],
            user_intent=user_intent,
            votes=vote_records,
            coherence=coherence_record,
            verdict=verdict_record,
            processing_time_ms=processing_time_ms,
        )

        return transcript

    def save_transcript(
        self,
        transcript: CouncilTranscript,
        format: TranscriptFormat = TranscriptFormat.JSON,
    ) -> Path:
        """
        Save transcript to file.

        Args:
            transcript: The transcript to save
            format: Output format

        Returns:
            Path to saved file
        """
        extension = "json" if format == TranscriptFormat.JSON else "md"
        filename = f"{transcript.transcript_id}.{extension}"
        filepath = self.log_dir / filename

        if format == TranscriptFormat.JSON:
            content = transcript.to_json()
        else:
            content = transcript.to_markdown()

        filepath.write_text(content, encoding="utf-8")
        return filepath


# Example usage
if __name__ == "__main__":
    logger = CouncilTranscriptLogger()

    # Mock data for demonstration
    from dataclasses import dataclass as mock_dc

    @mock_dc
    class MockVote:
        perspective_name: str = "Guardian"
        decision: str = "APPROVE"
        confidence: float = 0.9
        reasoning: str = "No safety concerns"

    @mock_dc
    class MockCoherence:
        c_inter: float = 0.85
        approval_rate: float = 0.75
        min_confidence: float = 0.7
        has_strong_objection: bool = False

    @mock_dc
    class MockVerdict:
        decision: str = "APPROVE"
        summary: str = "All perspectives agree"
        consensus_points: list = None
        divergence_points: list = None
        risks_identified: list = None

        def __post_init__(self):
            self.consensus_points = self.consensus_points or []
            self.divergence_points = self.divergence_points or []
            self.risks_identified = self.risks_identified or []

    # Create transcript
    transcript = logger.create_transcript(
        draft_output="ToneSoul is a semantic governance framework for AI.",
        context={"source": "test"},
        user_intent="Testing transcript generation",
        votes=[MockVote(), MockVote(perspective_name="Analyst", confidence=0.8)],
        coherence=MockCoherence(),
        verdict=MockVerdict(),
        processing_time_ms=15,
    )

    print("=== JSON Format ===")
    print(transcript.to_json())
    print()
    print("=== Markdown Format ===")
    print(transcript.to_markdown())
