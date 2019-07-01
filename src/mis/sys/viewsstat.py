import datetime
import locale
import logging
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import logout as sys_logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
from mis.models import Mis, Cars, CarStatus
from callcard.models import CallCard
from .sysutils import is_sys, is_mis_admin
RED = "#FF0000"
GREEN = "#C4FFD4"
GRAY = "#C0C0C0"


def findChildren(center_l, parent, facility_l, level):
    f_type = ["U", ["[Ц]", "red"], ["[С]", "green"], ["[ПС]", "blue"], ["[ПБ]", "yellow"]]
    for center in center_l:     # [0]=name [1]=mis_facility_id [2]=facility_parent
        if center[2] == parent:
            item = []
            level_p = f'{level}-'
            if len(level_p) > 6:
                logging.critical("Exceeding recursion level: 6")
                return
            item.append(center[0])
            item.append(level_p)
            item.append(f_type[center[5]])
            item.append(center[3])
            item.append(center[4])
            facility_l.append(item)
            findChildren(center_l, center[1], facility_l, level_p)


@login_required(login_url='/login/')
@user_passes_test(is_sys, login_url='/', redirect_field_name=None)
def stat_sys_view(request, mid):
    if not is_mis_admin(request.user, mid):
        return redirect('/login/')
    mis_obj = Mis.objects.get(id=mid)
    context = get_stat_context(request, mis_obj)
    context["refresh"] = False
    center_l = getFacility(mis_id=mid)
    facility_l = []
    findChildren(center_l, "0", facility_l, "")
    facility_stat = getFacilityStat(mis_id=mid)
    staff_stat = getStaffStat(mis_id=mid)
    cars_stat = getCarsStat(mis_id=mid)
    cars_year = getCarsYear(mis_id=mid)

    context["facility_l"] = facility_l
    context["facility_stat"] = facility_stat
    context["staff_stat"] = staff_stat
    context["cars_stat"] = cars_stat
    context["cars_year"] = cars_year
    context["is_mis_admin"] = "True"
    return render(request, "mis_stat_sys.html", context)


def get_stat_context(request, mis_obj):
    mis_id = mis_obj.id
    context = {
        "mis": mis_obj,
        "user": request.user.username,
        "timezone_now": timezone.now(),
        "hostname": settings.HOSTNAME,
        "info_link": f'/sys/mis/{mis_id}/',
        "is_mis_admin": "False",
    }
    return context


def getCarsYear(mis_id):
    result = []
    car_all_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(Q(mis_id=mis_id) & Q(is_active=True)).order_by('-year_made')
    car_work_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1)).order_by('-year_made')
    car_notwork_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=2)).order_by('-year_made')

    car_typec_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1) & Q(car_type=1)).order_by('-year_made')
    car_typeb_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1) & Q(car_type=2)).order_by('-year_made')
    car_typea1_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1) & Q(car_type=3)).order_by('-year_made')
    car_typea2_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1) & Q(car_type=4)).order_by('-year_made')
    car_typens_qs = Cars.objects.values('year_made').annotate(
        num=Count('year_made')).filter(
        Q(mis_id=mis_id) & Q(is_active=True) & Q(car_status=1) & Q(car_type=5)).order_by('-year_made')

    for car_all in car_all_qs:
        year_item = {}
        year_item['year'] = car_all['year_made']
        year_item['total'] = car_all['num']
        for car_work in car_work_qs:
            if car_all['year_made'] == car_work['year_made']:
                year_item['work'] = car_work['num']

        for car_notwork in car_notwork_qs:
            if car_all['year_made'] == car_notwork['year_made']:
                year_item['notwork'] = car_notwork['num']

        for car_typec in car_typec_qs:
            if car_all['year_made'] == car_typec['year_made']:
                year_item['typec'] = car_typec['num']
        for car_typeb in car_typeb_qs:
            if car_all['year_made'] == car_typeb['year_made']:
                year_item['typeb'] = car_typeb['num']
        for car_typea1 in car_typea1_qs:
            if car_all['year_made'] == car_typea1['year_made']:
                year_item['typea1'] = car_typea1['num']
        for car_typea2 in car_typea2_qs:
            if car_all['year_made'] == car_typea2['year_made']:
                year_item['typea2'] = car_typea2['num']
        for car_typens in car_typens_qs:
            if car_all['year_made'] == car_typens['year_made']:
                year_item['typens'] = car_typens['num']

        result.append(year_item)
    return result  # list(car_all_qs)


# Q(is_active=True) & Q(car_status=1)


def getCarsStat(mis_id):
    result = {}
    cursor1 = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor4 = connection.cursor()
    cursor5 = connection.cursor()
    q_type = 'select id, cartype_name, t2.cnt from mis_cartype left join \
    (select car_type_id, count(car_type_id) as cnt from mis_cars \
    where mis_id_id=%s and is_active=true and car_status_id=1 \
    group by car_type_id) t2 \
    on mis_cartype.id = t2.car_type_id order by mis_cartype.id'
    q_status = 'select is_active, count(is_active) from mis_cars \
    where mis_id_id=%s \
    group by is_active order by is_active desc'
    q_notwork = 'select count(*) from mis_cars where mis_id_id = %s and car_status_id=2'
    q_total = 'select count(*) from mis_cars where mis_id_id = %s'
    q_update = 'select max(date_modified) from mis_cars where mis_id_id = %s'
    cursor1.execute(q_type, [mis_id])
    cursor2.execute(q_status, [mis_id])
    cursor3.execute(q_total, [mis_id])
    cursor4.execute(q_notwork, [mis_id])
    cursor5.execute(q_update, [mis_id])
    type_qs = cursor1.fetchall()
    status_qs = cursor2.fetchall()
    total_qs = cursor3.fetchall()
    notwork_qs = cursor4.fetchall()
    update_qs = cursor5.fetchall()
    result['total'] = total_qs[0][0]
    result['notwork'] = notwork_qs[0][0]
    if len(status_qs) > 0:
        result['active'] = status_qs[0][1]
        if len(status_qs) > 1:
            result['not_active'] = status_qs[1][1]
        else:
            result['not_active'] = 0
        result['last_update'] = update_qs[0][0].strftime('%d/%m/%Y %H:%M:%S')
    result['C'] = type_qs[0][2]
    result['B'] = type_qs[1][2]
    result['A1'] = type_qs[2][2]
    result['A2'] = type_qs[3][2]
    result['nonst'] = type_qs[4][2]
    return result


def getStaffStat(mis_id):
    medical = [1, 2, 5, 6, 9, 10, 14, 15, 16, 17]
    # Лікар, Фельдшер, Стажер, Парамедик, Медична сестра, Акушерка, Інтерн, Фармацевт, Провізор
    nonmedical = [3, 4, 7, 18]  # Санітар, Водій, ЕМТ, Диспетчер
    admin = [8, 11, 12, 13]  # Адміністратор, Фахівець, Робітник, SYSTEM
    cursor1 = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor4 = connection.cursor()
    q_type = 'select title_id, count(title_id) from mis_staff \
    where mis_id_id=%s and is_active=true \
    group by title_id order by title_id'
    q_status = 'select is_active, count(is_active) from mis_staff \
    where mis_id_id=%s \
    group by is_active order by is_active desc'
    q_total = 'select count(*) from mis_staff where mis_id_id=%s'
    q_update = 'select max(date_modified) from mis_staff where mis_id_id=%s'
    cursor1.execute(q_type, [mis_id])
    cursor2.execute(q_status, [mis_id])
    cursor3.execute(q_total, [mis_id])
    cursor4.execute(q_update, [mis_id])
    type_qs = cursor1.fetchall()
    status_qs = cursor2.fetchall()
    total_qs = cursor3.fetchall()
    update_qs = cursor4.fetchall()
    result = {}
    result['active'] = status_qs[0][1]
    if len(status_qs) > 1:
        result['not_active'] = status_qs[1][1]
    else:
        result['not_active'] = 0
    result['total'] = total_qs[0][0]
    med = 0
    likar = 0
    feldsher = 0
    stager = 0
    inter = 0
    param = 0
    sister = 0
    akush = 0
    farma = 0
    proviz = 0
    nmed = 0
    emt = 0
    vodiy = 0
    sanitar = 0
    dispatcher = 0
    operator = 0
    adm = 0
    for item in type_qs:
        if item[0] in medical:
            med += item[1]
            if item[0] == 1:
                likar += item[1]
            elif item[0] == 2:
                feldsher += item[1]
            elif item[0] == 5:
                stager += item[1]
            elif item[0] == 6:
                param += item[1]
            elif item[0] == 9:
                sister += item[1]
            elif item[0] == 10:
                akush += item[1]
            elif item[0] == 14:
                inter = + item[1]
            elif item[0] == 15:
                farma = + item[1]
            elif item[0] == 16:
                proviz = + item[1]
            elif item[0] == 17:
                dispatcher += item[1]
        elif item[0] in nonmedical:
            nmed += item[1]
            if item[0] == 7:
                emt += item[1]
            elif item[0] == 4:
                vodiy += item[1]
            elif item[0] == 3:
                sanitar += item[1]
            elif item[0] == 18:
                operator += item[1]
        elif item[0] in admin:
            adm += item[1]
    result['midical'] = med
    result['likar'] = likar
    result['feldsher'] = feldsher
    result['stager'] = stager
    result['param'] = param
    #result['inshi'] = inshi
    result['sister'] = sister
    result['akush'] = akush
    result['inter'] = inter
    result['farma'] = farma
    result['proviz'] = proviz
    result['nonmedical'] = nmed
    result['emt'] = emt
    result['vodiy'] = vodiy
    result['sanitar'] = sanitar
    result['dispatcher'] = dispatcher
    result['operator'] = operator
    result['admin'] = adm
    result['last_update'] = update_qs[0][0].strftime('%d/%m/%Y %H:%M:%S')
    return result


def getFacilityStat(mis_id):
    cursor1 = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor4 = connection.cursor()
    q_type = 'select id, facilitytype_name, t2.cnt from mis_facilitytype left join \
    (select facility_type_id, count(facility_type_id) as cnt from mis_facility \
    where mis_id_id=%s and is_active=true \
    group by facility_type_id) t2 \
    on mis_facilitytype.id = t2.facility_type_id \
    order by id'
    q_status = 'select is_active, count(is_active) from mis_facility \
    where mis_id_id=%s \
    group by is_active order by is_active desc'
    q_total = 'select count(*) from mis_facility where mis_id_id=%s'
    q_update = 'select max(date_modified) from mis_facility where mis_id_id=%s'
    cursor1.execute(q_type, [mis_id])
    cursor2.execute(q_status, [mis_id])
    cursor3.execute(q_total, [mis_id])
    cursor4.execute(q_update, [mis_id])
    type_qs = cursor1.fetchall()
    status_qs = cursor2.fetchall()
    total_qs = cursor3.fetchall()
    update_qs = cursor4.fetchall()
    result = {}
    result['active'] = status_qs[0][1]
    if len(status_qs) > 1:
        result['not_active'] = status_qs[1][1]
    else:
        result['not_active'] = 0
    result['total'] = total_qs[0][0]
    result['center'] = type_qs[0][2]
    result['station'] = type_qs[1][2]
    result['substation'] = type_qs[2][2]
    result['pb'] = type_qs[3][2]
    result['last_update'] = update_qs[0][0].strftime('%d/%m/%Y %H:%M:%S')
    return result


def getFacility(mis_id):
    ret = []
    cursor = connection.cursor()
    q_str = 'select name, mis_facility_id, facility_parent, staff.staff_cnt, cars.cars_cnt, facility_type_id \
    from mis_facility left join (select mis_staff.facility_id_id as facility_id, \
    count(mis_staff.id) as staff_cnt from mis_staff where is_active=true \
    group by mis_staff.facility_id_id) staff on mis_facility.id = staff.facility_id \
    left join (select mis_cars.facility_id_id as facility_id, count(mis_cars.id) as cars_cnt \
    from mis_cars where is_active=true group by mis_cars.facility_id_id) cars \
    on mis_facility.id = cars.facility_id \
    where mis_id_id=%s and is_active=true order by id'
    cursor.execute(q_str, [mis_id])
    facility_qs = cursor.fetchall()
    ret = list(facility_qs)
    return ret
