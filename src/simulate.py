"""A simulator of tandem repeats."""

from __future__ import annotations
import random as rand
import numpy as np
from enum import Enum
from typing import Type
from genome import (
    Genome,
    ListGenome,
    LinkedListGenome
)

SIM_PARAMS = dict[str, object]


def sim_params(*,  # the args below must be given by keyword

               te_len: int = 200,       # mean te length
               te_offset: int = 500,    # mean te move

               # weight between insert,copy,disable
               weights: list[float] = (0.1, 2.0, 1.0)

               ) -> SIM_PARAMS:
    """Construct parameters for a simulation."""
    return {
        'te_len': te_len,
        'te_offset': te_offset,
        'weights': weights
    }


class Ops(Enum):
    """The different operations in the simulator."""

    INSERT = 1
    COPY = 2
    DISABLE = 3

    @staticmethod
    def sample(weights: list[int]) -> Ops:
        """Select which operation to do."""
        return rand.choices(list(Ops), weights)[0]


def sim_te(n: int, k: int,
           *,  # the args below must be given by keyword
           theta: SIM_PARAMS = sim_params(),
           seed: int | None = None,
           genome_class: Type[Genome] = ListGenome) -> str:
    """Simulate a genome of initial size n for k operations.

    >>> sim_te(30, 10, seed = 1984,
    ...        theta = sim_params(te_len=10))
    '---AAAA------------x--xAAAAxxx------AAAA-xxxxAAAA------'
    """
    rand.seed(seed)
    np.random.seed(seed)

    genome = genome_class(n)
    for _ in range(k):
        active = genome.active_tes()
        # weigh the operations with the number of active TEs
        op_weights = [
            theta['weights'][0],
            len(active) * theta['weights'][1],
            len(active) * theta['weights'][2],
        ]
        match Ops.sample(op_weights):
            case Ops.INSERT:
                pos = rand.randint(0, len(genome))
                length = np.random.geometric(1/theta['te_len'])
                genome.insert_te(pos, length)

            case Ops.COPY:
                te = rand.choice(active)
                offset = np.random.geometric(1/theta['te_offset'])
                if rand.random() < 0.5:
                    offset = -offset
                genome.copy_te(te, offset)

            case Ops.DISABLE:
                te = rand.choice(active)
                genome.disable_te(te)

    return str(genome)


if __name__ == '__main__':
    import timeit
    start_time = timeit.default_timer()
    sim_te(1_000_000, 1000)
    elapsed = timeit.default_timer() - start_time
    print("Python lists:", elapsed)

    start_time = timeit.default_timer()
    sim_te(1_000_000, 1000, genome_class=LinkedListGenome)
    elapsed = timeit.default_timer() - start_time
    print("Linked lists:", elapsed)
