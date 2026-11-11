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

## Fotografías del rediseño v4 (14-oct-2026)

| Asset | Origen | Autor / proveedor | Licencia | Transformación | Destino |
|---|---|---|---|---|---|
| `inventario-corral-nuevo-mexico-{800,1600}.{webp,jpg}` | [File:Beef cattle in a feedlot in New Mexico.jpg](https://commons.wikimedia.org/wiki/File:Beef_cattle_in_a_feedlot_in_New_Mexico.jpg), original 7855×5653 | Quintin Soloviev (obra propia, Commons) | **CC0** declarado en Commons al 2026-10-14 | Recorte 8:3 centrado en el sujeto, redimensionado a 1600×600 y 800×300; WebP q74, JPEG q80 progresivo | Banda de **Inventario** (Posiciones, Animales, Recepción y entrega) |
| `dinero-subasta-ganado-{800,1600}.{webp,jpg}` | [File:Cattle Auction - 50639453351.jpg](https://commons.wikimedia.org/wiki/File:Cattle_Auction_-_50639453351.jpg), original 4272×2848 | Alabama Extension (vía Flickr, Commons) | **CC0** declarado en Commons al 2026-10-14 | Recorte 8:3 centrado en el sujeto, redimensionado a 1600×600 y 800×300; WebP q74, JPEG q80 progresivo | Banda de **Dinero** (Liquidaciones, Cobros y pagos, Gastos, Cartera, Margen, Simulador) |
| `control-rancho-nocturno-{800,1600}.{webp,jpg}` | [File:CG Merlo Ranch and Cattle Operation Survives through Challenges (20220610-FPAC-LSC-0541).jpg](https://commons.wikimedia.org/wiki/File:CG_Merlo_Ranch_and_Cattle_Operation_Survives_through_Challenges_(20220610-FPAC-LSC-0541).jpg), original 5397×3598 | USDA (USDAgov, Flickr; obra del gobierno de EE. UU.) | **Dominio público** declarado en Commons al 2026-10-14 | Recorte 8:3 centrado en el sujeto, redimensionado a 1600×600 y 800×300; WebP q74, JPEG q80 progresivo | Banda de **Control** (Periodos, Usuarios, Sincronización, Documentos, Ayuda) |
| `sede-corral-aretes-{960,1600}.{webp,jpg}` y `sede-corral-aretes-banda-{800,1600}.{webp,jpg}` | [File:Beef cattle in a feedlot in New Mexico.jpg](https://commons.wikimedia.org/wiki/File:Beef_cattle_in_a_feedlot_in_New_Mexico.jpg), derivado de la miniatura de 3840 px de Commons (original 7855×5653) | Quintin Soloviev (obra propia, Commons) | **CC0** declarado en Commons al 2026-11-11; evidencia `asset-evidence/sede-corral-aretes.json` | Recorte vertical 4:5 centrado en los dos becerros con arete (960×1200 y 1600×2000) y banda 2:1 para tablet y celular (800×400 y 1600×800); WebP q74, JPEG q80 progresivo | Pantalla **Selecciona una sede** (reemplaza a `sede-pastoreo-fillmore`, 2026-11-11) |

| Archivo | Bytes | Dimensiones | SHA256 |
|---|---:|---|---|
| inventario-corral-nuevo-mexico-1600.webp | 205,712 | 1600×600 | `818adee5d94bbd21196575b1cf8c3823bd0e32e0c2cdd458571bb78fa7e39af5` |
| inventario-corral-nuevo-mexico-1600.jpg | 265,664 | 1600×600 | `117512807968efd4907101b820a209547ebe9b36327c7c5572b011fd2c63d757` |
| inventario-corral-nuevo-mexico-800.webp | 60,906 | 800×300 | `2ce8d2cac0a994faa267f1ea1ca5eefb3a39a4f2d1652e2664d3b5e854b84b1f` |
| inventario-corral-nuevo-mexico-800.jpg | 75,654 | 800×300 | `12454db1cc86b4bc9bd3345ca3fe7652b7d578f6c71429660b62df4df6ced37a` |
| dinero-subasta-ganado-1600.webp | 89,416 | 1600×600 | `b3bae5403bc505252a3b09b63a91d482f93f7aab2d0147aaabb0b811f4fc4f90` |
| dinero-subasta-ganado-1600.jpg | 162,071 | 1600×600 | `723bc79233557ec37feb2d5171beab52387591f8946d2f8c2051152b823cf93f` |
| dinero-subasta-ganado-800.webp | 36,126 | 800×300 | `7ed3cc3401e93e3739770c965b380be4c55d3bac9846a6ebd9eecc590303f617` |
| dinero-subasta-ganado-800.jpg | 55,343 | 800×300 | `6cc693fd9f279edbd50b36507197f07b1f1c057af03afe870ff9b5df90435705` |
| control-rancho-nocturno-1600.webp | 123,012 | 1600×600 | `6c540250a3b7fd6df08da83db916429b9a139104d2055eff7b834f02c297be93` |
| control-rancho-nocturno-1600.jpg | 181,648 | 1600×600 | `e567ef561e948ea418ac9f514a4cd5c5169c81769d35afee65bbe56a2fcf7849` |
| control-rancho-nocturno-800.webp | 32,218 | 800×300 | `c973a32f42c2f96bb70f18bf803b87853e20de949b18bcbc36bde9dc1e88778f` |
| control-rancho-nocturno-800.jpg | 46,222 | 800×300 | `1b5abc82a61e0da16789922cc7033114430277b6d28db2e23d460d41ef060b62` |

Criterio: sólo dominio público o CC0 (sin atribución obligatoria ni copyleft al recortar); se evitó retratar personas identificables de frente. Son contexto editorial, no evidencia de animales registrados.

## Videos de uso (14-oct-2026)

| Asset | Origen | Licencia |
|---|---|---|
| `frontend/public/videos/{compra,recepcion,venta-cobro,tablero}.mp4` (H.264 1280×720, 11–53 s) | Grabación propia del producto con Playwright en Chrome real, datos sintéticos DEMO (`DEMO Rancho Video …`, aretes `DEMO-VID-…`) | Propia del proyecto |
| `….vtt` | Subtítulos WebVTT en español generados en el instante de cada paso grabado | Propia del proyecto |
| `…-poster.jpg` | Fotograma del propio video (segundo 4.2) | Propia del proyecto |

Herramienta auxiliar instalada: `ffmpeg` de Playwright (`npx playwright install ffmpeg`, en `~/.cache/ms-playwright`), necesario para grabar; la conversión a MP4 usa el `ffmpeg` del sistema.

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

### Huellas de `sede-corral-aretes` (2026-11-11)
| Archivo | Bytes | Tamaño | SHA-256 |
|---|---|---|---|
| sede-corral-aretes-1600.webp | 660,702 | 1600×2000 | `0847427c8ec1e049fe3abfad70e672a52c2a106d5358668505115b03b0f7f700` |
| sede-corral-aretes-1600.jpg | 784,104 | 1600×2000 | `afd1253b556142334f4609ffb90b79fa7a551111e68eb7b4ad785495156cd786` |
| sede-corral-aretes-960.webp | 171,256 | 960×1200 | `43d4eeeeee743363b7b49a4234fc63cf42b1bee8a1da0dcec505deeb104de857` |
| sede-corral-aretes-960.jpg | 249,617 | 960×1200 | `c97a56b1e65caf676382f1a4d8ae592503a9e93fd52bf61fbec04428ab4f8154` |
| sede-corral-aretes-banda-1600.webp | 238,266 | 1600×800 | `47d20b8792e51d1de36ee4d0b44c788c7a1a834eac4dad3702bf9716d31c13ef` |
| sede-corral-aretes-banda-1600.jpg | 324,680 | 1600×800 | `e89fada371feba89af1d0b6553ceff55a8a0b7bce1c4dab856e4019a3b86b351` |
| sede-corral-aretes-banda-800.webp | 71,954 | 800×400 | `ae512fe0b84f526575e9a601c1d34be2a916b1602a6adfb6bb975fccb83b5be6` |
| sede-corral-aretes-banda-800.jpg | 93,171 | 800×400 | `42798de8ef21344096b6205258d581c5a5f7b0b99cdacedbea706723ddcc5440` |
