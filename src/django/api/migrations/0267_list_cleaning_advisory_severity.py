from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0266_list_cleaning_review_window'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listcleaningsuggestion',
            name='severity',
            field=models.CharField(
                blank=True,
                choices=[('must_fix', 'must_fix'),
                         ('advisory', 'advisory'),
                         ('internal_note', 'internal_note')],
                default='', max_length=20,
                help_text='Issues only. must_fix blocks approval, advisory '
                          'is shown as worth a look, internal_note is '
                          'never shown to the contributor.'),
        ),
    ]
