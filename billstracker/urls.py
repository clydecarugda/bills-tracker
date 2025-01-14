from django.urls import path
from .views import LoginPage, MainPage, BillList, BillDetail
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', MainPage, name='main'),
    path('bills-tracker/', BillList.as_view(), name='bills-tracker'),
    path('bill/<int:pk>', BillDetail.as_view(), name='bill-view'),
]
