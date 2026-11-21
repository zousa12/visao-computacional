"""Session-only attempts, accepted corrections and image reconstruction."""

from collections.abc import MutableMapping
from dataclasses import dataclass, field
import hashlib
from uuid import uuid4
from history_store import HistoryEvent

from PIL import Image

from answer_validation import AnswerFeedback


PROGRESS_KEY = "challenge_progress"
INPUT_PREFIXES = ("q1_", "q2_", "q3_", "q4_")


@dataclass(frozen=True)
class Attempt:
    preview: Image.Image | None
    feedback: AnswerFeedback | None
    error: str | None = None


@dataclass
class SessionProgress:
    identity: str
    size: tuple[int, int]
    attempts: dict[int, Attempt] = field(default_factory=dict)
    corrected: dict[int, Image.Image] = field(default_factory=dict)

    run_id: str = field(default_factory=lambda: str(uuid4()))
    pending_events: list[HistoryEvent] = field(default_factory=list)

    def expected_size(self, quadrant: int) -> tuple[int, int]:
        if quadrant not in (1, 2, 3, 4):
            raise ValueError("O quadrante deve ser de 1 a 4.")
        width, height = self.size
        left, top = width // 2, height // 2
        return (left if quadrant in (1, 3) else width - left,
                top if quadrant in (1, 2) else height - top)

    def record(self, quadrant: int, preview: Image.Image, feedback: AnswerFeedback, answer=None) -> None:
        expected = self.expected_size(quadrant)
        if feedback.correct and preview.size != expected:
            raise ValueError("A correção aceita precisa preservar as dimensões do quadrante.")
        self.attempts[quadrant] = Attempt(preview.copy(), feedback)
        if feedback.correct:
            self.corrected[quadrant] = preview.convert("RGB").copy()

        self.pending_events.append(HistoryEvent.create(
            self.run_id, self.identity, self.size, quadrant, answer,
            "correct" if feedback.correct else "incorrect", feedback.message,
            preview.size, len(self.corrected)))

    def record_error(self, quadrant: int, message: str, answer=None) -> None:
        self.expected_size(quadrant)
        self.attempts[quadrant] = Attempt(None, None, message)
        self.pending_events.append(HistoryEvent.create(
            self.run_id, self.identity, self.size, quadrant, answer,
            "invalid", message, completed=len(self.corrected)))

    def reconstruct(self) -> Image.Image | None:
        if not all(quadrant in self.corrected for quadrant in range(1, 5)):
            return None
        width, height = self.size
        left, top = width // 2, height // 2
        result = Image.new("RGB", self.size)
        for quadrant, position in enumerate(((0, 0), (left, 0), (0, top), (left, top)), 1):
            correction = self.corrected[quadrant]
            if correction.size != self.expected_size(quadrant):
                raise ValueError("As dimensões das correções não correspondem à imagem original.")
            result.paste(correction, position)
        return result


def image_identity(image: Image.Image, source_token: str = "") -> str:
    rgb = image.convert("RGB")
    digest = hashlib.sha256()
    digest.update(source_token.encode("utf-8"))
    digest.update(f"|{rgb.width},{rgb.height}|".encode("ascii"))
    digest.update(rgb.tobytes())
    return digest.hexdigest()


def clear_progress(state: MutableMapping) -> None:
    state.pop(PROGRESS_KEY, None)
    for key in list(state):
        if isinstance(key, str) and key.startswith(INPUT_PREFIXES):
            del state[key]


def ensure_progress(state: MutableMapping, image: Image.Image,
                    source_token: str = "") -> SessionProgress:
    if image.width < 2 or image.height < 2:
        raise ValueError("A imagem precisa ter pelo menos 2 x 2 pixels.")
    identity = image_identity(image, source_token)
    current = state.get(PROGRESS_KEY)
    if not isinstance(current, SessionProgress) or current.identity != identity:
        clear_progress(state)
        current = SessionProgress(identity, image.size)
        state[PROGRESS_KEY] = current
    return current
