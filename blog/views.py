from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Count
from .models import Post, Category
from .forms import PostForm, RegisterForm, CategoryForm


# ─────────────────────────────────────────
# VIEWS PUBLIK (tidak perlu login)
# ─────────────────────────────────────────

def post_list(request):
    """Halaman utama: daftar semua post dengan pencarian dan filter kategori"""
    posts = Post.objects.all().select_related('author', 'category')
    categories = Category.objects.all().annotate(post_count=Count('posts'))
    
    # Filter Pencarian (q)
    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
        
    # Filter Kategori (category slug)
    category_slug = request.GET.get('category', '')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=active_category)
        
    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'categories': categories,
        'query': query,
        'active_category': active_category,
    })


def post_detail(request, pk):
    """Halaman detail satu post"""
    post = get_object_or_404(Post, pk=pk)
    # Ambil artikel terkait di kategori yang sama (jika ada kategori)
    related_posts = []
    if post.category:
        related_posts = Post.objects.filter(category=post.category).exclude(pk=post.pk)[:3]
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related_posts
    })


def category_list(request):
    """Melihat katalog kategori beserta jumlah post"""
    categories = Category.objects.all().annotate(post_count=Count('posts'))
    return render(request, 'blog/category_list.html', {
        'categories': categories
    })


# ─────────────────────────────────────────
# VIEWS AUTH (login, register, logout)
# ─────────────────────────────────────────

def register_view(request):
    """Halaman registrasi user baru"""
    if request.user.is_authenticated:
        return redirect('post-list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Akun berhasil dibuat! Selamat datang, {user.username}!')
            return redirect('post-list')
    else:
        form = RegisterForm()
    
    return render(request, 'blog/register.html', {'form': form})


def login_view(request):
    """Halaman login"""
    if request.user.is_authenticated:
        return redirect('post-list')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            next_url = request.GET.get('next', 'post-list')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/login.html', {'form': form})


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.info(request, 'Kamu berhasil logout.')
    return redirect('post-list')


# ─────────────────────────────────────────
# VIEWS CRUD & DASHBOARD (WAJIB LOGIN)
# ─────────────────────────────────────────

@login_required
def dashboard_view(request):
    """Dashboard kelola postingan dan kategori sendiri"""
    user_posts = Post.objects.filter(author=request.user).select_related('category')
    categories = Category.objects.all().annotate(post_count=Count('posts'))
    
    # Menangani form penambahan kategori baru di dashboard
    if request.method == 'POST' and 'add_category' in request.POST:
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, 'Kategori baru berhasil ditambahkan!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Gagal menambahkan kategori. Silakan periksa kolom input.')
    else:
        category_form = CategoryForm()
        
    return render(request, 'blog/dashboard.html', {
        'posts': user_posts,
        'categories': categories,
        'category_form': category_form,
    })


@login_required
def post_create(request):
    """Buat post baru"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Catatan berhasil dibuat!')
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'Buat'
    })


@login_required
def post_update(request, pk):
    """Edit post yang sudah ada"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, 'Kamu tidak punya izin mengedit catatan ini!')
        return redirect('post-detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catatan berhasil diperbarui!')
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'Edit',
        'post': post
    })


@login_required
def post_delete(request, pk):
    """Hapus post"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, 'Kamu tidak punya izin menghapus catatan ini!')
        return redirect('post-detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Catatan berhasil dihapus!')
        return redirect('post-list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})