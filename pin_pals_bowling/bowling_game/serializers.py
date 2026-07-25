from restframework import serializers
from django.contrib.auth import get_user_model
from .models import BowlingGame, Frame, Roll

User = get_user_model()


class RollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roll
        fields = ['id', 'roll_number', 'pins_knocked_down']
        read_only_fields = ['id', 'roll_number']


class FrameSerializer(serializers.ModelSerializer):
    # Nest rolls inside each frame
    rolls = RollSerializer(many=True, read_only=True)

    class Meta:
        model = Frame
        fields = [
            'id', 
            'frame_number', 
            'frame_score', 
            'is_strike', 
            'is_spare', 
            'is_complete', 
            'rolls'
        ]
        read_only_fields = fields  # Frames are managed by the scoring service


class BowlingGameSerializer(serializers.ModelSerializer):
    # Nest frames inside the game
    frames = FrameSerializer(many=True, read_only=True)
    player_username = serializers.ReadOnlyField(source='player.username')

    class Meta:
        model = BowlingGame
        fields = [
            'id', 
            'player', 
            'player_username', 
            'status', 
            'total_score', 
            'created_at', 
            'updated_at', 
            'frames'
        ]
        read_only_fields = ['id', 'status', 'total_score', 'created_at', 'updated_at', 'frames']


class RecordRollInputSerializer(serializers.Serializer):
    """
    Input serializer specifically for validating incoming POST requests when throwing a ball.
    """
    pins = serializers.IntegerField(min_value=0, max_value=10)