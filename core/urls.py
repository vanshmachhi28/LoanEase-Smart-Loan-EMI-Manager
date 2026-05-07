from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('emi-calculator/', views.emi_calculator, name='emi_calculator'),


    path('apply-loan/', views.apply_loan, name='apply_loan'),

    path('my-loans/', views.my_loans, name='my_loans'),



    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),

    path(
    'update-loan-status/<int:loan_id>/<str:action>/',
    views.update_loan_status,
    name='update_loan_status'),



    path('download-emi-pdf/', views.download_emi_pdf, name='download_emi_pdf'),

    path('verify-loan/<int:loan_id>/', views.verify_loan, name='verify_loan'),

    #ChatBot
    path('chatbot/', views.loan_chatbot, name='chatbot'),

]
