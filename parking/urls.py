from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.home, name='home'),
    path('entry/', views.vehicle_entry, name='vehicle_entry'),
    path('view/', views.view_vehicles, name='view_vehicles'),
    path('edit/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('delete/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('search/', views.search_vehicle, name='search_vehicle'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exit/<int:vehicle_id>/', views.vehicle_exit, name='vehicle_exit'),
    path('vehicle/<int:vehicle_id>/', views.vehicle_details, name='vehicle_details'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('scan/', views.scan_vehicle, name='scan'),
    path('scan_ocr/', views.scan_ocr, name='scan_ocr'),
    path("receipt/<int:vehicle_id>/", views.receipt, name="receipt"),
    path("exit_receipt/<int:vehicle_id>/", views.exit_receipt, name="exit_receipt"),
    path('setup/', views.setup, name='setup'),
    path('about/',views.about, name='about'),
    path('features/',views.features, name='features'),
    path('contact/',views.contact, name='contact'),
    path("delete_all/", views.delete_all_vehicles, name="delete_all_vehicles")
]
=======
    path("", views.home, name="home"),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Vehicle
    path("entry/", views.vehicle_entry, name="vehicle_entry"),
    path("view/", views.view_vehicles, name="view_vehicles"),
    path("edit/<int:vehicle_id>/", views.edit_vehicle, name="edit_vehicle"),
    path("delete/<int:vehicle_id>/", views.delete_vehicle, name="delete_vehicle"),
    path("delete_all/", views.delete_all_vehicles, name="delete_all_vehicles"),

    # Search
    path("search/", views.search_vehicle, name="search_vehicle"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Exit
    path("exit/<int:vehicle_id>/", views.vehicle_exit, name="vehicle_exit"),
    path("exit_receipt/<int:vehicle_id>/", views.exit_receipt, name="exit_receipt"),

    # Vehicle Details
    path("vehicle/<int:vehicle_id>/", views.vehicle_details, name="vehicle_details"),

    # OCR
    path("scan/", views.scan_vehicle, name="scan"),
    path("scan_ocr/", views.scan_ocr, name="scan_ocr"),

    # Receipt
    path("receipt/<int:vehicle_id>/", views.receipt, name="receipt"),

    # Setup
    path("setup/", views.setup, name="setup"),

    # Static Pages
    path("about/", views.about, name="about"),
    path("features/", views.features, name="features"),
    path("contact/", views.contact, name="contact"),
]
>>>>>>> c58287a (Role updates)
