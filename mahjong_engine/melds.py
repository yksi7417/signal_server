from enum import Enum
from .tile import Tile # Ensure Tile is imported

class MeldType(Enum):
    PUNG = "Pung"
    KONG = "Kong"
    CHOW = "Chow"
    PAIR = "Pair" # Often treated separately but can be a type of meld conceptually

class Meld:
    def __init__(self, meld_type, tiles, revealed=False, claimed_from=None):
        self.meld_type = meld_type # MeldType Enum
        
        if not all(isinstance(t, Tile) for t in tiles):
            raise ValueError("Meld must be initialized with Tile objects.")

        self.raw_tiles = sorted(tiles) # Store all tiles that form the meld, sorted for consistency
        self.revealed = revealed # Was this meld revealed (claimed or declared)?
        self.claimed_from = claimed_from # player_id from whom a tile was claimed to make this meld (if any)

        if meld_type == MeldType.PUNG:
            if not (len(self.raw_tiles) == 3 and self.raw_tiles[0] == self.raw_tiles[1] == self.raw_tiles[2]):
                raise ValueError(f"Invalid tiles for Pung: {self.raw_tiles}")
            self.key_tile = self.raw_tiles[0] # The tile that makes up the Pung
        elif meld_type == MeldType.KONG:
            if not (len(self.raw_tiles) == 4 and self.raw_tiles[0] == self.raw_tiles[1] == self.raw_tiles[2] == self.raw_tiles[3]):
                raise ValueError(f"Invalid tiles for Kong: {self.raw_tiles}")
            self.key_tile = self.raw_tiles[0] # The tile that makes up the Kong
        elif meld_type == MeldType.CHOW:
            # Tiles must be sequential and of the same numeric suit
            if not (len(self.raw_tiles) == 3 and
                    self.raw_tiles[0].is_numeric_suit() and
                    self.raw_tiles[0].suit == self.raw_tiles[1].suit == self.raw_tiles[2].suit and
                    int(self.raw_tiles[1].value) == int(self.raw_tiles[0].value) + 1 and
                    int(self.raw_tiles[2].value) == int(self.raw_tiles[1].value) + 1):
                raise ValueError(f"Invalid tiles for Chow: {self.raw_tiles}")
            # Key tile for Chow is often the lowest tile in sequence.
            self.key_tile = self.raw_tiles[0]
        elif meld_type == MeldType.PAIR:
            if not (len(self.raw_tiles) == 2 and self.raw_tiles[0] == self.raw_tiles[1]):
                raise ValueError(f"Invalid tiles for Pair: {self.raw_tiles}")
            self.key_tile = self.raw_tiles[0]
        else:
            raise ValueError(f"Unknown meld type: {meld_type}")


    def __repr__(self):
        return f"{self.meld_type.value}({self.raw_tiles}, revealed={self.revealed})"

    def __eq__(self, other):
        if not isinstance(other, Meld): return False
        # For equality, check type, the actual tiles, and revealed status.
        # claimed_from is not part of equality as it's contextual metadata.
        return (self.meld_type == other.meld_type and 
                self.raw_tiles == other.raw_tiles and 
                self.revealed == other.revealed)

    def __hash__(self):
        # Convert list of tiles to tuple for hashing
        return hash((self.meld_type, tuple(self.raw_tiles), self.revealed))

# Convenience classes (Optional, but can be nice)
class Pung(Meld):
    def __init__(self, tile, revealed=False, claimed_from=None):
        # tile argument here is the Tile object that forms the Pung
        if not isinstance(tile, Tile):
            raise ValueError("Pung must be initialized with a Tile object.")
        super().__init__(MeldType.PUNG, [tile, tile, tile], revealed, claimed_from)

class Kong(Meld):
    def __init__(self, tile, revealed=False, claimed_from=None):
        if not isinstance(tile, Tile):
            raise ValueError("Kong must be initialized with a Tile object.")
        super().__init__(MeldType.KONG, [tile, tile, tile, tile], revealed, claimed_from)

class Pair(Meld):
    def __init__(self, tile): # Pairs are never "revealed" in the same way as other melds
        if not isinstance(tile, Tile):
            raise ValueError("Pair must be initialized with a Tile object.")
        super().__init__(MeldType.PAIR, [tile, tile], revealed=False)

class Chow(Meld):
    def __init__(self, t1, t2, t3, revealed=False, claimed_from=None):
        # t1, t2, t3 must be Tile objects
        if not all(isinstance(t, Tile) for t in [t1, t2, t3]):
            raise ValueError("Chow must be initialized with three Tile objects.")
        tiles = sorted([t1, t2, t3]) # Ensure they are sorted before passing to base Meld
        super().__init__(MeldType.CHOW, tiles, revealed, claimed_from)
