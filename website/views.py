from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from crm.models import BlogPost, Event, ContactSubmission, IronCircle


def home(request):
    """Landing page - serves the main site."""
    upcoming_events = Event.objects.filter(is_published=True).order_by('date')[:4]
    circles = IronCircle.objects.filter(is_open=True)[:6]
    return render(request, 'website/home.html', {
        'upcoming_events': upcoming_events,
        'circles': circles,
    })


def about(request):
    """About page - the mandate, vision, pillars."""
    return render(request, 'website/about.html')


def events(request):
    """Events listing page."""
    all_events = Event.objects.filter(is_published=True).order_by('date')
    return render(request, 'website/events.html', {'events': all_events})


def blog_list(request):
    """Blog listing page."""
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')
    return render(request, 'website/blog_list.html', {'posts': posts})


def blog_detail(request, slug):
    """Individual blog post."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'website/blog_detail.html', {'post': post})


def signup(request):
    """Handle the signup / interest form submission."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        message = request.POST.get('message', '').strip()
        how_heard = request.POST.get('how_heard', '').strip()

        if name and email:
            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone=phone,
                city=city,
                message=message,
                how_heard=how_heard,
            )
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'status': 'success', 'message': 'Thank you, brother. We will be in touch.'})
            messages.success(request, 'Thank you, brother. We will be in touch.')
            return redirect('home')
        else:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'status': 'error', 'message': 'Name and email are required.'}, status=400)
            messages.error(request, 'Please provide your name and email.')
            return redirect('home')

    return redirect('home')


def contact(request):
    """Contact page."""
    return render(request, 'website/contact.html')


def styleguide(request):
    """Brand v2 styleguide — live reference for palette, type, components."""
    return render(request, 'website/styleguide.html')
