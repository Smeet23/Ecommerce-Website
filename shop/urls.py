from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("login/", views.login_user, name="login_user"),  # Handles login submission
    path("register/", views.register_page, name="register"),
    path("register-user/", views.register_user, name="register_user"),  # Handles registration submission
    path("logout/", views.user_logout, name="logout"),
    
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("home/", views.index, name="ShopHome"),
]