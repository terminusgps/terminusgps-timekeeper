import pandas as pd
from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, UpdateView

from terminusgps_timekeeper.models import Employee, EmployeeShift
from terminusgps_timekeeper.utils import generate_random_password
from terminusgps_timekeeper.views.mixins import HtmxTemplateResponseMixin
from terminusgps_timekeeper.forms import (
    EmployeeBatchCreateForm,
    EmployeeCreateForm,
    EmployeeSearchForm,
)


class EmployeeCreateView(HtmxTemplateResponseMixin, FormView):
    extra_context = {"class": "flex flex-col gap-4", "title": "Create Employee"}
    field_css_class = "p-2 rounded bg-white border border-gray-600"
    partial_template_name = "terminusgps_timekeeper/employees/partials/_create.html"
    template_name = "terminusgps_timekeeper/employees/create.html"
    form_class = EmployeeCreateForm
    success_url = reverse_lazy("list employees")
    http_method_names = ["get", "post"]

    def form_valid(self, form: EmployeeCreateForm) -> HttpResponseRedirect:
        username: str = form.cleaned_data["email"]
        password: str = generate_random_password()

        employee = Employee.objects.create(
            user=get_user_model().objects.create_user(
                username=username, password=password
            ),
            code=form.cleaned_data["code"],
            phone=form.cleaned_data["phone"],
            pfp=form.cleaned_data["pfp"],
            title=form.cleaned_data["title"],
        )
        employee.save()
        return HttpResponseRedirect(self.get_success_url())


class EmployeeListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    http_method_names = ["get"]
    model = Employee
    template_name = "terminusgps_timekeeper/employees/list.html"
    partial_template_name = "terminusgps_timekeeper/employees/partials/_list.html"
    ordering = "user__username"
    paginate_by = 5
    extra_context = {"title": "Employees"}
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def get_queryset(self, **kwargs) -> QuerySet:
        queryset = super().get_queryset(**kwargs)
        form = EmployeeSearchForm({"q": self.request.GET.get("q")})
        if form.is_valid() and form.cleaned_data["q"] is not None:
            query = form.cleaned_data["q"]
            queryset = queryset.filter(
                Q(user__username__iexact=query) | Q(user__username__istartswith=query)
            )
        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["form"] = EmployeeSearchForm({"q": self.request.GET.get("q")})
        return context


class EmployeeBatchCreateView(HtmxTemplateResponseMixin, FormView):
    extra_context = {"class": "flex flex-col gap-4", "title": "Upload Batch File"}
    form_class = EmployeeBatchCreateForm
    partial_template_name = "terminusgps_timekeeper/employees/_create_batch.html"
    success_url = reverse_lazy("list employees")
    template_name = "terminusgps_timekeeper/employees/create_batch.html"
    http_method_names = ["get", "post"]

    def form_valid(self, form: EmployeeBatchCreateForm) -> HttpResponse:
        try:
            df = self.get_dataframe(form.cleaned_data["input_file"])
        except ValueError as e:
            form.add_error(
                "input_file",
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)

        if df is None:
            form.add_error(
                "input_file",
                ValidationError(
                    _(
                        "Whoops! Failed to extract data from the input file. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)

        for i, row in df.iterrows():
            email: str = str(row["Email"])
            phone: str | None = str(row["Phone"]) if pd.notna(row["Phone"]) else None
            title: str | None = str(row["Title"]) if pd.notna(row["Title"]) else None
            user: AbstractBaseUser = get_user_model().objects.create_user(
                username=email, password=generate_random_password()
            )
            Employee.objects.create(user=user, phone=phone, title=title)
        return super().form_valid(form=form)

    def get_dataframe(self, input_file: File) -> pd.DataFrame | None:
        ext = "".join(input_file.name.split(".")[-1])

        match ext:
            case "csv":
                df = pd.read_csv(input_file)
            case "xlsx":
                df = pd.read_excel(input_file)
            case _:
                raise ValueError(f"Invalid input file type: '{ext}'.")
        return self.validate_dataframe(df)

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """Raises :py:exec:`~django.core.exceptions.ValidationError` if any invalid columns are present in the :py:obj:`~pandas.DataFrame`."""
        target_cols: tuple[str, str, str] = ("Email", "Phone", "Title")
        bad_cols: list[str] = [col for col in df.columns if col not in target_cols]

        if bad_cols:
            raise ValueError(f"Invalid column names: '{bad_cols}'")
        return df


class EmployeeDetailView(HtmxTemplateResponseMixin, DetailView):
    model = Employee
    template_name = "terminusgps_timekeeper/employees/detail.html"
    partial_template_name = "terminusgps_timekeeper/employees/partials/_detail.html"
    queryset = Employee.objects.all()
    context_object_name = "employee"
    http_method_names = ["get", "patch"]
    extra_context = {"class": "flex flex-col gap-8", "title": "Employee Details"}

    @staticmethod
    def clean_status(value: str | None) -> bool | None:
        if value is None:
            return

        status = value.lower()
        status_map = {"true": True, "false": False}
        return status_map.get(status, None)

    def get_shifts(self, total: int = 5) -> QuerySet[EmployeeShift | EmployeeShift]:
        e, o = self.get_object(), "-start_datetime"
        return EmployeeShift.objects.filter(employee=e).order_by(o)[:total]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["latest_shifts"] = self.get_shifts(5)
        return context

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)

        status = self.clean_status(request.GET.get("status"))
        if status is not None:
            employee = self.get_object()
            employee.punch_card.punched_in = status
            employee.punch_card.save()
        return self.get(request, *args, **kwargs)


class EmployeeSetFingerprintView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    model = Employee
    template_name = "terminusgps_timekeeper/employees/set_fingerprint.html"
    partial_template_name = (
        "terminusgps_timekeeper/employees/partials/_set_fingerprint.html"
    )
    queryset = Employee.objects.all()
    context_object_name = "employee"
    http_method_names = ["get", "post"]
    fields = ["code"]
    extra_context = {"title": "Update Fingerprint", "class": "flex flex-col gap-4"}
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    initial = {"code": ""}

    def get_form(self, form_class=None) -> forms.ModelForm:
        css_class = "p-2 bg-white border border-gray-600 rounded"
        form = super().get_form(form_class)
        form.fields["code"].widget.attrs.update(
            {
                "class": css_class,
                "placeholder": "Waiting for fingerprint scan...",
                "autofocus": True,
            }
        )
        return form
