from django.contrib import admin
from .models import Recall, RecallProduct, RecallAcknowledgment


class RecallProductInline(admin.TabularInline):
    model = RecallProduct
    extra = 0
    fields = ["product_description", "brand_name", "upc_codes", "lot_numbers", "code_info"]


@admin.register(Recall)
class RecallAdmin(admin.ModelAdmin):
    list_display = ["external_id", "source", "title_short", "hazard_type", "classification", "status", "recall_initiation_date"]
    list_filter = ["source", "status", "classification", "hazard_type"]
    search_fields = ["title", "recalling_firm", "external_id"]
    readonly_fields = ["created_at", "updated_at", "last_synced_at", "raw_data"]
    inlines = [RecallProductInline]

    def title_short(self, obj):
        return obj.title[:60] + ("…" if len(obj.title) > 60 else "")
    title_short.short_description = "Title"


@admin.register(RecallAcknowledgment)
class RecallAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = ["recall", "restaurant", "status", "acknowledged_by", "remediation_date", "updated_at"]
    list_filter = ["status"]
    search_fields = ["recall__title", "restaurant__name"]
