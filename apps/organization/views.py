# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger

from courses.models import Course
from operation.models import UserFavorite
from organization.forms import UserAskForm
from organization.models import CourseOrg, CityDict, Teacher


class OrgView(View):
    """
    课程机构列表功能
    """

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        # 城市
        all_cities = CityDict.objects.all()
        # 组织排名
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        # 机构搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 取出筛选城市
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 取出排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        # 类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)
        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 5)
        except PageNotAnInteger:
            page = 1

        org_nums = all_orgs.count()

        # 5是每一页的数量
        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html',
                      {'all_orgs': orgs, 'all_cities': all_cities, 'org_nums': org_nums, 'city_id': city_id,
                       'category': category, 'hot_orgs': hot_orgs, 'sort': sort})


class AddUserAskView(View):
    """
    用户添加咨询
    """

    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 注意json双引号，json必须为双引号
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            # 注意json双引号，json必须为双引号
            return HttpResponse('{"status":"fail","msg":"wrong"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self, request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))

        # 课程机构点击数加一
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:3]
        return render(request, 'org-detail-homepage.html',
                      {'all_courses': all_courses, 'all_teachers': all_teachers, 'course_org': course_org,
                       'current_page': current_page, 'has_fav': has_fav})


class OrgCourseView(View):
    """
    机构课程页
    """

    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html',
                      {'course_org': course_org, 'all_courses': all_courses, 'current_page': current_page,
                       'has_fav': has_fav})


class OrgDescView(View):
    """
    机构介绍页
    """

    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html',
                      {'current_page': current_page, 'course_org': course_org, 'has_fav': has_fav})


class OrgTeacherView(View):
    """
    机构教师页
    """

    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html',
                      {'current_page': current_page, 'course_org': course_org, 'all_teachers': all_teachers,
                       'has_fav': has_fav})


class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)
        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse('{"status":"fail","msg":"用户未登录"}', content_type='application/json')
        # 判断是否已经收藏
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在，则表示用户取消收藏
            exist_records.delete()
            # 取消收藏时，收藏数减一
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            return HttpResponse('{"status":"success","msg":"收藏"}', content_type='application/json')
        else:
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav = UserFavorite()
                user_fav.user = request.user
                user_fav.fav_type = int(fav_type)
                user_fav.fav_id = int(fav_id)
                user_fav.save()
                # 收藏时，收藏数加一
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success","msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail","msg":"收藏出错"}', content_type='application/json')


class TeacherListView(View):
    """
    课程讲师列表页
    """

    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 课程讲师搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords) | Q(
                    work_position__icontains=search_keywords))

        # 根据热度排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')

        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers, 3, request=request)

        teachers = p.page(page)
        return render(request, 'teachers-list.html', {
            'all_teachers': teachers,
            'sorted_teacher': sorted_teacher,
            'sort': sort,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=teacher_id)

        # 教师点击数加一
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)

        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        has_teacher_faved = False
        if request.user.is_authenticated:
            # 判断用户登录状态
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher_id):
                has_teacher_faved = True

        has_org_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True

        return render(request, 'teacher-detail.html', {
            'teacher': teacher,
            'all_courses': all_courses,
            'sorted_teacher': sorted_teacher,
            'has_teacher_faved': has_teacher_faved,
            'has_org_faved': has_org_faved,
        })
