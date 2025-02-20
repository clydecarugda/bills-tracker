from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef, Exists
from billstracker.models import User, UserProfile

class Command(BaseCommand):
    help = "Create UserProfile for existing users"

    def handle(self, *args, **kwargs):
      users_without_profiles = User.objects.filter(
          ~Exists(UserProfile.objects.filter(user=OuterRef("pk")))
      )

      total_created = 0
      for user in users_without_profiles:
        UserProfile.objects.create(user=user)
        total_created += 1

      self.stdout.write(self.style.SUCCESS(f"Successfully created {total_created} User Profiles."))