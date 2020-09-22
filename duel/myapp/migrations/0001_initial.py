# Generated by Django 3.0.7 on 2020-09-13 09:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(0, 'Beginner'), (1, 'B1'), (2, 'B2'), (3, 'B3'), (4, 'B4'), (5, 'B5'), (6, 'B6'), (7, 'B7'), (8, 'B8'), (9, 'B9'), (10, 'Intermediate'), (11, 'I1'), (12, 'I2'), (13, 'I3'), (14, 'I4'), (15, 'I5'), (16, 'I6'), (17, 'I7'), (18, 'I8'), (19, 'I9'), (20, 'Winners'), (21, 'W1'), (22, 'W2'), (23, 'W3'), (24, 'W4'), (25, 'W5'), (26, 'W6'), (27, 'W7'), (28, 'W8'), (29, 'W9'), (30, 'Bronze'), (31, 'Br1'), (32, 'Br2'), (33, 'Br3'), (34, 'Br4'), (35, 'Br5'), (36, 'Br6'), (37, 'Br7'), (38, 'Br8'), (39, 'Br9'), (40, 'Silver'), (41, 'S1'), (42, 'S2'), (43, 'S3'), (44, 'S4'), (45, 'S5'), (46, 'S6'), (47, 'S7'), (48, 'S8'), (49, 'S9'), (50, 'Gold'), (51, 'G1'), (52, 'G2'), (53, 'G3'), (54, 'G4'), (55, 'G5'), (56, 'G6'), (57, 'G7'), (58, 'G8'), (59, 'G9'), (60, 'Diamond'), (61, 'D1'), (62, 'D2'), (63, 'D3'), (64, 'D4'), (65, 'D5'), (66, 'D6'), (67, 'D7'), (68, 'D8'), (69, 'D9'), (70, 'Untouchables'), (71, 'U1'), (72, 'U2'), (73, 'U3'), (74, 'U4'), (75, 'U5'), (76, 'U6'), (77, 'U7'), (78, 'U8'), (79, 'U9')], default=0)),
                ('league', models.IntegerField(choices=[(1, 'Math'), (2, 'Science'), (3, 'Literature'), (4, 'Art'), (5, 'Language')], default=1)),
                ('status', models.IntegerField(choices=[(0, 'Started'), (1, 'Hostasq'), (2, 'Sit0'), (3, 'Waitingg'), (4, 'Waitinga'), (5, 'Response1'), (6, 'Sit1'), (7, 'Selectq'), (8, 'Response2'), (9, 'Sit2'), (10, 'End')], default=0)),
                ('end_time', models.DateTimeField(verbose_name='END TIME')),
                ('password', models.IntegerField(null=True)),
                ('pattern', models.CharField(max_length=50)),
                ('round', models.PositiveSmallIntegerField(default=1, verbose_name='Round')),
                ('hg_score', models.FloatField(default=0, verbose_name='Host Score')),
                ('gg_score', models.FloatField(default=0, verbose_name='Guest Score')),
                ('hs_score', models.FloatField(default=0, verbose_name='Host Score')),
                ('gs_score', models.FloatField(default=0, verbose_name='Guest Score')),
                ('correspond', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='correspond', to=settings.AUTH_USER_MODEL, verbose_name='Correspond')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='question.Course', verbose_name='Current Course')),
                ('guest_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='quest', to=settings.AUTH_USER_MODEL, verbose_name='Gst')),
                ('host_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='host', to=settings.AUTH_USER_MODEL, verbose_name='Host')),
                ('q1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q1', to='question.Question', verbose_name='Q1')),
                ('q2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q2', to='question.Question', verbose_name='Q2')),
                ('q3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q3', to='question.Question', verbose_name='Q3')),
                ('q4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q4', to='question.Question', verbose_name='Q4')),
                ('q5', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q5', to='question.Question', verbose_name='Q5')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='winner', to=settings.AUTH_USER_MODEL, verbose_name='Winner')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coins', models.IntegerField(default=1000, verbose_name='Coins')),
                ('general_score', models.IntegerField(blank=True, default=0, verbose_name='General Score')),
                ('mobile', models.CharField(max_length=14, null=True, verbose_name='Mobile')),
                ('last_access', models.DateTimeField(auto_now=True, verbose_name='Last Access')),
                ('user', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserLeague',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.IntegerField(choices=[(1, 'Math'), (2, 'Science'), (3, 'Literature'), (4, 'Art'), (5, 'Language')], default=1)),
                ('games_count', models.IntegerField(blank=True, default=0, verbose_name='Game Count')),
                ('win_count', models.IntegerField(blank=True, default=0, verbose_name='Win Count')),
                ('score', models.IntegerField(blank=True, default=0, verbose_name='Score')),
                ('level', models.IntegerField(choices=[(0, 'Beginner'), (1, 'B1'), (2, 'B2'), (3, 'B3'), (4, 'B4'), (5, 'B5'), (6, 'B6'), (7, 'B7'), (8, 'B8'), (9, 'B9'), (10, 'Intermediate'), (11, 'I1'), (12, 'I2'), (13, 'I3'), (14, 'I4'), (15, 'I5'), (16, 'I6'), (17, 'I7'), (18, 'I8'), (19, 'I9'), (20, 'Winners'), (21, 'W1'), (22, 'W2'), (23, 'W3'), (24, 'W4'), (25, 'W5'), (26, 'W6'), (27, 'W7'), (28, 'W8'), (29, 'W9'), (30, 'Bronze'), (31, 'Br1'), (32, 'Br2'), (33, 'Br3'), (34, 'Br4'), (35, 'Br5'), (36, 'Br6'), (37, 'Br7'), (38, 'Br8'), (39, 'Br9'), (40, 'Silver'), (41, 'S1'), (42, 'S2'), (43, 'S3'), (44, 'S4'), (45, 'S5'), (46, 'S6'), (47, 'S7'), (48, 'S8'), (49, 'S9'), (50, 'Gold'), (51, 'G1'), (52, 'G2'), (53, 'G3'), (54, 'G4'), (55, 'G5'), (56, 'G6'), (57, 'G7'), (58, 'G8'), (59, 'G9'), (60, 'Diamond'), (61, 'D1'), (62, 'D2'), (63, 'D3'), (64, 'D4'), (65, 'D5'), (66, 'D6'), (67, 'D7'), (68, 'D8'), (69, 'D9'), (70, 'Untouchables'), (71, 'U1'), (72, 'U2'), (73, 'U3'), (74, 'U4'), (75, 'U5'), (76, 'U6'), (77, 'U7'), (78, 'U8'), (79, 'U9')], default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='UserCourseProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(blank=True, default=0, verbose_name='Score')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='question.Course', verbose_name='Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='GameRound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveSmallIntegerField(default=1, verbose_name='Round')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='question.Course', verbose_name='Current Course')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Game')),
                ('q1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rq1', to='question.Question', verbose_name='Q1')),
                ('q2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rq2', to='question.Question', verbose_name='Q2')),
                ('q3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rq3', to='question.Question', verbose_name='Q3')),
                ('q4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rq4', to='question.Question', verbose_name='Q4')),
                ('q5', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rq5', to='question.Question', verbose_name='Q5')),
            ],
        ),
        migrations.CreateModel(
            name='GameCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(choices=[(1, 'Waitingg'), (2, 'Waitingag'), (3, 'Waitingcg'), (4, 'Waitingah'), (5, 'Waitingch')], default=1)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='myapp.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend', to=settings.AUTH_USER_MODEL)),
                ('inviter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inviter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.IntegerField()),
                ('q1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q01', to='question.Question', verbose_name='Q1')),
                ('q10', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q10', to='question.Question', verbose_name='Q10')),
                ('q2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q02', to='question.Question', verbose_name='Q2')),
                ('q3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q03', to='question.Question', verbose_name='Q3')),
                ('q4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q04', to='question.Question', verbose_name='Q4')),
                ('q5', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q05', to='question.Question', verbose_name='Q5')),
                ('q6', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q06', to='question.Question', verbose_name='Q6')),
                ('q7', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q07', to='question.Question', verbose_name='Q7')),
                ('q8', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q08', to='question.Question', verbose_name='Q8')),
                ('q9', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='q09', to='question.Question', verbose_name='Q9')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
