# -*- coding: utf-8 -*-
# @author: hanzhi
# @email:  hanzhi@goldwind.com.cn
# @create: 2018/6/12 下午4:59
import xadmin
from organization.models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    list_filter = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city', 'add_time']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city__name', 'add_time']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums', 'image', 'address', 'city__name']
    relfield_style = 'fk-ajax'


class TeacherAdmin(object):
    list_display = ['name', 'org', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums',
                    'add_time']
    list_filter = ['name', 'org__name', 'work_years', 'work_company', 'work_position', 'points', 'click_nums',
                   'fav_nums', 'add_time']
    search_fields = ['name', 'org', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums']


xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
