from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path

from core import views, settings

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.main, name='main'),
    path('contact', views.contact, name='contact'),
    path('sign_in', views.login, name='login'),
    path('register', views.register, name='register'),
    path('guest', views.guest, name='guest'),
    path('logout', views.logout, name='logout'),
    path('my_kino', views.my_kino, name='my_kino'),
    path('review/<pk>', views.review, name='review'),
    path('price', views.price, name='price'),
    path('film/<pk>', views.session, name='film'),
    path('soon', views.soon, name='soon'),
    path('print_ticket', views.print_ticket, name='print_ticket'),
    path('trailer/<pk>', views.trailer, name='trailer'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('cabinet/page/<pk>', views.cabinet, name='cabinet_page'),
    path('soon/page/<pk>', views.soon, name='soon-page'),
    path('buy/session/session_id/', views.buy, name='buy_session_id'),
    path('print-report/<pk>', views.print_report, name='print_report'),
    path('<url_date>/page/<page_number>', views.main, name='url_date_page_number'),
    path('<url_date>/', views.main, name='url-date'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
