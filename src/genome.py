"""A circular genome for simulating transposable elements."""

from abc import (
    # A tag that says that we can't use this class except by specialising it
    ABC,
    # A tag that says that this method must be implemented by a child class
    abstractmethod
)
from typing import Iterable


class Genome(ABC):
    """Representation of a circular enome."""

    def __init__(self, n: int):
        """Create a genome of size n."""
        ...  # not implemented yet

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
    def __len__(self) -> int:
        """Get the current length of the genome."""
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
    active: dict[int, int]           # map from active IDs to their length

    def __init__(self, n: int):
        """Create a new genome with length n."""
        self.next_te_id = 1
        self.nuc = [0] * n
        self.active = {}

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
        return list(self.active)

    def __len__(self) -> int:
        """Return length of genome."""
        return len(self.nuc)

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


class LinkedListGenome(Genome):
    """
    Representation of a genome.

    Implements the Genome interface using linked lists.
    """

    next_te_id: int                  # For assigning IDs to TEs.
    nuc: list[int]                   # Content of the genome
    next: list[int]                  # Next pointers
    prev: list[int]                  # Prev pointers
    # Map from active IDs to their pos and length
    active: dict[int, tuple[int, int]]

    def __init__(self, n: int):
        """Create a new genome with length n."""
        self.next_te_id = 1
        self.nuc = [0] * n
        self.next = [(i + 1) % n for i in range(n)]
        self.prev = [(i - 1) % n for i in range(n)]
        self.active = {}

    def _get_index(self, pos: int) -> int:
        """
        Get the index in the list-arrays that corresponds to position.

        Since we use linked lists, we cannot index directly, but must
        search though the list from the beginning.
        """
        n = 0
        for _ in range(pos):
            n = self.next[n]
        return n

    def _insert_te_at_index(self, i: int, length: int) -> int:
        """
        Insert a new transposable element.

        Insert a new transposable element at the link at index i in
        the arrays.
        If the TE collides with an existing TE, i.e. genome[pos]
        already contains TEs, then that TE should be disabled and
        removed from the set of active TEs.
        Returns a new ID for the transposable element.
        """
        if self.nuc[i] in self.active:
            del self.active[self.nuc[i]]

        # insert the TE
        te = self.next_te_id
        self.next_te_id += 1

        j = self.prev[i]  # the node we should insert after

        n = len(self.nuc)
        self.active[te] = (n, length)
        self.nuc.extend([te] * length)
        self.next.extend([n + i + 1 for i in range(length - 1)] + [i])
        self.prev.extend([j] + [*range(n, n + length - 1)])
        self.next[j] = n
        self.prev[i] = n + length - 1

        return te

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
        i = self._get_index(pos)
        return self._insert_te_at_index(i, length)

    def _move_offset(self, i: int, offset: int) -> int:
        """Move for index i to the link offset away (either direction)."""
        if offset >= 0:
            for _ in range(offset):
                i = self.next[i]
        else:
            for _ in range(-offset):
                i = self.prev[i]
        return i

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
        pos, length = self.active[te]
        return self._insert_te_at_index(self._move_offset(pos, offset), length)

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
        return list(self.active)

    @property
    def _nucleotides(self) -> Iterable[int]:
        """Iterate through the nucleotides in the genome."""
        yield self.nuc[0]
        n = self.next[0]
        while n != 0:
            yield self.nuc[n]
            n = self.next[n]

    def __len__(self) -> int:
        """Return length of genome."""
        return len(self.nuc)

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
            for a in self._nucleotides
        )
