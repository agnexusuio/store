from __future__ import annotations

import html
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "products"
JSON_PATH = ROOT / "products.json"
JS_PATH = ROOT / "products.js"
PLACEHOLDER_IMAGE = "assets/laptop-placeholder.svg"

USER_AGENT = "Mozilla/5.0 (compatible; AGNEXUSCatalogBot/2.0)"
BRANDS = ["Asus", "Lenovo", "HP", "ACER", "MSI", "DELL", "ENV"]

PINSOFT_URLS = [
    "https://pinsoft.ec/laptop-notebook-portatiles/c-67.html",
    "https://pinsoft.ec/laptop-notebook-portatiles/c-67.html?page=2",
]

DIGITALPC_URL_TEMPLATE = "https://digitalpcecuador.com/categoria-producto/laptops/page/{page}/?orderby=price"
DIGITALPC_FIRST_PAGE = "https://digitalpcecuador.com/categoria-producto/laptops/?orderby=price"

# Datos reales extraidos de listados de AliExpress (2026-06-24/25)
ALIEXPRESS_PRODUCTS = [
    {
        "id": "ali-proj-001",
        "category": "Proyectores ANSI",
        "source": "aliexpress",
        "title": "Proyector Touyinger Z7 Linux HDR10+ 1080P 4K 1200 ANSI",
        "raw_title": "Proyector Touyinger Z7 con Sistema Linux, HDR10+, Full HD 1080P, Compatible con 4K, 1200 ANSI Lumenes, Enfoque Automatico, Portatil, para Interiores y Exteriores, Proyector Inteligente",
        "url": "https://es.aliexpress.com/item/1005012344223283.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/S3d7a3131d4b843dfa04c911f6f0a4d4cY.jpg_480x480q75.jpg_.avif",
        "price": 149.57,
        "lumenAnsi": 1200,
        "price_markup": 110,
        "secondary": "AliExpress · 1200 ANSI lumenes · Linux/HDR10+ · 1080P nativo",
        "description": "Proyector con alto brillo ANSI para cine en casa y presentaciones con buena luz ambiental.",
    },
    {
        "id": "ali-proj-002",
        "category": "Proyectores ANSI",
        "source": "aliexpress",
        "title": "Proyector Touyinger Z7 1080P 4K 1200 ANSI Smart TV",
        "raw_title": "Proyector Touyinger Z7 1080P HD 4K Smart TV 1200 ANSI Lumenes, Proyector de Video para Cine en Casa con Soporte de 360 Mini Beam",
        "url": "https://es.aliexpress.com/item/1005011624160042.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/See38149f0e58495390fda92645d35231z.jpg_480x480q75.jpg_.avif",
        "price": 137.13,
        "lumenAnsi": 1200,
        "price_markup": 110,
        "secondary": "AliExpress · 1200 ANSI lumenes · Smart TV · Soporte 360",
        "description": "Modelo compacto de alto brillo ANSI con enfoque en cine en casa y uso flexible.",
    },
    {
        "id": "ali-proj-003",
        "category": "Proyectores ANSI",
        "source": "aliexpress",
        "title": "Proyector Touyinger L9W Ultra 4K 1080P 1000 ANSI",
        "raw_title": "Proyector Touyinger L9W Ultra, Compatible con 4K 1080P, 2G+32G, 1000 ANSI, Enfoque Automatico y Correccion Trapezoidal, Wifi6, BT, Cine en Casa",
        "url": "https://es.aliexpress.com/item/1005012325397628.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/Sdaef64660af24482985388598ed7d453X.jpg_480x480q75.jpg_.avif",
        "price": 115.112,
        "lumenAnsi": 1000,
        "price_markup": 110,
        "secondary": "AliExpress · 1000 ANSI lumenes · Enfoque automatico · Wifi6/BT",
        "description": "Proyector de 1000 ANSI con conectividad moderna para entretenimiento y productividad.",
    },
    {
        "id": "ali-gls-001",
        "category": "Gafas IA",
        "source": "aliexpress",
        "title": "Gafas Lenovo IA 8K HD con traduccion en tiempo real",
        "raw_title": "Gafas Inteligentes Lenovo 8K HD con IA, Camara de 1600W, Traduccion en Tiempo Real, Llamadas Bluetooth, Grabacion de Audio y Video, Reproduccion de Musica, Gafas de Sol 2026",
        "url": "https://es.aliexpress.com/item/1005012432973677.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/S4b9441a4833f48d5adb0364234ab0c8fu.jpg_480x480q75.jpg_.avif",
        "price": 38.53,
        "price_markup": 70,
        "secondary": "AliExpress · Traduccion en tiempo real · Bluetooth · Camara integrada",
        "description": "Gafas inteligentes orientadas a traduccion de idiomas, llamadas y grabacion ligera.",
    },
    {
        "id": "ali-gls-002",
        "category": "Gafas IA",
        "source": "aliexpress",
        "title": "Gafas Xiaomi IA 8K HD con traduccion y dialogo",
        "raw_title": "Gafas Inteligentes Xiaomi con IA, Camara 8K HD, Luz LED, Traduccion, Dialogo, Grabacion de Video, Gafas de Sol Deportivas para Exteriores, Novedad 2026",
        "url": "https://es.aliexpress.com/item/1005012242662688.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/S03a2e1dbed874755bbd5413769ae0973q.jpg_480x480q75.jpg_.avif",
        "price": 32.09,
        "price_markup": 70,
        "secondary": "AliExpress · Traduccion y dialogo IA · Camara 8K HD · Luz LED",
        "description": "Gafas de traduccion IA pensadas para viajes y uso diario con funciones multimedia.",
    },
    {
        "id": "ali-gls-003",
        "category": "Gafas IA",
        "source": "aliexpress",
        "title": "Gafas IA con traduccion, bluetooth y control tactil",
        "raw_title": "Gafas Inteligentes con Traduccion IA, Lentes con Cambio de Color y Control Bluetooth, Llamadas Bluetooth, Gafas Inteligentes con IA",
        "url": "https://es.aliexpress.com/item/1005011803378382.html",
        "search_image": "https://ae-pic-a1.aliexpress-media.com/kf/Scb4e9678124b481a972e179480be4741x.jpg_480x480q75.jpg_.avif",
        "price": 26.35,
        "price_markup": 70,
        "secondary": "AliExpress · Traduccion IA · Control Bluetooth · Lentes fotocromaticos",
        "description": "Opcion accesible de gafas inteligentes con traduccion y funciones de conectividad.",
    },
]


def fetch_text(url: str, retries: int = 3) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def download_file(url: str, target: Path, retries: int = 3) -> bool:
    if not url:
        return False

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                content = response.read()
                if len(content) < 2048:
                    if attempt < retries - 1:
                        time.sleep(1.5 * (attempt + 1))
                    continue
                target.write_bytes(content)
            return target.exists() and target.stat().st_size >= 2048
        except Exception:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
    return False


def normalize_space(value: str) -> str:
    value = html.unescape(value or "")
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


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
    segment = normalize_space(segment)
    display = extract_display_from_text(segment)
    if display:
        return display
    if fallback_text:
        display = extract_display_from_text(normalize_space(fallback_text))
        if display:
            return display
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
        return match.group(1)
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
    model = re.split(
        r"(?i)\b(?:Intel|AMD|Ryzen|Celeron|N100|Core|RTX|[0-9]+GB|1TB|TB|SSD|HDD|RAM|TOUCH|W11|W10|WINDOWS|FHD|HD|IPS)\b",
        model,
    )[0].strip()
    model = re.sub(r"\s+", " ", model).strip(" /")
    return brand, model


def build_secondary(raw_title: str, processor_family: str, processor: str, display: str) -> str:
    raw = raw_title.lower()
    parts = ["Windows 11", processor, display]
    if "2 en 1" in raw or "docking" in raw:
        parts.append("Convertible 2 en 1")
    elif "ips" in raw:
        parts.append("Panel IPS")
    elif "120hz" in raw:
        parts.append("Panel Full HD 120Hz")
    elif processor_family == "Ryzen 7":
        parts.append("Chip Ryzen 7")
    else:
        parts.append("Perfil productivo")
    return " · ".join(parts)


def build_description(processor_family: str, raw_title: str) -> str:
    raw = raw_title.lower()
    if "rtx" in raw:
        return "Muy conveniente para edicion, diseno y tareas con impulso grafico adicional."
    if "2 en 1" in raw or "docking" in raw:
        return "Una opcion versatil para movilidad, clases y tareas diarias con formato tactil convertible."
    templates = {
        "Celeron": "Una entrada directa para tareas basicas con movilidad comoda y compra rapida.",
        "Intel N100": "Pensada para oficina y gestion diaria con formato amplio y experiencia simple de comparar.",
        "Core i3": "Buena eleccion para estudio, oficina y productividad con imagen sobria y moderna.",
        "Core i5": "Sube de nivel con un rendimiento mas solido para oficina, estudio y multitarea real.",
        "Core i7": "Pensada para una jornada mas agil, comoda y fluida en oficina, clases o home office.",
        "Ryzen 3": "Muy conveniente para quien busca movilidad, buena respuesta y almacenamiento solido.",
        "Ryzen 5": "Una base equilibrada para productividad diaria, clases y trabajo con buena fluidez.",
        "Ryzen 7": "Excelente para productividad exigente con una configuracion actual y muy competitiva.",
    }
    return templates.get(processor_family, "Equipo confiable para avanzar con trabajo, estudio y productividad diaria.")


def build_laptop_product(item: dict, index: int) -> dict:
    raw_title = item["title"]
    parts = [normalize_space(part) for part in raw_title.split("/") if normalize_space(part)]
    if len(parts) > 1:
        brand, model = clean_model(parts[0])
        processor = clean_processor(parts[1])
        ram = extract_ram(parts[2] if len(parts) > 2 else raw_title)
        storage = extract_storage(parts[3] if len(parts) > 3 else raw_title)
        display = extract_display(parts[4] if len(parts) > 4 else raw_title)
    else:
        brand, model = clean_model(raw_title)
        processor = clean_processor(raw_title)
        ram = extract_ram(raw_title)
        storage = extract_storage(raw_title)
        display = extract_display(raw_title)

    processor_family = normalize_processor_family(processor)
    title = f"{brand} {model} {processor} {ram} {storage} {display}".replace("  ", " ").strip()
    price = math.ceil((item["price"] + (90 if item["source"] == "pinsoft" else 70)) / 10) * 10

    return {
        "id": f"agn-{index:03d}",
        "source": item["source"],
        "category": "Laptops",
        "title": title,
        "processor": processor,
        "processorFamily": processor_family,
        "ram": ram,
        "storage": storage,
        "display": display,
        "secondary": build_secondary(item["title"], processor_family, processor, display),
        "description": build_description(processor_family, item["title"]),
        "price": price,
        "originUrl": item["url"],
        "sourcePrice": round(float(item["price"]), 2),
    }


def build_aliexpress_product(item: dict) -> dict:
    adjusted = math.ceil((float(item["price"]) + float(item["price_markup"])) / 10) * 10
    is_projector = item["id"].startswith("ali-proj")

    return {
        "id": item["id"],
        "source": "aliexpress",
        "category": item["category"],
        "title": item["title"],
        "processor": "AliExpress",
        "processorFamily": item["category"],
        "ram": "-",
        "storage": "-",
        "display": "-",
        "secondary": item["secondary"],
        "description": item["description"],
        "price": adjusted,
        "originUrl": item["url"],
        "sourcePrice": round(float(item["price"]), 2),
        "priceRule": f"+{int(item['price_markup'])} y redondeo a decena superior",
        "lumenAnsi": item.get("lumenAnsi") if is_projector else None,
        "rawTitle": item["raw_title"],
    }


def filename_for(title: str, prefix: str, ext: str = "jpg") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    slug = slug[:70].rstrip("-")
    return f"{prefix}-{slug}.{ext}"


def aliexpress_image_candidates(url: str) -> list[str]:
    if not url:
        return []
    candidates = [url]
    normalized = url
    normalized = normalized.replace("_480x480q75.jpg_.avif", "")
    normalized = normalized.replace("_480x480.png_.avif", "")
    normalized = normalized.replace("_640x640.jpg", "")
    if normalized != url:
        candidates.append(normalized)
    return [c for c in dict.fromkeys(candidates) if c]


def safe_existing_images() -> dict[str, str]:
    if not JSON_PATH.exists():
        return {}
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    existing = {}
    for item in data:
        product_id = item.get("id")
        image = item.get("image")
        if not product_id or not image:
            continue
        if image.startswith("assets/products/"):
            local_file = ROOT / image
            if local_file.exists() and local_file.is_file():
                existing[product_id] = image
    return existing


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    old_image_by_id = safe_existing_images()

    pinsoft_products = []
    for url in PINSOFT_URLS:
        try:
            pinsoft_products.extend(parse_pinsoft_listing(fetch_text(url)))
        except Exception as exc:
            print(f"Advertencia: no se pudo obtener datos de Pinsoft desde {url}: {exc}")
    pinsoft_products = sorted(pinsoft_products, key=lambda item: item["price"])[:20]

    digital_products = []
    try:
        digital_products.extend(parse_digital_listing(fetch_text(DIGITALPC_FIRST_PAGE)))
    except Exception as exc:
        print(f"Advertencia: no se pudo obtener datos de DigitalPC desde la pagina principal: {exc}")

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

    catalog: list[dict] = []
    files_to_keep = set()
    stats = {"downloaded": 0, "kept_old": 0, "placeholder": 0}

    laptop_items = pinsoft_products + digital_products
    for index, item in enumerate(laptop_items, start=1):
        product = build_laptop_product(item, index)
        image_name = filename_for(product["title"], f"{index:02d}")
        image_path = ASSETS_DIR / image_name

        candidates = []
        if item["source"] == "pinsoft":
            candidates.append(pinsoft_large_image(item["url"], item["image"]))
            candidates.append(item["image"].replace("/150x150/", "/510x510/"))
        else:
            candidates.append(digital_large_image(item["url"], item["image"]))
        candidates.append(item["image"])

        downloaded = any(download_file(candidate, image_path) for candidate in candidates if candidate)

        if downloaded:
            product["image"] = f"assets/products/{image_name}"
            files_to_keep.add(image_name)
            stats["downloaded"] += 1
        else:
            previous = old_image_by_id.get(product["id"])
            if previous:
                product["image"] = previous
                files_to_keep.add(Path(previous).name)
                stats["kept_old"] += 1
            else:
                product["image"] = PLACEHOLDER_IMAGE
                stats["placeholder"] += 1

        catalog.append(product)

    for ali in ALIEXPRESS_PRODUCTS:
        product = build_aliexpress_product(ali)
        image_name = filename_for(product["title"], product["id"])
        image_path = ASSETS_DIR / image_name

        candidates = aliexpress_image_candidates(ali["search_image"])
        downloaded = any(download_file(candidate, image_path) for candidate in candidates)

        if downloaded:
            product["image"] = f"assets/products/{image_name}"
            files_to_keep.add(image_name)
            stats["downloaded"] += 1
        else:
            previous = old_image_by_id.get(product["id"])
            if previous:
                product["image"] = previous
                files_to_keep.add(Path(previous).name)
                stats["kept_old"] += 1
            else:
                product["image"] = PLACEHOLDER_IMAGE
                stats["placeholder"] += 1

        catalog.append(product)

    for existing in ASSETS_DIR.glob("*"):
        if not existing.is_file():
            continue
        if existing.name.lower().endswith(".ini"):
            continue
        if existing.name not in files_to_keep:
            existing.unlink()

    JSON_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    JS_PATH.write_text("window.AGNEXUS_PRODUCTS = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    print("=" * 60)
    print(f"Catálogo generado: {len(catalog)} productos")
    print(f"Imágenes descargadas: {stats['downloaded']}")
    print(f"Imágenes conservadas del catálogo previo: {stats['kept_old']}")
    print(f"Productos con placeholder local: {stats['placeholder']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
