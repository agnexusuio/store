const PRODUCTS = Array.isArray(window.AGNEXUS_PRODUCTS) ? window.AGNEXUS_PRODUCTS : [];
const WHATSAPP_NUMBER = "593992217314";
const PLACEHOLDER_IMAGE = "assets/laptop-placeholder.svg";
const PROJECTOR_PLACEHOLDER_IMAGE = "assets/projector-placeholder.svg";

const searchInput = document.querySelector("#searchInput");
const processorFilter = document.querySelector("#processorFilter");
const sortSelect = document.querySelector("#sortSelect");
const categorySelect = document.querySelector("#categorySelect");
const productsGrid = document.querySelector("#productsGrid");
const resultsCount = document.querySelector("#resultsCount");
const template = document.querySelector("#productCardTemplate");

const money = new Intl.NumberFormat("es-EC", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

function buildWhatsAppUrl(product) {
  const message = `Hola, quiero cotizar la ${product.title} por ${money.format(product.price)}. ¿Está disponible?`;
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
}

function compareBySort(a, b, sortValue) {
  if (sortValue === "price-desc") {
    return b.price - a.price;
  }

  if (sortValue === "name-asc") {
    return a.title.localeCompare(b.title, "es");
  }

  return a.price - b.price;
}

function createCard(product) {
  const fragment = template.content.cloneNode(true);
  const image = fragment.querySelector(".product-image");
  const processor = fragment.querySelector(".product-processor");
  const title = fragment.querySelector(".product-title");
  const price = fragment.querySelector(".product-price");
  const specs = fragment.querySelector(".product-specs");
  const description = fragment.querySelector(".product-description");
  const whatsapp = fragment.querySelector(".product-whatsapp");

  // Garantizar que siempre haya una imagen válida
  // Seleccionar placeholder según categoría
  const isProjector = (product.category && product.category === "proyectores") || (product.processorFamily && product.processorFamily.toLowerCase() === "proyector");
  const imageUrl = product.image || (isProjector ? PROJECTOR_PLACEHOLDER_IMAGE : PLACEHOLDER_IMAGE);
  image.src = imageUrl;
  image.alt = product.title;

  // Fallback si la imagen principal falla
  image.addEventListener("error", () => {
    if (!image.src.endsWith(PLACEHOLDER_IMAGE)) {
      console.warn(`Imagen no disponible para ${product.title}, usando placeholder`);
      image.src = PLACEHOLDER_IMAGE;
    }
  }, { once: true });

  // Fallback adicional: si el src está vacío
  if (!imageUrl || imageUrl.trim() === "") {
    image.src = PLACEHOLDER_IMAGE;
  }

  processor.textContent = product.processorFamily;
  title.textContent = product.title;
  price.textContent = money.format(product.price);
  specs.textContent = product.secondary;
  description.textContent = product.description;
  whatsapp.href = buildWhatsAppUrl(product);

  const external = fragment.querySelector(".product-external");
  if (external) {
    if (product.externalLink) {
      external.href = product.externalLink;
      external.style.display = "inline-block";
    } else {
      external.style.display = "none";
    }
  }

  // Mostrar badge si es proyector
  const badge = fragment.querySelector('.product-badge');
  if (badge) {
    if (isProjector) {
      badge.textContent = 'Proyector';
      badge.style.display = 'inline-block';
    } else {
      badge.style.display = 'none';
    }
  }

  return fragment;
}

function renderProducts() {
  const searchValue = (searchInput.value || "").trim().toLowerCase();
  const processorValue = processorFilter.value;
  const categoryValue = categorySelect ? categorySelect.value : "all";
  const sortValue = sortSelect.value;

  const filtered = PRODUCTS
    .filter((product) => {
      const productCategory = product.category || "laptops";
      const haystack = [
        product.title,
        product.processor,
        product.processorFamily,
        product.ram,
        product.storage,
        product.display,
        product.secondary,
        product.description
      ].join(" ").toLowerCase();

      const matchesSearch = !searchValue || haystack.includes(searchValue);
      const matchesProcessor = processorValue === "all" || product.processorFamily === processorValue;
      const matchesCategory = categoryValue === "all" || productCategory === categoryValue;
      return matchesSearch && matchesProcessor && matchesCategory;
    })
    .sort((a, b) => compareBySort(a, b, sortValue));

  productsGrid.innerHTML = "";

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = "<strong>No encontramos coincidencias.</strong><p>Prueba con otro procesador, menos palabras o un orden distinto.</p>";
    productsGrid.append(empty);
  } else {
    filtered.forEach((product) => {
      productsGrid.append(createCard(product));
    });
  }

  // Mostrar conteo con etiqueta según categoría seleccionada
  let label;
  if (categoryValue === "all") {
    label = "productos";
  } else if (categoryValue === "proyectores") {
    label = `proyector${filtered.length === 1 ? "" : "es"}`;
  } else {
    label = `laptop${filtered.length === 1 ? "" : "s"}`;
  }
  resultsCount.textContent = `${filtered.length} ${label} disponibles`;
}

function fillProcessorFilter() {
  // Reconstruir opciones para evitar duplicados
  processorFilter.innerHTML = "<option value=\"all\">Todos</option>";
  const families = [...new Set(PRODUCTS.map((product) => product.processorFamily))].sort((a, b) =>
    a.localeCompare(b, "es")
  );

  families.forEach((family) => {
    const option = document.createElement("option");
    option.value = family;
    option.textContent = family;
    processorFilter.append(option);
  });
}

function fillCategorySelect() {
  if (!categorySelect) return;
  // Obtener categorías desde el catálogo (por defecto 'laptops')
  const cats = [...new Set(PRODUCTS.map((p) => p.category || "laptops"))].sort();
  // Limpiar y añadir opción 'Todas'
  categorySelect.innerHTML = "<option value=\"all\">Todas</option>";
  cats.forEach((cat) => {
    const option = document.createElement("option");
    option.value = cat;
    // Etiqueta legible
    if (cat === "proyectores") option.textContent = "Proyectores";
    else if (cat === "laptops") option.textContent = "Laptops";
    else option.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
    categorySelect.append(option);
  });
}

fillCategorySelect();
fillProcessorFilter();
if (categorySelect) {
  categorySelect.addEventListener("change", () => {
    fillProcessorFilter();
    renderProducts();
  });
}

searchInput.addEventListener("input", renderProducts);
processorFilter.addEventListener("change", renderProducts);
sortSelect.addEventListener("change", renderProducts);
renderProducts();
