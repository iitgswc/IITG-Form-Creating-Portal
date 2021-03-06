# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-19 23:58
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=200, verbose_name='Label')),
                ('slug', models.SlugField(blank=True, default='', max_length=100, verbose_name='Slug')),
                ('field_type', models.IntegerField(choices=[(1, 'Single line text'), (2, 'Multi line text'), (3, 'Email'), (13, 'Number'), (14, 'URL'), (4, 'Check box'), (5, 'Check boxes'), (6, 'Drop down'), (7, 'Multi select'), (8, 'Radio buttons'), (9, 'File upload'), (10, 'Date'), (11, 'Date/time'), (15, 'Date of birth'), (12, 'Hidden'), (100, 'My cool checkbox')], verbose_name='Type')),
                ('required', models.BooleanField(default=True, verbose_name='Required')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('choices', models.CharField(blank=True, help_text='Comma separated options where applicable. If an option itself contains commas, surround the option starting with the `character and ending with the ` character.', max_length=1000, verbose_name='Choices')),
                ('default', models.CharField(blank=True, max_length=2000, verbose_name='Default value')),
                ('placeholder_text', models.CharField(blank=True, max_length=100, null=True, verbose_name='Placeholder Text')),
                ('help_text', models.CharField(blank=True, max_length=100, verbose_name='Help text')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='Order')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Field',
                'verbose_name_plural': 'Fields',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='FieldEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_id', models.IntegerField()),
                ('value', models.CharField(max_length=2000, null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form field entry',
                'verbose_name_plural': 'Form field entries',
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('slug', models.SlugField(editable=False, max_length=100, unique=True, verbose_name='Slug')),
                ('intro', models.TextField(blank=True, verbose_name='Intro')),
                ('button_text', models.CharField(default='Submit', max_length=50, verbose_name='Button text')),
                ('response', models.TextField(blank=True, verbose_name='Response')),
                ('redirect_url', models.CharField(blank=True, help_text='An alternate URL to redirect to after form submission', max_length=200, null=True, verbose_name='Redirect url')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Published')], default=2, verbose_name='Status')),
                ('publish_date', models.DateTimeField(blank=True, help_text="With published selected, won't be shown until this time", null=True, verbose_name='Published from')),
                ('expiry_date', models.DateTimeField(blank=True, help_text="With published selected, won't be shown after this time", null=True, verbose_name='Expires on')),
                ('login_required', models.BooleanField(default=False, help_text='If checked, only logged in users can view the form', verbose_name='Login required')),
                ('send_email', models.BooleanField(default=True, help_text='If checked, the person entering the form will be sent an email', verbose_name='Send email')),
                ('email_from', models.EmailField(blank=True, help_text='The address the email will be sent from', max_length=254, verbose_name='From address')),
                ('email_copies', models.CharField(blank=True, help_text='One or more email addresses, separated by commas', max_length=200, verbose_name='Send copies to')),
                ('email_subject', models.CharField(blank=True, max_length=200, verbose_name='Subject')),
                ('email_message', models.TextField(blank=True, verbose_name='Message')),
                ('sites', models.ManyToManyField(default=[1], related_name='forms_form_forms', to='sites.Site')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form',
                'verbose_name_plural': 'Forms',
            },
        ),
        migrations.CreateModel(
            name='FormEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_time', models.DateTimeField(verbose_name='Date/time')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='forms.Form')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form entry',
                'verbose_name_plural': 'Form entries',
            },
        ),
        migrations.AddField(
            model_name='fieldentry',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='forms.FormEntry'),
        ),
        migrations.AddField(
            model_name='field',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='forms.Form'),
        ),
    ]
