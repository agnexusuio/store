# Mejoras al Script de Catálogo de Laptops

## Cambios Realizados

El script `scripts/update_catalog.py` ha sido mejorado para garantizar que se obtengan las imágenes de las laptops con estrategias robustas de fallback.

### 1. **Descarga Mejorada de Archivos**
- **Validación de Tamaño**: Ahora valida que las imágenes descargadas tengan al menos 5KB (evita descargas de páginas de error)
- **Reintentos Aumentados**: De 2 a 3 intentos con esperas progresivas
- **Mejor Manejo de Errores**: Gestiona HTTP 429 (rate limiting) y otros errores con pausas exponenciales

```python
def download_file(url: str, target: Path, retries: int = 3) -> bool:
    # Validación de tamaño mínimo
    if len(content) < 5000:  # 5KB mínimo
        # Reintentar
```

### 2. **Estrategia de Fallback Multi-Nivel**

El script ahora intenta descargar imágenes en este orden:

1. **Imagen Grande Primaria**: Desde la fuente original (Pinsoft o DigitalPC)
   - Pinsoft: Intenta obtener desde `og:image` o página de detalle
   - DigitalPC: Busca `data-large_image` o `og:image`

2. **Fallback de Resolución**: Si la imagen grande falla
   - Pinsoft: Cambia de `/150x150/` a `/510x510/`
   - DigitalPC: Usa la URL de thumbnail original

3. **Búsqueda Alternativa**: Si ambas fallan
   - Busca imágenes similares usando DuckDuckGo o Bing
   - Busca por marca y modelo: `"{brand} {model} laptop"`
   - Función `search_alternative_image()` extrae URLs de resultados

4. **Último Recurso**: URL de thumbnail original
   - Como último intento antes de usar placeholder

### 3. **Nuevas Funciones**

#### `search_alternative_image(brand: str, model: str) -> str | None`
```python
def search_alternative_image(brand: str, model: str) -> str | None:
    """Intenta descargar imagen de fuente alternativa usando búsqueda."""
    search_term = f"{brand} {model} laptop"
    # Busca en DuckDuckGo y Bing
    # Extrae URLs de imágenes de los resultados
```

### 4. **Mejor Seguimiento y Reportes**

El script ahora reporta estadísticas de descargas:

```
============================================================
📊 Resumen de descargas:
  ✓ Éxito directo: 18/40
  ⚠ Fallback resolución: 1/40
  🔄 Imagen alternativa: 1/40
  ✗ Sin imagen: 0/40
============================================================
```

Indicadores en la salida:
- `✓` = Descarga exitosa desde fuente primaria
- `⚠` = Usó fallback de resolución
- `🔄` = Descargó imagen alternativa similar
- `✗` = Usará placeholder (pero se intenta todas las estrategias)

### 5. **Gestión de Imágenes Faltantes**

Si no se puede descargar imagen alguna:
- El catálogo se genera correctamente de todas formas
- El frontend usa `assets/laptop-placeholder.svg` como fallback visual
- El evento `onerror` en la imagen del navegador muestra el placeholder

## Uso

```bash
# Ejecución manual
python scripts/update_catalog.py

# O a través del workflow
# Se ejecuta automáticamente cada lunes a las 12:00 UTC
```

## Mejoras Visibles

### En el Frontend (`app.js`)
```javascript
image.addEventListener("error", () => {
  if (!image.src.endsWith(PLACEHOLDER_IMAGE)) {
    image.src = PLACEHOLDER_IMAGE;
  }
}, { once: true });
```

### En el Backend (`scripts/update_catalog.py`)
- Múltiples fuentes de imágenes
- Fallbacks inteligentes por similitud de modelo
- Búsqueda web como respaldo
- Validación de integridad de descarga
- Estadísticas detalladas

## Comportamiento Garantizado

✅ **Garantizado**:
- Siempre intenta obtener imagen específica del producto
- Si falla, busca versiones alternativas de la misma URL
- Si ambas fallan, busca imágenes similares por marca/modelo
- Si todo falla, el frontend muestra placeholder profesional

❌ **No se deja sin imagen**:
- El catálogo siempre se genera correctamente
- Si no hay imagen del producto, se usa placeholder visual
- El usuario ve siempre algo relevante

## Próximas Mejoras (Futuro)

- [ ] Caché local de imágenes descargadas
- [ ] Compresión de imágenes para reducir tamaño
- [ ] API de imágenes dedicada
- [ ] Proxy de imágenes para evitar hotlinking
- [ ] Imágenes por categoría/precio como fallback final
