import re
import string
from random import choices

from django.db.models import F

from .models import Cart, GameCache, Question, Game, Course


def bad_request_message():
    return {"Message": "Sorry, input data is not valid"}


def random_token(size):
    alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(choices(alphabet, k=size))


def check_mobile_number(number):
    regex = r'(^(09|9)[1]\d{8}$)|(^(09|9)[9][0-4|9]\d{7}$)|(^(09|9)[3]\d{8}$)|(^(09|9)[0][1-5]\d{7}$)|(^(09|9)[2][' \
            r'0-2]\d{7}$) '
    return re.search(regex, number)


def get_game(game_id):
    if not isinstance(game_id, int):
        return None
    game = Game.objects.filter(pk=game_id)
    if game:
        return game[0]
    return None


def get_course(course_id):
    if not isinstance(course_id, int):
        return None
    course = Course.objects.filter(pk=course_id)
    if course:
        return course[0]
    return None


def create_user_carts(user, questions):
    for i in questions:
        user_card = Cart.objects.filter(user=user, question=i)
        if not user_card:
            Cart.objects.create(user=user, question=i, course=i.course)


def get_game_code(game_id):
    gc = GameCache.objects.filter(game__id=game_id)
    return gc[0].code if gc else 0


def calculate_score(answer):
    score = 0
    for i in answer:
        if i == '1':
            score += 3
        elif i == 'x':
            score -= 1
    return score


# type defines id carts are selected for Daily (TYPE IS FALSE) Games or Duel Games (TYPE IS TRUE)
def select_carts_for_user(user, course, tp):
    chance = 45 if tp else 27
    # First we fetch carts with view chance more than 45
    user_carts = Cart.objects.filter(course=course, user=user, view_chance__gte=chance).order_by(
        '-view_chance', '?')[:5]
    used_carts_count = 0
    comp_carts_ids = []
    questions = []  # Questions which are selected for game (not the carts)
    sc_ids = []  # Selected Question IDS, needed when we want to increase not selected cart's view chance
    while user_carts and len(questions) < 5:
        i = user_carts.pop()
        if i.question.comprehensive:
            comprehensive_questions = Question.objects.filter(comprehensive=i.question.comprehensive)
            if len(comprehensive_questions) + len(questions) <= 5:
                for j in comprehensive_questions:
                    questions.append(j)
                    crd = Cart.objects.get(question=j)
                    sc_ids.append(crd.id)
                    used_carts_count += 1
            else:
                comp_carts_ids.append(i.id)
                new_cart = Cart.objects.filter(course=course, user=user, view_chance__gte=chance).exclude(
                    id__in=comp_carts_ids).order_by('-view_chance', '?')[:1]
                if new_cart:
                    user_carts.append(new_cart[0])
        else:
            questions.append(i.question)
            sc_ids.append(i.id)
            used_carts_count += 1

    new_questions_count = 0
    # Now we check if there were not enough carts with that chance
    missing_carts = 5 - used_carts_count
    if missing_carts > 0:
        user_course_carts = Cart.objects.filter(course=course, user=user)
        uq_ids = []  # A list of all user's questions (which have cart for them)
        for i in user_course_carts:
            uq_ids.append(i.question.id)
        # Now we get (5 - count of already selected questions) new questions which user has not played yet
        more_questions = Question.objects.filter(course=course).exclude(id__in=uq_ids).order_by('id')[:missing_carts]
        while more_questions and len(questions) < 5:
            i = more_questions.pop()
            if i.comprehensive:
                comprehensive_questions = Question.objects.filter(comprehensive=i.comprehensive)
                if len(comprehensive_questions) + len(questions) <= 5:
                    for j in comprehensive_questions:
                        questions.append(j)
                        crd = Cart.objects.create(user=user, course=course, question=j)
                        sc_ids.append(crd.id)
                        new_questions_count += 1
                else:
                    uq_ids.append(i.id)
                    new_question = Question.objects.filter(course=course).exclude(id__in=uq_ids).order_by('id')[:1]
                    if new_question:
                        more_questions.append(new_question)
            else:
                crd = Cart.objects.create(user=user, question=i, course=course)
                questions.append(i)
                sc_ids.append(crd.id)
                new_questions_count += 1

        missing_carts -= new_questions_count
        if missing_carts > 0:
            # there is no question left so we need to reload some old carts
            more_carts = Cart.objects.filter(course=course, user=user, question__comprehensive__isnull=True).exclude(
                id__in=sc_ids).order_by('-view_chance', '?')[:missing_carts]
            for i in more_carts:
                questions.append(i.question_ref)
                sc_ids.append(i.id)

    # Now we should increase the view_chance of unselected carts
    Cart.objects.filter(course=course, user=user).exclude(id__in=sc_ids).update(view_chance=F('view_chance') + 3)

    return questions
