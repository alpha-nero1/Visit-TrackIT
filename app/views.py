from django.shortcuts import render, redirect
from django.views import View
import qrcode
import qrcode.image.svg
from io import BytesIO
from app.models import Domain, Visit
from django.core.files.base import ContentFile
from django.http import HttpResponse

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


class HomeView(View):
    template_name = 'app/home.html'

    def get(self, request):
        domains = Domain.objects.all()
        return render(
            request,
            self.template_name,
            {
                'domains': domains
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
                'visits': visits
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
