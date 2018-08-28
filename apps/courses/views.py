# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.http import HttpResponse
from pure_pagination import Paginator, PageNotAnInteger
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from courses.models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                    detail__icontains=search_keywords))

        # 对课程进行排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': courses, 'sort': sort, 'hot_courses': hot_courses
        })


class CourseDetailView(View):
    """
    课程详情页
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 获取课程标签，
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag).exclude(id=course_id)[:1]
        else:
            relate_courses = []

        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 课程的学习人数加一
        course.students += 1
        course.save()
        all_resources = CourseResource.objects.filter(course=course)

        # 当用户点击学习课程时，判断该用户是否原先已经关联过该课程，没有关联则进行关联
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 获取学习该课程的记录
        user_courses = UserCourse.objects.filter(course=course)
        # 获取学习该课程的用户的id列表
        user_ids = [user_course.id for user_course in user_courses]
        # 获取这些用户id学习过的课程记录
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出这些课程的课程id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        # 根据课程id获取课程信息
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        return render(request, 'course-video.html', {
            'course': course,
            'course_resources': all_resources,
            'relate_courses': relate_courses,
        })


class VideoPlayView(View):
    """
    视频播放页面
    """

    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))

        course = video.lesson.course
        course.students += 1
        course.save()

        # 当用户点击学习课程时，判断该用户是否原先已经关联过该课程，没有关联则进行关联
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 获取学习该课程的记录
        user_courses = UserCourse.objects.filter(course=course)
        # 获取学习该课程的用户的id列表
        user_ids = [user_course.id for user_course in user_courses]
        # 获取这些用户id学习过的课程记录
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出这些课程的课程id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        # 根据课程id获取课程信息
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        all_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-play.html', {
            'course': course,
            'course_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        })


class CourseCommentsView(View):
    """
    课程评论信息
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, 'course-comment.html', {
            'course': course,
            'course_resources': all_resources,
            'all_comments': all_comments
        })


class AddCommentsView(View):
    """
    用户添加课程评论
    """

    def post(self, request):
        # 判断用户登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail","msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success","msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"添加失败"}', content_type='application/json')
