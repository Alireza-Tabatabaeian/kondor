import re

from rest_framework import status
from rest_framework.response import Response

from question.questionStatics import League,CourseModel

from .appstatics import CallbackEndpoints, GameState
from .utilities import get_course, get_game, calculate_score


def course_is_right(course, game):
    if (game.round < 3 and course.course_model == CourseModel.SPECIALIZED) or (
            game.round > 2 and course.course_model == CourseModel.GENERAL):
        return False
    return (course != game.course) or (game.league == League.LANGUAGE and game.round == 4)


# tp is True if Duel game, False if Daily game
def check_answer(answer, tp):
    ln = 5 if tp else 10
    return isinstance(answer, str) and len(answer) == ln and re.fullmatch(r"[10x]*", answer) is not None


# tp is True if Duel, False if Daily Game
def verify_answer(user, verification, score, tp, password, gid=917):
    if verification is None:
        return False
    if not isinstance(verification, int):
        return False
    prime = 137 if tp else 3
    verify = gid * user.id + password + score * prime
    return verify == verification


def game_validate(game_id=0, user=None, callback=CallbackEndpoints.CourseRequest, **data):
    game, sts = verify_game_and_user(game_id, user)
    if not sts == 200:
        return None, sts
    if not check_user_access_game(game, user):
        return None, 403
    if not check_play_state(game, callback):
        return None, 403

    if callback == CallbackEndpoints.Update:
        return game, 200

    if not check_user_play_game(game, user):
        return None, 403

    if callback == CallbackEndpoints.CourseSelect:
        course = get_course(data.get('course', None))
        if course is None:
            return None, 404
        if not course_is_right(course):
            return None, 403

    elif callback == CallbackEndpoints.SendAnswer:
        answer = data.get('answer', None)
        if answer is None:
            return None, 404
        verification = data.get('verify', None)
        if verification is None or not check_answer(answer):
            return None, 808
        score = calculate_score(answer)
        if not verify_answer(user, verification, score, True, game.password, game.id):
            return None, 808
    return game, 200


def verify_game_and_user(game_id, user):
    game = get_game(game_id)
    if game is None:
        return None, 404
    if not user.is_authenticated:
        return None, 403
    return game, 200


def check_user_access_game(game, user):
    return game.host_user == user or game.guest_user == user


def check_user_play_game(game, user):
    return game.correspond == user


def check_play_state(game, callback):
    allowed = {
        CallbackEndpoints.CourseRequest: {GameState.STARTED, GameState.SELECTQ},
        CallbackEndpoints.Sit: {GameState.RESPONSE1, GameState.RESPONSE2, GameState.HOSTASQ},
        CallbackEndpoints.CourseSelect: {GameState.STARTED, GameState.SELECTQ},
        CallbackEndpoints.SendAnswer: {GameState.SIT0, GameState.SIT1, GameState.SIT2},
    }
    return callback == CallbackEndpoints.Update or game.status in allowed[callback]


def check_daily_answer(user, answer, verification, password):
    score = 0
    if answer:
        counter = 0
        for i in answer:
            if i == '1':
                score += 25 if counter < 5 else 75
            counter += 1
        verified_answer = verify_answer(user, verification, score, False, password)
        if check_answer(answer, False) and verified_answer:
            return score
    return None


def response_error(code):
    log = {
        404: {"msg": "Bad Request, Check inputs and try again", "code": status.HTTP_404_NOT_FOUND},
        403: {"msg": "Access Denied, You are not authorized to access", "code": status.HTTP_403_FORBIDDEN},
        808: {"msg": "Abnormal Activity Detected, do not try again", "code": status.HTTP_403_FORBIDDEN},
    }
    return Response({"Message": log[code]["msg"]}, log[code]["code"])
