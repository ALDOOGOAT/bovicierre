#!/usr/bin/env python3
"""Contraste WCAG 2.2 de los pares de tokens usados en frontend/src/styles.css (texto normal >=4.5, grande/UI >=3)."""
import sys
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4 for x in c]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True);return (la+.05)/(lb+.05)
PAIRS=[('texto/fondo','#1A231D','#F7F5EF',4.5),('secundario/superficie','#57635A','#FFFFFF',4.5),('secundario/fondo','#57635A','#F7F5EF',4.5),
('eyebrow tierra/fondo','#6B4F2E','#F7F5EF',4.5),('acción blanco/verde','#FFFFFF','#1E4D3A',4.5),('enlace verde/superficie','#1E4D3A','#FFFFFF',4.5),
('ok/ok-bg','#1E5B3E','#EAF4EC',4.5),('info/info-bg','#24507A','#EAF1F8',4.5),('warn/warn-bg','#7A5300','#FBF4E2',4.5),('error/error-bg','#9F2922','#FDF2F0',4.5),
('nav texto/sidebar','#D5E2D9','#123326',4.5),('nav grupo/sidebar','#9DB5A6','#123326',4.5),('sidebar subtítulo','#C9B48F','#123326',4.5),
('borde control/superficie','#8A8574','#FFFFFF',3.0),('borde control/superficie-2','#8A8574','#FBFAF6',3.0),('foco/superficie','#B37710','#FFFFFF',3.0),('foco sidebar','#F2C46B','#123326',3.0),
('resumen texto/verde','#CFE1D5','#173F2F',4.5),('botón tierra/verde','#123326','#F3EBDD',4.5),('uuid/superficie','#57635A','#FFFFFF',4.5),
# v4 ejecutivo (14-oct-2026): fondo cálido, cromo nocturno y oro
('v4 texto/fondo cálido','#17201A','#F4F2EE',4.5),('v4 secundario/fondo cálido','#55615A','#F4F2EE',4.5),('v4 eyebrow oro/fondo','#7C5A12','#F4F2EE',4.5),('v4 eyebrow oro/superficie','#7C5A12','#FFFFFF',4.5),
('v4 nav texto/noche','#D5E2D9','#0E2219',4.5),('v4 nav grupo/noche','#9DB5A6','#0E2219',4.5),('v4 subtítulo marca/noche','#C9B48F','#0E2219',4.5),('v4 nav texto/noche base','#D5E2D9','#050F0A',4.5),
('v4 eyebrow banda/velo','#E6C877','#081710',4.5),('v4 botón oro texto','#081710','#E6C877',4.5),('v4 voz activa','#7C5A12','#F6EDD3',4.5),('v4 foco/noche','#F2C46B','#0E2219',3.0),('v4 indicador oro/noche','#C9A24A','#0E2219',3.0)]
fail=0
for name,fg,bg,need in PAIRS:
    r=ratio(fg,bg);ok=r>=need;fail+=not ok
    print(f"{'OK ' if ok else 'FAIL'} {r:5.2f}:1 (mín {need}) {name} {fg} sobre {bg}")
sys.exit(1 if fail else 0)
