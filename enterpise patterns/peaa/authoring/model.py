"""Section model for the bilingual guide."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Section:
    id: str
    nav: str
    group: str
    title: str
    subtitle: str
    icon: str
    tone: str
    intent: str
    use: list[str]
    avoid: list[str]
    diagram: str
    relations: list[tuple[str, str]]
    lab: str
    demo: str
    snippet: str
    tasks: list[str]
    questions: list[tuple[str, str]]
    notes: list[str] = field(default_factory=list)
    html_block: str = ""

    def validate(self) -> None:
        if len(self.tasks) < 2:
            raise ValueError(f"{self.id} needs >= 2 tasks")
        if len(self.questions) < 4:
            raise ValueError(f"{self.id} needs >= 4 questions")
        if not self.intent.strip():
            raise ValueError(f"{self.id} missing intent")
