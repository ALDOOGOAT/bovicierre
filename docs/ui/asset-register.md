# Registro de assets visuales

Rediseño S1, 12-oct-2026. Ejecutor: agente Claude Opus 5.5 (Claude Code 2.1.296) por encargo del usuario; revisión humana de Jared/Aldo **pendiente**. Todos los assets se sirven localmente desde `frontend/public/img/` o el bundle; sin hotlink, trackers ni fuentes remotas.

## Fotografías

| Asset | Origen | Autor / proveedor | Licencia y evidencia | Obtenido | Transformación | Destino |
|---|---|---|---|---|---|---|
| `login-ganado-general-teran-{960,1280}.{webp,jpg}` | [File:Ganado de General Terán.jpg](https://commons.wikimedia.org/wiki/File:Ganado_de_General_Ter%C3%A1n.jpg) (Wikimedia Commons), original 3456×2592 | Jorge.a.izaguirre (subida a Commons) | **Dominio público** según la página del archivo (`LicenseShortName: Public domain`, `Copyrighted: False`, `AttributionRequired: false`). Metadatos y SHA1/SHA256 del original: [asset-evidence/login-ganado-general-teran.json](asset-evidence/login-ganado-general-teran.json) | 2026-10-12 vía API de Commons | Recorte centrado (0.45, 0.6), desenfoque gaussiano 0.6 px para bajar peso, WebP q58/q60 y JPEG q64/q66 (Pillow 10.2) | Panel izquierdo del acceso, con degradado verde superpuesto; `alt=""` (decorativa) y crédito visible en el pie del panel |
| `sede-pastoreo-fillmore-{800,1600}.{webp,jpg}` | [File:Cattle grazing, Fillmore County, Minnesota.jpg](https://commons.wikimedia.org/wiki/File:Cattle_grazing,_Fillmore_County,_Minnesota.jpg), original 2048×1536 | Y1997xf11 (subida a Commons) | **Dominio público** (`LicenseShortName: Public domain`, `Copyrighted: False`). Evidencia: [asset-evidence/sede-pastoreo-fillmore.json](asset-evidence/sede-pastoreo-fillmore.json) | 2026-10-12 vía API de Commons | Recorte 8:3 centrado verticalmente al 42 %, WebP q74/q76, JPEG q70/q72 | Cabecera de "Selecciona una sede"; `alt=""` (decorativa) |

Huellas SHA256 de los archivos servidos:

| Archivo | Bytes | Dimensiones | SHA256 |
|---|---:|---|---|
| login-ganado-general-teran-1280.webp | 204,130 | 1280×1100 | `036496887ce99ffdcdefb3c4a93884304992ddbc30d9f4a36df3a1194be14564` |
| login-ganado-general-teran-1280.jpg | 248,519 | 1280×1100 | `fbab2ec791751f4be68d238c4f5e37dfe26b3d8485045845590d821782909cba` |
| login-ganado-general-teran-960.webp | 96,536 | 960×720 | `72575345ae2e74d24e8a735542cfbcbe6abb9044610d7c8f664eae7e370c210f` |
| login-ganado-general-teran-960.jpg | 121,378 | 960×720 | `c3db95b8fc61e0cd617f67e0b7e070964be87125da26c366dc0de67f62dea8bb` |
| sede-pastoreo-fillmore-1600.webp | 197,718 | 1600×600 | `5fffe4363c0a482bd28af25736515330cecd1479a77175e1f0b46519b2180380` |
| sede-pastoreo-fillmore-1600.jpg | 204,451 | 1600×600 | `77a2c6411db9dffc9114009477632bc0409153014ee5dd412c5d5f4e6d0e588f` |
| sede-pastoreo-fillmore-800.webp | 53,974 | 800×300 | `88bec48b39508c1fefec20c3e17a7cea0c0bd0eb63769b89cdd597de7b0bfca9` |
| sede-pastoreo-fillmore-800.jpg | 52,791 | 800×300 | `a759dae8703f959b094bf6a46f1a794d5134f415d065d5c1e337770359792e4b` |

Presupuesto de imagen destacada 150–300 KB: cumplido (máx. 249 KB en el fallback JPEG; el navegador moderno descarga el WebP de 96–204 KB según `sizes`). AVIF no se generó: el Pillow local no tiene codificador AVIF y no se instaló otro solo para esto.

Límites: las fotos son contexto editorial, **no** son evidencia ni retrato de animales registrados en el sistema. No se usan en fichas, tablas financieras ni comprobantes. "Dominio público" es lo declarado por Wikimedia Commons al 2026-10-12; se conserva el JSON de esa consulta.

## Marca e iconos

| Asset | Origen | Licencia |
|---|---|---|
| Marca bovina (`BrandMark` en `frontend/src/brand.tsx`, también en `.empty-mark` como SVG en CSS) | Diseño original geométrico de esta campaña (cabeza y cuernos simplificados); no imita sellos oficiales | Propia del proyecto |
| Iconos de navegación (`NavIcon`) | Trazos SVG originales 20×20 escritos en esta campaña | Propia del proyecto |
| `frontend/public/favicon.svg` | Sin cambios | Existente |

## Tipografía

| Asset | Origen | Licencia | Versión / huella |
|---|---|---|---|
| Inter Variable, subconjunto latin, ejes wght (`inter-latin-wght-normal.woff2`, 48 KB) | npm `@fontsource-variable/inter@5.3.0` (publicado 2026-07-19), fuente rsms/inter | SIL Open Font License 1.1 (archivo `LICENSE` del paquete) | SHA256 `3100e775e8616cd2611beecfa23a4263d7037586789b43f035236a2e6fbd4c62`; empaquetada por Vite, `font-display: swap`, fallback de sistema |
