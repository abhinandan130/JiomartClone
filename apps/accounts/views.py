from django.shortcuts import render, redirect
from .models import Customer
import random
from django.contrib import messages
from .utils import send_otp_email
from django.utils import timezone
from datetime import timedelta
from .decorators import nocache


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "GET":
        list(messages.get_messages(request))

    if request.method == "POST":
        email = request.POST.get("email")
        user = Customer.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not registered. Please register first.")
            request.session["email_pending"] = email
            request.session.save()
            return redirect("register_details")

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_otp_email(email, otp)

        request.session["email"] = email
        request.session.save()

        return redirect("verify_otp")

    return render(request, "accounts/login.html", {
        "hide_footer": True,
        "hide_navitems": True
    })



# =========================
# REGISTER
# =========================
def register(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect("login")

        user = Customer.objects.create(
            name=request.POST.get("name"),
            email=email,
            phone=request.POST.get("phone"),
            location=request.POST.get("location"),
            is_registered=True
        )

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_otp_email(email, otp)

        request.session["email"] = email
        request.session.save()

        return redirect("verify_otp")

    return render(request, "accounts/register.html", {
        "hide_footer": True,
        "hide_navitems": True
    })


# =========================
# VERIFY OTP
# =========================
def verify_otp(request):
    email = request.session.get("email")

    if not email:
        return redirect("login")

    user = Customer.objects.filter(email=email).first()
    if not user:
        messages.error(request, "User not found. Please login again.")
        return redirect("login")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        if user.otp_created_at:
            expiry_time = user.otp_created_at + timedelta(minutes=5)
            if timezone.now() > expiry_time:
                messages.error(request, "OTP expired! Please request a new one.")
                return redirect("resend_otp")

        if entered_otp == user.otp:
            request.session["user_id"] = user.id
            request.session.save()

            if not user.is_registered:
                return redirect("register_details")

            return redirect("product_list")

        return render(request, "accounts/verify_otp.html", {
            "error": "Invalid OTP",
            "shake": True
        })

    return render(request, "accounts/verify_otp.html", {
        "hide_footer": True,
        "hide_navitems": True
    })


# =========================
# COMPLETE REGISTRATION
# =========================
def register_details(request):
    email = request.session.get("email_pending")

    if not email:
        return redirect("login")

    user = Customer.objects.filter(email=email).first()

    if request.method == "POST":
        name = request.POST.get("name")
        location = request.POST.get("location")

        if user:
            user.name = name
            user.location = location
            user.is_registered = True
        else:
            user = Customer.objects.create(
                email=email,
                name=name,
                location=location,
                is_registered=True
            )

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_otp_email(email, otp)

        request.session["email"] = email
        request.session.pop("email_pending", None)
        request.session.save()

        return redirect("verify_otp")

    return render(request, "accounts/details.html", {"email": email}, {
        "hide_footer": True,
        "hide_navitems": True
    })


# =========================
# RESEND OTP
# =========================
def resend_otp(request):
    email = request.session.get("email")
    user = Customer.objects.filter(email=email).first()

    if user:
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_otp_email(email, otp)

    messages.success(request, "New OTP sent to your email")
    return redirect("verify_otp")


# =========================
# Profile view
# =========================
@nocache
def profile_view(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    try:
        user = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        request.session.flush()
        return redirect("login")

    return render(request, "accounts/profile.html", {
        "user": user,
        "hide_footer": True,
        "hide_navitems": True
    })



# =========================
# LOGOUT
# =========================
@nocache
def logout_view(request):
    request.session.flush()
    response = redirect("product_list")
    return response
