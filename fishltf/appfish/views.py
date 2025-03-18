from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, DetailView
from .models import *
from django.db.models import Sum
from collections import defaultdict
from datetime import datetime
from django.db.models import Count, Sum, F, Case, When, Value, OuterRef, Subquery, Window, Max, FloatField, IntegerField
from django.db.models.functions import Coalesce, Rank, Cast
import math
from django.shortcuts import get_object_or_404


def get_size_multiplier():
    return Case(

        # baitfish
        When(
            size='baitfish',
            then=Value(0.1) + (
                (F('weight') - Value(0.0))
                /
                (F('fish_species__baitfish') - Value(0.0))
            ) * (Value(1.0) - Value(0.2))
        ),
        # Small
        When(
            size='small',
            then=Value(1.0) + (
                (F('weight') - Value(0.0))
                /
                (F('fish_species__threshold_small') - Value(0.0))
            ) * (Value(2.0) - Value(1.0))
        ),
        # Medium
        When(
            size='medium',
            then=Value(2.0) + (
                (F('weight') - F('fish_species__threshold_small'))
                /
                (F('fish_species__threshold_medium') - F('fish_species__threshold_small'))
            ) * (Value(4.0) - Value(2.0))
        ),
        # Big
        When(
            size='big',
            then=Value(3.0) + (
                (F('weight') - F('fish_species__threshold_medium'))
                /
                (F('fish_species__threshold_big') - F('fish_species__threshold_medium'))
            ) * (Value(7.0) - Value(4.0))
        ),
        # Trophy
        When(
            size='trophy',
            then=Value(5.0) + (
                (F('weight') - F('fish_species__threshold_big'))
                /
                (F('fish_species__threshold_trophy') - F('fish_species__threshold_big'))
            ) * (Value(12.0) - Value(7.0))
                    ),
        # Record
        When(
            size='record',
            then=Value(12.0) + (
                (F('weight') - F('fish_species__threshold_trophy'))
                /
                F('fish_species__threshold_trophy')
            )
        ),
        default=Value(1.0),
        output_field=FloatField()
    )
    pass


def get_fish_details_for_session(user, date_catch):
    """
    Возвращает строку с информацией о том, сколько каких рыб было поймано в указанную дату.
    Например: "Щука: 3, Карась: 2"
    """
    qs = (
        Catch.objects
        .filter(user=user, date_catch=date_catch)
        .values('fish_species__name')
        .annotate(count=Count('id'))
    )
    details = ", ".join(f"{item['fish_species__name']}: {item['count']}" for item in qs)
    return details

def get_top5_fishing_sessions(user):
    """
    Возвращает словарь с двумя наборами:
      - 'current': данные за текущий сезон (фильтр по текущему году)
      - 'all_time': данные за все сезоны (без фильтрации по году)

    Каждый набор содержит два списка:
      - top_by_weight: топ-5 сессий по суммарному весу уловов.
      - top_by_count: топ-5 сессий по количеству уловов.

    Для каждой сессии (даты) возвращаются:
      - date_catch: дата рыбалки,
      - total_weight: суммарный вес уловов в этот день,
      - catch_count: количество уловов в этот день,
      - fish_details: строка с информацией вида "Рыба: количество", например, "Щука: 3, Карась: 2"
    """
    current_year = datetime.now().year

    # --- Топ-5 по суммарному весу для текущего сезона ---
    top_by_weight_current = list(
        Catch.objects.filter(user=user, date_catch__year=current_year)
        .values('date_catch')
        .annotate(total_weight=Sum('weight'), catch_count=Count('id'))
        .order_by('-total_weight')[:5]
    )
    # Добавляем детали по рыбам для каждой сессии
    for session in top_by_weight_current:
        session['fish_details'] = get_fish_details_for_session(user, session['date_catch'])

    # --- Топ-5 по количеству уловов для текущего сезона ---
    top_by_count_current = list(
        Catch.objects.filter(user=user, date_catch__year=current_year)
        .values('date_catch')
        .annotate(total_weight=Sum('weight'), catch_count=Count('id'))
        .order_by('-catch_count')[:5]
    )
    for session in top_by_count_current:
        session['fish_details'] = get_fish_details_for_session(user, session['date_catch'])

    # --- Топ-5 по суммарному весу за все сезоны ---
    top_by_weight_all = list(
        Catch.objects.filter(user=user)
        .values('date_catch')
        .annotate(total_weight=Sum('weight'), catch_count=Count('id'))
        .order_by('-total_weight')[:5]
    )
    for session in top_by_weight_all:
        session['fish_details'] = get_fish_details_for_session(user, session['date_catch'])

    # --- Топ-5 по количеству уловов за все сезоны ---
    top_by_count_all = list(
        Catch.objects.filter(user=user)
        .values('date_catch')
        .annotate(total_weight=Sum('weight'), catch_count=Count('id'))
        .order_by('-catch_count')[:5]
    )
    for session in top_by_count_all:
        session['fish_details'] = get_fish_details_for_session(user, session['date_catch'])

    return {
        'current': {
            'top_by_weight': top_by_weight_current,
            'top_by_count': top_by_count_current,
        },
        'all_time': {
            'top_by_weight': top_by_weight_all,
            'top_by_count': top_by_count_all,
        }
    }



def get_biggest_fish(user, all_time=False):

    current_year = datetime.now().year
    catch_filter = {} if all_time else {'date_catch__year': current_year}

    # 1. Получаем для данного пользователя максимальный вес по каждому виду рыбы
    user_biggest_fish = (
        Catch.objects
        .filter(user=user, **catch_filter)
        .values('fish_species__name')
        .annotate(max_weight=Coalesce(Max('weight'), Value(0)))
    )

    fish_rankings = {}
    for fish in user_biggest_fish:
        species = fish['fish_species__name']
        user_max_weight = fish['max_weight']

        # 2. Получаем запись с максимальным весом для данного вида у пользователя, чтобы взять фото трофея
        user_best_catch = (
            Catch.objects
            .filter(user=user, fish_species__name=species, **catch_filter)
            .order_by('-weight')
            .first()
        )
        image_url = ''
        if user_best_catch and user_best_catch.image:
            image_url = user_best_catch.image.image.url

        # 3. Формируем ранжирование: для данного вида получаем максимальный вес для каждого пользователя
        all_fish_ranking = list(
            Catch.objects
            .filter(fish_species__name=species, **catch_filter)
            .values('user')
            .annotate(max_weight=Coalesce(Max('weight'), Value(0)))
            .order_by('-max_weight')
        )

        # 4. Определяем место (ранг) пользователя среди всех по этому виду
        rank = None
        for i, record in enumerate(all_fish_ranking, start=1):
            if abs(float(record['max_weight']) - float(user_max_weight)) < 1e-6:
                rank = i
                break
        if rank is None:
            rank = '-'

        fish_rankings[species] = {
            'max_weight': user_max_weight,
            'rank': rank,
            'image_url': image_url,
        }

    return fish_rankings



def get_fishermen_stats(all_time=False,  season_filter=None, current_depth=0):
    """
    Рассчитывает статистику по рыбакам с использованием get_size_multiplier для вычисления базовых очков.
    
    Итоговые баллы (total_points) вычисляются по формуле:
      total_points = base_points
         + бонус за трофеи
         + бонус за общий вес сезона (топ-5)
         + бонус за общее количество уловов (топ-5)
         - штраф, зависящий от соотношения количества сессий и общего количества уловов,
           с коэффициентом, зависящим от наиболее часто встречаемого размера улова.
           
    При этом базовые очки для каждого улова = fish_species.point * multiplier,
    где multiplier вычисляется через get_size_multiplier.
    Итоговые баллы округляются вверх до целого числа.
    """
    if season_filter is None:
        season_filter = {} if all_time else {'date_catch__year': datetime.now().year}

    # Защита от рекурсии
    if current_depth >= 2:
        return []
    
    # Получаем всех пользователей с профилем
    users = list(User.objects.filter(profile__isnull=False).select_related('profile'))
    stats_list = []

    # Коэффициенты для штрафа по размеру улова
    size_coeff_map = {
        'baitfish': 6,
        'small': 5,
        'medium': 4,
        'big': 3,
        'trophy': 2,
        'record': 1,
    }

    # Получаем список всех сезонов (годов)
    seasons = Catch.objects.dates('date_catch', 'year').distinct()

    for user in users:
        # Проверяем, есть ли у пользователя хотя бы одна рыбалка
        has_catches = Catch.objects.filter(user=user, **season_filter).exists()
        if not has_catches:
            stats_list.append({
                'user': user,
                'base_points': 0,
                'total_catches': 0,
                'total_weight': 0,
                'total_fishing_days': 0,
                'bonus_trophy': 0,
                'bonus_weight': 0,
                'bonus_count': 0,
                'penalty': 0,
                'total_points': 0,
                'place': None,
                'season_history': [],
            })
            continue

        # Получаем все уловы пользователя
        user_catches = list(
            Catch.objects.filter(user=user, **season_filter)
            .annotate(multiplier=get_size_multiplier())
        )

        # Разделяем уловы на "baitfish" и остальные
        non_bait_catches = [c for c in user_catches if c.size != "baitfish"]
        baitfish_catches = [c for c in user_catches if c.size == "baitfish"]

        # Базовые очки: учитываем все уловы (включая "baitfish")
        base_points = sum(c.fish_species.point * c.multiplier for c in user_catches)

        # total_catches и total_weight: учитываем только non-baitfish
        total_catches = len(non_bait_catches)
        total_weight = sum(c.weight for c in non_bait_catches)
        total_fishing_days = len({c.date_catch for c in user_catches})

        # Бонус за трофеи (только для non-baitfish)
        bonus_trophy = 0
        user_biggest = get_biggest_fish(user, all_time=all_time)
        for species, data in user_biggest.items():
            rank = data.get('rank')
            if isinstance(rank, int) and 1 <= rank <= 5:
                fish = Fish.objects.filter(name=species).first()
                if fish:
                    bonus_trophy += fish.point * (6 - rank)

        # Сбор истории сезонов без рекурсии
        season_history = []
        current_season_year = datetime.now().year
        for season in seasons:
            season_year = season.year
            if season_year == current_season_year and not all_time:
                continue  # Пропускаем текущий сезон

            # Получаем статистику для конкретного сезона напрямую через БД
            season_catches = Catch.objects.filter(
                user=user,
                date_catch__year=season_year
            ).annotate(multiplier=get_size_multiplier())

            # Рассчитываем базовые очки для сезона
            season_base_points = sum(
                c.fish_species.point * c.multiplier 
                for c in season_catches
            )

            # Получаем все уловы для данного сезона
            catches = Catch.objects.filter(
                date_catch__year=season_year
            ).annotate(
                multiplier=get_size_multiplier()
            ).values('user', 'fish_species__point', 'multiplier')

            # Создаем словарь для хранения суммарных очков по пользователям
            user_points = defaultdict(int)

            # Рассчитываем total_points в Python
            for catch in catches:
                user_id = catch['user']
                points = catch['fish_species__point'] * catch['multiplier']
                user_points[user_id] += points

            # Преобразуем результат в список для ранжирования
            user_totals = [
                {'user': user_id, 'total': total}
                for user_id, total in user_points.items()
            ]

            # Добавляем ранг
            user_totals_with_rank = []
            for rank, item in enumerate(sorted(user_totals, key=lambda x: x['total'], reverse=True), start=1):
                item['rank'] = rank
                user_totals_with_rank.append(item)

            # Находим ранг для конкретного пользователя
            season_rank = next((item['rank'] for item in user_totals_with_rank if item['user'] == user.id), None)
          
            if season_rank is not None:
                season_history.append({
                    'year': season_year,
                    'place': season_rank,  # Используем season_rank напрямую
                    'total_points': math.ceil(season_base_points),
                })

        stats_list.append({
            'user': user,
            'base_points': base_points,
            'total_catches': total_catches,
            'total_weight': total_weight,
            'total_fishing_days': total_fishing_days,
            'bonus_trophy': bonus_trophy,
            'bonus_weight': 0,
            'bonus_count': 0,
            'penalty': 0,
            'total_points': 0,
            'place': None,
            'season_history': season_history,
        })

    # ===== Бонусы за вес и количество =====
    eligible_stats = [s for s in stats_list if s['total_catches'] > 0]

    # Бонус по весу (топ-5)
    stats_by_weight = sorted(eligible_stats, key=lambda x: x['total_weight'], reverse=True)
    for idx, stat in enumerate(stats_by_weight[:5], start=1):
        stat['bonus_weight'] = 10 * (6 - idx)

    # Бонус по количеству (топ-5)
    stats_by_count = sorted(eligible_stats, key=lambda x: x['total_catches'], reverse=True)
    for idx, stat in enumerate(stats_by_count[:5], start=1):
        stat['bonus_count'] = 10 * (6 - idx)

    # ===== Штраф за соотношение =====
    for stat in eligible_stats:
        if stat['total_catches'] > 0:
            size_counts = defaultdict(int)
            for c in Catch.objects.filter(user=stat['user'], **season_filter).exclude(size="baitfish"):
                size_counts[c.size] += 1
            if size_counts:
                most_common_size = max(size_counts, key=lambda k: size_counts[k])
                w_coeff = size_coeff_map.get(most_common_size, 0)
                penalty = (stat['total_fishing_days'] / stat['total_catches']) * w_coeff
            else:
                penalty = 0
        else:
            penalty = 0
        stat['penalty'] = penalty

        # Итоговые очки
        raw_total = (
            stat['base_points']
            + stat['bonus_trophy']
            + stat['bonus_weight']
            + stat['bonus_count']
            - stat['penalty']
        )
        stat['total_points'] = math.ceil(raw_total)

    # Сортируем и назначаем места
    eligible_stats_sorted = sorted(eligible_stats, key=lambda x: x['total_points'], reverse=True)
    for idx, stat in enumerate(eligible_stats_sorted, start=1):
        stat['place'] = idx

    final_stats = eligible_stats_sorted + [s for s in stats_list if s['total_catches'] == 0]




    return final_stats


def calculate_rating():
    """
    Финальная версия с проверкой на отсутствие рыбалок.
    """
    users = list(User.objects.all())
    overall_ratings = defaultdict(float)
    current_year = datetime.now().year

    # Собираем информацию о наличии рыбалок для каждого пользователя
    user_has_catches = {
        user.id: Catch.objects.filter(user=user).exists()
        for user in users
    }

    # ===== 1. Сезонный рейтинг =====
    seasons = Catch.objects.dates('date_catch', 'year').distinct()

    for season in seasons:
        season_year = season.year
        season_filter = {'date_catch__year': season_year}

        # Получаем статистику для сезона
        season_stats = get_fishermen_stats(all_time=False, season_filter=season_filter)

        # Участвовал ли пользователь в сезоне (даже если не поймал рыбу)
        season_users = {stat['user'].id for stat in season_stats}

        # Количество участников сезона
        participants = len(season_stats)

        # Начисляем баллы только если пользователь участвовал в сезоне
        for user in users:
            user_id = user.id
            if not user_has_catches[user_id]:
                continue  # Пропускаем пользователей без рыбалок вообще

            # Если пользователь есть в статистике сезона
            if user_id in season_users:
                stat = next(s for s in season_stats if s['user'].id == user_id)
                place = stat['place']
                season_score = (participants * 10) / place
                overall_ratings[user_id] += season_score

    # ===== 2. Бонус за трофеи =====
    for user in users:
        if not user_has_catches[user.id]:
            continue

        trophy_bonus = 0
        biggest = get_biggest_fish(user, all_time=True)
        for species, data in biggest.items():
            rank = data.get('rank')
            if isinstance(rank, int) and 1 <= rank <= 5:
                fish = Fish.objects.filter(name=species).first()
                if fish:
                    trophy_bonus += fish.point * (6 - rank)
        overall_ratings[user.id] += trophy_bonus

    # ===== 3. Бонусы за вес и количество =====
    all_time_stats = get_fishermen_stats(all_time=True)
    stats_dict = {stat['user'].id: stat for stat in all_time_stats}

    for user in users:
        if not user_has_catches[user.id]:
            continue

        stat = stats_dict.get(user.id)
        if stat:
            # Бонус за количество
            overall_ratings[user.id] += stat.get('bonus_count', 0)
            # Бонус за вес
            overall_ratings[user.id] += stat.get('bonus_weight', 0)

    # ===== 4. Соотношение рыба/рыбалки =====
    for user in users:
        if not user_has_catches[user.id]:
            continue

        stat = stats_dict.get(user.id)
        if stat and stat['total_fishing_days'] > 0:
            ratio = stat['total_catches'] / stat['total_fishing_days']
            overall_ratings[user.id] += ratio

    # ===== Фикс для пользователей без рыбалок =====
    for user in users:
        if not user_has_catches[user.id]:
            overall_ratings[user.id] = 0

    # ===== Формируем итоговый рейтинг =====
    final_ratings = []
    for user in users:
        final_rating = math.ceil(overall_ratings.get(user.id, 0))
        final_ratings.append((user, final_rating))

    return sorted(final_ratings, key=lambda x: x[1], reverse=True)




# Create your views here.
class HomePageView(TemplateView):
    template_name = 'home.html'  # имя файла шаблона с расширением, соответствующим djinga

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.all()  # Передаём все профили
        context['rating']  = calculate_rating()
        context['stats']  = get_fishermen_stats()
        context ['news']  = Catch.objects.order_by('-created_at')[:5]
        return context



class ProfilePageView (DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'


    def get_object(self):
        return get_object_or_404(Profile, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        user = user_profile.user  # Получаем пользователя

        # Статистика за текущий сезон
        season_stats = get_fishermen_stats(all_time=False)
        user_season_stats = next((f for f in season_stats if f['user'].id == user.id), None)

        # Статистика за всё время
        all_time_stats = get_fishermen_stats(all_time=True)
        user_all_time_stats = next((f for f in all_time_stats if f['user'].id == user.id), None)

        context.update({
            'user_season_stats': user_season_stats,
            'user_all_time_stats': user_all_time_stats,
            'rating': calculate_rating(),
            'biggest_fish_season': get_biggest_fish(user, all_time=False),
            'biggest_fish_all_time': get_biggest_fish(user, all_time=True),
            'top_sessions': get_top5_fishing_sessions(user),
            'stat': user_season_stats,
        })

        return context




class TrophyPageView (TemplateView):
    template_name = 'trophy.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_fish'] = Fish.objects.all()
        context['years'] = Catch.objects.dates('date_catch', 'year')  # список годов
        context['all_time_option'] = "all"

        # Функция для расчёта рейтинга внутри группы (по виду рыбы)
        def calculate_ranks(catches):
            grouped = defaultdict(list)
            for catch in catches:
                grouped[catch.fish_species.id].append(catch)

            ranked = []
            for fish_id, catches_list in grouped.items():
                # Сортируем по весу по убыванию
                sorted_catches = sorted(catches_list, key=lambda x: x.weight, reverse=True)
                for i, catch in enumerate(sorted_catches, 1):
                    ranked.append({
                        'catch': catch,
                        'rank': i,
                        'fish_slug': catch.fish_species.name,
                    })
            return ranked

        # 1. Общий рейтинг (все сезоны)
        all_catches = Catch.objects.all().order_by('fish_species', '-weight')
        overall_ranks = calculate_ranks(all_catches)
        context['all_time_catches'] = overall_ranks

        # 2. Сезонные рейтинги: словарь {год: [рейтинговые данные]}
        seasonal_ranks = {}
        for year in context['years']:
            catches_year = Catch.objects.filter(date_catch__year=year.year).order_by('fish_species', '-weight')
            seasonal_ranks[year.year] = calculate_ranks(catches_year)
        context['season_catches'] = seasonal_ranks

        # Определяем активный сезон по GET-параметру (если нет – используем "all")
        active_season = self.request.GET.get('season', 'all')
        context['active_season'] = active_season

        # Выбираем набор для вывода в таблице
        if active_season == 'all':
            context['catches'] = overall_ranks
        else:
            try:
                active_year = int(active_season)
                context['catches'] = seasonal_ranks.get(active_year, [])
            except ValueError:
                context['catches'] = overall_ranks

        return context
    



class StatsPageView(TemplateView):
    template_name = 'stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Вкладки по сезонам и "За всё время"
        seasons = list(Catch.objects.dates('date_catch', 'year'))
        context['seasons'] = seasons
        active_season = self.request.GET.get('season', 'all')
        context['active_season'] = active_season
        
        # Если выбран конкретный сезон, формируем фильтр
        if active_season != 'all':
            try:
                active_year = int(active_season)
                season_filter = {'date_catch__year': active_year}
            except ValueError:
                season_filter = {}
        else:
            season_filter = {}

        # 2. Статистика: общее количество выловленных рыб по рыбакам
        fish_count_qs = (
            Catch.objects.filter(**( {} if active_season == 'all' else {'date_catch__year': active_season}))
            .values('user')
            .annotate(total_count=Count('id'))
            .order_by('-total_count')
        )
        total_fish_count = []
        for item in fish_count_qs:
            user_obj = User.objects.get(id=item['user'])
            total_fish_count.append({
                'user': user_obj,
                'total_count': item['total_count'],
            })
        context['total_fish_count'] = total_fish_count

        # 3. Статистика: общий вес выловленных рыб (в кг) по рыбакам
        weight_qs = (
            Catch.objects.filter(**season_filter)
            .values('user')
            .annotate(total_weight=Sum('weight'))
            .order_by('-total_weight')
        )
        total_weight = []
        for item in weight_qs:
            user_obj = User.objects.get(id=item['user'])
            total_weight.append({
                'user': user_obj,
                'total_weight': item['total_weight'],
                'total_weight_kg': item['total_weight'] / 1000.0 if item['total_weight'] else 0,
            })
        context['total_weight'] = total_weight

        # 4. Статистика по конкретному виду рыб:
        # Для каждого вида – максимальный улов, таблицы по количеству и по весу
        fish_stats = {}
        all_fish = Fish.objects.all()
        for fish in all_fish:
            catches = Catch.objects.filter(fish_species=fish, **season_filter)
            max_weight = catches.aggregate(max_weight=Max('weight'))['max_weight']
            
            # Таблица: по количеству выловов данного вида (убывание)
            species_count_qs = (
                catches.values('user')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            species_count = []
            for item in species_count_qs:
                user_obj = User.objects.get(id=item['user'])
                species_count.append({
                    'user': user_obj,
                    'count': item['count'],
                })
            
            # Таблица: по суммарному весу выловов данного вида (убывание)
            species_weight_qs = (
                catches.values('user')
                .annotate(total_weight=Sum('weight'))
                .order_by('-total_weight')
            )
            species_weight = []
            for item in species_weight_qs:
                user_obj = User.objects.get(id=item['user'])
                species_weight.append({
                    'user': user_obj,
                    'total_weight': item['total_weight'],
                    'total_weight_kg': item['total_weight'] / 1000.0 if item['total_weight'] else 0,
                })
            
            fish_stats[fish] = {
                'max_weight': max_weight,
                'by_count': species_count,
                'by_weight': species_weight,
            }
        context['fish_stats'] = fish_stats

        # 5. Таблица: кто в каком сезоне какое занял место (с баллами)
        # Для каждого сезона получаем статистику с использованием функции get_fishermen_stats
        if active_season == 'all':
            ranking_table = []
            for index , value in enumerate(calculate_rating(),start=1):
                ranking_table.append([index,value])
            
        else:
            try:
                active_year = int(active_season)
                ranking_table = get_fishermen_stats(all_time=False, season_filter={'date_catch__year': active_year})
            except ValueError:
                ranking_table = get_fishermen_stats(all_time=True)
        context['ranking_table'] = ranking_table


        # 6. Таблица: максимальное количество выловленных рыб за день
        max_catches_day_qs = (
            Catch.objects.filter(**( {} if active_season == 'all' else {'date_catch__year': active_season}))
            .values('user', 'date_catch')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        max_catches_day = list(max_catches_day_qs[:10])
        for item in max_catches_day:
            user_obj = User.objects.get(id=item['user'])
            item['user_obj'] = user_obj
        context['max_catches_day'] = max_catches_day


        # 7. Таблица: максимальный вес выловленных рыб за день
        max_weight_day_qs = (
            Catch.objects.filter(**( {} if active_season == 'all' else {'date_catch__year': active_season}))
            .values('user', 'date_catch')
            .annotate(total_weight=Sum('weight'))
            .order_by('-total_weight')
        )
        max_weight_day = list(max_weight_day_qs[:10])
        for item in max_weight_day:
            user_obj = User.objects.get(id=item['user'])
            item['user_obj'] = user_obj
            item['total_weight_kg'] = item['total_weight'] / 1000.0 if item['total_weight'] else 0
        context['max_weight_day'] = max_weight_day

        return context
    

class  AddUserPageView(TemplateView):
    template_name = 'adduser.html'
    pass

class  RulesPageView(TemplateView):
    template_name = 'rules.html'
    pass