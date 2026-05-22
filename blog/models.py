from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Post(models.Model):
    # Judul post, maksimal 200 karakter
    title = models.CharField(max_length=200)
    
    # Isi konten post (teks panjang)
    content = models.TextField()
    
    # Penulis: terhubung ke User Django bawaan
    # on_delete=CASCADE artinya kalau user dihapus, postnya ikut terhapus
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Kategori post (bisa kosong atau set null jika kategori dihapus)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    # Tanggal dibuat, otomatis diisi saat pertama kali disimpan
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Tanggal diupdate, otomatis diisi setiap kali disimpan
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Tampilan di admin Django
        return self.title

    class Meta:
        # Urutkan dari yang terbaru
        ordering = ['-created_at']