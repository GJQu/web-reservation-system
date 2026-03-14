"""WSGI entry point for Gunicorn and other production servers."""

from app import create_app

application = create_app()
