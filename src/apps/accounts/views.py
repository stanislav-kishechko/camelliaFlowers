from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import UserProfile


class LoginView(FormView):
    """
    View for handling user login functionality.

    This class-based view handles user login by rendering a form for username and
    password input, authenticating users based on the submitted credentials, and
    redirecting authenticated users to a success page. If a logged-in user tries
    to access the login page, they are redirected to the success page automatically.

    :ivar template_name: Specifies the path to the login template used for rendering.
    :type template_name: str
    :ivar form_class: The form class used for user login.
    :type form_class: LoginForm
    :ivar success_url: The URL where users are redirected after successful login.
    :type success_url: str
    """
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("dashboard:dashboard")

    def dispatch(self, request, *args, **kwargs):
        """
        Handles the HTTP request dispatch for a view. Overrides the parent dispatch
        method to redirect authenticated users to the dashboard. If the user is
        not authenticated, the method falls back to the parent's implementation.

        :param request: HttpRequest object representing the client's request.
        :type request: HttpRequest
        :param args: Additional positional arguments for the dispatch method.
        :param kwargs: Additional keyword arguments for the dispatch method.
        :return: An HttpResponse object or a redirection response based on the
            authentication state of the user.
        :rtype: HttpResponse
        """
        if request.user.is_authenticated:
            return redirect("dashboard:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Authenticate and log in a user based on the submitted form data. If the authentication
        is successful, the user is logged in and redirected to the success URL. Otherwise, an
        error message is displayed, and the form submission is marked as invalid.

        :param form: Submitted form containing 'username' and 'password' fields.
        :type form: Form
        :return: The response for a valid or invalid form submission.
        :rtype: HttpResponse
        """
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

            messages.success(self.request, "Ви успішно увійшли в систему!")

            return super().form_valid(form)
        else:
            messages.error(self.request, "Невірний email/username або пароль")
            return self.form_invalid(form)


class RegisterView(FormView):
    """
    Handles user registration via a form view.

    This class provides functionality for rendering a user registration template,
    processing registration form submissions, and handling successful or invalid
    form responses. It ensures that authenticated users are redirected away from
    the registration page and creates a user profile on successful registration.

    :ivar template_name: Path to the template used for rendering the registration
        page.
    :type template_name: str
    :ivar form_class: The form class used for user registration.
    :type form_class: type
    :ivar success_url: The URL to redirect to upon successful registration.
    :type success_url: str
    """
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        """
        Handles dispatching of a view based on the authentication state of the user.

        This method determines whether a user is authenticated. If the user is
        authenticated, it redirects them to the dashboard. If not, it proceeds
        with the default dispatch behavior.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: An HTTP response, redirecting to the dashboard if authenticated,
            or processing the default dispatch otherwise.
        :rtype: HttpResponse
        """
        if request.user.is_authenticated:
            return redirect("dashboard:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handles the validation and saving of a form for creating a user and associated user profile.

        :param form: Form instance containing data for creating a user. Must be validated before
                    being passed.
        :type form: Form
        :return: HTTP response indicating the success of form validation and redirection.
        :rtype: HttpResponse
        """
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()

        UserProfile.objects.create(user=user)

        messages.success(self.request, "Реєстрацію завершено! Тепер ви можете увійти.")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Будь ласка, виправте помилки в формі")

        return super().form_invalid(form)


class LogoutView(View):
    """
    Handles user logout functionality.

    This view logs the user out of the system, displays an informational message
    to the user, and redirects them to the login page.

    """
    def get(self, request, *args, **kwargs):
        logout(request)

        messages.info(request, "Ви вийшли з системи")

        return redirect("accounts:login")


class ProfileView(LoginRequiredMixin, View):
    """
    Handles the user's profile view.

    This class-based view is used for managing and displaying the user profile
    and its related data. It includes functionalities to display user statistics
    and to update the user's profile information based on user input. The view
    requires the user to be authenticated.

    :ivar login_url: URL to redirect unauthenticated users for login.
                     Utilized by the LoginRequiredMixin.
    :type login_url: str
    :ivar template_name: Path to the template that will be rendered for the profile
                         view.
    :type template_name: str
    """
    login_url = reverse_lazy("accounts:login")
    template_name = "accounts/profile.html"

    def get(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        user_stats = {
            "sales_count": 142,
            "revenue": "156k",
            "rating": 4.9,
            "success_rate": 87
        }

        context = {
            "user_stats": user_stats,
            "profile": profile,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        form_type = request.POST.get("form_type")
        if form_type == "personal":
            form = ProfileForm(request.POST, instance=request.user, profile_instance=profile)
            if form.is_valid():
                form.save()

                messages.success(request, "Профіль оновлено!")

                return redirect("accounts:profile")
            else:
                messages.error(request, "Помилка при оновленні профілю")

        return self.get(request, *args, **kwargs)
