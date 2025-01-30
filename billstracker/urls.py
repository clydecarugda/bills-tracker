from django.urls import path
from .views import LoginPage, MainPage, BillList, BillDetailView, DeleteBill, CreateBill, UpdateBill, PayBill, BillView, DeleteBillDetail, CreateCategory
from .views import ProfileView, PasswordChange
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('', MainPage.as_view(), name='main'),
    path('bills_tracker/', BillList.as_view(), name='bills-tracker'),
    path('bills_tracker/billdetail/<int:pk>', BillDetailView.as_view(), name='billdetail-view'),
    path('bills_tracker/bill/<int:pk>', BillView.as_view(), name='bill-view'),
    path('bills_tracker/bill/delete_bill/<int:pk>', DeleteBill.as_view(), name='bill-delete'),
    path('bills_tracker/bill/update_bill/<int:pk>', UpdateBill.as_view(), name='bill-update'),
    path('bills_tracker/create_bill/', CreateBill.as_view(), name='create-bill'),
    path('bills_tracker/bill/pay_bill/<int:b_id>/<int:d_id>', PayBill.as_view(), name='pay-bill'),
    path('bills_tracker/billdetail/delete_billdetail/<int:pk>', DeleteBillDetail.as_view(), name='billdetail-delete'),
    path('bills_tracker/bill/create_category/', CreateCategory.as_view(), name='create-category'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('profile/passwordchange/<int:pk>', PasswordChange.as_view(), name='password-change'),
]