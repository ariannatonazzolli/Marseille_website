from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.db.models import Count, Q
from map.models import Place

ARR_ORDER = ["1er","2e","3e","4e","5e","6e","7e","8e","9e","10e","11e","12e","13e","14e","15e","16e"]

def serve_google_verification_file(request):
    file_path = Path(settings.BASE_DIR) / "googlec2b4a3ec3165f0c3.html"

    if not file_path.exists() or not file_path.is_file():
        raise Http404

    content = file_path.read_text(encoding="utf-8")
    return HttpResponse(content, content_type="text/html; charset=utf-8")


def map_view(request):
    qs = Place.objects.filter(geocoded=True)

    places_data = [{
        "name": p.name,
        "address": p.address,
        "lat": p.lat,
        "lon": p.lon,
        "mainlevee": p.mainlevee,
        "arrondissement": p.arrondissement,
    } for p in qs]

    rows = (
        Place.objects.filter(geocoded=True)
        .values("arrondissement")
        .annotate(
            red=Count("id", filter=Q(mainlevee=False)),
            green=Count("id", filter=Q(mainlevee=True)),
        )
    )
    by_arr = {r["arrondissement"]: r for r in rows}
    chart_data = [
        {
            "arr": arr,
            "red": by_arr[arr]["red"] if arr in by_arr else 0,
            "green": by_arr[arr]["green"] if arr in by_arr else 0,
        }
        for arr in ARR_ORDER
    ]

    total_map   = len(places_data)
    total_chart = sum(d["red"] + d["green"] for d in chart_data)
    missing     = total_map - total_chart

    return render(request, "map/map.html", {
        "places_data": places_data,
        "chart_data": chart_data,
        "debug_missing": missing,
        "debug_total_map": total_map,
        "debug_total_chart": total_chart,
        "debug_arr_keys": list(by_arr.keys()),
    })