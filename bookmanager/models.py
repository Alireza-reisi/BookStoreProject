from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_comments", verbose_name="کاربر",
                             error_messages={
                                 "blank": "این فیلد اجباری است."
                             }
                             )

    # generic relation to ANY model (Book, Author, ...)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # actual comment
    text = models.TextField(max_length=500, verbose_name="متن نظر",
                            error_messages={
                                "blank": "این فیلد اجباری است."
                            })
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.content_object}"

    @property
    def likes_count(self):
        return self.reactions.filter(reaction='like').count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(reaction='dislike').count()


class CommentReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="reactions")
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')


class Author(models.Model):
    class WritingField(models.TextChoices):
        PHILOSOPHICAL = "philosophical", "فلسفی"
        PSYCHOLOGICAL = "psychological", "روانشناختی"
        MAGICAL_REALISM = "magical_realism", "رئالیسم جادویی"
        CRIME_MYSTERY = "crime_mystery", "معمایی و جنایی"
        ROMANCE_SOCIAL = "romance_social", "عاشقانه / اجتماعی"

        # ادبیات داستانی و رمان‌ها
        LITERARY_FICTION = "literary_fiction", "ادبیات داستانی"
        SOCIAL_NOVEL = "social_novel", "رمان اجتماعی"
        ROMANCE = "romance", "رمان عاشقانه"
        PHILOSOPHICAL_NOVEL = "philosophical_novel", "رمان فلسفی"
        POLITICAL_FICTION = "political_fiction", "ادبیات سیاسی"
        HISTORICAL_FICTION = "historical_fiction", "داستان تاریخی"
        REALISM = "realism", "رئالیسم"
        SOCIAL_REALISM = "social_realism", "رئالیسم اجتماعی"
        MAGIC_REALISM = "magic_realism", "رئالیسم جادویی"
        MODERNISM = "modernism", "مدرنیسم"
        POSTMODERN = "postmodern", "پست‌مدرنیسم"
        SURREAL = "surreal", "سوررئال"
        SHORT_STORY = "short_story", "داستان کوتاه"

        # شعر
        POETRY = "poetry", "شعر"
        MODERN_POETRY = "modern_poetry", "شعر معاصر"
        CLASSIC_POETRY = "classic_poetry", "شعر کلاسیک"

        # ژانرهای تخیلی و ماجراجویی
        FANTASY = "fantasy", "فانتزی"
        EPIC_FANTASY = "epic_fantasy", "فانتزی حماسی"
        SCIENCE_FICTION = "sci_fi", "علمی‌تخیلی"
        ADVENTURE = "adventure", "ماجراجویی"
        DYSTOPIAN = "dystopian", "دیستوپیا / پادآرمان‌شهری"

        # ژانرهای جنایی و هیجان‌انگیز
        CRIME = "crime", "جنایی"
        MYSTERY = "mystery", "معمایی"
        THRILLER = "thriller", "هیجان‌انگیز"
        DETECTIVE = "detective", "کارآگاهی"

        # ژانرهای فلسفی، فکری و عمیق
        PHILOSOPHY = "philosophy", "فلسفه"
        PSYCHOLOGY = "psychology", "روانشناسی"
        EXISTENTIAL = "existential", "اگزیستانسیالیسم"
        SOCIOLOGY = "sociology", "جامعه‌شناسی"

        # ژانرهای کودک و نوجوان
        CHILDREN = "children", "کودک"
        YOUNG_ADULT = "young_adult", "نوجوان"

        # ژانرهای مستند، روزنامه‌نگاری، زندگی‌نامه
        JOURNALISM = "journalism", "روزنامه‌نگاری"
        BIOGRAPHY = "biography", "زندگی‌نامه"
        MEMOIR = "memoir", "خاطره‌نویسی"
        REPORTAGE = "reportage", "گزارش‌نویسی"

        # ژانرهای مذهبی، اسطوره‌ای، تاریخی
        MYTHOLOGY = "mythology", "اسطوره"
        RELIGION = "religion", "دین"
        HISTORY = "history", "تاریخ"

        # ژانرهای موضوعی و کم‌یاب‌تر
        WAR_LITERATURE = "war", "ادبیات جنگ"
        SOCIAL_CRITICISM = "social_criticism", "نقد اجتماعی"
        SYMBOLISM = "symbolism", "سمبولیسم"
        HUMANITIES = "humanities", "انسانیات"

    name = models.CharField(
        max_length=150,
        verbose_name="نام نویسنده",
        error_messages={"blank": "این فیلد اجباری است."}
    )

    english_name = models.CharField(
        max_length=150,
        verbose_name="نام انگلیسی",
        error_messages={"blank": "این فیلد اجباری است."}
    )

    photo = models.ImageField(
        upload_to="img/authors",
        blank=True,
        null=True,
        verbose_name="عکس نویسنده"
    )

    biography = models.TextField(
        blank=True,
        null=True,
        verbose_name="بیوگرافی"
    )

    writing_field = models.CharField(
        max_length=50,
        choices=WritingField.choices,
        verbose_name="زمینه نویسندگی",
        blank=True,
        null=True
    )

    profession = models.CharField(
        max_length=50,
        verbose_name="پیشه",
        blank=True,
        null=True
    )

    nationality = CountryField(
        verbose_name="ملیت",
        blank=True,
        null=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        error_messages={
            "unique": "این اسلاگ قبلاً ثبت شده است. یک اسلاگ دیگر انتخاب کنید."
        }
    )

    comments = GenericRelation(Comment)

    class Meta:
        verbose_name = "نویسنده"
        verbose_name_plural = "نویسندگان"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("bookmanager:author_page", args=[self.slug])

    def save(self, *args, **kwargs):
        # ساخت اسلاگ یکتا
        if not self.slug:
            base_slug = slugify(self.english_name)
            slug = base_slug
            counter = 1

            while Author.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("bookmanager:author_detail", args=[self.slug])


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

    # def get_absolute_url(self):
        # return reverse('bookmanager:category_page', args=[self.slug])

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

    # def get_absolute_url(self):
    #     return reverse('bookmanager:publisher_detail', args=[self.slug])

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

    def get_absolute_url(self):
        return reverse("bookmanager:publisher_detail", args=[self.slug])


class Book(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ("physical", "فیزیکی"),
        ("digital", "دیجیتال"),
    )

    STATUS_CHOICES = (
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    )

    FORMAT_CHOICES = (
        ("paperback", "شومیز"),
        ("hardcover", "جلد سخت"),
        ("ebook", "الکترونیکی"),
        ("audio", "صوتی"),
    )

    title = models.CharField(max_length=150, verbose_name="عنوان کتاب",
                             error_messages={
                                 "blank": "این فیلد اجباری است."
                             })
    english_title = models.CharField(max_length=150, verbose_name="عنوان انگلیسی",
                                     error_messages={
                                         "blank": "این فیلد اجباری است."
                                     })

    slug = models.SlugField(unique=True, blank=True)

    translator = models.CharField(max_length=50, null=True, blank=True, verbose_name='مترجم')

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

    # Commercial Info
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="قیمت"
    )

    discount_price = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='درصد تخفیف'
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی"
    )

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        verbose_name="نوع محصول"
    )

    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        verbose_name="فرمت کتاب"
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="کد محصول (SKU)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت انتشار"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    # ---------- Book Info ----------
    isbn = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        verbose_name="شابک (ISBN)"
    )

    page_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="تعداد صفحات"
    )

    language = models.CharField(
        max_length=50,
        default="فارسی",
        verbose_name="زبان"
    )

    published_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ انتشار"
    )

    # ---------- Relations ----------
    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="نویسنده"
    )

    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ناشر"
    )

    categories = models.ManyToManyField(
        "Category",
        related_name="books",
        verbose_name="دسته‌بندی‌ها"
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="ایجادکننده"
    )

    # ---------- Stats ----------
    sell_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد فروش"
    )

    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد بازدید"
    )

    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد دانلود"
    )

    average_rating = models.FloatField(
        default=0,
        verbose_name="میانگین امتیاز"
    )

    # ---------- Dates ----------
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    comments = GenericRelation(Comment)

    class Meta:
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        if self.discount_price and self.discount_price > 0:
            return int(self.price * (100 - self.discount_price) / 100)
        return self.price

    def is_in_stock(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("bookmanager:book_detail", args=[self.slug])
