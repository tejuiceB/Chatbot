from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserRegistrationForm, AppointmentForm, BlogForm
from .models import UserProfile, Doctor, Blog, ChatMessage, Appointment
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User, AnonymousUser
from .chatbot_model.tejuice import TherapistChatbot
from django.utils import timezone

# Move the decorator definition to the top
def check_auth(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this feature.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def is_anonymous(user):
    return isinstance(user, AnonymousUser)

# Initialize chatbot
chatbot = TherapistChatbot()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                age=form.cleaned_data['age'],
                profile_picture=form.cleaned_data.get('profile_picture')
            )
            
            # Add doctor-specific information if user is a doctor
            if form.cleaned_data['user_type'] == 'doctor':
                profile.specialization = form.cleaned_data['specialization']
                profile.experience = form.cleaned_data['experience']
                profile.available_times = form.cleaned_data['available_times']
                profile.save()
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def home(request):
    blog_posts = Blog.objects.filter(status='approved').order_by('-created_at')[:3]
    doctors = UserProfile.objects.filter(user_type='doctor')[:4]  # Show latest 4 doctors
    return render(request, 'home.html', {
        'blogs': blog_posts,
        'doctors': doctors
    })

def blogs(request):
    blog_posts = Blog.objects.filter(status='approved').order_by('-created_at')
    form = None
    if request.user.is_authenticated:  # Allow all authenticated users to create blogs
        if request.method == 'POST':
            form = BlogForm(request.POST)
            if form.is_valid():
                blog = form.save(commit=False)
                blog.author = request.user
                blog.status = 'pending' if not request.user.is_superuser else 'approved'
                blog.save()
                messages.success(request, 'Blog post submitted successfully! It will be visible after admin approval.' if not request.user.is_superuser else 'Blog post created successfully!')
                return redirect('blogs')
        else:
            form = BlogForm()
    
    return render(request, 'blogs.html', {
        'blogs': blog_posts.filter(status='approved'),  # Show only approved blogs
        'form': form,
        'user_blogs': Blog.objects.filter(author=request.user) if request.user.is_authenticated else None
    })

@check_auth
def chat(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = chatbot.get_response(message)
        
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=response
        )
        return render(request, 'chat.html', {
            'response': response,
            'messages': ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]
        })
    return render(request, 'chat.html', {
        'messages': ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]
    })

@check_auth
def hospitals(request):
    return render(request, 'hospitals.html', {
        'api_key': settings.GOOGLE_MAPS_API_KEY
    })

@check_auth
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': user_profile})

@check_auth
def add_blog(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to add a blog.')
        return redirect('blogs')
    
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blogs')
    else:
        form = BlogForm()
    return render(request, 'add_blog.html', {'form': form})

@check_auth
def manage_blogs(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage blogs.')
        return redirect('blogs')
    
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        action = request.POST.get('action')
        
        try:
            blog = Blog.objects.get(id=blog_id)
            if action == 'approve':
                blog.status = 'approved'
                messages.success(request, 'Blog approved successfully.')
            elif action == 'reject':
                blog.status = 'rejected'
                messages.success(request, 'Blog rejected.')
            blog.save()
        except Blog.DoesNotExist:
            messages.error(request, 'Blog not found.')
    
    pending_blogs = Blog.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'manage_blogs.html', {'pending_blogs': pending_blogs})

@check_auth
def doctors(request):
    doctors = UserProfile.objects.filter(user_type='doctor')
    appointments = None
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        notes = request.POST.get('notes')
        
        try:
            doctor = User.objects.get(id=doctor_id)
            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=date,
                notes=notes,
                status='pending'
            )
            messages.success(request, 'Appointment request sent successfully!')
            return redirect('doctors')
        except User.DoesNotExist:
            messages.error(request, 'Doctor not found.')
    
    if request.user.userprofile.user_type == 'patient':
        appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
    
    return render(request, 'doctors.html', {
        'doctors': doctors,
        'appointments': appointments
    })

@check_auth
def manage_appointments(request):
    if request.user.userprofile.user_type != 'doctor':
        messages.error(request, 'You do not have permission to manage appointments.')
        return redirect('home')
    
    # Get all appointments for the doctor, not just today's
    appointments = Appointment.objects.filter(
        doctor=request.user
    ).order_by('-date')
    
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        
        try:
            appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
            if action == 'accept':
                appointment.status = 'confirmed'
                messages.success(request, 'Appointment confirmed.')
            elif action == 'reject':
                appointment.status = 'cancelled'
                messages.success(request, 'Appointment cancelled.')
            appointment.save()
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')
    
    return render(request, 'manage_appointments.html', {'appointments': appointments})
