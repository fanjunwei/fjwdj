from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import format_html
from models import *
# Register your models here.
def upper_case_name(obj):
    return ("<span style='color:red'>%s,%d</span>" % (obj.nickname, obj.sex)).upper()
upper_case_name.short_description = 'Name'
upper_case_name.allow_tags=True
def export_selected_objects(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    aa=ContentType.objects.get_for_id(ct.pk)
    return HttpResponseRedirect("/export/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
export_selected_objects.short_description = "my action"

def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    return response


class MessageInline(admin.StackedInline):

    model = WeiXinMessage


class WeiXinUserAdmin(admin.ModelAdmin):

    list_display = ['nickname', 'sex','is_active',upper_case_name]

    exclude = ['unionid']

class SubjectAdmin(admin.ModelAdmin):
    pass


class WeiXinMessageAdmin(admin.ModelAdmin):
    list_display_links=[]

    date_hierarchy = 'create_time'


admin.site.register(WeiXinUser, WeiXinUserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(WeiXinMessage, WeiXinMessageAdmin)
admin.site.add_action(export_selected_objects)
admin.site.add_action(export_as_json,'ex json')