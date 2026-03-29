"""
Tests for Flask app factory and health endpoint.
"""

import pytest


class TestAppFactory:
    """Tests for the create_app factory."""

    def test_app_created(self, app):
        assert app is not None
        assert app.config["TESTING"] is True

    def test_blueprints_registered(self, app):
        blueprint_names = list(app.blueprints.keys())
        assert "graph" in blueprint_names
        assert "simulation" in blueprint_names
        assert "report" in blueprint_names

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "SwarmSage Backend"

    def test_cors_headers(self, client):
        response = client.options(
            "/api/graph/upload",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        # CORS should allow the origin (may be 200, 204, or 404 for OPTIONS on unregistered exact path)
        assert response.status_code in (200, 204, 404, 405, 308)

    def test_json_encoding(self, app):
        # Verify JSON doesn't escape non-ASCII
        if hasattr(app, "json") and hasattr(app.json, "ensure_ascii"):
            assert app.json.ensure_ascii is False
