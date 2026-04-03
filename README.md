# AGNEXUS Landing Page

Sitio estático listo para GitHub Pages con una landing comercial para venta de laptops, catálogo combinado y filtros en frontend.

## Archivos principales

- `index.html`: estructura de la landing.
- `styles.css`: diseño responsive y visual.
- `app.js`: render del catálogo, búsqueda, filtros y cotización por WhatsApp.
- `products.json`: catálogo en JSON.
- `products.js`: catálogo listo para cargar en el navegador.
- `scripts/update_catalog.py`: actualización automática del catálogo e imágenes locales.
- `.github/workflows/deploy-pages.yml`: actualización y despliegue en GitHub Pages.

## Actualización del catálogo

El script `scripts/update_catalog.py`:

- extrae las 20 laptops más económicas de Pinsoft;
- extrae las 20 laptops más económicas de DigitalPCEcuador ordenadas por precio;
- recalcula el precio final con las reglas comerciales;
- descarga las imágenes a `assets/products/`;
- limpia imágenes viejas que ya no pertenezcan al catálogo;
- regenera `products.json` y `products.js`.

Ejecución manual:

```bash
python scripts/update_catalog.py
```

## Despliegue

El workflow de GitHub Actions:

- se ejecuta en cada push a `main` o `master`;
- permite ejecución manual;
- actualiza el catálogo cada lunes a las `12:00 UTC`;
- hace commit automático si cambian `products.json`, `products.js` o `assets/products/`;
- vuelve a desplegar el sitio en GitHub Pages.

## Nota

El proyecto usa rutas locales para las imágenes del catálogo y fallback visual desde `assets/laptop-placeholder.svg` si una imagen no carga.
