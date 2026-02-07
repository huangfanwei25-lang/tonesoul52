"""
Session Reporter - Session Intelligence Module

Generates insights and reports about the conversation session.
Analyzes emotional trajectory, key turning points, and theme distribution.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TurningPoint:
    """A significant moment in the conversation where something shifted."""

    turn_index: int
    description: str
    before_state: str  # e.g., "calm", "tense"
    after_state: str  # e.g., "conflict", "resolution"
    trigger: str  # What triggered the shift
    significance: float  # 0.0 to 1.0

    def to_dict(self) -> dict:
        return {
            "turn_index": self.turn_index,
            "description": self.description,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "trigger": self.trigger,
            "significance": self.significance,
        }


@dataclass
class ThemeCluster:
    """A group of related topics discussed in the session."""

    name: str
    keywords: List[str]
    turn_count: int
    emotional_tone: str  # dominant emotion for this theme

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "keywords": self.keywords,
            "turn_count": self.turn_count,
            "emotional_tone": self.emotional_tone,
        }


@dataclass
class SessionSummary:
    """Complete summary of a conversation session."""

    session_id: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    # Basic stats
    total_turns: int
    user_messages: int
    ai_responses: int

    # Emotional journey
    emotional_arc: List[str]  # List of emotional states per turn
    dominant_emotion: str
    emotional_volatility: float  # 0.0 (stable) to 1.0 (volatile)

    # Key events
    turning_points: List[TurningPoint]
    high_tension_moments: List[int]  # Turn indices

    # Themes
    theme_clusters: List[ThemeCluster]

    # Third Axiom summary
    commitments_made: int
    ruptures_detected: int
    values_strengthened: List[str]

    # Overall assessment
    session_quality: str  # "productive", "exploratory", "challenging", etc.
    summary_text: str

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_turns": self.total_turns,
            "user_messages": self.user_messages,
            "ai_responses": self.ai_responses,
            "emotional_arc": self.emotional_arc,
            "dominant_emotion": self.dominant_emotion,
            "emotional_volatility": self.emotional_volatility,
            "turning_points": [tp.to_dict() for tp in self.turning_points],
            "high_tension_moments": self.high_tension_moments,
            "theme_clusters": [tc.to_dict() for tc in self.theme_clusters],
            "commitments_made": self.commitments_made,
            "ruptures_detected": self.ruptures_detected,
            "values_strengthened": self.values_strengthened,
            "session_quality": self.session_quality,
            "summary_text": self.summary_text,
        }


class SessionReporter:
    """
    Generates insights and reports about conversation sessions.

    Key capabilities:
    1. Emotional trajectory analysis
    2. Turning point detection
    3. Theme clustering
    4. Third Axiom summary (commitments, ruptures, values)
    """

    # Emotional state keywords
    EMOTION_KEYWORDS = {
        "calm": ["好", "謝謝", "了解", "明白", "嗯", "沒問題", "可以"],
        "curious": ["為什麼", "如何", "怎麼", "什麼", "請問", "想知道", "好奇"],
        "frustrated": ["不是", "但是", "可是", "難道", "怎麼可能", "不對", "錯了"],
        "excited": ["太棒了", "厲害", "好耶", "！！", "真的嗎", "超讚", "太好了"],
        "sad": ["難過", "失望", "遺憾", "唉", "傷心", "沮喪", "悲傷"],
        "anxious": ["擔心", "怕", "如果", "萬一", "會不會", "不安", "緊張"],
        "hopeful": ["希望", "期待", "相信", "盼望", "應該會", "一定會"],
        "confused": ["困惑", "不懂", "什麼意思", "搞不懂", "不明白", "模糊"],
        "grateful": ["感謝", "謝謝你", "多謝", "感激", "太感謝", "幸好"],
    }

    # Theme keywords for clustering
    THEME_KEYWORDS = {
        "哲學思辨": ["意義", "存在", "自由", "意識", "真理", "價值", "本質"],
        "情感支持": ["感覺", "心情", "難過", "開心", "關心", "安慰", "陪伴"],
        "技術問題": ["程式", "代碼", "錯誤", "如何", "怎麼做", "實作", "bug"],
        "創意發想": ["想法", "創意", "設計", "可能性", "嘗試", "靈感"],
        "學習成長": ["學習", "理解", "知道", "原來", "教我", "解釋"],
        "日常對話": ["你好", "謝謝", "再見", "今天", "什麼時候", "在哪裡"],
    }

    def __init__(self):
        self._session_counter = 0

    def _generate_session_id(self) -> str:
        self._session_counter += 1
        return f"session_{datetime.now().strftime('%Y%m%d%H%M')}_{self._session_counter:03d}"

    def _detect_emotion(self, text: str) -> str:
        """Detect dominant emotion in a text."""
        text_lower = text.lower()
        emotion_scores = defaultdict(int)

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    emotion_scores[emotion] += 1

        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        return "neutral"

    def _build_emotional_arc(self, history: List[Dict]) -> List[str]:
        """Build a timeline of emotional states."""
        arc = []
        for turn in history:
            if turn.get("role") == "user":
                content = turn.get("content", "")
                emotion = self._detect_emotion(content)
                arc.append(emotion)
        return arc

    def _calculate_volatility(self, emotional_arc: List[str]) -> float:
        """Calculate emotional volatility (how much the emotion changes)."""
        if len(emotional_arc) < 2:
            return 0.0

        changes = 0
        for i in range(1, len(emotional_arc)):
            if emotional_arc[i] != emotional_arc[i - 1]:
                changes += 1

        divisor = len(emotional_arc) - 1
        if divisor == 0:
            return 0.0

        return min(changes / divisor, 1.0)

    def _detect_turning_points(
        self, history: List[Dict], emotional_arc: List[str]
    ) -> List[TurningPoint]:
        """Detect significant turning points in the conversation."""
        turning_points = []

        for i in range(1, len(emotional_arc)):
            if emotional_arc[i] != emotional_arc[i - 1]:
                # Get the corresponding message
                user_msgs = [h for h in history if h.get("role") == "user"]
                if i < len(user_msgs):
                    trigger_msg = user_msgs[i].get("content", "")[:50]
                else:
                    trigger_msg = "unknown"

                significance = 0.5
                # Higher significance for more extreme shifts
                if emotional_arc[i - 1] == "calm" and emotional_arc[i] in ["frustrated", "anxious"]:
                    significance = 0.8
                elif emotional_arc[i] == "calm" and emotional_arc[i - 1] in [
                    "frustrated",
                    "anxious",
                ]:
                    significance = 0.7

                turning_points.append(
                    TurningPoint(
                        turn_index=i,
                        description=f"情緒從 {emotional_arc[i-1]} 轉變為 {emotional_arc[i]}",
                        before_state=emotional_arc[i - 1],
                        after_state=emotional_arc[i],
                        trigger=trigger_msg,
                        significance=significance,
                    )
                )

        return turning_points

    def _find_high_tension_moments(
        self, history: List[Dict], emotional_arc: List[str]
    ) -> List[int]:
        """Find turn indices where tension was high."""
        high_tension_emotions = {"frustrated", "anxious", "sad"}
        return [i for i, e in enumerate(emotional_arc) if e in high_tension_emotions]

    def _classify_session(
        self, turning_points: List[TurningPoint], volatility: float, dominant_emotion: str
    ) -> str:
        """Classify the overall session quality."""
        if volatility < 0.3 and dominant_emotion in ["calm", "curious"]:
            return "productive"
        elif len(turning_points) > 3:
            return "dynamic"
        elif dominant_emotion in ["frustrated", "anxious"]:
            return "challenging"
        elif dominant_emotion == "curious":
            return "exploratory"
        else:
            return "conversational"

    def _generate_summary_text(
        self,
        total_turns: int,
        dominant_emotion: str,
        turning_points: List[TurningPoint],
        commitments: int,
        session_quality: str,
    ) -> str:
        """Generate a human-readable summary."""
        lines = []

        lines.append(f"這次對話共進行了 {total_turns} 個回合。")

        emotion_label = {
            "calm": "平靜",
            "curious": "好奇",
            "frustrated": "受挫",
            "excited": "興奮",
            "sad": "低落",
            "anxious": "焦慮",
            "neutral": "中性",
            "hopeful": "期待",
            "confused": "困惑",
            "grateful": "感恩",
        }.get(dominant_emotion, dominant_emotion)
        lines.append(f"整體情緒氛圍為「{emotion_label}」。")

        if turning_points:
            lines.append(f"對話中有 {len(turning_points)} 個情緒轉折點。")

        if commitments > 0:
            lines.append(f"AI 在對話中做出了 {commitments} 個語義承諾。")

        quality_label = {
            "productive": "有建設性的",
            "dynamic": "富有變化的",
            "challenging": "面對挑戰的",
            "exploratory": "探索性的",
            "conversational": "自然流暢的",
        }.get(session_quality, session_quality)
        lines.append(f"這是一次{quality_label}對話。")

        return " ".join(lines)

    def _detect_themes(self, history: List[Dict], emotional_arc: List[str]) -> List[ThemeCluster]:
        """Detect theme clusters from conversation content."""
        theme_counts = defaultdict(lambda: {"count": 0, "emotions": []})

        user_emotion_idx = 0
        for msg in history:
            content = msg.get("content", "")
            role = msg.get("role", "")

            # Track emotion for this turn
            current_emotion = "neutral"
            if role == "user" and user_emotion_idx < len(emotional_arc):
                current_emotion = emotional_arc[user_emotion_idx]
                user_emotion_idx += 1

            # Match themes
            for theme_name, keywords in self.THEME_KEYWORDS.items():
                for kw in keywords:
                    if kw in content:
                        theme_counts[theme_name]["count"] += 1
                        theme_counts[theme_name]["emotions"].append(current_emotion)
                        break  # Only count each theme once per message

        # Build ThemeClusters for themes that appeared at least twice
        clusters = []
        for theme_name, data in theme_counts.items():
            if data["count"] >= 2:
                # Find dominant emotion for this theme
                emotions = data["emotions"]
                dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "neutral"

                clusters.append(
                    ThemeCluster(
                        name=theme_name,
                        keywords=self.THEME_KEYWORDS.get(theme_name, [])[:3],  # Top 3 keywords
                        turn_count=data["count"],
                        emotional_tone=dominant_emotion,
                    )
                )

        # Sort by frequency
        clusters.sort(key=lambda c: c.turn_count, reverse=True)
        return clusters[:5]  # Return top 5 themes

    def analyze(
        self,
        history: List[Dict],
        self_commits: Optional[List] = None,
        ruptures: Optional[List] = None,
        emergent_values: Optional[List] = None,
    ) -> SessionSummary:
        """
        Analyze a conversation history and generate a session summary.

        Args:
            history: List of conversation turns [{role, content}, ...]
            self_commits: Optional list of SelfCommit objects from Third Axiom
            ruptures: Optional list of SemanticRupture objects
            emergent_values: Optional list of EmergentValue objects
        """
        session_id = self._generate_session_id()

        # Count messages
        user_messages = len([h for h in history if h.get("role") == "user"])
        ai_responses = len([h for h in history if h.get("role") == "assistant"])
        total_turns = len(history)

        # Emotional analysis
        emotional_arc = self._build_emotional_arc(history)
        dominant_emotion = (
            max(set(emotional_arc), key=emotional_arc.count) if emotional_arc else "neutral"
        )
        volatility = self._calculate_volatility(emotional_arc)

        # Key events
        turning_points = self._detect_turning_points(history, emotional_arc)
        high_tension = self._find_high_tension_moments(history, emotional_arc)

        # Third Axiom stats
        commitments_made = len(self_commits) if self_commits else 0
        ruptures_detected = len(ruptures) if ruptures else 0
        values_list = [v.name if hasattr(v, "name") else str(v) for v in (emergent_values or [])]

        # Classification
        session_quality = self._classify_session(turning_points, volatility, dominant_emotion)

        # Summary text
        summary_text = self._generate_summary_text(
            total_turns, dominant_emotion, turning_points, commitments_made, session_quality
        )

        return SessionSummary(
            session_id=session_id,
            start_time=datetime.now(),  # Ideally would track actual start
            end_time=datetime.now(),
            total_turns=total_turns,
            user_messages=user_messages,
            ai_responses=ai_responses,
            emotional_arc=emotional_arc,
            dominant_emotion=dominant_emotion,
            emotional_volatility=volatility,
            turning_points=turning_points,
            high_tension_moments=high_tension,
            theme_clusters=self._detect_themes(history, emotional_arc),
            commitments_made=commitments_made,
            ruptures_detected=ruptures_detected,
            values_strengthened=values_list,
            session_quality=session_quality,
            summary_text=summary_text,
        )
