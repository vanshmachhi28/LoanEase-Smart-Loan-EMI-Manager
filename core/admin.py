from django.contrib import admin
from .models import CustomerQuery, Loan, LoanType



@admin.register(CustomerQuery)
class CustomerQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate')
    search_fields = ('name',)



@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'loan_type',
        'loan_amount',
        'interest_rate',
        'tenure_years',
        'status',
        'applied_at'
    )
    list_filter = ('status', 'loan_type')
    search_fields = ('user__username',)
    actions = ['approve_loans', 'reject_loans']

    def approve_loans(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_loans.short_description = "Reject selected loans"






