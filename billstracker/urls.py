from django.urls import path
from .views import LoginPage, MainPage, BillList, BillDetailView, DeleteBill, CreateBill, UpdateBill, PayBill, BillView, DeleteBillDetail, CreateCategory
from .views import ProfileView, PasswordChange, AccountView, MoneyAccountList, MoneyAccountAdd, MoneyAccountView, MoneyAccountDelete, MoneyAccountUpdate
from .views import MoneyTransfer, TransactionHistory, AccountGroupList, AccountGroupAdd, AccountGroupDelete, AccountGroupView, AccountGroupEdit, MoneyIncome
from .views import MoneyExpense, AdminView, FeedbackCreate, MonthlyExpenseDataView, IncomeExpenseDataView, ExpenseTrendDataView
from .views import GetBillsList, UserSetting, GetCategoryListIncome, GetCategoryListExpense, UpdateCategory, DeleteCategory, CreateCategory2

from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', MainPage.as_view(), name='main'),
    
    path('bills-tracker/', BillList.as_view(), name='bills-tracker'),
    path('bills-tracker/get-bills-list-data', GetBillsList.as_view(), name='get-bills-list'),
    path('bills-tracker/billdetail/<int:pk>', BillDetailView.as_view(), name='billdetail-view'),
    path('bills-tracker/bill/<int:pk>', BillView.as_view(), name='bill-view'),
    path('bills-tracker/bill/delete-bill/<int:pk>', DeleteBill.as_view(), name='bill-delete'),
    path('bills-tracker/bill/update-bill/<int:pk>', UpdateBill.as_view(), name='bill-update'),
    path('bills-tracker/create-bill/', CreateBill.as_view(), name='create-bill'),
    path('bills-tracker/bill/pay-bill/<int:b_id>/<int:d_id>', PayBill.as_view(), name='pay-bill'),
    path('bills-tracker/billdetail/delete-billdetail/<int:pk>', DeleteBillDetail.as_view(), name='billdetail-delete'),
    path('bills-tracker/bill/createcategory/', CreateCategory.as_view(), name='create-category'),
    
    path('money-tracker/dashboard', AccountView.as_view(), name='money-dashboard'),
    path('money-tracker/accounts', MoneyAccountList.as_view(), name='money-accounts'),
    path('money-tracker/accounts/add', MoneyAccountAdd.as_view(), name='money-accounts-add'),
    path('money-tracker/accounts/<int:pk>', MoneyAccountView.as_view(), name='money-accounts-view'),
    path('money-tracker/accounts/delete/<int:pk>', MoneyAccountDelete.as_view(), name='money-accounts-delete'),
    path('money-tracker/accounts/edit/<int:pk>', MoneyAccountUpdate.as_view(), name='money-accounts-edit'),
    path('money-tracker/accounts/transfer', MoneyTransfer.as_view(), name='money-accounts-transfer'),
    path('money-tracker/transaction-history', TransactionHistory.as_view(), name='money-transaction-history'),
    path('money-tracker/account-groups', AccountGroupList.as_view(), name='money-account-groups'),
    path('money-tracker/account-groups/add', AccountGroupAdd.as_view(), name='money-account-group-add'),
    path('money-tracker/account-groups/<int:pk>', AccountGroupView.as_view(), name='money-account-group-view'),
    path('money-tracker/account-groups/<int:pk>/edit', AccountGroupEdit.as_view(), name='money-account-group-edit'),
    path('money-tracker/account-groups/<int:pk>/delete', AccountGroupDelete.as_view(), name='money-account-group-delete'),
    path('money-tracker/accounts/income', MoneyIncome.as_view(), name='money-accounts-income'),
    path('money-tracker/accounts/expense', MoneyExpense.as_view(), name='money-accounts-expense'),
    
    path('profile/admin/', AdminView.as_view(), name='profile-admin'),
    path('profile/feedback/new', FeedbackCreate.as_view(), name='feedback-new'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('profile/passwordchange/<int:pk>', PasswordChange.as_view(), name='password-change'),
    path('profile/settings', UserSetting.as_view(), name='user-settings'),
    
    path('get-monthly-expense-data/', MonthlyExpenseDataView.as_view(), name='get-monthly-expense-data'),
    path('get-income-expense-data/', IncomeExpenseDataView.as_view(), name='get-income-expense-data'),
    path('get-expense-trends-data/', ExpenseTrendDataView.as_view(), name='get-expense-trend-data'),
    
    path('profile/settings/get-income-category-data/', GetCategoryListIncome.as_view(), name='get-income-category-data'),
    path('profile/settings/get-expense-category-data/', GetCategoryListExpense.as_view(), name='get-expense-category-data'),
    path('profile/settings/create-category/', CreateCategory2.as_view(), name='create-category'),
    path('profile/settings/update-category/', UpdateCategory.as_view(), name='update-category'),
    path('profile/settings/delete-category/', DeleteCategory.as_view(), name='delete-category'),
]