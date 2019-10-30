from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('apps.users.urls', namespace='users')),
    url(r'', include('apps.contents.urls', namespace='contents')),
    url(r'', include('apps.verifications.urls', namespace='verifications')),

]
