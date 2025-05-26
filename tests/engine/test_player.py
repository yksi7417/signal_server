import pytest
from mahjong_engine.player import Player
from mahjong_engine.tile import Tile
from mahjong_engine.melds import Pung
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent
from mahjong_engine.constants import SUIT_DOTS, SUIT_BAMBOO, WIND_EAST


@pytest.fixture
def player_with_agent():
    agent = AIPlayerAgent(player_id=0)
    player = Player(player_id=0, agent=agent)
    player.wind = WIND_EAST
    return player


def test_player_creation(player_with_agent):
    player = player_with_agent
    assert player.player_id == 0
    assert isinstance(player.agent, AIPlayerAgent)
    assert player.hand == []
    assert player.revealed_sets == []
    assert player.discards == []
    assert player.score == 0
    assert player.wind == WIND_EAST


def test_player_creation_no_agent_no_wind():
    player = Player(player_id=1)
    assert player.player_id == 1
    assert player.agent is None
    assert player.wind is None


def test_player_add_revealed_set(player_with_agent):
    player = player_with_agent
    tile1 = Tile(SUIT_DOTS, '1')
    pung_meld = Pung(tile1, revealed=True)

    player.add_revealed_set(pung_meld)
    assert len(player.revealed_sets) == 1
    assert player.revealed_sets[0] == pung_meld

    with pytest.raises(ValueError, match="Can only add Meld objects to revealed_sets"):
        player.add_revealed_set("not a meld")


def test_player_repr(player_with_agent):
    player = player_with_agent
    expected_repr_initial = f"Player(player_id=0, agent=AIPlayerAgent, wind={WIND_EAST}, revealed_sets=0)"
    assert repr(player) == expected_repr_initial

    player.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_BAMBOO, '7')]
    player.add_revealed_set(Pung(Tile(SUIT_DOTS, '5'), revealed=True))

    expected_repr_detailed = f"Player(player_id=0, agent=AIPlayerAgent, wind={WIND_EAST}, revealed_sets=1)"
    assert repr(player) == expected_repr_detailed


def test_player_repr_no_agent_no_wind():
    player = Player(player_id=2)
    expected = "Player(player_id=2, agent=None, wind=None, revealed_sets=0)"
    assert repr(player) == expected


def test_player_set_agent(player_with_agent):
    player = player_with_agent
    assert isinstance(player.agent, AIPlayerAgent)

    new_agent = HumanPlayerAgent(player_id=0)
    player.set_agent(new_agent)
    assert isinstance(player.agent, HumanPlayerAgent)

    expected = f"Player(player_id=0, agent=HumanPlayerAgent, wind={WIND_EAST}, revealed_sets=0)"
    assert repr(player) == expected
