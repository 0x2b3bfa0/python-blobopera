"""Audio jitter templates.

This module defines the protocol buffer format used for the default set of
jitter templates used by the audio engine. The :py:class:`Jitter` class can
be used to serialize and deserialize the ``jittertemplates.proto`` file from
the original Blob Opera application.
"""
from functools import partial
from random import Random
from typing import Any, Callable, Iterator

import proto  # type: ignore
from more_itertools import pairwise


class Template(proto.Message):
    """Individual jitter template.

    Attributes:
        values (Sequence[float]): Float jitter values.
    """

    values = proto.RepeatedField(proto.FLOAT, number=1)


class Jitter(proto.Message):
    """List of jitter templates.

    Attributes:
        templates (Sequence[Template]): Jitter templates.
    """

    templates = proto.RepeatedField(Template, number=1)


class Generator:
    """Jitter value generator, reverse-engineered from the original.

    Given a list of templates where each template holds a list of float
    values, this algorithm will perform the following steps:

    1. Loop endlessly over randomly chosen templates, allowing the inner
       code to access both the current template and the previous template.

    2. Overlap each of these template pairs by the specified number of
       positions and perform a weighted mix of the overlapping values:

       .. code-block::

           1 2 3 · · · ·
           · · 4 5 6 · ·
           · · · · 7 8 9
           - - - - - - -
           1 2 * 5 * 8 9

       The mixing algorithm creates a smooth transition between the old
       and new templates by cross-fading the overlapping values from the
       old and new templates.

    Yields:
        float: Jitter values.
    """

    def __init__(self, jitter: Jitter, *, overlap: int = 10, seed: Any = None):
        """Initialize the generator.

        Arguments:
            jitter: A protocol buffer message with jitter templates.
            overlap: The amount of values that should overlap when cross-fading
                two adjacent templates.
            seed: The seed to use for the pseudorandom number generator. Useful
                for obtaining deterministic results while performing unit
                tests.
        """
        self.random: Random = Random(seed)
        self.jitter: Jitter = jitter
        self.overlap: int = overlap

    def __iter__(self) -> Iterator[float]:
        """Chain templates in a random order with smooth transitions.

        Yields:
            Jitter values.
        """
        # Create a partial function that returns a randomly chosen template.
        choose: Callable = partial(self.random.choice, self.jitter.templates)
        # Create an iterator that provides randomly chosen templates.
        random: Iterator[Template] = iter(choose, None)
        # Alias the overlap variable for simplicity.
        count: int = self.overlap

        # Iterate over randomly chosen templates with (previous, current) pairs
        for previous, current in pairwise(random):  # (0, 1), (1, 2), (2, 3)...

            # Get the tail (last values) of the previous template and the head
            # (first values) of the current template. Due to an off-by-one
            # error in the original code, the tail from the previous template
            # starts one index earlier and ends with the penultimate value.
            tail, head = (
                previous.values[-count - 1 : -1],
                current.values[:count],
            )

            # For each pair of overlapped values:
            for index, (old, new) in enumerate(zip(tail, head)):
                # Calculate the mixing weights for the pair of values.
                increasing, decreasing = (weight := index / count), 1 - weight
                # Yield the weighted mix of the overlapping values.
                yield old * decreasing + new * increasing

            # Yield all the remaining (non-overlapping) values.
            yield from current.values[count:][:-count]
