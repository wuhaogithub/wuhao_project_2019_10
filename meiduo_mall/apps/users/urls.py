from django.conf.urls import url
from . import views
urlpatterns = [
    # 采用严格的开始和结束
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^center/$', views.UserCenterInfoView.as_view(), name='center'),
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    url(r'^emailsactive/$', views.EmailActiveView.as_view(), name='emailactive'),
    url(r'^site/$', views.UserCenterSiteView.as_view(), name='site'),
    url(r'^browse_histories/$', views.UserHistoryView.as_view(), name='history'),
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='createaddress'),
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name='addressesupdate'),
]