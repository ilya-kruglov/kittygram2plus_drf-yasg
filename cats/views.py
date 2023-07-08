from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.throttling import ScopedRateThrottle

from .models import Achievement, Cat, User
# from .pagination import CatsPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (OwnerOrReadOnly,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request'
    # Обратите внимание: если раньше список объектов был прямо в теле JSON,
    # то теперь объекты вложены в список results.
    # Если пагинация установлена на уровне проекта, то для отдельного класса
    # её можно отключить, установив для атрибута pagination_class
    # значение None.
    # Вот он наш собственный класс пагинации с page_size=20

    # pagination_class = CatsPagination

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')

    # Поиск можно проводить и по содержимому полей связанных моделей.
    # Доступные для поиска поля связанной модели указываются через нотацию с
    # двойным подчёркиванием: ForeignKey текущей модели__имя поля в
    # связанной модели.
    # search_fields = ('achievements__name', 'owner__username')

    # filter_backends = (filters.SearchFilter,)
    # # Определим, что значение параметра search должно быть началом
    # # искомой строки
    # search_fields = ('^name',)

    search_fields = ('name',)
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов
        # без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
