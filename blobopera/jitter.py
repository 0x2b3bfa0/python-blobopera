from random import Random

import proto


class Template(proto.Message):
    """Sequence of jitter values."""

    values = proto.RepeatedField(proto.FLOAT, number=1, json_name="values")


class Jitter(proto.Message):
    """Set of jitter templates."""

    templates = proto.RepeatedField(Template, number=1, json_name="templates")


class Generator:
    """Jitter value generator."""

    def __init__(self, jitter: Jitter, seed: any = None):
        self.templates: list[list] = [
            list(template.values) for template in jitter.templates
        ]
        self.random: Random = Random(seed)
        self.previous: list = self.random.choice(self.templates)
        self.current: list = self.random.choice(self.templates)
        self.frame: int = 0

    def __next__(self) -> float:
        if self.frame >= 10:
            result: float = self.current[self.frame]
        else:
            result: float = self._combine(
                self.previous[len(self.previous) - 1 - 10 + self.frame],
                self.current[self.frame],
                self._normalize(0, 10, self.frame),
            )

        self.frame += 1
        if self.frame >= len(self.current) - 10:
            new = self.random.choice(self.templates)
            self.previous, self.current = self.current, new
            self.frame = 0

        return result

    def __iter__(self):
        return self

    def _normalize(self, offset: int, limit: int, value: int):
        normalized = (value - offset) / (limit - offset)
        return max(0, min(normalized, 1))  # Clamp value

    def _combine(self, previous: float, current: float, value: float) -> float:
        return (1 - value) * previous + value * current
