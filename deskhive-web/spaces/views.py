"""Section 1: direct HTML, in-memory data, no template or ORM."""
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views import View
from django.views.decorators.http import require_safe
from .data import LOCATIONS


def page(title, body):
    """Escape inserted text; body is a fragment built with format_html."""
    return HttpResponse(format_html(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>{}</title></head><body><nav aria-label="Main">'
        '<a href="{}">Home</a> | <a href="{}">Locations</a> | '
        '<a href="{}">About</a></nav><main><h1>{}</h1>{}</main></body></html>',
        title, reverse("spaces:home"), reverse("spaces:location_list"),
        reverse("spaces:about"), title, body,
    ))


def get_location(code):
    try:
        return LOCATIONS[code]
    except KeyError as exc:
        raise Http404("Unknown DeskHive location") from exc


@require_safe
def home(request):
    return page("DeskHive", format_html(
        '<p>DeskHive offers coworking spaces in Lyon, Lille and Barcelona.</p>'
        '<p><a href="{}">Browse our locations</a></p>'
        '<p>This classroom site displays a catalogue; it does not accept bookings yet.</p>',
        reverse("spaces:location_list"),
    ))


@require_safe
def location_list(request):
    items = format_html_join(
        "",
        '<li><a href="{}">{}</a> - {}</li>',
        (
            (reverse("spaces:location_detail", kwargs={"code": code}),
             location["city"], location["address"])
            for code, location in LOCATIONS.items()
        ),
    )
    return page("Locations", format_html("<ul>{}</ul>", items))


@require_safe
def location_detail(request, code):
    location = get_location(code)
    spaces = format_html_join(
        "",
        "<li>{} - {} EUR/hour</li>",
        ((space["name"], space["hourly_rate"]) for space in location["spaces"]),
    )
    return page(location["city"], format_html(
        "<p>{}</p><h2>Spaces</h2><ul>{}</ul>",
        location["address"], spaces,
    ))


@require_safe
def location_summary(request, code):
    location = get_location(code)
    return JsonResponse({
        "code": code,
        "city": location["city"],
        "address": location["address"],
        "spaces": location["spaces"],
    })


class AboutView(View):
    http_method_names = ["get", "head", "options"]

    def get(self, request):
        return page("About DeskHive", format_html(
            "<p>{}</p>",
            "DeskHive is a fictional coworking company with locations "
            "in Lyon, Lille and Barcelona.",
        ))
