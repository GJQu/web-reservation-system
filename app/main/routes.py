from flask import render_template

from app.main import bp


@bp.route("/")
def index():
    return render_template("home.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/gallery")
def gallery():
    images = [
        {"url": "static/portfolio/WechatIMG24752.jpg", "alt": "Image 1 Description"},
        {"url": "static/portfolio/WechatIMG24753.jpg", "alt": "Image 2 Description"},
        {"url": "static/portfolio/WechatIMG24754.jpg", "alt": "Image 3 Description"},
        {"url": "static/portfolio/WechatIMG24755.jpg", "alt": "Image 4 Description"},
        {"url": "static/portfolio/WechatIMG24756.jpg", "alt": "Image 5 Description"},
        {"url": "static/portfolio/WechatIMG24757.jpg", "alt": "Image 6 Description"},
        {"url": "static/portfolio/WechatIMG24758.jpg", "alt": "Image 7 Description"},
        {"url": "static/portfolio/WechatIMG24759.jpg", "alt": "Image 8 Description"},
        {"url": "static/portfolio/WechatIMG24760.jpg", "alt": "Image 9 Description"},
        {"url": "static/portfolio/WechatIMG24761.jpg", "alt": "Image 10 Description"},
    ]
    return render_template("gallery.html", images=images)


@bp.route("/contact")
def contact():
    return render_template("contact.html")
