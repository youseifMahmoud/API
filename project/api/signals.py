from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Child

@receiver(post_save, sender=User)
def create_child_profile(sender, instance, created, **kwargs):
    print(f"Signal Triggered for: {instance.email}, Created: {created}")  # للتحقق من استدعاء الإشارة

    if created:
        # تحقق مما إذا كان الطفل موجودًا مسبقًا
        existing_child = Child.objects.filter(user=instance).exists()
        
        if not existing_child:  # إذا لم يكن لديه طفل، قم بإنشائه
            Child.objects.create(
                user=instance,
                name=instance.name if instance.name else "Default Name",
                age=instance.age if instance.age else 0,
                medical_info=instance.medical_info if instance.medical_info else "",
                qr_code="Generated QR Code",
                additional_data="Default data"
            )
        else:
            print(f"Child already exists for {instance.email}, skipping creation.")
