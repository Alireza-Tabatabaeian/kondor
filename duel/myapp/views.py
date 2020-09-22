import datetime
from random import randint
from time import time

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework.views import APIView

from card.models import Cart
from question.models import Question, Course
from question.serializers import QuestionSerializer, CourseSerializer
from question.questionStatics import League, CourseModel
from rest_framework_simplejwt.tokens import RefreshToken

from .appstatics import CallbackEndpoints, GameState, GameCacheStatus
from .check_access import check_daily_answer, response_error
from .gameutilities import needed_coins, league_available, user_join_a_game, join_user_as_guest, buildup_game
from .ghasedaksms import send_verification
from .models import UserProfile, Game, GameCache, DailyGame, GameRound, UserLeague, \
    UserCourseProgress, VerifyCode, InviteRelation
from .serializers import DailyGameSerializer, GameRoundSerializer
from .utilities import create_user_carts, get_game_code, select_carts_for_user, bad_request_message
from .userutilities import set_user_password, check_mobile_number, get_profile_by_mobile, create_verify_code_for_user, \
    user_json_output_format, verification_error, remove_user_verification_code, check_username_availability, \
    user_available_message, username_available_message, setup_user, get_inviter, avoid_mobile_duplication, valid_user
from .check_access import game_validate


# class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsOwnerProfileOrReadOnly, permissions.IsAuthenticated]


class UserLogin(APIView):
    def post(self, request):
        mob = request.data['mobile']
        profile, sts = get_profile_by_mobile(mob)
        if sts == status.HTTP_200_OK:
            code = create_verify_code_for_user(profile.mobile)
            send_verification(mob, "signup", code)
            return Response({"Message": "SMS was sent"}, status.HTTP_200_OK)
        else:
            return Response(profile, sts)


class UserLoginVerify(APIView):
    def post(self, request):
        mob = request.data['mobile']
        code = int(request.data['code'])
        if code == 0:
            return Response(bad_request_message(), status.HTTP_400_BAD_REQUEST)
        profile, sts = get_profile_by_mobile(mob)
        if sts != status.HTTP_200_OK:
            return Response(profile, sts)
        verify = VerifyCode.objects.filter(mobile=profile.mobile)
        if not verify:
            return Response(bad_request_message(), status.HTTP_400_BAD_REQUEST)
        if verify[0].code != code:
            return Response(verification_error(), status.HTTP_406_NOT_ACCEPTABLE)
        user = profile.user
        hsh1, hsh2, opp = set_user_password(user)
        token = RefreshToken.for_user(user)
        json = user_json_output_format(user.username, token, hsh1, hsh2, opp)
        remove_user_verification_code(mob)
        return Response(json, sts)


class UsernameAvailability(APIView):
    def get(self, request, username):
        if check_username_availability(username):
            return Response(username_available_message(), status.HTTP_200_OK)
        return Response(user_available_message(), status.HTTP_406_NOT_ACCEPTABLE)


class FastUserSignup(APIView):
    def post(self, request):
        user, json, sts = setup_user(name=request.data['username'])
        return Response(json, status.HTTP_201_CREATED)


class UserSignUpFinal(APIView):
    def post(self, request):
        code = int(request.data['code'])
        mob = request.data['mobile']
        if code == 0:
            return Response(bad_request_message(), status.HTTP_400_BAD_REQUEST)
        msg, sts = avoid_mobile_duplication(mob)
        if sts != status.HTTP_200_OK:
            return Response(msg, sts)
        verify = VerifyCode.objects.filter(mobile=mob)
        if not verify:
            return Response(bad_request_message(), status.HTTP_400_BAD_REQUEST)
        if verify[0].code != code:
            return Response(verification_error(), status.HTTP_406_NOT_ACCEPTABLE)
        user, json, sts = setup_user(number=mob, name=request.data['username'])
        if request.data['invitation'] != "":
            inviter = get_inviter(request.data['invitation'])
            if inviter:
                InviteRelation.objects.create(inviter=inviter, friend=user)
        return Response(json, status.HTTP_200_OK)


class UserSignUpRequest(APIView):
    def post(self, request):
        mob = request.data['mobile']
        msg, sts = avoid_mobile_duplication(mob)
        if sts != status.HTTP_200_OK:
            return Response(msg, sts)
        code = create_verify_code_for_user(mob)
        start = time()
        send_verification(mob, "signup", code)
        end = time()
        print(end - start)
        return Response({"Message": "SMS was sent"}, status.HTTP_200_OK)


class GameRequest(APIView):
    def post(self, request):
        user = request.user
        profile, sts = valid_user(user)
        if sts != status.HTTP_200_OK:
            return Response(profile, sts)
        if profile.coins < needed_coins(request.data['challengeType']):
            return Response({"Message": "Not Enough Coins"}, status.HTTP_406_NOT_ACCEPTABLE)
        league = request.data['league']
        if not league_available(league):
            return Response({"Message": "League not available"}, status.HTTP_400_BAD_REQUEST)
        game, sts = user_join_a_game(user, profile, league, type)
        if sts == status.HTTP_200_OK:
            data = join_user_as_guest(game, user, profile)
        else:
            data = buildup_game(league, game, user, profile)
        return Response(data, status.HTTP_201_CREATED)


@api_view(['GET'])
def update_game(request, *args, **kwargs):
    if request.method == 'GET':
        user = request.user
        if kwargs.get("game_id", None) is not None:
            game_id = kwargs["game_id"]
        else:
            return Response({"Message": "Bad Request"}, status.HTTP_404_NOT_FOUND)

        code = get_game_code(game_id)
        if kwargs.get("code", None) is not None:
            if code.value == kwargs['code']:
                return Response({"Message": "Game is UpToDate"}, status.HTTP_200_OK)

        game, sts = game_validate(game_id, user, CallbackEndpoints.Update)
        if game is None:
            if sts == 404:
                return Response({"Message": "Game not found!!!"}, status.HTTP_404_NOT_FOUND)
            else:
                return Response({"Message": "Access Denied!!!"}, status.HTTP_403_FORBIDDEN)

        if kwargs.get("code", None) is None:  # silly user has no code
            rounds = GameRound.objects.filter(game=game).order_by('round')
            r_data = GameRoundSerializer(data=rounds, many=True) if rounds else '{}'
            return Response({"Game": game, "round": r_data, "code": code}, status.HTTP_205_RESET_CONTENT)

        user_code = kwargs.get("code")
        if user_code == GameCacheStatus.WaitingG:
            guest_profile = UserProfile.objects.get(user=game.guest_user)

            if game.league == League.MATH:
                score = "math_score"
            elif game.league == League.SCIENCE:
                score = "science_score"
            elif game.league == League.LITERATURE:
                score = "literature_score"
            elif game.league == League.ART:
                score = "art_score"
            else:
                score = "language_score"

            if code == GameCacheStatus.WaitingAG:
                return Response({
                    "opponent": {
                        "id": game.guest_user.id,
                        "name": game.guest_user.first_name,
                        "general_score": guest_profile.general_score,
                        "league_score": getattr(guest_profile, score)
                    },
                    "game": {
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    }
                }, status.HTTP_200_OK)
            elif code == GameCacheStatus.WaitingCG:
                return Response({
                    "opponent": {
                        "id": game.guest_user.id,
                        "name": game.guest_user.first_name,
                        "general_score": guest_profile.general_score,
                        "league_score": getattr(guest_profile, score)
                    },
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    }
                }, status.HTTP_200_OK)
            elif code == GameCacheStatus.WaitingAH:
                return Response({
                    "opponent": {
                        "id": game.guest_user.id,
                        "name": game.guest_user.first_name,
                        "general_score": guest_profile.general_score,
                        "league_score": getattr(guest_profile, score)
                    },
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    },
                    "course": {
                        "id": game.course.id
                    }
                }, status.HTTP_200_OK)
        elif user_code == GameCacheStatus.WaitingAG:
            if code == GameCacheStatus.WaitingCG:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    }
                }, status.HTTP_200_OK)
            elif code == GameCacheStatus.WaitingAH:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    },
                    "course": {
                        "id": game.course.id
                    }
                }, status.HTTP_200_OK)
        elif user_code == GameCacheStatus.WaitingCG:
            if code == GameCacheStatus.WaitingAH:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    },
                    "course": {
                        "id": game.course.id
                    }
                }, status.HTTP_200_OK)
        elif user_code == GameCacheStatus.WaitingAH:
            if code == GameCacheStatus.WaitingCG:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    }
                }, status.HTTP_200_OK)
            elif code == GameCacheStatus.WaitingAG:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    },
                    "course": {
                        "id": game.course.id
                    }
                }, status.HTTP_200_OK)
        elif user_code == GameCacheStatus.WaitingCH:
            if code == GameCacheStatus.WaitingAG:
                return Response({
                    "game": {
                        "pattern": game.pattern,
                        "status": game.status.value,
                        "correspond": game.correspond,
                        "end_time": game.end_time
                    },
                    "course": {
                        "id": game.course.id
                    }
                }, status.HTTP_200_OK)

        rounds = GameRound.objects.filter(game=game).order_by('round')
        r_data = GameRoundSerializer(data=rounds, many=True) if rounds else '{}'
        return Response({"Game": game, "round": r_data, "code": code}, status.HTTP_205_RESET_CONTENT)


@api_view(['GET'])
def time_is_up(request, *args, **kwargs):
    if request.method == 'GET':
        user = request.user
        if kwargs.get("game_id", None) is not None:
            game_id = kwargs["game_id"]
        else:
            return Response({"Message": "Bad Request"}, status.HTTP_404_NOT_FOUND)

        game, sts = game_validate(game_id, user, CallbackEndpoints.Update)
        if game is None:
            if sts == 404:
                return Response({"Message": "Game not found!!!"}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Message": "Access Denied!!!"}, status.HTTP_403_FORBIDDEN)

        if game.end_time < datetime.datetime.now(datetime.timezone.utc):
            game.finish_it(True)
            game.save()
            h_profile = UserProfile.objects.get(user=game.host_user)
            if game.guest_user:
                h_profile.finish_it(game, True)
                h_profile.save()
                g_profile = UserProfile.objects.get(user=game.guest_user)
                g_profile.finish_it(game, False)
                g_profile.save()
            else:
                if game.status == GameState.WAITINGG:
                    h_profile.coins += 500
                    h_profile.save()
            gc = GameCache.objects.get(game__id=game_id)
            gc.code = GameCacheStatus.Finished


@api_view(['GET', 'POST'])
def course_selection(request, *args, **kwargs):
    user = request.user
    if request.method == 'GET':
        if kwargs.get("game_id", None) is not None:
            game_id = kwargs["game_id"]
        else:
            return Response({"Message": "Game ID needed"}, status.HTTP_400_BAD_REQUEST)
        game, sts = game_validate(game_id, user, CallbackEndpoints.CourseRequest)
        if game is None:
            return Response({"Message": "Game not found or access is restricted"}, status.HTTP_400_BAD_REQUEST)
        if game.round == 1:
            courses = Course.objects.filter(course_model=CourseModel.GENERAL)
            cs = CourseSerializer(data=courses, many=True)
            cs.is_valid()
            return Response({"Courses : ": cs.data, "Game : ": game.id}, status.HTTP_200_OK)
        elif game.round == 2:
            courses = Course.objects.filter(course_model=CourseModel.GENERAL).exclude(id=game.course.id)
            cs = CourseSerializer(data=courses, many=True)
            cs.is_valid()
            return Response({"Courses : ": cs.data, "Game : ": game.id}, status.HTTP_200_OK)
        elif game.round == 3:
            courses = Course.objects.filter(course_model=CourseModel.SPECIALIZED, league=game.league)
            cs = CourseSerializer(data=courses, many=True)
            cs.is_valid()
            return Response({"Courses : ": cs.data, "Game : ": game.id}, status.HTTP_200_OK)
        else:
            if game.league == 5:
                courses = Course.objects.filter(course_model=CourseModel.SPECIALIZED, league=game.league)
                cs = CourseSerializer(data=courses, many=True)
                cs.is_valid()
                return Response({"Courses : ": cs.data, "Game : ": game.id}, status.HTTP_200_OK)
            else:
                courses = Course.objects.filter(course_model=CourseModel.SPECIALIZED,
                                                league=game.league).exclude(id=game.course.id)
                cs = CourseSerializer(data=courses, many=True)
                cs.is_valid()
                return Response({"Courses : ": cs.data, "Game : ": game.id}, status.HTTP_200_OK)
    else:
        course_id = request.data['course']
        game_id = request.data['game']
        game, sts = game_validate(game_id, user, CallbackEndpoints.CourseSelect, course=course_id)
        if game is None:
            return Response({"Message": "Game not Found or Course not Found or Access denied"},
                            status.HTTP_400_BAD_REQUEST)
        course = Course.objects.get(pk=course_id)

        questions = select_carts_for_user(user, course, True)
        rnd = GameRound()
        rnd.round = game.round
        game.course = course
        rnd.course = course
        game.password = randint(1000, 9999)
        game.q1 = questions[0]
        rnd.q1 = questions[0]
        game.q2 = questions[1]
        rnd.q2 = questions[1]
        game.q3 = questions[2]
        rnd.q3 = questions[2]
        game.q4 = questions[3]
        rnd.q4 = questions[3]
        game.q5 = questions[4]
        rnd.q5 = questions[4]
        rnd.save()
        game.status = GameState.RESPONSE2 if game.status == GameState.SELECTQ else GameState.HOSTASQ
        game.round = game.round + 1 if game.status == GameState.SELECTQ else game.round
        game.save()
        gc = GameCache.objects.get(game=game)
        if gc.code != GameCacheStatus.WaitingG:
            gc.code = GameCacheStatus.WaitingAH if game.host_user == user else GameCacheStatus.WaitingAG
            gc.save()
        return Response({
            "questions": [game.q1.id, game.q2.id, game.q3.id, game.q4.id, game.q5.id],
            "course": game.course,
            "password": game.password,
            "code": gc.code},
            status.HTTP_201_CREATED)


@api_view(['POST'])
def sit_in_test(request):
    user = request.user
    game_id = request.data['Game_id']
    game, sts = game_validate(game_id, user, CallbackEndpoints.Sit)
    if Game is None:
        return Response({"Message": "Access Denied or Game Not Found"}, status.HTTP_400_BAD_REQUEST)
    questions = [game.q1, game.q2, game.q3, game.q4, game.q5]
    questions_ids = [game.q1.id, game.q2.id, game.q3.id, game.q4.id, game.q5.id]
    create_user_carts(user, questions)
    game.password = randint(1000, 9999)
    game.status = GameState.RESPONSE1
    game.save()
    return Response({
        "questions": questions_ids,
        "password": game.password
    })


@api_view(['POST'])
def send_answers(request):
    user = request.user
    game_id = request.data['game']
    answer = request.data['answer']
    verify = request.data['verify']
    course = request.data['course']
    game, sts = game_validate(game_id, user, CallbackEndpoints.SendAnswer, answer=answer, verify=verify)
    if game is None:
        return Response({"Message": "Bad Request"}, status.HTTP_400_BAD_REQUEST)

    user_course_progress = UserCourseProgress.objects.filter(user=user, course=course)
    if not user_course_progress:
        user_course_progress = UserCourseProgress.objects.create(user=user, course=course)
    else:
        user_course_progress = user_course_progress[0]
    host = user == game.host_user
    round_score = 0
    progress_score = 0
    questions = [game.q1, game.q2, game.q3, game.q4, game.q5]
    i = 0
    for ans in answer:
        crd = Cart.objects.get(user_ref=user, question_ref=questions[i])
        if ans == '1':
            round_score += 3
            crd.levelUp()
            progress_score += 1
        else:
            if ans == 'x':
                round_score -= 1
            progress_score -= (crd.box - 1)
            crd.reset()
        crd.save()
        user_course_progress.score += progress_score
        user_course_progress.save()
        i += 1

    game.pattern += answer + ','
    if game.correspond == game.host_user:
        if game.round < 3:
            game.hg_score += round_score
        else:
            game.hs_score += round_score
    else:
        if game.round < 3:
            game.gg_score += round_score
        else:
            game.gs_score += round_score
    if game.status == GameState.HOSTASQ:
        game.status = GameState.WAITINGG

    elif game.status == GameState.RESPONSE1:
        if game.round < 4:
            game.status = GameState.SELECTQ
            game.round += 1
        else:
            game.pattern = game.pattern[:-1]
            game.finish_it(False)
            h_profile = UserProfile.objects.get(user=game.host_user)
            g_profile = UserProfile.objects.get(user=game.guest_user)
            h_profile.finish_it(game, True)
            g_profile.finish_it(game, False)
            h_profile.save()
            g_profile.save()

    else:
        game.status = GameState.WAITINGA
        game.correspond = game.host_user if game.correspond == game.guest_user else game.guest_user
        game.end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)

    game.save()
    gc = GameCache.objects.get(game=game)
    if gc.code != GameCacheStatus.WaitingG:
        if host:
            gc = GameCacheStatus.WaitingCH if game.status == GameState.RESPONSE1 else GameCacheStatus.WaitingAG
        else:
            gc = GameCacheStatus.WaitingCG if game.status == GameState.RESPONSE1 else GameCacheStatus.WaitingAH
    if game.status == GameState.RESPONSE1 and game.round == 4:
        gc.code = GameCacheStatus.Finished
        gc.save()

    scores = [game.hg_score + 3 * game.hs_score, game.gg_score + 3 * game.gs_score]

    return Response(
        {
            "Results": {
                "pattern": game.pattern,
                "my_scores": scores[0] if host else scores[1],
                "co_scores": scores[1] if host else scores[0],
            },
            "code": gc.code
        },
        status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def daily_game_endpoint(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"Message": "You need to login first"}, status.HTTP_403_FORBIDDEN)
    up = UserProfile.objects.get(user=user)
    if request.method == 'GET':
        leagues = {"math_score": League.MATH, "science_score": League.SCIENCE, "literature_score": League.LITERATURE,
                   "art_score": League.ART, "language_score": League.LANGUAGE}
        max_score = 0
        selected_league = League.MATH
        for key in leagues:
            score = getattr(up, key)
            if score > max_score:
                selected_league = leagues[key]
                max_score = score

        general_course = Course.objects.filter(course_model=CourseModel.GENERAL).order_by('?')[0]
        questions = select_carts_for_user(user, general_course, False)
        specialized_course = \
            Course.objects.filter(course_model=CourseModel.SPECIALIZED, league=selected_league).order_by('?')[0]
        questions += select_carts_for_user(user, specialized_course, False)
        password = randint(1111, 9999)
        dg = DailyGame.objects.create(user=user,
                                      q1=questions[0],
                                      q2=questions[1],
                                      q3=questions[2],
                                      q4=questions[3],
                                      q5=questions[4],
                                      q6=questions[5],
                                      q7=questions[6],
                                      q8=questions[7],
                                      q9=questions[8],
                                      q10=questions[9],
                                      password=password
                                      )
        dgs = DailyGameSerializer(dg)
        json = JSONRenderer().render(dgs.data)
        return Response({"Game": json}, status.HTTP_201_CREATED)

    else:
        dg = DailyGame.objects.filter(user=user)
        if dg:
            dg = dg[0]
        else:
            return Response({"Message": "Bad Request"}, status.HTTP_400_BAD_REQUEST)
        answer = request.data.get('answer', None)
        verification = request.data.get('verify', None)

        score = check_daily_answer(user, answer, verification, dg.password)
        q = 0

        questions = [dg.q1, dg.q2, dg.q3, dg.q4, dg.q5, dg.q6, dg.q7, dg.q8, dg.q9, dg.q10]

        for i in answer:
            c = Cart.objects.get(user_ref=user, question_ref=questions[q])
            if i == '1':
                c.levelUp()
            else:
                c.reset()
            c.save()
            q += 1

        if score is None:
            return Response({"Message": "Are you trying to cheat?"}, status.HTTP_406_NOT_ACCEPTABLE)
        up.coins += score
        up.save()
        dg.delete()
        return Response({"coins": score}, status.HTTP_200_OK)


@api_view(['GET'])
def update_user_questions(request, **kwargs):
    last_id = kwargs.get('id', None)
    if not isinstance(last_id, int) or last_id is None:
        return Response({"Message": "Bad Input"}, status.HTTP_400_BAD_REQUEST)
    questions = Question.objects.filter(id__gt=last_id)
    question_serialized = QuestionSerializer(questions, many=True)
    question_serialized_json = JSONRenderer().render(question_serialized.data)
    return Response(question_serialized_json, status.HTTP_200_OK)
