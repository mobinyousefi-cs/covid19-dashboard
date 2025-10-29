#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: COVID-19 Spread Analysis with Flask
File: app.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-29
Updated: 2025-10-29
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Flask application factory, routes, and folium map rendering.
===========================================================================
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

from flask import Flask, abort, jsonify, render_template, request, url_for
import folium
from folium.plugins import MarkerCluster

from .config import Config
from .data_pipeline import ensure_data, load_summary, load_country_detail, top10_countries
from .utils import fmt_int


def create_app(config_object: Any | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).with_name("templates")),
        static_folder=str(Path(__file__).with_name("assets")),
        static_url_path="/assets",
    )

    # Load configuration
    if config_object is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # Ensure data available
    ensure_data(app.config)

    # ------------------------------- ROUTES ------------------------------- #
    @app.route("/")
    def index():
        by_country, by_date = load_summary(app.config)
        top10 = top10_countries(app.config)
        totals = {
            "confirmed": fmt_int(by_country["confirmed"].sum()),
            "deaths": fmt_int(by_country["deaths"].sum()),
            "recovered": fmt_int(by_country["recovered"].sum()),
        }
        return render_template(
            "index.html",
            by_country=by_country.head(50).to_dict(orient="records"),
            timeseries=by_date.to_dict(orient="records"),
            top10=top10.to_dict(orient="records"),
            totals=totals,
        )

    @app.route("/map")
    def map_view():
        by_country, _ = load_summary(app.config)
        # Build a folium map centered roughly on [20, 0]
        fmap = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodbpositron")
        cluster = MarkerCluster(name="COVID-19 Countries").add_to(fmap)

        # Plot markers if we have lat/lon in raw data; otherwise center by country centroids unknown
        # We'll attach popup with summary numbers.
        # For lack of per-country lat/lon, we won't drop markers. If dataset has lat/lon rows, those will appear.
        # Iterate through raw-level rows for better spatial coverage.
        from .data_pipeline import load_raw

        raw = load_raw(app.config)
        if {"lat", "lon"}.issubset(raw.columns):
            latest_date = raw["date"].max() if "date" in raw.columns else None
            if latest_date is not None:
                raw = raw[raw["date"] == latest_date]
            raw_geo = raw.dropna(subset=["lat", "lon"])[:5000]  # safety limit
            for _, row in raw_geo.iterrows():
                popup_html = f"""
                <b>{row.get('country','Unknown')}</b><br>
                {row.get('province_state','')}<br>
                Confirmed: {fmt_int(row.get('confirmed'))}<br>
                Deaths: {fmt_int(row.get('deaths'))}<br>
                Recovered: {fmt_int(row.get('recovered'))}
                """
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=4,
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300),
                ).add_to(cluster)

        folium.LayerControl().add_to(fmap)
        map_html = fmap._repr_html_()
        return render_template("map.html", map_html=map_html)

    @app.route("/country/<name>")
    def country_detail(name: str):
        df = load_country_detail(app.config, name)
        if df.empty:
            abort(404)
        totals = {
            "confirmed": fmt_int(df["confirmed"].sum()),
            "deaths": fmt_int(df["deaths"].sum()),
            "recovered": fmt_int(df["recovered"].sum()),
        }
        return render_template(
            "country.html",
            country=name,
            rows=df.to_dict(orient="records"),
            totals=totals,
        )

    @app.route("/api/top10")
    def api_top10():
        return jsonify(top10_countries(app.config).to_dict(orient="records"))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app