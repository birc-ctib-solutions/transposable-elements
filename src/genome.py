"""A circular genome for simulating transposable elements."""

from abc import (
    # A tag that says that we can't use this class except by specialising it
    ABC,
    # A tag that says that this method must be implemented by a child class
    abstractmethod
)


class Genome(ABC):
    """Representation of a circular enome."""

    @abstractmethod
    def insert_te(self, pos: int, length: int) -> int:
        """
        Insert a new transposable element.

        Insert a new transposable element at position pos and len
        nucleotide forward.

        If the TE collides with an existing TE, i.e. genome[pos]
        already contains TEs, then that TE should be disabled and
        removed from the set of active TEs.

        Returns a new ID for the transposable element.
        """
        ...  # not implemented yet

    @abstractmethod
    def copy_te(self, te: int, offset: int) -> int | None:
        """
        Copy a transposable element.

        Copy the transposable element te to an offset from its current
        location.

        The offset can be positive or negative; if positive the te is copied
        upwards and if negative it is copied downwards. If the offset moves
        the copy left of index 0 or right of the largest index, it should
        wrap around, since the genome is circular.

        If te is not active, return None (and do not copy it).
        """
        ...  # not implemented yet

    @abstractmethod
    def disable_te(self, te: int) -> None:
        """
        Disable a TE.

        If te is an active TE, then make it inactive. Inactive
        TEs are already inactive, so there is no need to do anything
        for those.
        """
        ...  # not implemented yet

    @abstractmethod
    def active_tes(self) -> list[int]:
        """Get the active TE IDs."""
        ...  # not implemented yet

    @abstractmethod
    def __str__(self) -> str:
        """
        Return a string representation of the genome.

        Create a string that represents the genome. By nature, it will be
        linear, but imagine that the last character is immidiatetly followed
        by the first.

        The genome should start at position 0. Locations with no TE should be
        represented with the character '-', active TEs with 'A', and disabled
        TEs with 'x'.
        """
        ...  # not implemented yet


class ListGenome(Genome):
    """
    Representation of a genome.

    Implements the Genome interface using Python's built-in lists
    """

    next_te_id: int                  # For assigning IDs to TEs.
    nuc: list[int]                   # The genome (as a linear list).
    active: dict[int, int]            # map from active IDs to their length

    def __init__(self, n: int):
        """Create a new genome with length n."""
        self.next_te_id = 1
        self.nuc = [0] * n
        self.active = {}

    def insert_te(self, pos: int, length: int) -> int | None:
        """
        Insert a new transposable element.

        Insert a new transposable element at position pos and len
        nucleotide forward.

        If the TE collides with an existing TE, i.e. genome[pos]
        already contains TEs, then that TE should be disabled and
        removed from the set of active TEs.

        Returns a new ID for the transposable element.
        """
        # If we have collisions, destroy the existing TE that
        # is hit.
        if self.nuc[pos] in self.active:
            del self.active[self.nuc[pos]]

        # insert the TE
        te = self.next_te_id
        self.next_te_id += 1
        self.active[te] = length
        self.nuc[pos:pos] = [te] * length

        return te

    def copy_te(self, te: int, offset: int) -> int | None:
        """
        Copy a transposable element.

        Copy the transposable element te to an offset from its current
        location.

        The offset can be positive or negative; if positive the te is copied
        upwards and if negative it is copied downwards. If the offset moves
        the copy left of index 0 or right of the largest index, it should
        wrap around, since the genome is circular.

        If te is not active, return None (and do not copy it).
        """
        if te not in self.active:
            return None
        # Find the location of the TE. It is a lot of bookkeeping
        # to keep track of positions in a changing genome, so we
        # explicitly search for the bugger instead.
        pos = self.nuc.index(te)
        length = self.active[te]
        return self.insert_te((pos + offset) % len(self.nuc), length)

    def disable_te(self, te: int) -> None:
        """
        Disable a TE.

        If te is an active TE, then make it inactive. Inactive
        TEs are already inactive, so there is no need to do anything
        for those.
        """
        if te in self.active:
            del self.active[te]

    def active_tes(self) -> list[int]:
        """Get the active TE IDs."""
        return [te for te in self.active]

    def __str__(self) -> str:
        """
        Return a string representation of the genome.

        Create a string that represents the genome. By nature, it will be
        linear, but imagine that the last character is immidiatetly followed
        by the first.

        The genome should start at position 0. Locations with no TE should be
        represented with the character '-', active TEs with 'A', and disabled
        TEs with 'x'.
        """
        return ''.join(
            '-' if a == 0 else
            'A' if a in self.active else
            'x'
            for a in self.nuc
        )


genome = ListGenome(20)
print(genome)
print(genome.active_tes())
genome.insert_te(5, 10)   # Insert te 1
print(genome)
print(genome.active_tes())
genome.insert_te(10, 10)  # Disable 1 but make 2 active
print(genome)
print(genome.active_tes())
genome.copy_te(2, 20)     # Make TE 3 20 to the right of the start of 2
print(genome)
print(genome.active_tes())
genome.copy_te(2, -15)     # Make TE 3 15 to the right of the start of 2
print(genome)
print(genome.active_tes())
genome.insert_te(50, 10)
print(genome)
print(genome.active_tes())
genome.disable_te(3)
print(genome)
print(genome.active_tes())
