from django.shortcuts import render, redirect
from django.views import View
import qrcode
import qrcode.image.svg
from io import BytesIO
from app.models import Domain, Visit
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# When developing locally uncomment and replace string with '/'
visit_url_prefix = 'https://visit-trackit.herokuapp.com/'


def get_visit_url(domain_name, username):
    domain_url = visit_url_prefix + 'visit?domain=' + domain_name + '&username=' + username
    return domain_url


def get_qrcode_stream(uri):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(uri, image_factory=factory, box_size=20)
    stream = BytesIO()
    img.save(stream)
    return stream


def get_or_set_domain(domain_name, user):
    domain = None
    domain_uri = get_visit_url(domain_name, user.username)
    try:
        domain = Domain.objects.get(name=domain_name, user=user)
    except:
        stream = get_qrcode_stream(domain_uri)
        domain = Domain(name=domain_name, qr_code=stream.getvalue().decode(), user=user)
        domain.save()
    return domain


def signup_user(username,email,password):
    try:
        user = User.objects.create_user(username, email,password)
        user.save()
    except e:
        print('Signup error', e)


def authenticate_user(request, username, password) :
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # A backend authenticated the credentials
        return redirect('/')
    else:
        return redirect('/login')
        # No backend authenticated the credentials


# Home view.
class HomeView(View):
    template_name = 'app/home.html'

    def get(self, request):
        domains = Domain.objects.filter(user__username=request.user.username)
        return render(
            request,
            self.template_name,
            {
                'domains': domains
            }
        )

    def post(self, request):
        domain_name = request.POST.get('domain')        
        domain = get_or_set_domain(domain_name, request.user)
        # Redirect to the page for that domain.
        return redirect('/view?domain=' + domain.name)
        

class DomainView(View):
    template_name = 'app/domain.html'

    def get(self, request):
        domain_name = request.GET.get('domain')
        try:
            domain = Domain.objects.get(name=domain_name, user=request.user)
            visits = Visit.objects.filter(domain=domain).order_by('-created_at')

            return render(
                request,
                self.template_name,
                {
                    'domain': domain,
                    'visits': visits
                }
            )
        except Exception as e:
            print(e)
            return redirect('/')


class VisitView(View):
    def get(self, request):
        domain_url = request.GET.get('domain')
        username = request.GET.get('username')
        # Create visit object.
        visit = Visit(domain=Domain.objects.get(name=domain_url, user__username=username))
        visit.save()
        # redirect to actual site.
        return redirect(domain_url)


class DownloadView(View):
    def post(self, request):
        domain_url = request.POST.get('domain')
        visit_uri = get_visit_url(domain_url, request.user.username)
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
        return authenticate_user(request, username, password)


class SignupView(View):
    def get(self, request):        
        return render(request,'app/signup.html')

    def post(self,request):
        username = request.POST.get('username') 
        password=request.POST.get('password')
        email=request.POST.get('email')
        signup_user(username,email,password)
        return authenticate_user(request, username, password)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')
