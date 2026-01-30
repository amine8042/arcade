from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TECHNICIEN', 'Technicien'),
        ('INVITE', 'Invité'),
        
    )

    cin = models.CharField(max_length=20, unique=True)
    adresse = models.CharField(max_length=255)
    date_embauche = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='INVITE')

    def save(self, *args, **kwargs):
        if self.role == 'ADMIN':
            
            pass
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """إرجاع الاسم الكامل للمستخدم"""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() if full_name.strip() else self.username
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class MachineArcade(models.Model):
    ETAT_CHOICES = (
        ('DISPONIBLE', 'Disponible'),
        ('EN_PANNE', 'En Panne'),
        ('EN_MAINTENANCE', 'En Maintenance'),
        ('HORS_SERVICE', 'Hors Service'),
    )
    
    nom = models.CharField(max_length=100)
    type_jeu = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='DISPONIBLE')
    date_fabrication = models.DateField()
    frequence_panne = models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.nom} - {self.zone}"

    def mettre_a_jour_etat(self, nouvel_etat):
        """تحديث حالة الآلة"""
        self.etat = nouvel_etat
        self.save()
    
    def incrementer_frequence_panne(self):
        """زيادة تردد الأعطال"""
        self.frequence_panne += 1
        self.save()


class Panne(models.Model):
    STATUT_CHOICES = (
        ('SIGNALEE', 'Signalée'),
        ('EN_COURS', 'En cours de traitement'),
        ('REPAREE', 'Réparée'),
    )
    
    PRIORITE_CHOICES = (
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
        ('URGENTE', 'Urgente'),  
    )
    
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='SIGNALEE')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    date_declaration = models.DateTimeField(auto_now_add=True)
    date_reparation = models.DateTimeField(null=True, blank=True)
    
    date_traitement = models.DateTimeField(null=True, blank=True)  
    technicien_assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pannes_assignees',
        limit_choices_to={'role': 'TECHNICIEN'}
    )
    commentaires = models.TextField(null=True, blank=True)  
    duree_reparation = models.DurationField(null=True, blank=True)  
    pieces_remplacees = models.TextField(null=True, blank=True)  
    cout_reparation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    machine = models.ForeignKey(MachineArcade, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pannes_signalees')

    class Meta:
        ordering = ['-date_declaration']  
        verbose_name = "Panne"
        verbose_name_plural = "Pannes"

    def __str__(self):
        return f"Panne #{self.id} - {self.machine.nom}"

    def save(self, *args, **kwargs):
       
        if self.statut == 'EN_COURS' and not self.date_traitement:
            self.date_traitement = timezone.now()
        
       
        if self.statut == 'REPAREE' and not self.date_reparation:
            self.date_reparation = timezone.now()
            
          
            if self.machine.etat == 'EN_PANNE':
                self.machine.mettre_a_jour_etat('DISPONIBLE')
        
        
        if self.statut == 'SIGNALEE':
            if self.machine.etat != 'EN_PANNE':
                self.machine.mettre_a_jour_etat('EN_PANNE')
                self.machine.incrementer_frequence_panne()
        
        super().save(*args, **kwargs)
    
    def marquer_comme_reparée(self, technicien=None, commentaires=None, pieces=None, cout=None):
        """وظيفة مساعدة لتمييز العطل كمصلحة"""
        self.statut = 'REPAREE'
        if technicien:
            self.technicien_assignee = technicien
        if commentaires:
            self.commentaires = commentaires
        if pieces:
            self.pieces_remplacees = pieces
        if cout:
            self.cout_reparation = cout
        self.save()
    
    def get_duree_reparation(self):
        """حساب مدة الإصلاح"""
        if self.date_reparation and self.date_traitement:
            return self.date_reparation - self.date_traitement
        return None
    
    def get_statut_color(self):
        """الحصول على لون الحالة"""
        colors = {
            'SIGNALEE': '#fa709a',
            'EN_COURS': '#4facfe',
            'REPAREE': '#43e97b',
        }
        return colors.get(self.statut, '#666')
    
    def get_priorite_color(self):
        """الحصول على لون الأولوية"""
        colors = {
            'URGENTE': '#ff0000',
            'HAUTE': '#ff4757',
            'MOYENNE': '#ffa502',
            'BASSE': '#2ed573',
        }
        return colors.get(self.priorite, '#666')


class Maintenance(models.Model):
    ETAT_CHOICES = (
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    )
    
    TYPE_CHOICES = (
        ('PREVENTIVE', 'Préventive'),
        ('CORRECTIVE', 'Corrective'),
        ('PREDICTIVE', 'Prédictive'),
    )
    
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='PLANIFIEE')
    type_maintenance = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PREVENTIVE')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    date_debut_reelle = models.DateTimeField(null=True, blank=True)  
    date_fin_reelle = models.DateTimeField(null=True, blank=True)    
    cout_maintenance = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    rapport = models.FileField(upload_to='maintenance_rapports/', null=True, blank=True)
    pieces_utilisees = models.TextField(null=True, blank=True)

    machine = models.ForeignKey(MachineArcade, on_delete=models.CASCADE)
    technicien = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TECHNICIEN'}
    )

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenances"

    def __str__(self):
        return f"Maintenance {self.machine.nom} ({self.get_type_maintenance_display()})"
    
    def save(self, *args, **kwargs):
        
        if self.etat == 'TERMINEE' and self.date_fin_reelle:
            self.machine.derniere_maintenance = self.date_fin_reelle.date()
            self.machine.save()
        super().save(*args, **kwargs)
    
    def demarrer_maintenance(self):
        """بدء الصيانة"""
        self.etat = 'EN_COURS'
        self.date_debut_reelle = timezone.now()
        self.machine.mettre_a_jour_etat('EN_MAINTENANCE')
        self.save()
    
    def terminer_maintenance(self):
        """إنهاء الصيانة"""
        self.etat = 'TERMINEE'
        self.date_fin_reelle = timezone.now()
        self.machine.mettre_a_jour_etat('DISPONIBLE')
        self.save()