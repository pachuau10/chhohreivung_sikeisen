from django.db import migrations, models


def copy_avatar_to_avatar_url(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    for profile in Profile.objects.exclude(avatar=''):
        profile.avatar_url = profile.avatar
        profile.avatar = ''
        profile.save(update_fields=['avatar_url', 'avatar'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar_url',
            field=models.URLField(blank=True),
        ),
        migrations.RunPython(copy_avatar_to_avatar_url, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='avatars/'),
        ),
    ]
