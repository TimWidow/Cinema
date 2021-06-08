from os import startfile
from django.shortcuts import redirect, HttpResponse, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator
from django.contrib import auth
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
from films.models import Film, Session, Ticket, Booking, Sell
from kinouser.models import Kinouser
from guest_review.models import GuestReview, AdminReview
from review.models import Review
from .forms import UserCreateForm


def contact(request):
    args = dict()
    args['user'] = request.user
    return render(request, 'contact.html', args)


@csrf_protect
def guest(request):
    args = dict()
    args['user'] = request.user
    all_reviews = reviews = []

    for _review in GuestReview.objects.all():
        reviews.append(_review)
        try:
            reviews.append(AdminReview.objects.get(guestReview=_review))
        except AdminReview.DoesNotExist:
            pass

        all_reviews.append(reviews.copy())
        reviews.clear()
    args['reviews'] = all_reviews

    if request.POST:
        if request.POST.get('admin', '') == 'false':
            GuestReview(name=request.POST.get('name', ''), email=request.POST.get('email', ''),
                        text=request.POST.get('comment', ''), date=datetime.now().date()).save()
        elif request.POST.get('admin', '') == 'true':
            AdminReview(
                text=request.POST.get('comment', ''),
                guestReview=GuestReview.objects.get(id=request.POST.get('guest_id', ''))
            ).save()

        return redirect('/guest/')

    return render(request, 'guest.html', args)


def logout(request):
    auth.logout(request)
    return redirect("/")


@csrf_protect
def login(request):
    args = dict()
    if request.POST:
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            args['user'] = request.user

            return redirect("/")
        else:
            args['login_error'] = "Неверный логин"
            return render(request, 'signin.html', args)
    else:
        return render(request, 'signin.html', args)


@csrf_protect
def register(request):
    args = dict()
    args['form'] = UserCreateForm()
    if request.POST:
        new_user_form = UserCreateForm(request.POST)
        if new_user_form.is_valid():
            new_user_form.save()
            new_user = auth.authenticate(username=new_user_form.cleaned_data['email'],
                                         password=new_user_form.cleaned_data['password2'])
            auth.login(request, new_user)

            return redirect('/')

        else:
            args['reg_error'] = 'Error.'
            args['form'] = new_user_form
    return render(request, 'register.html', args)


def main(request, url_date=datetime.today().date(), page_number=1):
    tmp_args, tmp_args2 = dict(), dict()

    tmp_args['Понедельник'] = tmp_args2['Pon'] = 1
    tmp_args['Вторник'] = tmp_args2['Vt'] = 2
    tmp_args['Среда'] = tmp_args2['Sr'] = 3
    tmp_args['Четверг'] = tmp_args2['Cht'] = 4
    tmp_args['Пятница'] = tmp_args2['Pyat'] = 5
    tmp_args['Суббота'] = tmp_args2['Sub'] = 6
    tmp_args['Воскресенье'] = tmp_args2['Voskr'] = 7

    dates_for_weekday = dates = []
    dates.append((datetime.today().date().strftime('%Y-%m-%d'),
                  datetime.isoweekday(datetime.today().date())))
    dates_for_weekday.append((datetime.today().date().strftime('%Y-%m-%d'),
                              datetime.isoweekday(datetime.today().date())))

    for i in range(1, 7):
        dates_for_weekday.append(
            ((datetime.today().date() + timedelta(days=i)).strftime('%Y-%m-%d'),
             datetime.isoweekday((datetime.today().date() + timedelta(days=i)))))
        dates.append(
            ((datetime.today().date() + timedelta(days=i)).strftime('%Y-%m-%d'),
             datetime.isoweekday((datetime.today().date() + timedelta(days=i)))))

    def reverse_dictionary(dictionary):
        new_dictionary = dict()

        for key in dictionary:
            new_dictionary.setdefault(dictionary[key], key)
        return new_dictionary

    def fill_dates(_args, second_args, _dates):
        new_args = reverse_dictionary(_args)
        new_second_args = reverse_dictionary(second_args)
        for one_date in range(len(_dates)):
            _args[new_args[_dates[one_date][1]]] = _dates[one_date][0]
            second_args[new_second_args[_dates[one_date][1]]] = _dates[one_date][0]
        return _args, second_args

    args, args2 = fill_dates(tmp_args, tmp_args2, dates)

    args.update(args2)
    args['user'] = request.user
    args['date_url'] = str(url_date)
    args['for_date'] = datetime.strptime(str(url_date), '%Y-%m-%d').date()
    if isinstance(url_date, str):
        args['weekday'] = datetime.isoweekday(datetime.strptime(url_date, '%Y-%m-%d').date())
    else:
        args['weekday'] = datetime.isoweekday(url_date)
    sessions = Session.objects.filter(date=str(url_date))
    a = b = []

    for _session in sessions:
        if _session.film not in a:
            a.append(_session.film)
            b.append(_session)

    current_page = Paginator(b, 3)
    args['sessions'] = current_page.page(page_number)
    if len(b) == 0:
        args['no_sessions'] = True
    return render(request, 'main.html', args)


def my_kino(request):
    args = dict()
    args['user'] = request.user
    return render(request, 'my_kino.html', args)


def price(request):
    args = dict()
    args['user'] = request.user
    return render(request, 'price.html', args)


def session(request, name=''):
    args = dict()
    session_data = {}
    args['user'] = request.user
    film = Session.objects.filter(film__url_name=name)

    if film:
        sessions = Session.objects.filter(film__url_name=name,
                                          date__gt=(datetime.today().date() - timedelta(days=1)))
        args['sessions'] = sessions

        a = 0
        for i in range(10):
            date = datetime.today().date() + timedelta(days=a)
            a += 1
            if Session.objects.filter(film__url_name=name, date=date):
                session_data[str(date)] = []
                if (len(Session.objects.filter(film__url_name=name, date=date))) > 1:
                    for i_ in range(len(Session.objects.filter(film__url_name=name, date=date))):
                        if Session.objects.filter(film__url_name=name, date=date)[i_].date == datetime.today().date():
                            session_data[str(date)].append(
                                'Время сеанса : ' + str(
                                    Session.objects.filter(film__url_name=name, date=date)[i_].time))
                            session_data[str(date)].append(
                                Session.objects.filter(film__url_name=name, date=date)[i_].price)
                            session_data[str(date)].append(
                                'session_id=' + str(Session.objects.filter(film__url_name=name, date=date)[i_].id))
                else:
                    if Session.objects.filter(film__url_name=name, date=date)[0].date >= datetime.today().date():
                        session_data[str(date)].append(
                            'Время сеанса : ' + str(Session.objects.filter(film__url_name=name, date=date)[0].time))
                        session_data[str(date)].append(Session.objects.filter(film__url_name=name, date=date)[0].price)
                        session_data[str(date)].append(
                            'session_id=' + str(Session.objects.filter(film__url_name=name, date=date)[0].id))

        args['film'] = Film.objects.filter(url_name=name)[0]
        args['session_data'] = session_data

        return render(request, 'session.html', args)

    return redirect('/')


@csrf_exempt
def buy(request, session_id):
    args = dict()
    if request.method == 'POST':
        user = request.user
        if request.POST.get('service', ) == 'buy':
            session_id = Session.objects.get(id=request.POST.get('session_id', ''))
            new_tickets = request.POST.get('tickets', '')[:-1]

            for i in new_tickets.split(','):
                ticket = Ticket(row=i.split(':')[0],
                                seat=i.split(':')[1],
                                session_id=session_id, price=i.split(':')[2])
                ticket.save()
                user.tickets.add(ticket)

            return HttpResponse('ok', content_type='text/html')

        elif request.POST.get('service', ) == 'booking':
            session_id = Session.objects.get(id=request.POST.get('session_id', ''))
            new_tickets = request.POST.get('tickets', '')[:-1]
            name_user = request.user.firstname + " " + request.user.lastname

            for i in new_tickets.split(','):
                ticket = Booking(row=i.split(':')[0], seat=i.split(':')[1],
                                 session_id=session_id, forname=name_user,
                                 price=i.split(':')[2])
                ticket.save()
                user.bron.add(ticket)

            return HttpResponse('ok', content_type='text/html')
    else:
        _session = Session.objects.filter(id=session_id)
        args['user'] = request.user
        args['session'] = _session[0]
        red_ticket = ''
        black_ticket = ''
        for i in Ticket.objects.filter(seans_id=session_id):
            red_ticket += (str(i.row) + ',' + str(i.seat)) + ";"

        for i in Booking.objects.filter(seans_id=session_id):
            black_ticket += (str(i.row) + ',' + str(i.seat)) + ";"

        prices = _session[0].price.split(',')
        price1, price2 = prices[0], prices[1]
        args['price1'] = price1
        args['price2'] = price2
        args['red_ticket'] = red_ticket
        args['black_ticket'] = black_ticket
        if request.user.is_authenticated():
            args['user_name'] = request.user.firstname + " " + request.user.lastname

        return render(request, 'buy_window.html', args)


def soon(request, page_number=1):
    args = dict()
    args['user'] = request.user

    films = Film.objects.filter(in_theatre__gt=(datetime.today().date()) + timedelta(days=30))
    current_page = Paginator(films, 3)
    args['films'] = current_page.page(page_number)

    return render(request, 'soon.html', args)


def trailer(request, name=''):
    args = dict()
    args['user'] = request.user

    film = Film.objects.filter(url_name=name)
    if film:
        args['films'] = film
        args['film'] = film[0]
        return render(request, 'trailer.html', args)

    return redirect('/')


@csrf_protect
def review(request, name=''):
    args = dict()
    args['user'] = request.user
    args['film'] = Film.objects.filter(url_name=name)[0]
    args['comment'] = Review.objects.filter(film__url_name=name)
    if request.method == 'POST':
        Review(name=request.POST.get('name', ''),
               email=request.POST.get('email', ''),
               text=request.POST.get('comment', ''),
               film=Film.objects.get(url_name=name),
               date=datetime.now().date()).save()

        return render(request, 'review.html', args)
    else:
        if Film.objects.filter(url_name=name):
            return render(request, 'review.html', args)

    return redirect('/')


@csrf_exempt
def test_buy(request):
    session_id = Session.objects.get(id=request.POST.get('session_id', ''))
    new_tickets = request.POST.get('tickets', '')[:-1]

    for i in new_tickets.split(','):
        Ticket(row=i[0], seat=i[2], seans_id=session_id)

    return HttpResponse('ok', content_type='text/html')


def create_ticket(ticket):
    c = canvas.Canvas(settings.MEDIA_ROOT + "tickets.pdf", pagesize=(607, 265))

    c.drawImage(image="static/img/ticket.png", x=0, y=0)
    pdfmetrics.registerFont(TTFont('font', 'Arial.TTF'))
    pdfmetrics.registerFont(TTFont('test', 'static/fonts/BuxtonSketch.ttf'))
    c.setFont("font", 20)
    c.drawString(130, 170, 'Место в зале:')
    c.drawString(280, 170, 'Ряд: ' + str(ticket.row) + ',')
    c.drawString(360, 170, 'Место: 15' + str(ticket.seat))
    c.setFont("test", 28)
    c.drawString(130, 230, ticket.session_id.film.name)
    c.setFont("font", 21)
    c.drawString(130, 120, str(ticket.session_id.date))
    c.drawString(350, 120, ticket.session_id.time)
    c.setFont("font", 25)
    c.drawString(30, 50, 'Цена: ' + str(ticket.price))
    c.setFont("font", 20)
    c.drawString(520, 230, str(ticket.id))

    c.showPage()

    c.save()

    startfile(settings.MEDIA_ROOT + "tickets.pdf")


def print_ticket(request):
    admin = 'ticket_true'
    try:
        ticket = Ticket.objects.get(id=request.POST.get('id_ticket', ''))
        create_ticket(ticket)
    except Exception as e:
        print(e)
        admin = 'ticket_false'

    return cabinet(request, admin=admin)


def cabinet(request, page_number=1, admin='0'):
    args = dict()

    user = request.user
    args['user'] = user
    args['admin'] = admin

    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if not request.user.is_superuser:

            dates = []
            for ticket in user.tickets.all():
                dates.append(Session.objects.get(id=ticket.session_id.id).date)

            for booking in user.booking.all():
                dates.append(Session.objects.get(id=booking.session_id.id).date)
            dates.sort()
            dates.reverse()
            tickets = []

            for date in dates:
                for ticket in user.tickets.all():
                    if ticket.session_id.date == date:
                        if ticket not in tickets:
                            tickets.append(ticket)
                for booking in user.booking.all():
                    if booking.session_id.date == date:
                        if booking in tickets:
                            pass
                        else:
                            tickets.append(booking)

            current_page = Paginator(tickets, 6)
            args['tickets'] = current_page.page(page_number)

        else:
            if admin == 'tickets':
                args['user_name'] = Kinouser.objects.get(
                    bilets=Ticket.objects.get(id=request.POST.get('id_ticket', ''))).lastname
                args['session_name'] = Ticket.objects.get(id=request.POST.get('id_ticket', '')).session_id.film.name

            elif admin == 'ticket_false':
                args['error'] = 'Данного билета не существует. Проверьте правильность кода билета.'

            elif admin == 'session_true':
                my_session = Session.objects.get(id=request.POST.get('id_session', ''))
                args['session_date'] = my_session.date
                args['session_name'] = my_session.film.name
                args['session_time'] = my_session.time

            elif admin == 'session_false':
                args['session_false'] = 'На данный сеанс еще не проданы билеты.'

            elif admin == 'date_null' or admin == 'date_false':
                args['date_error'] = 'На данный день нет купленных билетов.'

    return render(request, 'cabinet.html', args)


def print_report(request, variety):
    if variety == 'session':
        admin = 'session_true'
        try:
            sells = [Sell.objects.get(seans_id=request.POST.get('id_session', ''))]
            create_report(sells, 'session')
        except Exception as e:
            print(e)
            admin = 'session_false'

        return cabinet(request, admin=admin)

    elif variety == 'date':
        admin = 'date_true'
        try:
            sells = Sell.objects.filter(seans_id__date=request.POST.get('date_session', ''))
            if sells.count() > 0:
                create_report(sells, 'date')
            else:
                admin = 'date_null'
        except Exception as e:
            print(e)
            admin = 'date_false'

        return cabinet(request, admin=admin)

    elif variety == 'interval':
        admin = 'interval_true'
        try:
            sells = Sell.objects.filter(
                seans_id__date__range=[request.POST.get('date1_session', ''),
                                       request.POST.get('date2_session', '')])
            create_report(sells, 'interval')
        except Exception as e:
            print(e)
            admin = 'interval_false'

        return cabinet(request, admin=admin)

    elif variety == 'week':
        admin = 'week_true'
        try:
            today = datetime.now().date()
            week = datetime.today().date() - timedelta(days=7)
            sells = Sell.objects.filter(seans_id__date__range=[week, today])

            create_report(sells, 'week')
        except Exception as e:
            print(e)
            admin = 'week_false'

        return cabinet(request, admin=admin)

    elif variety == 'month':
        admin = 'month_true'
        try:
            today = datetime.now().date()
            month = datetime.today().date() - timedelta(days=30)
            sells = Sell.objects.filter(seans_id__date__range=[month, today])

            create_report(sells, 'month')
        except Exception as e:
            print(e)
            admin = 'month_false'

        return cabinet(request, admin=admin)
    elif variety == 'half_year':
        admin = 'half_true'
        try:
            today = datetime.now().date()
            half_year = datetime.today().date() - timedelta(days=180)
            sells = Sell.objects.filter(seans_id__date__range=[half_year, today])
            create_report(sells, 'half_year')
        except Exception as e:
            print(e)
            admin = 'half_false'

        return cabinet(request, admin=admin)
    return cabinet(request)


def create_report(sells, variety):
    c = canvas.Canvas(settings.MEDIA_ROOT + "report.pdf")
    pdfmetrics.registerFont(TTFont('font', 'Arial.TTF'))
    pdfmetrics.registerFont(TTFont('test', 'static/fonts/BuxtonSketch.ttf'))
    c.setFont("test", 20)

    if variety == 'session':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра за сеанс')
    elif variety == 'date':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра по дате')
    elif variety == 'interval':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра по датам')
    elif variety == 'week':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра за неделю')
    elif variety == 'month':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра за месяц')
    elif variety == 'halfyear':
        c.drawString(130, 800, 'Отчет по продаже билетов кинотеатра за полгода')

    c.line(50, 780, 550, 780)
    c.line(50, 50, 550, 50)
    y = 740
    k = 1
    index = 1
    for i in sells:
        if k == 6:
            c.showPage()
            c.setFont("test", 20)
            c.drawString(160, 800, 'Отчёт по продаже билетов кинотеатра')
            c.line(50, 780, 550, 780)
            c.line(50, 50, 550, 50)
            k = 1
            y = 740
        c.drawString(50, y, str(index))
        c.drawString(100, y, i.session_id.film.name)
        c.drawString(160, y - 25, 'Дата сеанса:')
        c.drawString(160, y - 50, 'Время сеанса:')
        c.drawString(160, y - 75, 'Количество проданных билетов: ')
        c.drawString(160, y - 100, 'Общая выручка : ')
        c.drawString(465, y - 25, str(i.session_id.date))
        c.drawString(465, y - 50, str(i.session_id.time))
        c.drawString(465, y - 75, str(i.kol_bil))
        c.drawString(465, y - 100, str(i.summa) + " грн")
        y -= 140
        k += 1
        index += 1

    c.save()
    c.showPage()

    startfile(settings.MEDIA_ROOT + 'report.pdf')
