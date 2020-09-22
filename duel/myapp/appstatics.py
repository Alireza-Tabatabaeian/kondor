from django.db import models


class Level(models.IntegerChoices):
    BEGINNER = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5 = 5
    B6 = 6
    B7 = 7
    B8 = 8
    B9 = 9
    INTERMEDIATE = 10
    I1 = 11
    I2 = 12
    I3 = 13
    I4 = 14
    I5 = 15
    I6 = 16
    I7 = 17
    I8 = 18
    I9 = 19
    WINNERS = 20
    W1 = 21
    W2 = 22
    W3 = 23
    W4 = 24
    W5 = 25
    W6 = 26
    W7 = 27
    W8 = 28
    W9 = 29
    BRONZE = 30
    BR1 = 31
    BR2 = 32
    BR3 = 33
    BR4 = 34
    BR5 = 35
    BR6 = 36
    BR7 = 37
    BR8 = 38
    BR9 = 39
    SILVER = 40
    S1 = 41
    S2 = 42
    S3 = 43
    S4 = 44
    S5 = 45
    S6 = 46
    S7 = 47
    S8 = 48
    S9 = 49
    GOLD = 50
    G1 = 51
    G2 = 52
    G3 = 53
    G4 = 54
    G5 = 55
    G6 = 56
    G7 = 57
    G8 = 58
    G9 = 59
    DIAMOND = 60
    D1 = 61
    D2 = 62
    D3 = 63
    D4 = 64
    D5 = 65
    D6 = 66
    D7 = 67
    D8 = 68
    D9 = 69
    UNTOUCHABLES = 70  # Limit 100 000
    U1 = 71
    U2 = 72
    U3 = 73
    U4 = 74
    U5 = 75
    U6 = 76
    U7 = 77
    U8 = 78
    U9 = 79


class CallbackEndpoints(models.IntegerChoices):
    CourseRequest = 1
    CourseSelect = 2
    SendAnswer = 3
    Update = 4
    Sit = 5


class GameState(models.IntegerChoices):
    STARTED = 0
    HOSTASQ = 1
    SIT0 = 2
    WAITINGG = 3
    WAITINGA = 4
    RESPONSE1 = 5
    SIT1 = 6
    SELECTQ = 7
    RESPONSE2 = 8
    SIT2 = 9
    END = 10


class GameCacheStatus(models.IntegerChoices):
    WaitingG = 1
    WaitingAG = 2
    WaitingCG = 3
    WaitingAH = 4
    WaitingCH = 5
