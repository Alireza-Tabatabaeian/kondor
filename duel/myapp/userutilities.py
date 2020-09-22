from random import randint
from django.contrib.auth.models import User
from .utilities import check_mobile_number, random_token, bad_request_message
from .models import UserProfile, VerifyCode
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from time import time
import concurrent.futures


def setup_user(number="", name=""):
    start = time()
    if number != "":
        if not check_mobile_number(number):
            return mobile_error_message(), status.HTTP_400_BAD_REQUEST

    user = create_new_user(name)
    if user is None:
        return None, bad_request_message(), status.HTTP_400_BAD_REQUEST

    with concurrent.futures.ThreadPoolExecutor() as executor:
        t = executor.submit(set_user_password, user)
        t2 = executor.submit(buildup_user_profile, user, number)

    token = RefreshToken.for_user(user)
    t2.result()
    json = user_json_output_format(user.username, token, t.result()["hsh1"], t.result()["hsh2"], t.result()["opp"])
    end = time()
    print(end - start)
    return user, json, status.HTTP_201_CREATED


def set_user_password(user):
    hsh1 = randint(100, 999)
    hsh2 = randint(100, 999)
    opp = randint(1, 2)
    some_code = hsh1 + hsh2 if opp == 1 else hsh1 * hsh2
    user.set_password(user.username + some_code.__str__())
    user.save()
    return {'hsh1': hsh1, 'hsh2': hsh2, 'opp': opp}


def buildup_user_profile(user, mobile=None):
    do_while = True
    invitation = ""
    while do_while:
        invitation = random_token(8)
        p = UserProfile.objects.filter(invite=invitation)
        if not p:
            do_while = False

    UserProfile.objects.create(user=user, invite=invitation, mobile=mobile)


def check_username_availability(username):  # username can be used for new user
    return False if User.objects.filter(username=username) else True


def user_available_message():
    return {"Message": "User already available!!!"}


def username_available_message():
    return {"Message": "Username is ok;)"}


def create_new_user(name=""):
    if name != "":
        if check_username_availability(name):
            return User.objects.create(username=name)
        else:
            return None
    do_while = True
    username = ""
    while do_while:
        username = "gu_" + random_token(8)
        u = User.objects.filter(username=username)
        if not u:
            do_while = False

    return User.objects.create(username=username)


def create_verify_code_for_user(mobile):
    # check to see if user already has a verify code
    code = VerifyCode.objects.filter(mobile=mobile)
    if code:
        return code[0].code
    # if not
    code = randint(1000, 9999)
    VerifyCode.objects.create(mobile=mobile, code=code)
    return code


def verification_error():
    return {"Message": "Code is Wrong!!!"}


def get_profile_by_mobile(mobile):
    check = check_mobile_number(mobile)
    if not check:
        return mobile_error_message(), status.HTTP_400_BAD_REQUEST
    profile = UserProfile.objects.filter(mobile=mobile)
    if profile:
        return profile[0], status.HTTP_200_OK
    return user_error_message(), status.HTTP_404_NOT_FOUND


def get_inviter(invitation):
    try:
        user = UserProfile.objects.get(invite=invitation).user
        print(user)
        return user
    except User.DoesNotExist:
        return None


def remove_user_verification_code(mobile):
    code = VerifyCode.objects.filter(mobile=mobile)
    if code:
        code.delete()


def user_json_output_format(username, token, hsh1, hsh2, opp):
    return {
        "username": username,
        "metadata": {
            "hash1": hsh1,
            "hash2": hsh2,
            "opp": opp
        },
        "token": {
            "refresh": str(token),
            "access": str(token.access_token),
        },
    }


def avoid_mobile_duplication(mob):
    if mob != "" and not check_mobile_number(mob):
        return mobile_error_message(), status.HTTP_400_BAD_REQUEST
    profile, sts = get_profile_by_mobile(mob)
    if sts == status.HTTP_200_OK:
        return mobile_exist_message(), status.HTTP_403_FORBIDDEN
    return {""}, status.HTTP_200_OK


def mobile_error_message():
    return {"Message": "Wrong Mobile Number"}


def mobile_exist_message():
    return {"Message": "Mobile Number Already exist, Try to login"}


def user_error_message():
    return {"Message": "User not Found"}
