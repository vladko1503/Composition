import datetime
import locale
import logging
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import logout as sys_logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.conf import settings
from mis.models import Mis
from .sysutils import is_mis_admin, is_sys

RED = "#EBCCDC"
YELLOW = "#FCE6AD"
# GREEN = "#C4FFD4" # More bright
GREEN = "#C4E5D4"
GRAY = "#B0B0B0"
# SUN = "#DBBCCC"
SAT = "#FF0000"
SUN = "#EE0000"


@login_required(login_url='/login/')
@user_passes_test(is_sys, login_url='/', redirect_field_name=None)
def mis_sysday_view(request, mid, mdate):
    if not is_mis_admin(request.user, mid):
        return redirect('/login/')
    try:
        sdate = str(mdate)
        this_date = date(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:]))
    except Exception as ex:
        raise Http404
    context = get_sysday_context(request, mid, mdate)
    context["mdate"] = mdate
    context["info_link"] = f'/sys/mis/{mid}/'
    context["is_mis_admin"] = "True"
    context["refresh"] = True
    return render(request, "mis_day_sys.html", context)


def get_sysday_context(request, mid, sdate):
    this_date = date(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:]))
    date_s = this_date.strftime("%d/%m/%Y")
    title = []
    item = {}
    item['name'] = date_s
    item['link'] = f'/sys/mis/{mid}/{sdate}/calls/'
    title.append(item)
    for hour in range(0, 24):
        item = {}
        item['name'] = f'{hour}'
        item['link'] = f'/sys/mis/{mid}/{sdate}/{hour}/'
        title.append(item)
    heartbeat = getHeartbeatDay(mis_id=mid, this_date=this_date)
    calls = getCallDay(mis_id=mid, this_date=this_date)
    fake = getCallTypeDay(mis_id=mid, this_date=this_date, call_type=[1])
    crew_call = getCallTypeDay(mis_id=mid, this_date=this_date, call_type=[3])
    advise = getCallTypeDay(mis_id=mid, this_date=this_date, call_type=[2, 5, 7])
    refuse = getCallTypeDay(mis_id=mid, this_date=this_date, call_type=[6])
    noanswer = getCallTypeDay(mis_id=mid, this_date=this_date, call_type=[8])

    ed_call = getEdCallDay(mis_id=mid, this_date=this_date)
    dpv = getOperatorOnDuty(mis_id=mid, this_date=this_date, operator=2)
    # dpv_id = dpv.pop()
    dn = getOperatorOnDuty(mis_id=mid, this_date=this_date, operator=4)
    # dn_id = dn.pop()
    crew_duty = getCrewOnDuty(mis_id=mid, this_date=this_date)
    crew_count = crew_duty.pop()
    mis_obj = get_object_or_404(Mis, id=mid)
    context = {
        "mis": mis_obj,
        "user": request.user.username,
        "timezone_now": timezone.now(),
        "hostname": settings.HOSTNAME,
        "mdate": this_date,
        "date_s": date_s,
        "title": title,
        "heartbeat": heartbeat,
        "calls": calls,
        "noanswer": noanswer,
        "refuse": refuse,
        "fake": fake,
        "advise": advise,
        "crew_call": crew_call,
        "ed_call": ed_call,
        "crew_duty": crew_duty,
        "dpv": dpv,
        #"dpv_id": dpv_id,
        "dpv_count": len(dpv) - 1,
        "dn": dn,
        #"don_id": dn_id,
        "dn_count": len(dn) - 1,
        "crew_count": crew_count,
        "is_mis_admin": "False",
    }
    return context


# Weekly views
@login_required(login_url='/login/')
@user_passes_test(is_sys, login_url='/', redirect_field_name=None)
def mis_sysdetails_view(request, mid):
    context = get_sysdetailed_context(request, mid)
    if is_mis_admin(request.user, mid):
        context["info_link"] = f'/sys/mis/{mid}/'
        context["is_mis_admin"] = "True"
        context["refresh"] = True
    context["breadcrumb"] = True
    return render(request, "mis_details_sys.html", context)


def get_sysdetailed_context(request, mid):
    t_d = {}
    t_d[0] = timezone.now()
    t_d[1] = (timezone.now() - timedelta(days=1))
    t_d[2] = (timezone.now() - timedelta(days=2))
    t_d[3] = (timezone.now() - timedelta(days=3))
    t_d[4] = (timezone.now() - timedelta(days=4))
    t_d[5] = (timezone.now() - timedelta(days=5))
    t_d[6] = (timezone.now() - timedelta(days=6))
    t_d[7] = (timezone.now() - timedelta(days=7))
    # locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    is_adm = is_mis_admin(request.user, mid)
    errors = None
    heartbeat = getHeartbeatSum(mis_id=mid, t_d=t_d)
    calls, ytd = getCallSum(mis_id=mid, t_d=t_d)
    fake = getCallTypeSum(mis_id=mid, t_d=t_d, ytd=ytd, call_type=[1])
    crew_call = getCallTypeSum(mis_id=mid, t_d=t_d, ytd=ytd, call_type=[3])
    advise = getCallTypeSum(mis_id=mid, t_d=t_d, ytd=ytd, call_type=[2, 5, 7])
    refuse = getCallTypeSum(mis_id=mid, t_d=t_d, ytd=ytd, call_type=[6])
    noanswer = getCallTypeSum(mis_id=mid, t_d=t_d, ytd=ytd, call_type=[8])

    ed_call = getEdCallSum(mis_id=mid, t_d=t_d, ytd=ytd)
    title = []
    title_names = ['За рік', '%', t_d[0].strftime('%d/%m'), t_d[1].strftime('%d/%m'),
                   t_d[2].strftime('%d/%m'), t_d[3].strftime('%d/%m'), t_d[4].strftime('%d/%m'),
                   t_d[5].strftime('%d/%m'), t_d[6].strftime('%d/%m'), t_d[7].strftime('%d/%m'), ]
    title_links = ['None', 'None', f"/sys/mis/{mid}/{t_d[0].strftime('%Y%m%d')}",
                   f"/sys/mis/{mid}/{t_d[1].strftime('%Y%m%d')}", f"/sys/mis/{mid}/{t_d[2].strftime('%Y%m%d')}",
                   f"/sys/mis/{mid}/{t_d[3].strftime('%Y%m%d')}", f"/sys/mis/{mid}/{t_d[4].strftime('%Y%m%d')}",
                   f"/sys/mis/{mid}/{t_d[5].strftime('%Y%m%d')}", f"/sys/mis/{mid}/{t_d[6].strftime('%Y%m%d')}",
                   f"/sys/mis/{mid}/{t_d[7].strftime('%Y%m%d')}", ]
    title_wday = ['None', 'None', t_d[0].weekday(), t_d[1].weekday(), t_d[2].weekday(), t_d[3].weekday(),
                  t_d[4].weekday(), t_d[5].weekday(), t_d[6].weekday(), t_d[7].weekday(), ]

    for name, link, wday in zip(title_names, title_links, title_wday):
        item = {}
        item['name'] = name
        if is_adm:
            item['link'] = link
        else:
            item['link'] = "None"
        if wday == 5:
            item['dcolor'] = SAT
        elif wday == 6:
            item['dcolor'] = SUN
        else:
            item['dcolor'] = None
        title.append(item)
    mis_obj = get_object_or_404(Mis, id=mid)
    context = {
        "mis": mis_obj,
        "user": request.user.username,
        "timezone_now": timezone.now(),
        "title": title,
        "title_links": title_links,
        "heartbeat": heartbeat,
        "calls": calls,
        "noanswer": noanswer,
        "fake": fake,
        "advise": advise,
        "refuse": refuse,
        "crew_call": crew_call,
        "ed_call": ed_call,
        "hostname": settings.HOSTNAME,
    }
    return context


@login_required(login_url='/login/')
@user_passes_test(is_sys, login_url='/', redirect_field_name=None)
def syshome(request):
    context = get_syshome_context(request)
    context["refresh"] = True
    return render(request, "home.html", context)


def get_syshome_context(request):
    mis_list = []
    context = {}
    today_list = getCallToday()
    #yesterday_list = getCallYesterday()
    call_av_list = getCallAv()
    er_av_list = getErAv()
    ed_av_list = getEdAv()
    cars_list = getCars()
    facility_list = getFacility()
    staff_list = getStaff()
    # qs = Mis.objects.all().order_by('id')
    for today_item, call_av_item, er_av_item, ed_av_item, facility_item, staff_item, car_item in zip(
            today_list, call_av_list, er_av_list, ed_av_list, facility_list, staff_list, cars_list
    ):
        mis_item = {}
        mis_item['id'] = today_item["id"]
        mis_item['mis_name'] = today_item["mis_name"]
        if today_item["call_num"] is not None:
            mis_item['today'] = today_item["call_num"]
        else:
            mis_item['today'] = ""

        if call_av_item["call_num"] is not None:
            mis_item['call_av'] = call_av_item["call_num"]
        else:
            mis_item['call_av'] = ""

        ###########
        if er_av_item["call_num"] is not None:
            mis_item['er_av'] = er_av_item["call_num"]  # "{:.1f}%".format(ytd_pp)
            if call_av_item["call_num"] is not None and call_av_item["call_num"] != 0:
                mis_item['er_avp'] = "{:.1f}%".format(er_av_item["call_num"] / call_av_item["call_num"] * 100)
            else:
                mis_item['er_avp'] = ""
        else:
            mis_item['er_av'] = ""
            mis_item['er_avp'] = ""

        ###########
        if ed_av_item["call_num"] is not None:
            mis_item['ed_av'] = ed_av_item["call_num"]  # "{:.1f}%".format(ytd_pp)
            mis_item['ed_avp'] = ""
            if ed_av_item["call_num"] is not None and er_av_item["call_num"] != 0:
                # logging.error(f'ed_av_item["call_num"]: {ed_av_item["call_num"]}')
                # logging.error(f'er_av_item["call_num"]: {er_av_item["call_num"]}')
                mis_item['ed_avp'] = "{:.1f}%".format(ed_av_item["call_num"] / er_av_item["call_num"] * 100)
        else:
            mis_item['ed_av'] = ""
            mis_item['ed_avp'] = ""

        if facility_item["facility_num"] is not None:
            mis_item['facility'] = facility_item["facility_num"]
        else:
            mis_item['facility'] = ""
        if staff_item["staff_num"] is not None:
            mis_item['staff'] = staff_item["staff_num"]
        else:
            mis_item['staff'] = ""

        if car_item["car_num"] is not None:
            mis_item['car'] = car_item["car_num"]
        else:
            mis_item['car'] = ""

        # mis_item['status'] = "00ff00"
        mis_item['status'] = GREEN
        if ((today_item["date_modified"] - today_item["timestamp"]) / timedelta(seconds=1)) > 1:
            # if ((qs_today_item.date_modified - qs_today_item.timestamp) / timedelta(seconds=1)) > 1:
            mis_item['mis_heartbeat'] = today_item["date_modified"]  # date_modified
        else:
            mis_item['mis_heartbeat'] = today_item["mis_heartbeat"]  # mis_heartbeat
        # mis_item['mis_heartbeat'] = qs_item.mis_heartbeat
        if mis_item['mis_heartbeat'] is None:
            mis_item['status'] = GRAY
            # mis_item['mis_heartbeat'] = 'Не підєднана'
        else:
            timedif = (timezone.now() - today_item["date_modified"]).seconds
            # timedif = (timezone.now() - qs_today_item.date_modified).seconds
            if timedif > 60:
                mis_item['status'] = "FCE6AD"
                # mis_item['status'] = "F0F000"
            if timedif > 240:
                mis_item['status'] = RED
                # mis_item['status'] = "ff00000"

        mis_list.append(mis_item)
    context = {
        "user": request.user.username,
        "mis_list": mis_list,
        "timezone_now": timezone.now(),
    }
    return context


def getEdCallSum(mis_id, t_d, ytd):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    qx_str = "select count(distinct callcard_callcard.id), date(callcard_callcard.start_datetime) from callcard_callcard \
        inner join callcard_callrecord on (callcard_callrecord.card_id_id=callcard_callcard.id) \
        where callcard_callrecord.call_station_id=11 \
        and callcard_callcard.mis_id_id = %s \
        and callcard_callcard.start_datetime > now() - interval '8 day' \
        group by date(callcard_callcard.start_datetime) \
        order by date(callcard_callcard.start_datetime) desc"
    q_str = "select count(distinct callcard_callcard.id) from callcard_callcard \
        inner join callcard_callrecord on callcard_callcard.id=callcard_callrecord.card_id_id \
        where callcard_callcard.mis_id_id = %s \
        and callcard_callrecord.call_station_id = 11 \
        and callcard_callcard.start_datetime >= %s"

    # select count(id) from callcard_callrecord \
    #     where call_station_id = 11 and mis_id_id = %s and date_part('year', timestamp) = date_part('year', now())"
    cursor.execute(q_str, [mis_id, '2019-01-01'])
    cursor1.execute(qx_str, [mis_id])
    qs_edCallSum = cursor.fetchall()
    qs_edxCallSum = cursor1.fetchall()
    edCallSum = {}
    edCallSum["YTD"] = qs_edCallSum[0][0]
    edCallxSum = {}
    for q_edxCallSum in qs_edxCallSum:
        edCallxSum[q_edxCallSum[1]] = q_edxCallSum[0]
    edCallSum["dates"] = edCallxSum
    if ytd:
        ytd_pp = edCallSum['YTD'] / ytd * 100
    else:
        ytd_pp = 0
    edCalls = [edCallSum['YTD'], "{:.1f}%".format(ytd_pp),
               edCallSum['dates'].get(t_d[0].date(), ""),
               edCallSum['dates'].get(t_d[1].date(), ""),
               edCallSum['dates'].get(t_d[2].date(), ""),
               edCallSum['dates'].get(t_d[3].date(), ""),
               edCallSum['dates'].get(t_d[4].date(), ""),
               edCallSum['dates'].get(t_d[5].date(), ""),
               edCallSum['dates'].get(t_d[6].date(), ""),
               edCallSum['dates'].get(t_d[7].date(), ""), ]
    return edCalls


def getCallTypeSum(mis_id, t_d, ytd, call_type):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    year_now = f'{timezone.now().year}-01-01'
    qx_str = "select count(*), date(start_datetime) from callcard_callcard \
        where call_result_id in %s and mis_id_id = %s and start_datetime > now() - interval '8 day' \
        group by date(start_datetime) \
        order by date(start_datetime) desc"
    q_str = "select count(id) from callcard_callcard \
        where call_result_id in %s and mis_id_id = %s and start_datetime >= %s"
    cursor.execute(q_str, [tuple(call_type), mis_id, year_now])
    cursor1.execute(qx_str, [tuple(call_type), mis_id])
    qs_fakeCallSum = cursor.fetchall()
    qs_fakexCallSum = cursor1.fetchall()
    fakeCallSum = {}
    fakeCallSum["YTD"] = qs_fakeCallSum[0][0]
    fakeCallxSum = {}
    for q_fakexCallSum in qs_fakexCallSum:
        fakeCallxSum[q_fakexCallSum[1]] = q_fakexCallSum[0]
    fakeCallSum["dates"] = fakeCallxSum
    if ytd:
        ytd_pp = fakeCallSum['YTD'] / ytd * 100
    else:
        ytd_pp = 0
    calls = [fakeCallSum['YTD'], "{:.1f}%".format(ytd_pp),
             fakeCallSum['dates'].get(t_d[0].date(), ""),
             fakeCallSum['dates'].get(t_d[1].date(), ""),
             fakeCallSum['dates'].get(t_d[2].date(), ""),
             fakeCallSum['dates'].get(t_d[3].date(), ""),
             fakeCallSum['dates'].get(t_d[4].date(), ""),
             fakeCallSum['dates'].get(t_d[5].date(), ""),
             fakeCallSum['dates'].get(t_d[6].date(), ""),
             fakeCallSum['dates'].get(t_d[7].date(), ""), ]
    return calls


def getCallSum(mis_id, t_d):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    year_now = f'{timezone.now().year}-01-01'
    qx_str = "select count(*), date(start_datetime) from callcard_callcard \
        where mis_id_id = %s and start_datetime > now() - interval '8 day' \
        group by date(start_datetime) \
        order by date(start_datetime) desc"
    q_str = "select count(id) from callcard_callcard \
        where mis_id_id = %s and start_datetime >= %s"
    cursor.execute(q_str, [mis_id, year_now])
    cursor1.execute(qx_str, [mis_id])
    qs_callSum = cursor.fetchall()
    qs_callxSum = cursor1.fetchall()
    callSum = {}
    callSum["YTD"] = qs_callSum[0][0]

    callxSum = {}
    for q_callxSum in qs_callxSum:
        callxSum[q_callxSum[1]] = q_callxSum[0]
    callSum["dates"] = callxSum
    calls = [callSum['YTD'], "100.00%",
             callSum['dates'].get(t_d[0].date(), ""),
             callSum['dates'].get(t_d[1].date(), ""),
             callSum['dates'].get(t_d[2].date(), ""),
             callSum['dates'].get(t_d[3].date(), ""),
             callSum['dates'].get(t_d[4].date(), ""),
             callSum['dates'].get(t_d[5].date(), ""),
             callSum['dates'].get(t_d[6].date(), ""),
             callSum['dates'].get(t_d[7].date(), ""), ]
    return calls, callSum["YTD"]


def getEdCallDay(mis_id, this_date):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    qx_str = "select count(distinct callcard_callcard.id), date_part('hour', callcard_callcard.start_datetime) as hour \
        from callcard_callcard \
        inner join callcard_callrecord on callcard_callcard.id=callcard_callrecord.card_id_id \
        where callcard_callrecord.call_station_id = 11 and callcard_callcard.mis_id_id = %s \
        and date(callcard_callcard.start_datetime) = %s \
        group by date_part('hour', callcard_callcard.start_datetime) \
        order by date_part('hour', callcard_callcard.start_datetime) asc"
    q_str = "select count(distinct callcard_callcard.id) from callcard_callcard \
        inner join callcard_callrecord on callcard_callcard.id=callcard_callrecord.card_id_id \
        where callcard_callcard.mis_id_id = %s and callcard_callrecord.call_station_id = 11 \
        and date(callcard_callcard.start_datetime) = %s"
    cursor.execute(q_str, (mis_id, date_s))
    cursor1.execute(qx_str, (mis_id, date_s))
    qs_edCallSum = cursor.fetchall()
    qs_edxCallSum = cursor1.fetchall()
    edCalls = []
    edCalls.append(qs_edCallSum[0][0])
    edCallxSum = {}
    for q_edxCallSum in qs_edxCallSum:
        edCallxSum[q_edxCallSum[1]] = q_edxCallSum[0]
    for hour in range(0, 24):
        edCalls.append(edCallxSum.get(hour, ""))
    return edCalls


def getCallTypeDay(mis_id, this_date, call_type):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    qx_str = "select count(*), date_part('hour', start_datetime) as hour \
        from callcard_callcard \
        where call_result_id in %s and mis_id_id = %s and date(start_datetime) = %s\
        group by date_part('hour', start_datetime) \
        order by date_part('hour', start_datetime) asc"
    q_str = "select count(id) from callcard_callcard \
        where call_result_id in %s and mis_id_id = %s and date(start_datetime) = %s"
    cursor.execute(q_str, (tuple(call_type), mis_id, date_s))
    cursor1.execute(qx_str, (tuple(call_type), mis_id, date_s))
    qs_fakeCallSum = cursor.fetchall()
    qs_fakexCallSum = cursor1.fetchall()
    crCalls = []
    crCalls.append(qs_fakeCallSum[0][0])
    fakeCallxSum = {}
    for q_fakexCallSum in qs_fakexCallSum:
        fakeCallxSum[q_fakexCallSum[1]] = q_fakexCallSum[0]
    for hour in range(0, 24):
        crCalls.append(fakeCallxSum.get(hour, ""))
    return crCalls


def getCallDay(mis_id, this_date):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    qx_str = "select count(*), date_part('hour', start_datetime) as hour \
        from callcard_callcard \
        where mis_id_id = %s and date(start_datetime) = %s\
        group by date_part('hour', start_datetime) \
        order by date_part('hour', start_datetime) asc"
    q_str = "select count(id) from callcard_callcard \
        where mis_id_id = %s and date(start_datetime) = %s"
    cursor.execute(q_str, (mis_id, date_s))
    cursor1.execute(qx_str, (mis_id, date_s))
    qs_callSum = cursor.fetchall()
    qs_callxSum = cursor1.fetchall()
    calls = []
    calls.append(qs_callSum[0][0])
    callxSum = {}
    for q_callxSum in qs_callxSum:
        callxSum[q_callxSum[1]] = q_callxSum[0]
    for hour in range(0, 24):
        calls.append(callxSum.get(hour, ""))
    return calls


def getOperatorOnDuty(mis_id, this_date, operator):
    cursor = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    t_b = time(00, 00, 00)
    t_e = time(23, 59, 59)
    start_datetime = datetime.combine(this_date, t_b)
    end_datetime = datetime.combine(this_date, t_e)
    dpv_str = "select operator_id_id, t2.mis_staff_id, t2.first_name, start_datetime from callcard_callrecord \
    left join (select id, mis_staff_id, first_name from mis_staff) t2 \
    on callcard_callrecord.operator_id_id = t2.id \
    where mis_id_id = %s and call_station_id= %s and \
    callcard_callrecord.start_datetime between %s::timestamp and %s::timestamp \
    order by callcard_callrecord.start_datetime asc"

    cursor.execute(dpv_str, (mis_id, operator, start_datetime, end_datetime))
    qs_dpv = cursor.fetchall()
    dpv = {}
    dpv_id = []
    for q_dpv in qs_dpv:
        dpv_detail = dpv.get(q_dpv[1], None)
        if dpv_detail is None:
            dpv_detail = {}
            dpv_id.append(q_dpv[0])
        call_start = q_dpv[3]
        hour_c = dpv_detail.get(call_start.hour, 0)
        hour_c += 1
        dpv_detail[call_start.hour] = hour_c
        dpv[q_dpv[1]] = dpv_detail

    res = []
    dpv_total = []
    for hour in range(0, 24):
        hour_c = 0
        for dpv_item in dpv.items():
            if dpv_item[1].get(hour, 0):
                hour_c += 1
        dpv_total.append(hour_c)
    res.append(dpv_total)

    for dpv_item, dpv_id in zip(dpv.items(), dpv_id):
        dpv_line = []
        dpv_line.append([dpv_item[0], dpv_id])
        dpv_hours = dpv_item[1]
        for hour in range(0, 24):
            dpv_line.append([dpv_hours.get(hour, ""), "/"])
        res.append(dpv_line)
    return res


def getCrewOnDuty(mis_id, this_date):
    cursor = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    t = time(0, 1)
    end_time = datetime.combine(this_date, t)
    qx_str = "select id, crew_id, mis_crew_id, shift_start, shift_end, is_active \
            from crew_crew where mis_id_id = %s \
            and date(shift_start) <= %s \
            and shift_end  >= %s \
            order by id asc"
    cursor.execute(qx_str, (mis_id, date_s, end_time))
    qs_crews = cursor.fetchall()
    crew_duty = []
    crew_count = {}
    crew_count_f = {}
    for q_crew in qs_crews:
        color = GRAY
        if q_crew[5] == True:
            color = GREEN
        crew = []
        crew_1 = {}
        crew_1["name"] = q_crew[1]
        crew_1["color"] = color
        crew.append(crew_1)
        crew_2 = {}
        crew_2["name"] = q_crew[2]
        crew_2["color"] = color
        crew.append(crew_2)
        crew_i = {}
        shift_start = q_crew[3]
        shift_end = q_crew[4]
        # this_date
        for hour in range(0, 24):
            hour_crew = crew_count.get(hour, {})
            hour_c = crew_count_f.get(hour, 0)
            crew_i = {}
            this_time_s = time(hour, 59, 59)
            this_hour_s = datetime.combine(this_date, this_time_s)
            this_time_e = time(hour, 0)
            this_hour_e = datetime.combine(this_date, this_time_e)

            if shift_start <= this_hour_s and shift_end >= this_hour_e:
                mis_crew = hour_crew.get(q_crew[2], None)
                if mis_crew is None:
                    hour_crew[q_crew[2]] = 1
                    hour_c += 1

                crew_i["name"] = ""
                crew_i["color"] = GREEN
            else:
                crew_i["name"] = ""
                crew_i["color"] = GRAY

            # if shift_start <= this_hour_s and shift_end >= this_hour_e:
            #     hour_c += 1
            #     crew_i["name"] = ""
            #     crew_i["color"] = GREEN
            # else:
            #     crew_i["name"] = ""
            #     crew_i["color"] = GRAY

            crew_count[hour] = hour_crew
            crew.append(crew_i)
            crew_count_f[hour] = hour_c
        crew_duty.append(crew)
    crew_duty.append(crew_count_f)
    return crew_duty


def getHeartbeatDay(mis_id, this_date):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    date_s = this_date.strftime("%Y-%m-%d")
    qx_str = "select count(*), date_part('hour', timestamp) as hour \
        from heartbeat_heartbeat \
        where mis_id_id = %s and date(timestamp) = %s\
        group by date_part('hour', timestamp) \
        order by date_part('hour', timestamp) asc"
    q_str = "select count(id) from heartbeat_heartbeat \
        where mis_id_id = %s and date(timestamp) = %s"
    cursor.execute(q_str, (mis_id, date_s))
    cursor1.execute(qx_str, (mis_id, date_s))
    qs_hbSum = cursor.fetchall()
    qs_hbxSum = cursor1.fetchall()
    heartbeat = []
    heartbeat.append(qs_hbSum[0][0])
    hbxSum = {}
    for q_hbxSum in qs_hbxSum:
        hbxSum[q_hbxSum[1]] = q_hbxSum[0]
    for hour in range(0, 24):
        heartbeat.append(hbxSum.get(hour, ""))
    return heartbeat


def getHeartbeatSum(mis_id, t_d):
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    qx_str = "select count(*), date(timestamp) from heartbeat_heartbeat \
        where mis_id_id = %s and timestamp > now() - interval '8 day' \
        group by date(timestamp) \
        order by date(timestamp) desc"
    q_str = "select count(id) from heartbeat_heartbeat \
        where mis_id_id = %s and date_part('year', timestamp) = date_part('year', now())"
    cursor.execute(q_str, [mis_id])
    cursor1.execute(qx_str, [mis_id])
    qs_hbSum = cursor.fetchall()
    qs_hbxSum = cursor1.fetchall()
    hbSum = {}
    hbSum["YTD"] = qs_hbSum[0][0]
    hbxSum = {}
    for q_hbxSum in qs_hbxSum:
        hbxSum[q_hbxSum[1]] = q_hbxSum[0]
    hbSum["dates"] = hbxSum
    heartbeat = [hbSum['YTD'], "",
                 hbSum['dates'].get(t_d[0].date(), ""),
                 hbSum['dates'].get(t_d[1].date(), ""),
                 hbSum['dates'].get(t_d[2].date(), ""),
                 hbSum['dates'].get(t_d[3].date(), ""),
                 hbSum['dates'].get(t_d[4].date(), ""),
                 hbSum['dates'].get(t_d[5].date(), ""),
                 hbSum['dates'].get(t_d[6].date(), ""),
                 hbSum['dates'].get(t_d[7].date(), ""), ]
    return heartbeat


def getCallToday():
    cursor = connection.cursor()
    cursor.execute('select id, mis_name, timestamp, mis_heartbeat, date_modified, t2.call_c \
        from mis_mis left join \
        (select callcard_callcard.mis_id_id as call_id, Count(callcard_callcard.id) as call_c \
        from callcard_callcard \
        where date(callcard_callcard.start_datetime)=date(now()) \
        group by callcard_callcard.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id;')
    qs_today = cursor.fetchall()
    today_list = []
    for qs_today_item in qs_today:
        today_item = {}
        today_item["id"] = qs_today_item[0]
        today_item["mis_name"] = qs_today_item[1]
        today_item["timestamp"] = qs_today_item[2]
        today_item["mis_heartbeat"] = qs_today_item[3]
        today_item["date_modified"] = qs_today_item[4]
        today_item["call_num"] = qs_today_item[5]
        today_list.append(today_item)
    return today_list


def getCars():
    cursor = connection.cursor()
    cursor.execute("select id, t2.car_c from mis_mis left join \
        (select mis_cars.mis_id_id as car_id , Count(mis_cars.mis_id_id) as car_c \
        from mis_cars where is_active=true \
        group by mis_cars.mis_id_id) t2 on mis_mis.id = t2.car_id where mis_mis.is_active=True \
        order by mis_mis.id;")
    qs_staff = cursor.fetchall()
    staff_list = []
    for qs_staff_item in qs_staff:
        staff_item = {}
        staff_item["id"] = qs_staff_item[0]
        staff_item["car_num"] = qs_staff_item[1]
        staff_list.append(staff_item)
    return staff_list


def getStaff():
    cursor = connection.cursor()
    cursor.execute("select id, t2.call_c from mis_mis left join \
        (select mis_staff.mis_id_id as call_id , Count(mis_staff.mis_id_id) as call_c \
        from mis_staff where is_active=true \
        group by mis_staff.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id;")
    qs_staff = cursor.fetchall()
    staff_list = []
    for qs_staff_item in qs_staff:
        staff_item = {}
        staff_item["id"] = qs_staff_item[0]
        staff_item["staff_num"] = qs_staff_item[1]
        staff_list.append(staff_item)
    return staff_list


def getFacility():
    cursor = connection.cursor()
    cursor.execute("select id, t2.call_c from mis_mis left join \
        (select mis_facility.mis_id_id as call_id , Count(mis_facility.mis_id_id) as call_c \
        from mis_facility where is_active=true \
        group by mis_facility.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id;")
    qs_facility = cursor.fetchall()
    facility_list = []
    for qs_facility_item in qs_facility:
        facility_item = {}
        facility_item["id"] = qs_facility_item[0]
        facility_item["facility_num"] = qs_facility_item[1]
        facility_list.append(facility_item)
    return facility_list


def getCallAv():
    cursor = connection.cursor()
    cursor.execute("select id, t2.call_c from mis_mis left join \
        (select callcard_callcard.mis_id_id as call_id , Count(callcard_callcard.id) as call_c \
        from callcard_callcard \
        where date(callcard_callcard.start_datetime) <= date(TIMESTAMP 'yesterday') \
        and date(callcard_callcard.start_datetime) >= date(now() - interval '7 day') \
        group by callcard_callcard.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id;")
    qs_call_av = cursor.fetchall()
    call_av_list = []
    for qs_av_item in qs_call_av:
        call_av_item = {}
        call_av_item["id"] = qs_av_item[0]
        if qs_av_item[1]:
            call_av_item["call_num"] = round(qs_av_item[1] / 7)
        else:
            call_av_item["call_num"] = qs_av_item[1]
        call_av_list.append(call_av_item)
    return call_av_list


def getErAv():
    cursor = connection.cursor()
    cursor.execute("select id, t2.call_c from mis_mis left join \
        (select callcard_callcard.mis_id_id as call_id , count(callcard_callcard.id) as call_c \
        from callcard_callcard \
        where date(callcard_callcard.start_datetime) <= date(TIMESTAMP 'yesterday') \
        and date(callcard_callcard.start_datetime) >= date(now() - interval '7 day') \
        and call_result_id = 3 \
        group by callcard_callcard.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id")
    qs_call_av = cursor.fetchall()
    call_av_list = []
    for qs_av_item in qs_call_av:
        call_av_item = {}
        call_av_item["id"] = qs_av_item[0]
        if qs_av_item[1]:
            call_av_item["call_num"] = round(qs_av_item[1] / 7)
        else:
            call_av_item["call_num"] = qs_av_item[1]
        call_av_list.append(call_av_item)
    return call_av_list


def getEdAv():
    cursor = connection.cursor()
    cursor.execute("select id, t2.call_c from mis_mis left join \
        (select callcard_callcard.mis_id_id as call_id , count(distinct callcard_callcard.id) as call_c \
        from callcard_callcard \
        inner join callcard_callrecord on callcard_callcard.id=callcard_callrecord.card_id_id \
        where callcard_callrecord.call_station_id = 11 \
        and date(callcard_callcard.start_datetime) <= date(TIMESTAMP 'yesterday') \
        and date(callcard_callcard.start_datetime) >= date(now() - interval '7 day') \
        group by callcard_callcard.mis_id_id) t2 on mis_mis.id = t2.call_id where mis_mis.is_active=True \
        order by mis_mis.id")
    qs_call_av = cursor.fetchall()
    call_av_list = []
    for qs_av_item in qs_call_av:
        call_av_item = {}
        call_av_item["id"] = qs_av_item[0]
        if qs_av_item[1]:
            call_av_item["call_num"] = round(qs_av_item[1] / 7)
        else:
            call_av_item["call_num"] = qs_av_item[1]
        call_av_list.append(call_av_item)
    return call_av_list


def mis_logout(request):
    logging.info('mis_logout: ', request.user.id)
    sys_logout(request)
    return HttpResponseRedirect('/login/')
