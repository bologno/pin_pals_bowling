from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BowlingGame(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bowling_games')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    total_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game #{self.id} - {self.player.username} ({self.total_score} pts)"


class Frame(models.Model):
    game = models.ForeignKey(BowlingGame, on_delete=models.CASCADE, related_name='frames')
    frame_number = models.PositiveSmallIntegerField()  # 1 to 10
    frame_score = models.PositiveIntegerField(default=0) # Accumulated frame score
    is_strike = models.BooleanField(default=False)
    is_spare = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ['frame_number']
        unique_together = ('game', 'frame_number')

    def __str__(self):
        return f"Game #{self.game_id} - Frame {self.frame_number}"


class Roll(models.Model):
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name='rolls')
    roll_number = models.PositiveSmallIntegerField()  # 1, 2, or 3 (10th frame only)
    pins_knocked_down = models.PositiveSmallIntegerField()  # 0 to 10

    class Meta:
        ordering = ['roll_number']
        unique_together = ('frame', 'roll_number')

    def __str__(self):
        return f"Frame {self.frame.frame_number}, Roll {self.roll_number}: {self.pins_knocked_down} pins"