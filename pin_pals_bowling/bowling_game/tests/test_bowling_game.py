import pytest
from django.contrib.auth import get_user_model
from bowling_game.models import BowlingGame
from bowling_game.services.bowling_service import BowlingScoringService

User = get_user_model()

# Parameterized tests helper
def play_fixture(times, game, pins=1):
    for i in range(times):
        BowlingScoringService.record_roll(game=game, pins=pins)
        game.refresh_from_db()

@pytest.fixture
def player(db):
    """Fixture to create a test user."""
    return User.objects.create_user(username="lebowski", password="password123")


@pytest.mark.django_db
def test_create_game_and_record_rolls(player):
    """Tests creating a game and throwing a spare followed by a 5-pin roll."""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    # 2. Roll 1: 7 pins
    BowlingScoringService.record_roll(game=game, pins=7)
    
    # Refresh model state from DB
    game.refresh_from_db()
    assert game.frames.count() == 1
    assert game.frames.first().rolls.count() == 1
    # Score should be pending (not calculated until frame/lookahead completes)
    assert game.total_score == 0

    # 3. Roll 2: 3 pins (Completes Spare for Frame 1)
    BowlingScoringService.record_roll(game=game, pins=3)
    game.refresh_from_db()
    
    frame_1 = game.frames.get(frame_number=1)
    assert frame_1.is_spare is True
    assert frame_1.is_complete is True

    # 4. Roll 3: 5 pins (Frame 2, Roll 1 - resolves Frame 1 spare bonus!)
    BowlingScoringService.record_roll(game=game, pins=5)
    game.refresh_from_db()

    # Frame 1 score = 10 + 5 = 15 points
    frame_1.refresh_from_db()
    assert frame_1.frame_score == 15
    # assert game.total_score == 1


@pytest.mark.django_db
def test_perfect_game(player):
    """Tests hitting strike on all frames for every roll possible"""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    play_fixture(12, game, 10)
    frame_10 = game.frames.get(frame_number=10)

    assert frame_10.is_strike is True
    assert frame_10.is_complete is True


    assert frame_10.frame_score == 300
    assert game.total_score == 300


@pytest.mark.django_db
def test_all_spares(player):

    """Tests creating a game and throwing a spare on every frame."""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    play_fixture(21, game, 5)
    frame_10 = game.frames.get(frame_number=10)
    
    assert frame_10.is_strike is False
    assert frame_10.is_spare is True
    assert frame_10.is_complete is True
    
    game.refresh_from_db()
    assert game.total_score == 150

@pytest.mark.django_db
def test_open_frame(player):

    """Tests creating an all open frames and no bonus at 10th."""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    play_fixture(20, game)
    frame_10 = game.frames.get(frame_number=10)
    
    assert frame_10.is_strike is False
    assert frame_10.is_spare is False
    assert frame_10.is_complete is True
    
    game.refresh_from_db()
    assert game.total_score == 20
    assert game.status == 'COMPLETED'


@pytest.mark.django_db
def test_last_frame_strike_plus_two(player):

    """Tests creating a game and throwing a spare on every frame."""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    play_fixture(10, game, 10)
    frame_10 = game.frames.get(frame_number=10)


    # Roll 11: 3 pins 1st bonus roll
    BowlingScoringService.record_roll(game=game, pins=3)
    game.refresh_from_db()

    # Roll 12: 3 pins 2nd bonus roll
    BowlingScoringService.record_roll(game=game, pins=3)
    game.refresh_from_db()
    
    assert frame_10.is_strike is False
    assert frame_10.is_spare is False
    assert frame_10.is_complete is False
    
    game.refresh_from_db()
    assert game.total_score == 279

@pytest.mark.django_db
def test_last_frame_spare_plus_one(player):

    """Tests creating a game and throwing a spare on every frame."""
    # 1. Start a new game
    game = BowlingGame.objects.create(player=player)
    assert game.total_score == 0
    assert game.status == 'IN_PROGRESS'

    play_fixture(9, game, 10)

    # Roll 10: 7 pins 
    BowlingScoringService.record_roll(game=game, pins=7)
    game.refresh_from_db()

    # Roll 11: 3 pins Spare
    BowlingScoringService.record_roll(game=game, pins=3)
    game.refresh_from_db()
    frame_10 = game.frames.get(frame_number=10)
    
    assert frame_10.is_strike is False
    assert frame_10.is_spare is True
    assert frame_10.is_complete is False
    BowlingScoringService.record_roll(game=game, pins=3)
    game.refresh_from_db()
    
    assert game.total_score == 270


