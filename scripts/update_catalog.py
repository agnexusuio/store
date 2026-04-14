from __future__ import annotations

import html
import json
import math
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "products"
JSON_PATH = ROOT / "products.json"
JS_PATH = ROOT / "products.js"

USER_AGENT = "Mozilla/5.0 (compatible; AGNEXUSCatalogBot/1.0)"
BRANDS = ["Asus", "Lenovo", "HP", "ACER", "MSI", "DELL", "ENV"]

PINSOFT_URLS = [
    "https://pinsoft.ec/laptop-notebook-portatiles/c-67.html",
    "https://pinsoft.ec/laptop-notebook-portatiles/c-67.html?page=2",
]

DIGITALPC_URL_TEMPLATE = "https://digitalpcecuador.com/categoria-producto/laptops/page/{page}/?orderby=price"
DIGITALPC_FIRST_PAGE = "https://digitalpcecuador.com/categoria-producto/laptops/?orderby=price"


def fetch_text(url: str, retries: int = 3) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def download_file(url: str, target: Path, retries: int = 2) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45) as response, target.open("wb") as fh:
                shutil.copyfileobj(response, fh)
            return target.exists() and target.stat().st_size > 0
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            return False
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return False


def normalize_space(value: str) -> str:
    value = html.unescape(value or "")
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_pinsoft_listing(page_html: str) -> list[dict]:
    products = []
    chunks = page_html.split('<div class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-xs-6 col_product">')
    for chunk in chunks:
        url_match = re.search(r'<a class="p_img_href\s+not-slider" href="([^"]+)"', chunk)
        title_match = re.search(r'<a href="[^"]+" class="model_product">(.*?)</a>', chunk, re.S)
        image_match = re.search(r'data-src="([^"]+)"', chunk)
        price_match = re.search(r'<span class="ccp">\$</span>([\d.]+)', chunk)
        if not all([url_match, title_match, image_match, price_match]):
            continue
        products.append(
            {
                "source": "pinsoft",
                "url": urllib.parse.urljoin("https://pinsoft.ec/", url_match.group(1)),
                "title": normalize_space(title_match.group(1)),
                "image": urllib.parse.urljoin("https://pinsoft.ec/", image_match.group(1)),
                "price": float(price_match.group(1)),
            }
        )
    return products


def parse_digital_listing(page_html: str) -> list[dict]:
    products = []
    chunks = page_html.split('<div class="product-grid">')
    for chunk in chunks:
        url_match = re.search(r'<a class="product-image" href="([^"]+)"', chunk)
        title_match = re.search(r'<a class="product-name" href="[^"]+">\s*(.*?)\s*<span class="price">', chunk, re.S)
        image_match = re.search(r'data-original="([^"]+)"', chunk)
        price_match = re.search(r'<span class="price">.*?\$([\d.,]+)', chunk, re.S)
        if not all([url_match, title_match, image_match, price_match]):
            continue
        products.append(
            {
                "source": "digitalpc",
                "url": url_match.group(1),
                "title": normalize_space(title_match.group(1)),
                "image": image_match.group(1),
                "price": float(price_match.group(1).replace(",", "")),
            }
        )
    return products


def pinsoft_large_image(product_url: str, fallback: str) -> str:
    try:
        page = fetch_text(product_url)
    except Exception:
        return fallback.replace("/150x150/", "/products/")
    match = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    if match:
        return match.group(1)
    match = re.search(r'<a href="(getimage/products/[^"]+)" data-lightbox=', page)
    if match:
        return urllib.parse.urljoin(product_url, match.group(1))
    return fallback.replace("/150x150/", "/products/")


def digital_large_image(product_url: str, fallback: str) -> str:
    try:
        page = fetch_text(product_url)
    except Exception:
        return fallback
    match = re.search(r'data-large_image="([^"]+)"', page)
    if match:
        return match.group(1)
    match = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    if match:
        return match.group(1)
    return fallback


def normalize_processor_family(processor: str) -> str:
    lowered = processor.lower()
    if "celeron" in lowered:
        return "Celeron"
    if "n100" in lowered:
        return "Intel N100"
    if "i3" in lowered:
        return "Core i3"
    if "i5" in lowered:
        return "Core i5"
    if "i7" in lowered:
        return "Core i7"
    if "ryzen 3" in lowered:
        return "Ryzen 3"
    if "ryzen 5" in lowered:
        return "Ryzen 5"
    if "ryzen 7" in lowered:
        return "Ryzen 7"
    return "Otros"


def normalize_display_value(value: str) -> str:
    return f'{value.replace(",", ".").strip()}"'


def extract_display_from_text(text: str) -> str | None:
    match = re.search(r"(\d{1,2}(?:[.,]\d)?)\s*(?:\"|”|pulgadas|inch|inches)\b", text, flags=re.I)
    return normalize_display_value(match.group(1)) if match else None


def extract_display(segment: str, fallback_text: str | None = None) -> str:
    """Extrae y verifica el tamaño de pantalla, priorizando unidades explícitas."""
    segment = normalize_space(segment)
    display = extract_display_from_text(segment)
    if display:
        return display
    if fallback_text:
        fallback_text = normalize_space(fallback_text)
        display = extract_display_from_text(fallback_text)
        if display:
            return display
    match = re.search(r"(\d{1,2}(?:[.,]\d)?)\s*$", segment)
    if match:
        return normalize_display_value(match.group(1))
    if fallback_text:
        match = re.search(r"(\d{1,2}(?:[.,]\d)?)\s*$", fallback_text)
        if match:
            return normalize_display_value(match.group(1))
    return '15.6"'


def extract_storage(segment: str) -> str:
    segment = segment.upper().replace(" TB ", "GB ").replace("512 TB", "512GB")
    segment = segment.replace("NVME", "SSD").replace("PCIE", "").replace("M.2", "").strip()
    match = re.search(r"(128|256|512|1TB)\s*GB?|1\s*TB", segment)
    if "1 TB" in segment or "1TB" in segment:
        return "1TB SSD"
    if match:
        value = match.group(0).replace(" ", "")
        value = "1TB" if "1TB" in value else re.sub(r"GB?$", "GB", value)
        return f"{value} SSD"
    return "512GB SSD"


def extract_ram(segment: str) -> str:
    match = re.search(r"(\d+)\s*GB", segment.upper())
    return f"{match.group(1)}GB RAM" if match else "8GB RAM"


def clean_processor(segment: str) -> str:
    segment = normalize_space(segment)
    replacements = {
        "Intel®": "Intel",
        "Core™": "Core",
        "AMD®": "AMD",
        "Ryzen™": "Ryzen",
        "Celeron®": "Celeron",
        "Inside ": "",
        " de 13.ª Gen.": "",
        " 13va. Gen.": "",
        " 13va.Gen.": "",
        " (Serie 1)": "",
    }
    for old, new in replacements.items():
        segment = segment.replace(old, new)
    match = re.search(
        r"(Intel\s+Celeron\s+N\d+|Intel\s+N100|Intel\s+Core\s+[iI]\d[-\w]*|AMD\s+Ryzen\s+\d+\s*[-\w]*|Ryzen\s+\d+\s*[-\w]*)",
        segment,
    )
    if match:
        return match.group(1).replace("AMD ", "").replace("Intel ", "Intel ")
    return segment.split(",")[0].strip()


def clean_model(segment: str) -> tuple[str, str]:
    segment = normalize_space(segment)
    segment = re.sub(r"^(Unknown|AGNEXUS)\b[\s\-:]*", "", segment, flags=re.I)
    segment = re.sub(r"^[A-Z]{1,3}:\s*\d+\s*", "", segment)
    segment = re.sub(r"^\d+\s*", "", segment)
    segment = re.sub(r"^Cod(?:igo)?[^ ]*\s*", "", segment, flags=re.I)
    segment = re.sub(r"^(Laptop|Laptopt/Tablet|Kit)\s+", "", segment, flags=re.I)

    brand = next((item for item in BRANDS if re.search(rf"\b{re.escape(item)}\b", segment, flags=re.I)), None)
    if not brand and re.search(r"\bENV\b", segment, flags=re.I):
        brand = "ENV"
    if not brand:
        brand = "ENV"

    match = re.search(rf"(?i)\b{re.escape(brand)}\b(.*)", segment)
    model = match.group(1).strip() if match else segment
    model = re.sub(r"^(Laptop|Kit)\s+", "", model, flags=re.I)
    model = re.split(r"(?i)\b(?:Intel|AMD|Ryzen|Celeron|N100|Core|RTX|[0-9]+GB|1TB|TB|SSD|HDD|RAM|TOUCH|W11|W10|WINDOWS|FHD|HD|IPS)\b", model)[0].strip()
    model = model.replace("(E1504F)", "E1504F").replace("VIVOBOOK", "VivoBook").replace("IDEAPAD", "IdeaPad").replace("INSPIRON", "Inspiron")
    model = re.sub(r"\s+", " ", model).strip(" /")
    return brand, model


def build_secondary(raw_title: str, processor_family: str, processor: str, display: str) -> str:
    raw = raw_title.lower()
    parts = ["Windows 11"]
    if "rtx" in raw:
        match = re.search(r"rtx\s*\d+", raw)
        parts.append(match.group(0).upper() if match else "Graficos dedicados")
    elif "ips" in raw:
        parts.append("Panel IPS")
    elif "wuxga" in raw:
        parts.append("Pantalla WUXGA")
    elif "120hz" in raw:
        parts.append("Panel Full HD 120Hz")
    elif "16gb" in raw:
        parts.append("16GB RAM")
    elif "wifi 6e" in raw:
        parts.append("Wi-Fi 6E")
    elif "wifi 6" in raw:
        parts.append("Wi-Fi 6")
    elif "docking" in raw or "2 en 1" in raw:
        parts.append("Convertible 2 en 1")
    elif processor_family == "Ryzen 7":
        parts.append("Chip Ryzen 7")
    else:
        parts.append("Perfil productivo")
    if "huella" in raw:
        parts.append("Lector de huellas")
    # Add processor and display
    parts.insert(1, processor)
    parts.insert(2, display)
    return " · ".join(parts[:5])  # Allow up to 5 parts


def build_description(processor_family: str, raw_title: str) -> str:
    raw = raw_title.lower()
    if "rtx" in raw:
        return "Muy conveniente para edición, diseño y tareas con impulso gráfico adicional."
    if "2 en 1" in raw or "docking" in raw:
        return "Una opción versátil para movilidad, clases y tareas diarias con formato táctil convertible."
    templates = {
        "Celeron": "Una entrada directa para tareas básicas con movilidad cómoda y compra rápida.",
        "Intel N100": "Pensada para oficina y gestión diaria con formato amplio y experiencia simple de comparar.",
        "Core i3": "Buena elección para estudio, oficina y productividad con imagen sobria y moderna.",
        "Core i5": "Sube de nivel con un rendimiento más sólido para oficina, estudio y multitarea real.",
        "Core i7": "Pensada para una jornada más ágil, cómoda y fluida en oficina, clases o home office.",
        "Ryzen 3": "Muy conveniente para quien busca movilidad, buena respuesta y almacenamiento sólido.",
        "Ryzen 5": "Una base equilibrada para productividad diaria, clases y trabajo con buena fluidez.",
        "Ryzen 7": "Excelente para productividad exigente con una configuración actual y muy competitiva.",
    }
    return templates.get(processor_family, "Equipo confiable para avanzar con trabajo, estudio y productividad diaria.")


def build_product(item: dict, index: int) -> dict:
    raw_title = item["title"]
    parts = [normalize_space(part) for part in raw_title.split("/") if normalize_space(part)]
    if len(parts) > 1:
        brand, model = clean_model(parts[0])
        processor = clean_processor(parts[1])
        ram = extract_ram(parts[2] if len(parts) > 2 else raw_title)
        storage = extract_storage(parts[3] if len(parts) > 3 else raw_title)
        display = extract_display(parts[4] if len(parts) > 4 else raw_title, raw_title)
    else:
        brand, model = clean_model(raw_title)
        processor = clean_processor(raw_title)
        if not processor:
            image_name = Path(item["image"]).name.replace("-", " ").replace("_", " ")
            processor = clean_processor(image_name)
        ram = extract_ram(raw_title)
        storage = extract_storage(raw_title)
        display = extract_display(raw_title)
    processor_family = normalize_processor_family(processor)
    title = f"{brand} {model} {processor} {ram} {storage} {display}".replace("  ", " ").strip()
    price = math.ceil((item["price"] + (90 if item["source"] == "pinsoft" else 70)) / 10) * 10
    return {
        "id": f"agn-{index:03d}",
        "title": title,
        "processor": processor.replace("AMD ", ""),
        "processorFamily": processor_family,
        "ram": ram,
        "storage": storage,
        "display": display,
        "secondary": build_secondary(item["title"], processor_family, processor.replace("AMD ", ""), display),
        "description": build_description(processor_family, item["title"]),
        "price": price,
    }


def filename_for(item: dict, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", item["title"].lower()).strip("-")
    slug = slug[:72].rstrip("-")
    return f"{index:02d}-{slug}.png"


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    pinsoft_products = []
    for url in PINSOFT_URLS:
        try:
            pinsoft_products.extend(parse_pinsoft_listing(fetch_text(url)))
        except Exception as exc:
            print(f"Advertencia: no se pudo obtener datos de Pinsoft desde {url}: {exc}")
    pinsoft_products = sorted(pinsoft_products, key=lambda item: item["price"])[:20]

    digital_products = []
    try:
        first = parse_digital_listing(fetch_text(DIGITALPC_FIRST_PAGE))
        digital_products.extend(first)
    except Exception as exc:
        print(f"Advertencia: no se pudo obtener datos de DigitalPC desde la página principal: {exc}")
        first = []

    page = 2
    while len(digital_products) < 20:
        url = DIGITALPC_URL_TEMPLATE.format(page=page)
        try:
            items = parse_digital_listing(fetch_text(url))
        except Exception as exc:
            print(f"Advertencia: no se pudo obtener datos de DigitalPC desde {url}: {exc}")
            break
        if not items:
            break
        digital_products.extend(items)
        page += 1
    digital_products = digital_products[:20]

    catalog = []
    files_to_keep = set()
    for index, item in enumerate(pinsoft_products + digital_products, start=1):
        product = build_product(item, index)
        image_name = filename_for(item, index)
        image_path = ASSETS_DIR / image_name
        product["image"] = f"assets/products/{image_name}"
        files_to_keep.add(image_name)

        best_image = (
            pinsoft_large_image(item["url"], item["image"])
            if item["source"] == "pinsoft"
            else digital_large_image(item["url"], item["image"])
        )
        if not download_file(best_image, image_path):
            if not image_path.exists():
                fallback = item["image"].replace("/150x150/", "/510x510/") if item["source"] == "pinsoft" else item["image"]
                download_file(fallback, image_path)

        catalog.append(product)

    for existing in ASSETS_DIR.glob("*"):
        if existing.is_file() and existing.name not in files_to_keep:
            existing.unlink()

    JSON_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    JS_PATH.write_text("window.AGNEXUS_PRODUCTS = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
