import datetime
from django.utils.timezone import localdate
from rest_framework import viewsets
from rest_framework.response import Response
from .models import CycleLog, CycleConfig
from .serializers import CycleLogSerializer

class CycleLogViewSet(viewsets.ModelViewSet):
    serializer_class = CycleLogSerializer

    # 1. Sécurité en lecture : On ne voit que nos propres logs
    def get_queryset(self):
        return CycleLog.objects.filter(user=self.request.user)

    # 2. Sécurité en écriture : On lie automatiquement le log à l'utilisateur connecté
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # 1. On récupère les constantes et on extrait leur valeurs
        luteal_setting = CycleConfig.objects.filter(key="luteale_duration").first()
        ovulation_setting = CycleConfig.objects.filter(key="ovulation_duration").first()
        luteal_duration = luteal_setting.value if luteal_setting else 14
        ovulation_duration = ovulation_setting.value if ovulation_setting else 2

        # 2. On récupère les données user triées
        queryset = self.get_queryset().order_by("-start_date")

        # S'il n'y a aucun historique, on renvoie une liste vide immédiate pour éviter les crashs
        if not queryset.exists():
            return Response([])

        # 3. On cree la valeur cycle moyen en fonction de l'historique user ou fallback value
        recent_logs = list(queryset[:7])
        if len(recent_logs) > 1 :
            intervals = []
            for i in range(len(recent_logs) - 1):
                diff = recent_logs[i].start_date - recent_logs[i+1].start_date
                intervals.append(diff.days)

            average_cycle_length = sum(intervals) / len(intervals)
        else: 
            average_cycle_length = 28

        # 4. Variables de base de données
        last_log = queryset.first()
        start_date = last_log.start_date
        period_duration = last_log.period_duration

        # 5. Calcul du Jour J
        current_date = localdate()
        current_day_index = (current_date - start_date).days + 1

        # 6. Creation du tableau individuel de Phases
        menstrual_start = 1
        menstrual_end = period_duration
        luteal_end = int(average_cycle_length)
        luteal_start = luteal_end - luteal_duration + 1
        ovulatory_end = luteal_start - 1
        ovulatory_start = ovulatory_end - ovulation_duration + 1
        follicular_start = menstrual_end + 1
        follicular_end = ovulatory_start - 1

        # 6. Calcul de la phase actuelle (Ta logique optimisée avec sécurité retard)
        if current_day_index > average_cycle_length:
            current_phase = "Late / Next Cycle Pending"
        elif current_day_index < follicular_start: 
            current_phase = "Menstrual Phase"
        elif current_day_index > ovulatory_end: 
            current_phase = "Luteal Phase"
        elif current_day_index > menstrual_end and current_day_index < ovulatory_start: 
            current_phase = "Follicular Phase"
        else: 
            current_phase = "Oppulatory Phase"

        # 7. Date estimée du prochain cycle (Formule Excel transposée)
        days_remaining = int(average_cycle_length) - current_day_index
        next_cycle_date = current_date + datetime.timedelta(days=days_remaining)

        # 8. On transforme le queryset brut en JSON pour la partie historique
        serializer = self.get_serializer(queryset, many=True)
        
        # 9. On renvoie le dictionnaire final (la réponse de l'API)
        return Response({
            "recap_excel": {
                "average_cycle_length": average_cycle_length,
                "current_date": current_date,
                "current_day_index": current_day_index,
                "current_phase": current_phase,
                "next_cycle_date": next_cycle_date
            },
            "history": serializer.data
        })
