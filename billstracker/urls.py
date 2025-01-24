from django.urls import path
from .views import LoginPage, MainPage, BillList, BillDetailView, DeleteBill, CreateBill, UpdateBill, PayBill
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', MainPage.as_view(), name='main'),
    path('bills_tracker/', BillList.as_view(), name='bills-tracker'),
    path('bill/<int:pk>', BillDetailView.as_view(), name='bill-view'),
    path('delete_bill/<int:pk>', DeleteBill.as_view(), name='bill-delete'),
    path('update_bill/<int:pk>', UpdateBill.as_view(), name='bill-update'),
    path('create_bill/', CreateBill.as_view(), name='create-bill'),
    path('pay_bill/<int:pk>', PayBill.as_view(), name='pay-bill'),
]
