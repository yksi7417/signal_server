import unittest
from mahjong_engine.game_state import GameState
from mahjong_engine.player import Player
from mahjong_engine.tile import Tile
from mahjong_engine.melds import Pung 
from mahjong_engine.constants import INIT_HAND_SIZE, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_DOTS, SUIT_WINDS, SUIT_DRAGONS
from mahjong_engine.player_agent import HumanPlayerAgent, AIPlayerAgent

class TestGameState(unittest.TestCase):

    def setUp(self):
        # Common setup can go here if needed
        pass

    def test_win_check_after_draw_4_revealed_sets(self):
        """Test win check after drawing the last tile for a pair, with 4 revealed Pungs."""
        game = GameState(num_players=1) 
        player_0 = game.players[0]
        player_0.agent = HumanPlayerAgent(player_id=0) # Ensure agent type if relevant
        game.current_player_index = 0

        player_0.revealed_sets = [
            Pung(Tile(SUIT_BAMBOO, '3')),
            Pung(Tile(SUIT_BAMBOO, '7')),
            Pung(Tile(SUIT_BAMBOO, '6')),
            Pung(Tile(SUIT_CHARACTERS, '3'))
        ]
        # Player has 4 Pungs * 3 tiles/Pung = 12 tiles revealed.
        # Hand should have INIT_HAND_SIZE - 12 tiles. If INIT_HAND_SIZE = 13, hand has 1 tile.
        self.assertEqual(INIT_HAND_SIZE, 13, "Test assumes INIT_HAND_SIZE is 13 for hand setup.")
        player_0.hand = [Tile(SUIT_BAMBOO, '2')] # One tile, waiting for its pair

        winning_tile = Tile(SUIT_BAMBOO, '2')
        
        # Set up the wall: winning tile first, then enough other unique tiles
        other_tiles = []
        # Create a diverse set of tiles for the rest of the wall to avoid unintended consequences
        for suit in [SUIT_DOTS, SUIT_WINDS, SUIT_DRAGONS]:
            for i in range(1, 8): # Values 1-7 for Dots, Winds, Dragons have distinct representations
                if suit == SUIT_WINDS and i > 4: continue # Winds only E,S,W,N (1-4)
                if suit == SUIT_DRAGONS and i > 3: continue # Dragons only R,G,W (1-3)
                other_tiles.append(Tile(suit, str(i)))
        
        game.wall = [winning_tile] + other_tiles[:50] # Ensure wall is sufficiently populated

        # Player draws the winning tile
        drawn_tile_obj = game.draw_tile_for_current_player()
        
        self.assertIsNotNone(drawn_tile_obj, "A tile should have been drawn from the wall.")
        self.assertEqual(drawn_tile_obj, winning_tile, "The wrong tile was drawn.")
        self.assertTrue(game.winner_found, "Winner should be found after drawing the completing pair tile.")
        self.assertEqual(game.winning_player_id, player_0.player_id, "The winning player ID is incorrect.")

    def test_win_claim_on_discard(self):
        """Test that a player can claim win on another player's discard."""
        game = GameState(num_players=2)
        player_0 = game.players[0] # Discarder
        player_1 = game.players[1] # Winner

        player_0.agent = HumanPlayerAgent(player_id=0)
        player_1.agent = HumanPlayerAgent(player_id=1)

        # Setup Player 1 (claimer) to have a hand ready to win
        # 3 revealed Pungs = 9 tiles
        player_1.revealed_sets = [
            Pung(Tile(SUIT_BAMBOO, '3')),
            Pung(Tile(SUIT_BAMBOO, '4')),
            Pung(Tile(SUIT_BAMBOO, '5'))
        ]
        # Hand needs INIT_HAND_SIZE - 9 tiles = 13 - 9 = 4 tiles.
        # These 4 tiles + discarded tile should form 1 meld + 1 pair.
        # Waiting for: Tile(SUIT_CHARACTERS, '1') for a pair with an existing C1.
        # Hand will be: C1 (for pair), C2, C3, C4 (for Chow).
        player_1.hand = [
            Tile(SUIT_CHARACTERS, '1'), 
            Tile(SUIT_CHARACTERS, '2'),
            Tile(SUIT_CHARACTERS, '3'),
            Tile(SUIT_CHARACTERS, '4')
        ]
        self.assertEqual(len(player_1.hand), INIT_HAND_SIZE - len(player_1.revealed_sets) * 3, "Player 1 hand size incorrect before discard event.")


        # Setup Player 0 (discarder)
        game.current_player_index = 0
        discard_tile_obj = Tile(SUIT_CHARACTERS, '1') # The tile Player 1 needs to win

        # Player 0's hand must be INIT_HAND_SIZE + 1 tiles before discard.
        # Create a dummy hand for Player 0 that includes the discard_tile_obj
        player_0_hand_list = [discard_tile_obj]
        # Fill the rest of P0's hand with unique tiles different from discard_tile_obj
        temp_suit_idx = 0
        temp_val_idx = 1
        suits_for_dummy = [SUIT_DOTS, SUIT_WINDS, SUIT_DRAGONS, SUIT_BAMBOO, SUIT_CHARACTERS] # Cycle through suits
        
        while len(player_0_hand_list) < INIT_HAND_SIZE + 1:
            suit = suits_for_dummy[temp_suit_idx]
            val = str(temp_val_idx)
            
            # Avoid issues with Winds/Dragons values
            if suit == SUIT_WINDS and temp_val_idx > 4: val = '1' 
            if suit == SUIT_DRAGONS and temp_val_idx > 3: val = '1'
            
            potential_tile = Tile(suit, val)
            if potential_tile != discard_tile_obj and potential_tile not in player_0_hand_list:
                 player_0_hand_list.append(potential_tile)

            temp_val_idx +=1
            if temp_val_idx > 9:
                temp_val_idx = 1
                temp_suit_idx = (temp_suit_idx + 1) % len(suits_for_dummy)

        player_0.hand = player_0_hand_list
        self.assertEqual(len(player_0.hand), INIT_HAND_SIZE + 1, "Player 0 hand size incorrect before discard.")
        
        # Player 0 discards the tile
        discard_successful = game.discard_tile_for_current_player({
            'suit': discard_tile_obj.suit,
            'value': discard_tile_obj.value
        })

        self.assertTrue(discard_successful, "Discard operation failed.")
        
        # Check for Player 1's win claim
        self.assertEqual(game.pending_claim_player_id, player_1.player_id, "Player 1 should have a pending win claim.")
        self.assertEqual(game.claim_type_pending, "WIN", "The pending claim type should be WIN.")
        self.assertEqual(game.potential_claim_tile, discard_tile_obj, "The potential claim tile is incorrect.")

if __name__ == '__main__':
    unittest.main()
