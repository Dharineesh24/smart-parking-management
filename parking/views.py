from unittest import result

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Vehicle
from django.db.models import Sum
from django.http import HttpResponse
from django.core.files import File
from io import BytesIO
import qrcode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import cv2
import numpy as np
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ultralytics import YOLO
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile
import os
import easyocr
reader = easyocr.Reader(['en'], gpu=False)

BASE_DIR = Path(__file__).resolve().parent.parent

model = YOLO(str(BASE_DIR / "parking" / "models" / "best.pt"))

@login_required(login_url="login")
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, "about.html")

def features(request):
    return render(request, "features.html")

def contact(request):
    return render(request, "contact.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("dashboard")
            else:
                return redirect("vehicle_entry")

        return HttpResponse("Invalid Username or Password")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def vehicle_entry(request):
    if request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        slot = request.POST["parking_slot"]

        if Vehicle.objects.filter(parking_slot=slot, status="Parked").exists():
            return HttpResponse("This parking slot is already occupied!")

        vehicle = Vehicle.objects.create(
            owner=request.user,
            owner_name=request.POST["owner_name"],
            vehicle_number=request.POST["vehicle_number"],
            vehicle_type=request.POST["vehicle_type"],
            phone_number=request.POST["phone_number"],
            parking_slot=slot,
        )
@login_required
def vehicle_entry(request):
    if request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":

        slot = request.POST["parking_slot"]

        if Vehicle.objects.filter(parking_slot=slot, status="Parked").exists():
            return HttpResponse("This parking slot is already occupied!")

        vehicle = Vehicle.objects.create(
            owner=request.user,
            owner_name=request.POST["owner_name"],
            vehicle_number=request.POST["vehicle_number"],
            vehicle_type=request.POST["vehicle_type"],
            phone_number=request.POST["phone_number"],
            parking_slot=slot,
        )

        # QR Code
        url = f"http://127.0.0.1:8000/vehicle/{vehicle.id}/"

        qr = qrcode.make(url)

        buffer = BytesIO()
        qr.save(buffer)

        vehicle.qr_code.save(
            f"{vehicle.vehicle_number}.png",
            File(buffer),
            save=True
        )

        # Barcode
        code128 = barcode.get(
            "code128",
            vehicle.vehicle_number,
            writer=ImageWriter()
        )

        barcode_buffer = BytesIO()
        code128.write(barcode_buffer)

        vehicle.barcode.save(
            f"{vehicle.vehicle_number}.png",
            ContentFile(barcode_buffer.getvalue()),
            save=True
        )

        return redirect("receipt", vehicle_id=vehicle.id)

    return render(request, "vehicle_entry.html")


@login_required
def view_vehicles(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'view_vehicles.html', {'vehicles': vehicles})


@login_required
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        vehicle.owner_name = request.POST['owner_name']
        vehicle.vehicle_number = request.POST['vehicle_number']
        vehicle.vehicle_type = request.POST['vehicle_type']
        vehicle.phone_number = request.POST['phone_number']
        vehicle.parking_slot = request.POST['parking_slot']
        vehicle.save()

        return redirect('view_vehicles')

    return render(request, 'edit_vehicle.html', {
        'vehicle': vehicle
    })

@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    return redirect('view_vehicles')

def search_vehicle(request):
    vehicle = None

    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number")
        vehicle = Vehicle.objects.filter(vehicle_number=vehicle_number).first()

    return render(request, "search_vehicle.html", {
        "vehicle": vehicle
    })

@login_required
def dashboard(request):

    total_vehicles = Vehicle.objects.count()
    parked_vehicles = Vehicle.objects.filter(status="Parked").count()
    exited_vehicles = Vehicle.objects.filter(status="Exited").count()

    today = timezone.now().date()

    today_entry = Vehicle.objects.filter(
        entry_time__date=today
    ).count()

    today_exit = Vehicle.objects.filter(
        exit_time__date=today
    ).count()

    today_collection = Vehicle.objects.filter(
        exit_time__date=today
    ).aggregate(total=Sum("amount"))["total"] or 0

    recent_vehicles = Vehicle.objects.order_by("-entry_time")[:5]

    context = {
        "total_vehicles": total_vehicles,
        "parked_vehicles": parked_vehicles,
        "exited_vehicles": exited_vehicles,
        "today_entry": today_entry,
        "today_exit": today_exit,
        "today_collection": today_collection,
        "recent_vehicles": recent_vehicles,
    }

    return render(request, "dashboard.html", context)

from math import ceil
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone

@login_required
def vehicle_exit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if vehicle.status == "Exited":
        return HttpResponse("Vehicle already exited.")

    vehicle.exit_time = timezone.now()

    duration = vehicle.exit_time - vehicle.entry_time

    # 1 day = ₹20
    days = ceil(duration.total_seconds() / (24 * 60 * 60))

    if days < 1:
        days = 1

    vehicle.amount = days * 20

    vehicle.status = "Exited"
    vehicle.save()

    return redirect("exit_receipt", vehicle_id=vehicle.id)

@login_required
def vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    return render(request, "vehicle_details.html", {"vehicle": vehicle})

@login_required
def scan_vehicle(request):
    return render(request, "scan.html")

@csrf_exempt
def scan_ocr(request):

    if request.method != "POST":
        return JsonResponse({"vehicle_number": ""})

    image = request.FILES.get("image")
    language = request.POST.get("language", "en")

    if not image:
        return JsonResponse({"vehicle_number": ""})

    img = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    if img is None:
        return JsonResponse({"vehicle_number": ""})

    # YOLO Detection
    results = model(img)

    plate = None

    for r in results:
        if len(r.boxes) > 0:
            x1, y1, x2, y2 = r.boxes.xyxy[0].cpu().numpy().astype(int)
            plate = img[y1:y2, x1:x2]
            break

    if plate is None:
        plate = img

    # OCR
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    result = reader.readtext(
        gray,
        detail=0,
        paragraph=False,
        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        decoder="beamsearch",
        width_ths=0.7,
        height_ths=0.7,
    )

    vehicle_number = ""

    for text in result:

        text = text.replace(" ", "").upper()

        match = re.search(
            r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}",
            text
        )

        if match:
            vehicle_number = match.group()
            break
    print("Detected:", vehicle_number)

    if not vehicle_number:
        return JsonResponse({"vehicle_number": ""})

    # Already Parked -> Exit
    existing_vehicle = Vehicle.objects.filter(
        vehicle_number=vehicle_number,
        status="Parked"
    ).first()

    if existing_vehicle:
        return JsonResponse({
            "vehicle_number": vehicle_number,
            "redirect_url": f"/exit/{existing_vehicle.id}/"
        })

    # New Entry
    vehicle = Vehicle.objects.create(
    owner=request.user,
    owner_name="Parking User",
    vehicle_number=vehicle_number,
    vehicle_type="Bike",
    phone_number="0000000000",
    parking_slot="A1",
    language=language,
)
    
    # QR Code
    url = f"http://127.0.0.1:8000/vehicle/{vehicle.id}/"

    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer)

    vehicle.qr_code.save(
        f"{vehicle.vehicle_number}.png",
        File(buffer),
        save=True
    )

    # Barcode
    code128 = barcode.get(
        "code128",
        vehicle.vehicle_number,
        writer=ImageWriter()
    )

    barcode_buffer = BytesIO()
    code128.write(barcode_buffer)

    vehicle.barcode.save(
        f"{vehicle.vehicle_number}.png",
        ContentFile(barcode_buffer.getvalue()),
        save=True
    )

    return JsonResponse({
        "vehicle_number": vehicle.vehicle_number,
        "redirect_url": f"/receipt/{vehicle.id}/"
    })


def receipt(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    return render(request, "receipt.html", {
        "vehicle": vehicle
    })

def exit_receipt(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    duration = vehicle.exit_time - vehicle.entry_time

    days = duration.days
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    return render(request, "exit_receipt.html", {
        "vehicle": vehicle,
        "days": days,
        "hours": hours,
        "minutes": minutes,
    })

from .models import ParkingSetup

@login_required 
@staff_member_required
def setup(request):

    setup = ParkingSetup.objects.first()

    if request.method == "POST":

        if not setup:
            setup = ParkingSetup()

        setup.parking_name = request.POST.get("parking_name")
        setup.owner_name = request.POST.get("owner_name")
        setup.mobile_number = request.POST.get("mobile_number")
        setup.email = request.POST.get("email")
        setup.address = request.POST.get("address")
        setup.one_day_fee = request.POST.get("one_day_fee")
        setup.default_language = request.POST.get("default_language")

        if request.FILES.get("parking_logo"):
            setup.parking_logo = request.FILES.get("parking_logo")

        setup.save()

        return redirect("setup")

    return render(request, "setup.html", {
        "setup": setup
    })

from django.contrib import messages

@login_required
@staff_member_required
def delete_all_vehicles(request):
    Vehicle.objects.all().delete()
    messages.success(request, "All vehicles deleted successfully.")
    return redirect("view_vehicles")

