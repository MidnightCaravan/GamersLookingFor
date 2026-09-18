from flask import Flask, render_template, request
import json
from pathlib import Path


app = Flask(__name__)


BASE_DIR = Path(__file__).resolve().parent

PRODUCTS_FILE = BASE_DIR / "data" / "products.json"
ARTICLES_FILE = BASE_DIR / "data" / "articles.json"


# Amazon Associates
AMAZON_ASSOCIATE_ID = "affiliat0211f-20"
AMAZON_DOMAIN = "https://www.amazon.com"


def load_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_articles():
    with open(ARTICLES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_amazon_url(asin):
    if not asin:
        return None

    return f"{AMAZON_DOMAIN}/dp/{asin}?tag={AMAZON_ASSOCIATE_ID}"


def prepare_product(product):
    product = dict(product)

    product["amazon_url"] = build_amazon_url(
        product.get("amazon_asin")
    )

    return product


def find_product(product_id):
    products = load_products()

    product = next(
        (
            product
            for product in products
            if product["id"] == product_id
        ),
        None
    )

    if product is None:
        return None

    return prepare_product(product)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/gaming-laptops")
def gaming_laptops():
    products = load_products()

    laptop_products = [
        prepare_product(product)
        for product in products
        if product["category"] == "gaming-laptops"
    ]

    return render_template(
        "category.html",
        category_name="Gaming Laptops",
        category_slug="gaming-laptops",
        products=laptop_products
    )


@app.route("/gaming-pcs")
def gaming_pcs():
    products = load_products()

    pc_products = [
        prepare_product(product)
        for product in products
        if product["category"] == "gaming-pcs"
    ]

    return render_template(
        "category.html",
        category_name="Gaming PCs",
        category_slug="gaming-pcs",
        products=pc_products
    )


@app.route("/graphics-cards")
def graphics_cards():
    products = load_products()

    gpu_products = [
        prepare_product(product)
        for product in products
        if product["category"] == "graphics-cards"
    ]

    return render_template(
        "category.html",
        category_name="Graphics Cards",
        category_slug="graphics-cards",
        products=gpu_products
    )


@app.route("/monitors")
def monitors():
    products = load_products()

    monitor_products = [
        prepare_product(product)
        for product in products
        if product["category"] == "monitors"
    ]

    return render_template(
        "category.html",
        category_name="Gaming Monitors",
        category_slug="monitors",
        products=monitor_products
    )


@app.route("/product/<product_id>")
def product(product_id):
    selected_product = find_product(product_id)

    if selected_product is None:
        return "Product not found", 404

    return render_template(
        "product.html",
        product=selected_product
    )


@app.route("/compare")
def compare():
    products = load_products()

    requested_ids = request.args.get("ids", "").strip()

    if requested_ids:
        selected_ids = [
            product_id.strip()
            for product_id in requested_ids.split(",")
            if product_id.strip()
        ]

        selected_products = [
            prepare_product(product)
            for product in products
            if product["id"] in selected_ids
        ]
    else:
        selected_products = [
            prepare_product(product)
            for product in products
        ]

    return render_template(
        "compare.html",
        products=selected_products
    )


@app.route("/articles")
def articles():
    articles = load_articles()

    products = load_products()

    product_lookup = {
        product["id"]: prepare_product(product)
        for product in products
    }

    for article in articles:
        article["product"] = product_lookup.get(
            article.get("product_id")
        )

    return render_template(
        "articles.html",
        articles=articles
    )


@app.route("/articles/<slug>")
def article(slug):
    articles = load_articles()

    selected_article = next(
        (
            article
            for article in articles
            if article["slug"] == slug
        ),
        None
    )

    if selected_article is None:
        return "Article not found", 404

    product = find_product(
        selected_article.get("product_id")
    )

    return render_template(
        "article.html",
        article=selected_article,
        product=product
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    products = load_products()
    articles = load_articles()

    product_results = []
    article_results = []

    if query:
        search_term = query.lower()

        for product in products:
            searchable_text = " ".join(
                str(product.get(field, ""))
                for field in [
                    "brand",
                    "name",
                    "badge",
                    "exact_sku",
                    "description",
                    "cpu",
                    "gpu",
                    "ram",
                    "storage",
                    "display"
                ]
            ).lower()

            if search_term in searchable_text:
                product_results.append(
                    prepare_product(product)
                )

        for article in articles:
            searchable_text = " ".join(
                str(article.get(field, ""))
                for field in [
                    "title",
                    "category",
                    "excerpt",
                    "author"
                ]
            ).lower()

            for section in article.get("content", []):
                searchable_text += " "
                searchable_text += str(
                    section.get("heading", "")
                )
                searchable_text += " "
                searchable_text += " ".join(
                    section.get("paragraphs", [])
                )

            if search_term in searchable_text.lower():
                article_results.append(article)

    return render_template(
        "search.html",
        query=query,
        products=product_results,
        articles=article_results
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )
