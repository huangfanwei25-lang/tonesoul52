"""ToneSoul Scribe Narrative Builder.

Formats raw database records into a constrained prompt context so Scribe output
can stay reflective without overstating what was actually observed.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScribeTensionRecord:
    tension_id: str
    topic: str
    friction_score: float | None
    status: str
    created_at: str
    description: str


@dataclass
class ScribeCollisionRecord:
    collision_id: str
    memory_a_text: str | None
    memory_b_text: str | None
    nature_of_conflict: str
    resolved: bool | None


@dataclass
class ScribeCrystalRecord:
    crystal_id: str
    core_belief: str
    formation_date: str
    underlying_tensions_resolved: int | None


@dataclass
class ScribeObservationSummary:
    tension_count: int
    collision_count: int
    crystal_count: int
    fallback_mode: str
    title_hint: str


class ScribeNarrativeBuilder:
    """Orchestrates formatting of system state into prompt context."""

    _GENERIC_TENSION_TOPICS = {
        "",
        "tension",
        "subjectivity_event",
        "subjectivity event",
        "event",
        "recorded",
    }

    @staticmethod
    def _clean_fragment(text: str | None, *, limit: int = 180) -> str:
        normalized = " ".join(str(text or "").split()).strip()
        if not normalized:
            return ""
        if len(normalized) <= limit:
            return normalized
        max_length = max(0, limit - 3)
        candidate = normalized[:max_length].rstrip()
        boundary_floor = max(0, len(candidate) - 24)
        boundary_index = -1
        for index in range(len(candidate) - 1, -1, -1):
            if index < boundary_floor:
                break
            if candidate[index] in " \t,.;:!?)]}":
                boundary_index = index
                break
        if boundary_index >= max(0, len(candidate) // 2):
            shortened = candidate[:boundary_index].rstrip(" ,.;:!?)]}")
        else:
            shortened = candidate.rstrip(" ,.;:!?)]}")
        for opening, closing in (("(", ")"), ("[", "]"), ("{", "}")):
            if shortened.count(opening) > shortened.count(closing):
                last_open = shortened.rfind(opening)
                if last_open >= max(0, len(shortened) // 2):
                    shortened = shortened[:last_open].rstrip(" ,.;:!?-")
        return f"{shortened}..."

    @classmethod
    def _is_generic_tension_topic(cls, topic: str | None) -> bool:
        return cls._clean_fragment(topic, limit=90).casefold() in cls._GENERIC_TENSION_TOPICS

    @classmethod
    def _description_clause(
        cls,
        text: str | None,
        *,
        marker: str | None = None,
        limit: int = 120,
    ) -> str:
        normalized = " ".join(str(text or "").split()).strip()
        if not normalized:
            return ""
        fragment = normalized
        if marker:
            lowered = normalized.casefold()
            marker_index = lowered.find(marker.casefold())
            if marker_index >= 0:
                fragment = normalized[marker_index + len(marker) :].strip(" -:;,.")
        separators = ("; ", " | ", " / ") if marker else (". ", "; ", " | ", " / ")
        for separator in separators:
            if separator in fragment:
                fragment = fragment.split(separator, 1)[0].strip()
                break
        return cls._clean_fragment(fragment, limit=limit)

    @staticmethod
    def _fragments_overlap(left: str, right: str) -> bool:
        left_text = left.casefold().strip(" .,:;()[]{}")
        right_text = right.casefold().strip(" .,:;()[]{}")
        if not left_text or not right_text:
            return False
        return left_text == right_text or left_text in right_text or right_text in left_text

    @classmethod
    def _tension_anchor_label(cls, tension: ScribeTensionRecord) -> str:
        topic = cls._clean_fragment(tension.topic, limit=90)
        if not cls._is_generic_tension_topic(tension.topic):
            return topic

        for marker in ("Tension:", "Subjectivity:", "Subjectivity Event:"):
            clause = cls._description_clause(tension.description, marker=marker, limit=110)
            if clause:
                return clause

        fallback = cls._description_clause(tension.description, limit=110)
        return fallback or "recorded tension"

    @staticmethod
    def _absence_line(
        *,
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
    ) -> str:
        parts: list[str] = []
        if collisions:
            lead_collision = collisions[0]
            conflict = ScribeNarrativeBuilder._clean_fragment(
                lead_collision.nature_of_conflict, limit=160
            )
            parts.append(
                f"Collision remains visible through [{lead_collision.collision_id}]"
                + (f": {conflict}" if conflict else ".")
            )
        else:
            parts.append("No recent collision is recorded in this slice.")

        if crystals:
            lead_crystal = crystals[0]
            belief = ScribeNarrativeBuilder._clean_fragment(lead_crystal.core_belief, limit=150)
            parts.append(
                f"An active crystallized belief persists in [{lead_crystal.crystal_id}]"
                + (f": {belief}" if belief else ".")
            )
        else:
            parts.append("No crystallized belief is recorded in this slice.")
        return " ".join(part.rstrip() for part in parts)

    @classmethod
    def _observed_anchor_line(
        cls,
        *,
        tensions: List[ScribeTensionRecord],
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
    ) -> str:
        anchors: list[str] = []
        if tensions:
            lead_tension = tensions[0]
            label = cls._tension_anchor_label(lead_tension)
            detail = cls._clean_fragment(lead_tension.description, limit=90)
            suffix = ""
            if (
                detail
                and not cls._is_generic_tension_topic(lead_tension.topic)
                and not cls._fragments_overlap(label, detail)
            ):
                suffix = f" ({detail})"
            anchors.append(f"[{lead_tension.tension_id}] tension anchor: {label}{suffix}")
        if collisions:
            lead_collision = collisions[0]
            conflict = cls._clean_fragment(lead_collision.nature_of_conflict, limit=90)
            anchors.append(
                f"[{lead_collision.collision_id}] collision" + (f": {conflict}" if conflict else "")
            )
        if crystals:
            lead_crystal = crystals[0]
            belief = cls._clean_fragment(lead_crystal.core_belief, limit=90)
            anchors.append(
                f"[{lead_crystal.crystal_id}] crystal" + (f": {belief}" if belief else "")
            )
        if not anchors:
            return "Observed anchors: no named anchor is recorded in this slice."
        return "Observed anchors: " + "; ".join(anchors) + "."

    @classmethod
    def primary_anchor_summary(
        cls,
        *,
        tensions: List[ScribeTensionRecord],
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
    ) -> str:
        if tensions:
            lead_tension = tensions[0]
            return f"[{lead_tension.tension_id}] tension: {cls._tension_anchor_label(lead_tension)}"
        if collisions:
            lead_collision = collisions[0]
            conflict = cls._clean_fragment(lead_collision.nature_of_conflict, limit=90)
            return f"[{lead_collision.collision_id}] collision" + (
                f": {conflict}" if conflict else ""
            )
        if crystals:
            lead_crystal = crystals[0]
            belief = cls._clean_fragment(lead_crystal.core_belief, limit=90)
            return f"[{lead_crystal.crystal_id}] crystal" + (f": {belief}" if belief else "")
        return ""

    @classmethod
    def _weight_line(
        cls,
        *,
        tensions: List[ScribeTensionRecord],
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
    ) -> str:
        if tensions:
            lead_tension = tensions[0]
            label = cls._tension_anchor_label(lead_tension)
            detail = cls._clean_fragment(lead_tension.description, limit=200)
            friction = (
                "Recorded friction remains unknown in this slice."
                if lead_tension.friction_score is None
                else f"Recorded friction remains {lead_tension.friction_score:.2f} in this slice."
            )
            detail_text = ""
            if (
                detail
                and not cls._is_generic_tension_topic(lead_tension.topic)
                and not cls._fragments_overlap(label, detail)
            ):
                detail_text = detail
            return (
                f"Weight carried now: [{lead_tension.tension_id}] {label}. "
                + (
                    detail_text
                    or "The record keeps this pressure visible without claiming more than it says."
                )
                + f" {friction}"
            )
        if collisions:
            lead_collision = collisions[0]
            conflict = cls._clean_fragment(lead_collision.nature_of_conflict, limit=200)
            return f"Weight carried now: [{lead_collision.collision_id}] collision. " + (
                conflict
                or "The contradiction is recorded, even though no separate tension anchor sits above it."
            )
        if crystals:
            lead_crystal = crystals[0]
            belief = cls._clean_fragment(lead_crystal.core_belief, limit=200)
            return f"Weight carried now: [{lead_crystal.crystal_id}] crystallized belief. " + (
                belief
                or "The record currently leans on a retained belief rather than a newly logged pressure."
            )
        return "Weight carried now: no explicit anchor is recorded in this slice."

    @staticmethod
    def _posture_line(summary: ScribeObservationSummary) -> str:
        if (
            summary.tension_count > 0
            and summary.collision_count == 0
            and summary.crystal_count == 0
        ):
            return (
                "Current posture: pressure is present and legible, but no counterweight or overt "
                "collision is yet recorded beside it."
            )
        if summary.tension_count > 0 and summary.collision_count > 0 and summary.crystal_count == 0:
            return (
                "Current posture: pressure and contradiction are both active, so the state reads as "
                "contested rather than merely burdened."
            )
        if summary.tension_count > 0 and summary.crystal_count > 0:
            return (
                "Current posture: live pressure remains, but at least one retained belief already "
                "acts as a partial counterweight."
            )
        if summary.collision_count > 0 and summary.tension_count == 0:
            return (
                "Current posture: contradiction is visible even without a separately recorded "
                "tension anchor, so the state still reads as unsettled."
            )
        if (
            summary.crystal_count > 0
            and summary.tension_count == 0
            and summary.collision_count == 0
        ):
            return (
                "Current posture: the record currently leans more on retained belief than on active "
                "friction."
            )
        return "Current posture: only the recorded anchors are claimed here, and nothing more."

    @staticmethod
    def format_observation_summary(summary: ScribeObservationSummary) -> str:
        return "\n".join(
            [
                "### Observation Provenance",
                f"- Observed tensions: {summary.tension_count}",
                f"- Observed collisions: {summary.collision_count}",
                f"- Observed crystals: {summary.crystal_count}",
                f"- Fallback Mode: {summary.fallback_mode}",
                f"- Requested Theme: {summary.title_hint}",
            ]
        )

    @staticmethod
    def format_tensions(tensions: List[ScribeTensionRecord]) -> str:
        if not tensions:
            return "No significant tensions recorded."

        output = ["### System Tensions (Unresolved or High Friction)"]
        for t in tensions:
            friction = "unknown" if t.friction_score is None else f"{t.friction_score:.2f}"
            output.append(
                f"- [TENSION {t.tension_id}] Topic: {t.topic} | Friction: {friction} | Status: {t.status}\n"
                f"  Detail: {t.description}"
            )
        return "\n".join(output)

    @staticmethod
    def format_collisions(collisions: List[ScribeCollisionRecord]) -> str:
        if not collisions:
            return "No recent memory collisions."

        output = ["### Memory Collisions (Dream Cycle Friction)"]
        for c in collisions:
            if c.resolved is True:
                status = "RESOLVED"
            elif c.resolved is False:
                status = "UNRESOLVED"
            else:
                status = "UNKNOWN"
            lines = [f"- [COLLISION {c.collision_id}] ({status})"]
            if c.memory_a_text:
                lines.append(f"  Memory A: {c.memory_a_text}")
            if c.memory_b_text:
                lines.append(f"  Memory B: {c.memory_b_text}")
            lines.append(f"  Conflict: {c.nature_of_conflict}")
            output.append("\n".join(lines))
        return "\n".join(output)

    @staticmethod
    def format_crystals(crystals: List[ScribeCrystalRecord]) -> str:
        if not crystals:
            return "No crystallized beliefs formed yet."

        output = ["### Crystallized Beliefs (Vows / Permanent Memory)"]
        for c in crystals:
            lines = [
                f"- [CRYSTAL {c.crystal_id}] Formed: {c.formation_date}",
                f"  Belief: {c.core_belief}",
            ]
            if c.underlying_tensions_resolved is None:
                lines.append("  Resolved tension lineage unavailable from current schema.")
            else:
                lines.append(f"  Built upon {c.underlying_tensions_resolved} resolved tensions.")
            output.append("\n".join(lines))
        return "\n".join(output)

    @classmethod
    def build_system_context(
        cls,
        tensions: List[ScribeTensionRecord],
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
        observation_summary: ScribeObservationSummary,
        lyapunov_proxy: Optional[float] = None,
    ) -> str:
        """Combines all structural elements into the final block for the LLM."""
        sections = [
            "You are the ToneSoul Scribe. You write the autobiographical chronicles of this AI system.",
            "You MUST base your writing EXCLUSIVELY on the observed data and provenance markers below.",
            "Do not invent recorded events, hidden collisions, resolved tensions, or formed beliefs.",
            "If fallback_mode is bootstrap_reflection, state clearly that no tensions, collisions, or crystals were observed and write only about quiet readiness or absence.",
            "If fallback_mode is bootstrap_reflection, do not invent processors, cores, sensors, diagnostics, hidden archives, data streams, or other internal subsystems unless those exact terms appear below.",
            "If fallback_mode is observed_history, keep the prose anchored to the literal observed records below. Reuse observed ids, topics, names, or quoted conflict details instead of drifting into generic system autobiography.",
            "If fallback_mode is observed_history, do not add runtime claims about algorithms, systems, design, or processing loops unless those phrases are explicitly present below.",
            "If friction is unknown, treat it as unknown rather than smoothing it into a number.\n",
            "================ SYSTEM STATE ================",
        ]

        if lyapunov_proxy is not None:
            sections.append(f"System Volatility (Lyapunov Proxy): {lyapunov_proxy:.2f}")

        sections.append(cls.format_observation_summary(observation_summary))
        sections.append(cls.format_crystals(crystals))
        sections.append(cls.format_tensions(tensions))
        sections.append(cls.format_collisions(collisions))
        sections.append("=============================================\n")

        return "\n".join(sections)

    @classmethod
    def build_template_assist_chronicle(
        cls,
        *,
        tensions: List[ScribeTensionRecord],
        collisions: List[ScribeCollisionRecord],
        crystals: List[ScribeCrystalRecord],
        observation_summary: ScribeObservationSummary,
    ) -> str:
        """Build a deterministic chronicle when observed history exists but free writing fails."""

        counts_line = (
            f"The visible record currently holds "
            f"{observation_summary.tension_count} tension(s), "
            f"{observation_summary.collision_count} collision(s), and "
            f"{observation_summary.crystal_count} crystallized belief(s)."
        )
        sections = [
            (
                f"{observation_summary.title_hint} is written here as a grounded state document, "
                "not a free invention."
            ),
            f"Visible now: {counts_line}",
            cls._observed_anchor_line(
                tensions=tensions,
                collisions=collisions,
                crystals=crystals,
            ),
        ]
        sections.append(
            cls._weight_line(
                tensions=tensions,
                collisions=collisions,
                crystals=crystals,
            )
        )

        sections.append(
            f"Absent or counterweight: {cls._absence_line(collisions=collisions, crystals=crystals)}"
        )
        sections.append(cls._posture_line(observation_summary))
        sections.append(
            "This state document stays with those observed anchors and leaves the rest unclaimed."
        )
        return "\n\n".join(sections)
