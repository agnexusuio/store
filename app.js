const PRODUCTS = Array.isArray(window.AGNEXUS_PRODUCTS) ? window.AGNEXUS_PRODUCTS : [];
const WHATSAPP_NUMBER = "593992217314";
const PLACEHOLDER_IMAGE = "assets/laptop-placeholder.svg";

const searchInput = document.querySelector("#searchInput");
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

  image.src = product.image || PLACEHOLDER_IMAGE;
  image.alt = product.title;
  image.addEventListener("error", () => {
    if (!image.src.endsWith(PLACEHOLDER_IMAGE)) {
      image.src = PLACEHOLDER_IMAGE;
    }
  }, { once: true });

  processor.textContent = product.processorFamily;
  title.textContent = product.title;
  price.textContent = money.format(product.price);
  specs.textContent = product.secondary;
  description.textContent = product.description;
  whatsapp.href = buildWhatsAppUrl(product);

  return fragment;
}

function renderProducts() {
  const searchValue = (searchInput.value || "").trim().toLowerCase();
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
      const matchesProcessor = processorValue === "all" || product.processorFamily === processorValue;
      return matchesSearch && matchesProcessor;
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

  resultsCount.textContent = `${filtered.length} laptop${filtered.length === 1 ? "" : "s"} disponibles`;
}

function fillProcessorFilter() {
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

fillProcessorFilter();
searchInput.addEventListener("input", renderProducts);
processorFilter.addEventListener("change", renderProducts);
sortSelect.addEventListener("change", renderProducts);
renderProducts();
