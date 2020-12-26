import random


class Templates:
    def __init__(self, templates: dict):
        self.templates: list[list] = [
            list(template["values"])
            for template in templates["templates"]
            ]
        self.previous: list = self.random()  # previousTemplate
        self.current: list = self.random() # currentTemplate
        self.frame: int = 0  # currentTemplateFrame

    def __iter__(self):
        return self

    def __next__(self) -> float:
        return self.next()

    def next(self) -> float:
        if self.frame >= 10:
            result: float = self.current[self.frame]
        else:
            result: float = self.combine(
                self.previous[len(self.previous) - 1 - 10 + self.frame],
                self.current[self.frame],
                self.normalize(0, 10, self.frame)
                )

        self.frame += 1
        if self.frame >= len(self.current) - 10:
            self.previous, self.current = self.current, self.random()
            self.frame = 0

        return result

    def random(self) -> list:  # getRandomTemplate
        return random.choice(self.templates)

    def clamp(self, minimum: float, value: float, maximum: float) -> float:
        return min(maximum, max(value, minimum))

    def normalize(self, offset: int, limit: int, value: int):
        normalized = (value - offset) / (limit - offset)
        return self.clamp(0, normalized, 1)

    def combine(self, previous: float, current: float, value: float) -> float:
        return (1 - value) * previous + value * current

