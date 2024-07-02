from django.core.exceptions import ValidationError
from django.db import models, transaction


class LeadState(models.Model):
    # pk экземпляров модели
    STATE_NEW = 1  # Новый
    STATE_IN_PROGRESS = 2  # В работе
    STATE_POSTPONED = 3  # Приостановлен
    STATE_DONE = 4  # Завершен
    name = models.CharField(
        u"Название",
        max_length=50,
        unique=True,
    )


class Lead(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=u"Имя",
    )
    state = models.ForeignKey(
        LeadState,
        on_delete=models.PROTECT,
        default=LeadState.STATE_NEW,
        verbose_name=u"Состояние",
    )

    TRANSITIONS_ORDER = { #таблица допустимых переходов
        LeadState.STATE_NEW: [LeadState.STATE_IN_PROGRESS],
        LeadState.STATE_IN_PROGRESS: [LeadState.STATE_POSTPONED, LeadState.STATE_DONE],
        LeadState.STATE_POSTPONED: [LeadState.STATE_IN_PROGRESS, LeadState.STATE_DONE],
        LeadState.STATE_DONE: []
    }

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_state = Lead.objects.get(pk=self.pk).state_id
            if old_state != self.state_id:# если изменен статус то...
                if self.state_id not in self.TRANSITIONS_ORDER.get(old_state, []):# смотрим может ли из нынешнего состояния перейти в следующее
                     raise ValidationError(f"Статус объекта не может перейти из {old_state} в {self.state_id}")
                self._handle_transition(old_state, self.state_id)
        super().save(*args, **kwargs)

    @transaction.atomic
    def _handle_transition(self, old_state, new_state): #атомарная хаб функция, которая с вызывает функцию в зависимости от параметров состояния
        transition_method = f"_on_transition_from_{old_state}_to_{new_state}"
        if hasattr(self, transition_method):
            getattr(self, transition_method)()

    # Обработчики кастомной логики

    def _on_transition_from_1_to_2(self):
        # кастомная логика
        print(f"Переход из статуса NEW в IN_PROGRESS для Lead с айди {self.pk}")

    def _on_transition_from_2_to_3(self):
        # кастомная логика
        print(f"Переход из статуса IN_PROGRESS в POSTPONED для Lead с айди {self.pk}")

    def _on_transition_from_2_to_4(self):
        # кастомная логика
        print(f"Переход из статуса IN_PROGRESS в DONE для Lead с айди {self.pk}")

    def _on_transition_from_3_to_2(self):
        # кастомная логика
        print(f"Переход из статуса POSTPONED в IN_PROGRESS для Lead с айди {self.pk}")

    def __on_transition_from_3_to_4(self):
        # кастомная логика
        print(f"Переход из статуса POSTPONED в DONE для Lead с айди  {self.pk}")