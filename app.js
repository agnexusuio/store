const PRODUCTS = Array.isArray(window.AGNEXUS_PRODUCTS) ? window.AGNEXUS_PRODUCTS : [];
const WHATSAPP_NUMBER = "593992217314";
const PLACEHOLDER_IMAGE = "assets/laptop-placeholder.svg";

const searchInput = document.querySelector("#searchInput");
const productTypeFilter = document.querySelector("#productTypeFilter");
const processorFilter = document.querySelector("#processorFilter");
const sortSelect = document.querySelector("#sortSelect");
const productsGrid = document.querySelector("#productsGrid");
const resultsCount = document.querySelector("#resultsCount");
const template = document.querySelector("#productCardTemplate");

const money = new Intl.NumberFormat("es-EC", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const HIDDEN_ORIGIN_WORDS = /\b(aliexpress|amazon|mercadolibre|pinsoft|digitalpc|digitalpcecuador)\b/gi;

function hideOriginText(value) {
  if (!value) {
    return "";
  }

  return value
    .replace(HIDDEN_ORIGIN_WORDS, "")
    .replace(/\s*[·|,-]\s*[·|,-]*/g, " · ")
    .replace(/^[·|,\-\s]+|[·|,\-\s]+$/g, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

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

function getProductType(product) {
  return product.category || "Laptops";
}

function isLaptop(product) {
  return getProductType(product).toLowerCase() === "laptops";
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
  const imageUrl = product.image || PLACEHOLDER_IMAGE;
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

  processor.textContent = hideOriginText(product.processorFamily);
  title.textContent = product.title;
  price.textContent = money.format(product.price);
  specs.textContent = hideOriginText(product.secondary);
  description.textContent = hideOriginText(product.description);
  whatsapp.href = buildWhatsAppUrl(product);

  return fragment;
}

function renderProducts() {
  const searchValue = (searchInput.value || "").trim().toLowerCase();
  const typeValue = productTypeFilter.value;
  const processorValue = processorFilter.value;
  const sortValue = sortSelect.value;

  const filtered = PRODUCTS
    .filter((product) => {
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
      const matchesType = typeValue === "all" || getProductType(product) === typeValue;
      const matchesProcessor = !isLaptop(product) || processorValue === "all" || product.processorFamily === processorValue;
      return matchesSearch && matchesType && matchesProcessor;
    })
    .sort((a, b) => compareBySort(a, b, sortValue));

  productsGrid.innerHTML = "";

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = "<strong>No encontramos coincidencias.</strong><p>Prueba con otro tipo de producto, procesador u orden de resultados.</p>";
    productsGrid.append(empty);
  } else {
    filtered.forEach((product) => {
      productsGrid.append(createCard(product));
    });
  }

  resultsCount.textContent = `${filtered.length} producto${filtered.length === 1 ? "" : "s"} disponibles`;
}

function fillProcessorFilter() {
  const families = [...new Set(PRODUCTS.filter(isLaptop).map((product) => product.processorFamily))].sort((a, b) =>
    a.localeCompare(b, "es")
  );

  families.forEach((family) => {
    const option = document.createElement("option");
    option.value = family;
    option.textContent = family;
    processorFilter.append(option);
  });
}

function fillProductTypeFilter() {
  const categories = [...new Set(PRODUCTS.map((product) => getProductType(product)))].sort((a, b) =>
    a.localeCompare(b, "es")
  );

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    productTypeFilter.append(option);
  });
}

fillProductTypeFilter();
fillProcessorFilter();
searchInput.addEventListener("input", renderProducts);
productTypeFilter.addEventListener("change", renderProducts);
processorFilter.addEventListener("change", renderProducts);
sortSelect.addEventListener("change", renderProducts);
renderProducts();
