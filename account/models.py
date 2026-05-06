from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ------------------------------------------
# ---------- customize User model ----------
# ------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Users must have an phone number')

        extra_fields.setdefault('is_active', True)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        user = self.create_user(phone, password)
        user.is_admin = True

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True, verbose_name="شماره تلفن")
    is_active = models.BooleanField(default=True, verbose_name="فعال بودن")
    is_admin = models.BooleanField(default=False, verbose_name="ادمین")
    is_superuser = models.BooleanField(default=False, verbose_name="سوپر یوزر")

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربر'

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perm(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


# ------------------------------------------
# --------- OTP login/signup model ---------
# ------------------------------------------

class OTP(models.Model):
    phone = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")
    verification_code = models.CharField(max_length=6, verbose_name="کد تایید")
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اعتبار سنجی پیامکی'
        verbose_name_plural = 'اعتبار سنجی پیامکی'

    def __str__(self):
        return self.phone
