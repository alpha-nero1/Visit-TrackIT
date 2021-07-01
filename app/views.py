from django.shortcuts import render, redirect
from django.views import View
import qrcode
import qrcode.image.svg
from io import BytesIO
from app.models import Domain, Visit
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

visit_url_prefix = 'https://visit-trackit.herokuapp.com/'

def get_qrcode_stream(str):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(str, image_factory=factory, box_size=20)
    stream = BytesIO()
    img.save(stream)
    return stream


def get_or_set_domain(domain_name):
    domain = None
    domain_uri = visit_url_prefix + 'visit?domain=' + domain_name
    try:
        domain = Domain.objects.get(name=domain_name)
    except:
        stream = get_qrcode_stream(domain_name)
        domain = Domain(name=domain_name, qr_code=stream.getvalue().decode())
        domain.save()
    return domain


def signup_user(username,email,password):
    try:
        user = User.objects.create_user(username, email,password)
        user.save()
        print(user)
    except e:
        print('Already Present',e)


def authenticate_user(userName,passWord) :
    user = authenticate(username=userName, password=passWord)
    print(user)
    if user is not None:
    # A backend authenticated the credentials
        return redirect('/')
    else:
        return redirect('/login')
    # No backend authenticated the credentials


class HomeView(View):
    template_name = 'app/home.html'

    def get(self, request):
        domains = Domain.objects.all()
        print(request.user)
        return render(
            request,
            self.template_name,
            {
                'domains': domains,
                'user':request.user
            }
        )

    def post(self, request):
        domain_name = request.POST.get('domain')        
        domain = get_or_set_domain(domain_name)
        # Redirect to the page for that domain.
        return redirect('/view?domain=' + domain.name)
        

class DomainView(View):
    template_name = 'app/domain.html'

    def get(self, request):
        domain_name = request.GET.get('domain')
        domain = Domain.objects.get(name=domain_name)
        visits = Visit.objects.filter(domain=domain)

        return render(
            request,
            self.template_name,
            {
                'domain': domain,
                'visits': visits,
                'user':request.user
            }
        )


class VisitView(View):
    def get(self, request):
        domain_url = request.GET.get('domain')
        # Create visit object.
        visit = Visit(domain=Domain.objects.get(name=domain_url))
        visit.save()
        # redirect to actual site.
        return redirect(domain_url)


class DownloadView(View):
    def post(self, request):
        domain_url = request.POST.get('domain')
        visit_uri = visit_url_prefix + '/visit?domain=' + domain_url
        string_to_return = get_qrcode_stream(visit_uri).getvalue()

        file_to_send = ContentFile(string_to_return)
        response = HttpResponse(file_to_send,'image/*')
        response['Content-Length'] = file_to_send.size    
        response['Content-Disposition'] = 'attachment; filename="qr_code_' + domain_url + '.svg"'
        return response   


class LoginView(View):
    def get(self, request):        
        return render(request,'app/login.html')

    def post(self,request):
        username = request.POST.get('username') 
        password=request.POST.get('password')
        return authenticate_user(username, password)


class SignupView(View):
    def get(self, request):        
        return render(request,'app/signup.html')

    def post(self,request):
         username = request.POST.get('username') 
         password=request.POST.get('password')
         email=request.POST.get('email')
         signup_user(username,email,password)
         return authenticate_user(username, password)
