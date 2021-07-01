from django.shortcuts import render, redirect
from django.views import View
import qrcode
import qrcode.image.svg
from io import BytesIO
from app.models import Domain, Visit

def get_or_set_domain(domain_name):
    domain = None
    try:
        domain = Domain.objects.get(name=domain_name)
    except:
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(domain, image_factory=factory, box_size=20)
        stream = BytesIO()
        img.save(stream)
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

        return render(
            request,
            self.template_name,
            {
                'domain': domain
            }
        )
