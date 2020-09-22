from django.contrib.auth.models import User
from django.db import models
from card.models import Cart
from question.models import Question, Course
from question.questionStatics import League
from .appstatics import Level, GameState, GameCacheStatus


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", default=1)
    coins = models.IntegerField('Coins', default=1000)
    mobile = models.CharField('Mobile', max_length=14, null=True)
    avatar = models.IntegerField('Avatar', default=1)
    invite = models.CharField('Invitation Code', max_length=11, null=True)
    general_score = models.IntegerField('General Score', default=0, blank=True)
    general_level = models.IntegerField('General Level', default=1, blank=True)

    def __str__(self):
        return self.user.username

    def finish_it(self, game, host):
        if game.winner is not None:
            if game.winner == self.user:
                self.coins += 800
        else:
            self.coins += 400

        g_score = game.hg_score if host else game.gg_score
        self.general_score += g_score

        user_league = UserLeague.objects.get(user=game.user, league=game.league)
        user_league.finish_it(game, host, self.general_score)
        user_league.save()


class UserLeague(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    league = models.IntegerField(choices=League.choices, default=League.MATH)
    games_count = models.IntegerField("Game Count", default=0, blank=True)
    win_count = models.IntegerField("Win Count", default=0, blank=True)
    score = models.IntegerField("Score", default=0, blank=True)
    level = models.IntegerField(choices=Level.choices, default=Level.BEGINNER)

    def level_score(self):
        score = (
            120, 360, 720, 1200, 1800, 2400, 3120, 3960, 4920, 6000,
            6180, 6540, 7080, 7800, 8700, 9600, 10680, 11940, 13380, 15000,
            15240, 15720, 16440, 17400, 18600, 19800, 21240, 22920, 24940, 27000,
            27300, 27900, 28800, 30000, 31500, 33000, 34800, 36900, 39300, 42000,
            42180, 42540, 43080, 43800, 44700, 45600, 46680, 47940, 49380, 51000,
            51120, 51360, 51720, 52200, 52800, 53400, 54120, 54960, 55920, 57000,
            57060, 57180, 57360, 57600, 57900, 58200, 58560, 58980, 59460, 60000,
            60800, 62400, 64800, 68000, 72000, 76000, 80800, 86400, 92800, 100000
        )
        return score[self.level]

    def finish_it(self, game, host, general):
        self.games_count += 1
        if game.winner is not None:
            if game.winner == self.user:
                self.win_count += 1
        s_score = game.hs_score if host else game.gs_score
        self.score += 3 * s_score
        if self.score + general > self.level_score():
            self.level += 1


class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name='Course', on_delete=models.CASCADE)
    score = models.IntegerField('Score', default=0, blank=True)


class GameRound(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    q1 = models.ForeignKey(Question, verbose_name="Q1", on_delete=models.PROTECT, related_name="rq1", null=True)
    q2 = models.ForeignKey(Question, verbose_name="Q2", on_delete=models.PROTECT, related_name="rq2", null=True)
    q3 = models.ForeignKey(Question, verbose_name="Q3", on_delete=models.PROTECT, related_name="rq3", null=True)
    q4 = models.ForeignKey(Question, verbose_name="Q4", on_delete=models.PROTECT, related_name="rq4", null=True)
    q5 = models.ForeignKey(Question, verbose_name="Q5", on_delete=models.PROTECT, related_name="rq5", null=True)

    course = models.ForeignKey(Course, verbose_name="Current Course", on_delete=models.PROTECT, null=True)

    round = models.PositiveSmallIntegerField("Round", default=1)


class Game(models.Model):
    host_user = models.ForeignKey(User, verbose_name="Host", on_delete=models.PROTECT, related_name='host')
    guest_user = models.ForeignKey(User, verbose_name="Gst", on_delete=models.PROTECT, related_name='quest', null=True,
                                   blank=True)

    level = models.IntegerField('Level')
    league = models.IntegerField(choices=League.choices, default=League.MATH)

    status = models.IntegerField(choices=GameState.choices, default=GameState.STARTED)
    end_time = models.DateTimeField("END TIME")
    correspond = models.ForeignKey(User, verbose_name="Correspond", on_delete=models.PROTECT, related_name="correspond")
    course = models.ForeignKey(Course, verbose_name="Current Course", on_delete=models.PROTECT, null=True)
    password = models.IntegerField(null=True)
    round = models.PositiveSmallIntegerField("Round", default=1)

    h_pattern = models.CharField(max_length=25, null=True)
    g_pattern = models.CharField(max_length=25, null=True)

    winner = models.ForeignKey(User, verbose_name="Winner", on_delete=models.PROTECT, related_name='winner', null=True,
                               blank=True)
    q1 = models.ForeignKey(Question, verbose_name="Q1", on_delete=models.PROTECT, related_name="q1", null=True)
    q2 = models.ForeignKey(Question, verbose_name="Q2", on_delete=models.PROTECT, related_name="q2", null=True)
    q3 = models.ForeignKey(Question, verbose_name="Q3", on_delete=models.PROTECT, related_name="q3", null=True)
    q4 = models.ForeignKey(Question, verbose_name="Q4", on_delete=models.PROTECT, related_name="q4", null=True)
    q5 = models.ForeignKey(Question, verbose_name="Q5", on_delete=models.PROTECT, related_name="q5", null=True)

    def __str__(self):
        return "{} : This game is {}".format(self.id, self.get_status_display())

    def finish_it(self, dead):
        self.status = GameState.END
        h_score = self.hg_score + 3 * self.hs_score
        g_score = self.gg_score + 3 * self.gs_score
        if dead:
            self.winner = self.guest_user if self.correspond == self.host_user else self.host_user
        else:
            if h_score > g_score:
                self.winner = self.host_user
            elif h_score < g_score:
                self.winner = self.guest_user

    def league_field_name(self):
        if self.league == League.MATH:
            return "math_score", "math_level"
        elif self.league == League.SCIENCE:
            return "science_score", "science_level"
        elif self.league == League.LITERATURE:
            return "literature_score", "literature_level"
        elif self.league == League.ART:
            return "art_score", "art_level"
        else:
            return "language_score", "language_level"


class GameCache(models.Model):
    game = models.OneToOneField(Game, on_delete=models.PROTECT)
    code = models.IntegerField(choices=GameCacheStatus.choices, default=GameCacheStatus.WaitingG)


class DailyGame(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    q1 = models.ForeignKey(Question, verbose_name="Q1", on_delete=models.PROTECT, related_name="q01", null=True)
    q2 = models.ForeignKey(Question, verbose_name="Q2", on_delete=models.PROTECT, related_name="q02", null=True)
    q3 = models.ForeignKey(Question, verbose_name="Q3", on_delete=models.PROTECT, related_name="q03", null=True)
    q4 = models.ForeignKey(Question, verbose_name="Q4", on_delete=models.PROTECT, related_name="q04", null=True)
    q5 = models.ForeignKey(Question, verbose_name="Q5", on_delete=models.PROTECT, related_name="q05", null=True)
    q6 = models.ForeignKey(Question, verbose_name="Q6", on_delete=models.PROTECT, related_name="q06", null=True)
    q7 = models.ForeignKey(Question, verbose_name="Q7", on_delete=models.PROTECT, related_name="q07", null=True)
    q8 = models.ForeignKey(Question, verbose_name="Q8", on_delete=models.PROTECT, related_name="q08", null=True)
    q9 = models.ForeignKey(Question, verbose_name="Q9", on_delete=models.PROTECT, related_name="q09", null=True)
    q10 = models.ForeignKey(Question, verbose_name="Q10", on_delete=models.PROTECT, related_name="q10", null=True)
    password = models.IntegerField()


class VerifyCode(models.Model):
    mobile = models.CharField('Mobile', max_length=14, default="")
    code = models.IntegerField('Code')
    created = models.DateTimeField('Created', auto_now=True)


class InviteRelation(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="inv")
    friend = models.OneToOneField(User, on_delete=models.CASCADE, related_name="frnd")
