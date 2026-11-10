from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0270_list_cleaning_removed_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='listcleaningrun',
            name='review_until',
            field=models.DateTimeField(
                blank=True, null=True,
                help_text='Deadline for the contributor to submit changes.'),
        ),
        migrations.AddField(
            model_name='listcleaningrun',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listcleaningrun',
            name='closed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listcleaningrun',
            name='closed_reason',
            field=models.CharField(
                blank=True,
                choices=[('submitted', 'Contributor submitted'),
                         ('lapsed', 'Window lapsed, list as uploaded')],
                default='', max_length=20),
        ),
        migrations.CreateModel(
            name='ListCleaningEvent',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('kind', models.CharField(
                    choices=[('opened', 'opened'), ('resumed', 'resumed'),
                             ('left', 'left'), ('submitted', 'submitted'),
                             ('lapsed', 'lapsed')],
                    max_length=20)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='events', to='api.listcleaningrun')),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
