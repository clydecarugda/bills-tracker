from django.urls import path
from .views import LoginPage, MainPage, BillList, BillDetail, DeleteBill, CreateBill, UpdateBill
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', MainPage, name='main'),
    path('bills_tracker/', BillList.as_view(), name='bills-tracker'),
    path('bill/<int:pk>', BillDetail.as_view(), name='bill-view'),
    path('delete_bill/<int:pk>', DeleteBill.as_view(), name='bill-delete'),
    path('update_bill/<int:pk>', UpdateBill.as_view(), name='bill-update'),
    path('create_bill/', CreateBill.as_view(), name='create-bill'),
]
