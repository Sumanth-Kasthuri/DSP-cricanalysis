from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):

    def __str__(self):
        return self.username

class FavoriteTeam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorite_teams')
    team_id = models.CharField(max_length=50)
    team_name = models.CharField(max_length=100)
    team_sname = models.CharField(max_length=50, blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'team_id')
        verbose_name = "Favorite Team"
        verbose_name_plural = "Favorite Teams"
    
    def __str__(self):
        return f"{self.user.username} - {self.team_name}"
