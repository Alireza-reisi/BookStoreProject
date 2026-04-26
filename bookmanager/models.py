from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام نویسنده",
                            error_messages={
                                "blank": "این فیلد اجباری است."
                            })
    english_name = models.CharField(max_length=150, verbose_name="نام انگلیسی",
                                    error_messages={
                                        "blank": "این فیلد اجباری است."
                                    })

    photo = models.ImageField(
        upload_to="img/authors",
        blank=True,
        null=True,
        verbose_name="عکس نویسنده"
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="وب‌سایت"
    )
    biography = models.TextField(
        blank=True,
        null=True,
        verbose_name="بیوگرافی"
    )

    slug = models.SlugField(unique=True, blank=True,
                            error_messages={'unique': "این اسلاگ قبلاً ثبت شده است. یک اسلاگ دیگر انتخاب کنید.", })

    class Meta:
        verbose_name = "نویسنده"
        verbose_name_plural = "نویسندگان"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Bookmanager:author_page", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.english_name)
            slug = base_slug
            counter = 1
            while Author.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name="نام دسته",
                            error_messages={
                                'unique': "این نام قبلاً ثبت شده است. یک نام دیگر انتخاب کنید.",
                                'blank': "این فیلد اجباری است."
                            })
    english_name = models.CharField(unique=True, max_length=50, verbose_name="نام انگلیسی",
                                    error_messages={
                                        'unique': "این نام انگلیسی قبلاً ثبت شده است. یک نام دیگر انتخاب کنید.",
                                        'blank': "این فیلد اجباری است."
                                    })
    image = models.ImageField(upload_to='img/categories', blank=True, null=True, verbose_name="تصویر دسته")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    slug = models.SlugField(max_length=60, unique=True, blank=True,
                            error_messages={
                                'unique': "این اسلاگ قبلاً ثبت شده است. یک اسلاگ دیگر انتخاب کنید.", })

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse('Bookmanager:category_page', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.english_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام ناشر",
                            error_messages={
                                "blank": "این فیلد اجباری است."
                            })
    english_name = models.CharField(max_length=150, verbose_name="نام انگلیسی ناشر",
                                    error_messages={
                                        "blank": "این فیلد اجباری است."
                                    })

    logo = models.ImageField(
        upload_to='img/publishers',
        blank=True,
        null=True,
        verbose_name="لوگو ناشر"
    )

    website = models.URLField(blank=True, null=True, verbose_name="وب‌سایت")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    slug = models.SlugField(unique=True, blank=True,
                            error_messages={
                                'unique': "این اسلاگ قبلاً ثبت شده است. یک اسلاگ دیگر انتخاب کنید.", })

    class Meta:
        verbose_name = "ناشر"
        verbose_name_plural = "ناشران"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Bookmanager:publisher_page', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.english_name)
            slug = base_slug
            counter = 1

            while Publisher.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Book(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ("physical", "فیزیکی"),
        ("digital", "دیجیتال"),
    )

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    # -------------------
    # Basic Info
    # -------------------

    title = models.CharField(max_length=150, verbose_name="عنوان کتاب",
                             error_messages={
                                 "blank": "این فیلد اجباری است."
                             })
    english_title = models.CharField(max_length=150, verbose_name="عنوان انگلیسی",
                                     error_messages={
                                         "blank": "این فیلد اجباری است."
                                     })

    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    image = models.ImageField(
        upload_to="img/books/",
        default="assets/img/default.jpg",
        verbose_name="تصویر کتاب"
    )

    file = models.FileField(
        upload_to="file/books/",
        blank=True,
        null=True,
        verbose_name="فایل کتاب (برای نسخه دیجیتال)"
    )

    # -------------------
    # Commercial Info
    # -------------------

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="قیمت"
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="قیمت با تخفیف"
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی انبار"
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default="physical",
        verbose_name="نوع محصول"
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="شناسه انبار (SKU)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت انتشار"
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # -------------------
    # Relations
    # -------------------

    author = models.ForeignKey(
        "Author",
        on_delete=models.SET_NULL,
        null=True,
        related_name="books"
    )

    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        related_name="books"
    )

    categories = models.ManyToManyField(
        "Category",
        related_name="books"
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_books"
    )

    # -------------------
    # Stats
    # -------------------

    sell_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    # -------------------
    # Dates
    # -------------------

    published_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------
    # Meta
    # -------------------

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"

    # -------------------
    # Methods
    # -------------------

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Bookmanager:book_page", args=[self.slug])

    @property
    def final_price(self):
        """
        قیمت نهایی بعد از تخفیف
        """
        if self.discount_price:
            return self.discount_price
        return self.price

    def is_in_stock(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.english_title)
            slug = base_slug
            counter = 1

            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Comment(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="کتاب",
        error_messages={
            "blank": "این فیلد اجباری است."
        }
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="book_comments",
        verbose_name="کاربر",
        error_messages={
            "blank": "این فیلد اجباری است."
        }
    )

    text = models.TextField(max_length=500, verbose_name="متن نظر",
                            error_messages={
                                "blank": "این فیلد اجباری است."
                            })
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book.title} - {self.author.username}"
