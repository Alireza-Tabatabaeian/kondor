from datetime import datetime

from rest_framework import status

from duel.myapp.appstatics import GameState, GameCacheStatus
from duel.myapp.models import UserLeague, Game, UserProfile, GameCache


def needed_coins(challenge_type=1):
    return 500


def league_available(league):
    return False if league is None or not isinstance(league, int) or league > 5 or league < 1 else True


def user_join_a_game(user, profile, league, challenge_type):
    user_league = UserLeague.objects.filter(user=user, league=league)
    if not user_league:
        user_league = UserLeague.objects.create(user=user, league=league)
    else:
        user_league = user_league[0]
    user_level = profile.general_level + 3 * user_league.level
    return is_there_a_game(league, user_level, user, challenge_type)


def is_there_a_game(league, level, user, challenge_type):
    open_games = Game.objects.filter(league=league, level=level, status=GameState.WAITINGG).exclude(
        host_user=user)[:1]
    if not open_games:
        open_games = Game.objects.filter(league=league, level__gte=level - 1, level__lte=level + 1,
                                         status=GameState.WAITINGG).exclude(host_user=user)[:1]
    return level, status.HTTP_404_NOT_FOUND if not open_games else open_games[0], status.HTTP_200_OK


def join_user_as_guest(game, user, profile):
    game.guest_user = user
    game.status = GameState.WAITINGA
    profile.coins -= needed_coins()
    profile.save()
    game.correspond = user
    game.end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
    game.save()
    host_profile = UserProfile.objects.get(user=game.host_user)
    host_league = UserLeague.objects.get(user=game.host_user, league=game.league)
    gc = GameCache.objects.get(game=game)
    gc.code = GameCacheStatus.WaitingAG
    gc.save()
    return {
        "game_id": game.id,
        "opponent": {
            "name": game.host_user.first_name,
            "general_score": host_profile.general_score,
            "league_score": host_league.score
        },
        "course": game.course,
        "correspond": game.correspond,
        "deadline": game.end_time,
        "cache": gc.code
    }


def buildup_game(league, level, user, profile):
    game = Game.objects.create(
        league=league, level=level, status=GameState.STARTED, host_user=user, correspond=user,
        end_time=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
    )
    gc = GameCache.objects.create(game=game, code=GameCacheStatus.WaitingG)
    profile.coins -= needed_coins()
    profile.save()
    return {
        "game_id": game.id,
        "opponent": 0,
        "deadline": game.end_time,
        "cache": gc.code,
    }
