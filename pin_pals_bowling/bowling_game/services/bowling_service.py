from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import BowlingGame, Frame, Roll


class BowlingScoringService:

    @classmethod
    @transaction.atomic
    def record_roll(cls, game: BowlingGame, pins: int) -> Roll:
        """
        Records a new roll for the game, updates frame metadata,
        and recalculates running scores.
        """
        if pins < 0 or pins > 10:
            raise ValidationError("Pins must be between 0 and 10.")

        if game.status == 'COMPLETED':
            raise ValidationError("This game is already finished.")

        # 1. Fetch or create the active frame
        current_frame = cls._get_or_create_active_frame(game)
        if not current_frame:
            raise ValidationError("This game is already complete.")

        # 2. Validate pins against previous rolls in this frame
        existing_rolls = list(current_frame.rolls.all())
        roll_number = len(existing_rolls) + 1

        cls._validate_roll(current_frame, existing_rolls, pins)

        # 3. Create the roll
        roll = Roll.objects.create(
            frame=current_frame,
            roll_number=roll_number,
            pins_knocked_down=pins
        )
        existing_rolls.append(roll)

        # 4. Update frame flags (strike, spare, is_complete)
        cls._update_frame_status(current_frame, existing_rolls)

        # 5. Recalculate scores across all completed/lookahead frames
        cls.recalculate_game_score(game)

        return roll

    @classmethod
    def _get_or_create_active_frame(cls, game: BowlingGame) -> Frame | None:
        """Finds current active frame or creates the next frame up to 10."""
        last_frame = game.frames.order_by('frame_number').last()

        if not last_frame:
            return Frame.objects.create(game=game, frame_number=1)

        if not last_frame.is_complete:
            return last_frame

        if last_frame.frame_number < 10:
            return Frame.objects.create(
                game=game, 
                frame_number=last_frame.frame_number + 1
            )

        return None  # All 10 frames finished

    @classmethod
    def _validate_roll(cls, frame: Frame, existing_rolls: list[Roll], pins: int):
        """Validates pin counts for frames 1-9 and special rules for frame 10."""
        roll_count = len(existing_rolls)

        if frame.frame_number < 10:
            if roll_count == 1:
                first_pins = existing_rolls[0].pins_knocked_down
                if first_pins + pins > 10:
                    raise ValidationError(f"Invalid pin count. Only {10 - first_pins} pins left.")
        else:
            # 10th Frame pin rules
            if roll_count == 1:
                first_pins = existing_rolls[0].pins_knocked_down
                if first_pins < 10 and (first_pins + pins > 10):
                    raise ValidationError(f"Invalid pin count. Only {10 - first_pins} pins left.")
            elif roll_count == 2:
                r1 = existing_rolls[0].pins_knocked_down
                r2 = existing_rolls[1].pins_knocked_down

                if r1 < 10 and (r1 + r2 < 10):
                    raise ValidationError("Frame 10 complete — no third roll allowed without a strike or spare.")

                if r1 == 10 and r2 < 10 and (r2 + pins > 10):
                    raise ValidationError(f"Invalid pin count. Only {10 - r2} pins left.")

    @classmethod
    def _update_frame_status(cls, frame: Frame, rolls: list[Roll]):
        """Sets strike, spare, and completion states on the frame."""
        pins = [r.pins_knocked_down for r in rolls]

        if frame.frame_number < 10:
            if pins[0] == 10:
                frame.is_strike = True
                frame.is_complete = True
            elif len(pins) == 2:
                frame.is_complete = True
                if sum(pins) == 10:
                    frame.is_spare = True
        else:
            # Frame 10 Rules
            if len(pins) == 2:
                if pins[0] == 10:
                    frame.is_strike = True
                elif sum(pins) == 10:
                    frame.is_spare = True
                elif sum(pins) < 10:
                    frame.is_complete = True
            elif len(pins) == 3:
                frame.is_complete = True

        frame.save()

    @classmethod
    def recalculate_game_score(cls, game: BowlingGame):
        """
        Traverses frames 1-10 to calculate frame_score and total_score.
        Applies lookahead rules for strikes (+2 rolls) and spares (+1 roll).
        """
        frames = list(game.frames.prefetch_related('rolls').order_by('frame_number'))

        # Flatten all rolls thrown in order to simplify lookahead calculation
        all_rolls = []
        for f in frames:
            for r in f.rolls.all():
                all_rolls.append(r.pins_knocked_down)

        roll_idx = 0
        running_total = 0

        for frame in frames:
            frame_rolls = list(frame.rolls.all())
            if not frame_rolls:
                break

            if frame.frame_number < 10:
                # Frames 1 through 9
                if frame.is_strike:
                    # Strike: Needs next 2 rolls to resolve frame score
                    if len(all_rolls) >= roll_idx + 3:
                        frame_pts = 10 + all_rolls[roll_idx + 1] + all_rolls[roll_idx + 2]
                        running_total += frame_pts
                        frame.frame_score = running_total
                    roll_idx += 1

                elif frame.is_spare:
                    # Spare: Needs next 1 roll to resolve frame score
                    if len(all_rolls) >= roll_idx + 3:
                        frame_pts = 10 + all_rolls[roll_idx + 2]
                        running_total += frame_pts
                        frame.frame_score = running_total
                    roll_idx += 2

                elif frame.is_complete:
                    # Open Frame
                    frame_pts = sum(r.pins_knocked_down for r in frame_rolls)
                    running_total += frame_pts
                    frame.frame_score = running_total
                    roll_idx += 2

            else:
                # Frame 10
                if frame.is_complete:
                    frame_pts = sum(r.pins_knocked_down for r in frame_rolls)
                    running_total += frame_pts
                    frame.frame_score = running_total

            frame.save()

        # Update Game Total & Status
        game.total_score = running_total
        
        tenth_frame = game.frames.filter(frame_number=10, is_complete=True).first()
        if tenth_frame:
            game.status = 'COMPLETED'

        game.save()