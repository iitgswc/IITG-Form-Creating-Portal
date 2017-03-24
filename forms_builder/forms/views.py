from __future__ import unicode_literals

import json
from csv import writer
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.http import urlquote
from django.views.generic.base import TemplateView
from email_extras.utils import send_mail_template
from io import BytesIO, StringIO
from forms_builder.forms.settings import CSV_DELIMITER, UPLOAD_ROOT
from forms_builder.forms.forms import FormForForm, EntriesForm
from forms_builder.forms.models import Form, Field, FormEntry, FieldEntry
from forms_builder.forms.settings import EMAIL_FAIL_SILENTLY
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.utils import split_choices

from django.views.generic import View
from .forms import LoginForm, CreateForm, CreateField
from django.contrib import auth
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from forms_builder.forms.utils import now, slugify


class FormDetail(TemplateView):
    template_name = "forms/form_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FormDetail, self).get_context_data(**kwargs)
        print("context is")
        print(context)
        print(context["view"])
        print(self.request.user)
        published = Form.objects.published(for_user=self.request.user)
        print("published is")
        print(published)
        context["form"] = get_object_or_404(published, slug=kwargs["slug"])
        return context

    def get(self, request, *args, **kwargs):
        print(args, kwargs)
        context = self.get_context_data(**kwargs)
        print("context")
        print(context)
        login_required = context["form"].login_required
        # print("login reqd ")
        # print(login_required)
        if login_required and not request.user.is_authenticated():
            # path = urlquote(request.get_full_path())
            # bits = (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
            # print(bits)
            # return redirect("%s?%s=%s" % bits)
            temp = '/forms/login?next=/forms/' + context["slug"]
            return redirect(temp)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        published = Form.objects.published(for_user=request.user)
        form = get_object_or_404(published, slug=kwargs["slug"])
        form_for_form = FormForForm(form, RequestContext(request), request.POST or None, request.FILES or None)
        if not form_for_form.is_valid():
            form_invalid.send(sender=request, form=form_for_form)
        else:
            # Attachments read must occur before model save,
            # or seek() will fail on large uploads.
            attachments = []
            for f in form_for_form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))
            entry = form_for_form.save()
            form_valid.send(sender=request, form=form_for_form, entry=entry)
            self.send_emails(request, form_for_form, form, entry, attachments)
            if not self.request.is_ajax():
                return redirect(form.redirect_url or
                                reverse("forms:form_sent", kwargs={"slug": form.slug}))
        context = {"form": form, "form_for_form": form_for_form}
        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            json_context = json.dumps({
                "errors": context["form_for_form"].errors,
                "form": context["form_for_form"].as_p(),
                "message": context["form"].response,
            })
            if context["form_for_form"].errors:
                return HttpResponseBadRequest(json_context,
                                              content_type="application/json")
            return HttpResponse(json_context, content_type="application/json")
        return super(FormDetail, self).render_to_response(context, **kwargs)

    def send_emails(self, request, form_for_form, form, entry, attachments):
        subject = form.email_subject
        if not subject:
            subject = "%s - %s" % (form.title, entry.entry_time)
        fields = []
        for (k, v) in form_for_form.fields.items():
            value = form_for_form.cleaned_data[k]
            if isinstance(value, list):
                value = ", ".join([i.strip() for i in value])
            fields.append((v.label, value))
        context = {
            "fields": fields,
            "message": form.email_message,
            "request": request,
        }
        email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
        email_to = form_for_form.email_to()
        if email_to and form.send_email:
            send_mail_template(subject, "form_response", email_from,
                               email_to, context=context,
                               fail_silently=EMAIL_FAIL_SILENTLY)
        headers = None
        if email_to:
            headers = {"Reply-To": email_to}
        email_copies = split_choices(form.email_copies)
        if email_copies:
            send_mail_template(subject, "form_response_copies", email_from,
                               email_copies, context=context,
                               attachments=attachments,
                               fail_silently=EMAIL_FAIL_SILENTLY,
                               headers=headers)


form_detail = FormDetail.as_view()


def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    context = {"form": get_object_or_404(published, slug=slug)}
    return render_to_response(template, context, RequestContext(request))


class LoginView(View):
    """
    View class for handling login functionality.
    """
    template_name = 'forms/login.html'
    port = 995
    next = ''

    def get(self, request):
        self.next = request.GET.get('next', '')
        print("*********************************************************************************************")
        print(self.next)
        if request.user.is_authenticated():  # removed .is_superuser
            print("0000000000000000000000000000000000000000000")
            return redirect(self.next)
        args = dict(form=LoginForm(None), next=self.next)
        print(args["next"])
        return render(request, self.template_name, args)

    def post(self, request):
        redirect_to = request.POST.get('next')
        print(redirect_to)
        print('lasdjfalsfdjkal;sfjaos;kldjf')
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            server = form.cleaned_data.get('login_server')
            user = auth.authenticate(username=username, password=password, server=server, port=self.port)
            print(user)
            if user is not None:
                print("uesr is not none")
                print(request.get_host())
                if is_safe_url(url=redirect_to, host=request.get_host()):
                    auth.login(request=request, user=user)
                    print("*******----------------------------------------------------------------------------------")
                    print(redirect_to)
                    return redirect(redirect_to)
                else:
                    print("in else")
                    args = dict(form=LoginForm(None), next=redirect_to)
                    print(args["next"])
                    return render(request, self.template_name, args)
            else:
                form.add_error(None, 'No user exists for given credentials.')
                return render(request, self.template_name, dict(form=form, next=redirect_to))
        else:
            return render(request, self.template_name, dict(form=form, next=redirect_to))


class CreateView(View):
    """
    View class for handling login functionality.
    """
    template_name = 'forms/create.html'
    next = ''

    def get(self, request):
        self.next = request.GET.get('next', '')
        print("*********************************************************************************************")
        print(self.next)
        if request.user.is_authenticated() and not request.user.is_superuser:
            # print("0000000000000000000000000000000000000000000")
            context = {
                "form": CreateForm(None)
            }
            return render(request, self.template_name, context)
        if not request.user.is_authenticated():
            temp = '/forms/login?next=/forms/create'
            return redirect(temp)
        args = dict(form=CreateForm(None))
        return render(request, self.template_name, args)

    def post(self, request):
        redirect_to = 'forms/createfield.html'
        form = CreateForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data.get('title')
            login_required = form.cleaned_data.get('login_required')
            published_date = form.cleaned_data.get('published_date')
            expiry_date = form.cleaned_data.get('expiry_date')
            intro = form.cleaned_data.get('intro')
            response = form.cleaned_data.get('response')
            no_of_fields = form.cleaned_data.get('no_of_fields')

            print(title, login_required, published_date, expiry_date, intro, response)

            f = Form()
            f.user = request.user
            f.title = title
            f.login_required = login_required
            f.publish_date = published_date
            f.expiry_date = expiry_date
            f.intro = intro
            f.response = response
            f.send_email = False
            f.save()
            # print(f.id)
            request.session['formid'] = f.id
            request.session['no_of_fields'] = no_of_fields
            print("12312312312312323123123123132123")
            print(f)
            return redirect('forms:createfield')
        else:
            return render(request, self.template_name, dict(form=form))


class CreateFieldView(View):
    """
    View class for handling login functionality.
    """
    template_name = 'forms/createfield.html'
    next = ''

    def get(self, request):
        self.next = request.GET.get('next', '')
        print("*********************************************************************************************")
        print(self.next)
        print(request.user)
        if request.user.is_authenticated():  # and not request.user.is_superuser

            context = {
                "no_of_fields": request.session["no_of_fields"]
            }
            namelist = []
            argsdict = {}
            for i in range(0, request.session["no_of_fields"]):
                tmp = "form" + str(i)
                namelist.append(tmp)
                argsdict[tmp] = CreateField(None, prefix=tmp)

            context["namelist"] = namelist
            context["argsdict"] = argsdict
            print("user name not none")
            print(context)
            return render(request, self.template_name, context)
        if not request.user.is_authenticated():
            print("usr none")
            temp = '/forms/login?next=/forms/create'
            return redirect(temp)
        print("chutiyapa")
        # only two possiblites either auth. or not auth.
        # args = dict(form=CreateForm(None))
        # return render(request, self.template_name, args)

    def post(self, request):
        # redirect_to = 'createfield.html'
        print(request.POST)
        form1 = CreateField(request.POST, prefix="1")

        context = {
            "no_of_fields": request.session["no_of_fields"]
        }
        namelist = []
        argsdict = {}
        booltmp = True
        for i in range(0, request.session["no_of_fields"]):
            tmp = "form" + str(i)
            namelist.append(tmp)
            tmpform = CreateField(request.POST, prefix=tmp)
            argsdict[tmp] = tmpform
            if not tmpform.is_valid():
                booltmp = False

        context["namelist"] = namelist
        context["argsdict"] = argsdict
        print("contect")
        print(context)
        if booltmp is False:
            return render(request, self.template_name, context)

        for i in range(0, request.session["no_of_fields"]):
            tmp = "form" + str(i)
            tmpform = argsdict[tmp]
            label = tmpform.cleaned_data.get('label')

            field_type = tmpform.cleaned_data.get('field_type')
            required = tmpform.cleaned_data.get('required')
            default = tmpform.cleaned_data.get('default')
            placeholder_text = tmpform.cleaned_data.get('placeholder_text')
            help_text = tmpform.cleaned_data.get('help_text')
            choices = tmpform.cleaned_data.get('choices')

            f = Field()
            f.form = Form.objects.get(id=request.session["formid"])
            f.label = label
            print(f.label)
            f.field_type = field_type
            f.required = required
            f.default = default
            f.placeholder_text = placeholder_text
            f.help_text = help_text
            f.choices = choices
            f.save()
            print("popopopopopopopopopopopopopopopopo")

        return redirect('forms:main')


class TestView(View):
    def get(self, request):
        auth.logout(request)
        return redirect('forms:main')


class MainView(View):
    def get(self, request):
        if request.user is not None and request.user.is_authenticated():
            context = {
                "forms": Form.objects.filter(user=request.user),
            }
            print(Form.objects.filter(user=request.user))
            template_name = 'forms/main.html'
            return render(request, template_name, context)
        else:
            temp = '/forms/login?next=/forms'
            return redirect(temp)
            # return render(request,'forms/login.html',context)


class ExportCsvView(View):
    def get(self, request, formid):

        export = False
        if request.user.is_authenticated():
            form = get_object_or_404(Form, id=formid)

            if form.user.id == request.user.id:
                post = request.POST or None
                args = form, request, FormEntry, FieldEntry, post
                entries_form = EntriesForm(*args)
                print(entries_form)
                submitted = entries_form.is_valid() or export
                print(submitted)
                if submitted:
                    response = HttpResponse(content_type="text/csv")
                    fname = "%s-%s.csv" % (form.slug, slugify(now().ctime()))
                    attachment = "attachment; filename=%s" % fname
                    response["Content-Disposition"] = attachment
                    queue = StringIO()
                    try:
                        csv = writer(queue, delimiter=CSV_DELIMITER)
                        writerow = csv.writerow
                    except TypeError:
                        queue = BytesIO()
                        delimiter = bytes(CSV_DELIMITER, encoding="utf-8")
                        csv = writer(queue, delimiter=delimiter)
                        writerow = lambda row: csv.writerow([c.encode("utf-8")
                                                             if hasattr(c, "encode") else c for c in row])
                    writerow(entries_form.columns())
                    for row in entries_form.rows(csv=True):
                        writerow(row)
                    data = queue.getvalue()
                    response.write(data)
                    return response
                else:
                    return HttpResponse("hasdsdhsdh")
            else:
                return HttpResponse("hasdsdhsdh")
        else:
            return HttpResponse("sdgsdsdgsdg")
            # have to see for not returnign and doing anything
