// La hoja de Sonner viaja empaquetada abajo; su <style> en línea lo quita el plugin de vite.config.ts (CSP style-src 'self').
import {Avisos} from './aviso';
import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import '@fontsource-variable/atkinson-hyperlegible-next';
import '@fontsource-variable/atkinson-hyperlegible-mono';
import '@fontsource-variable/big-shoulders-display';
import '@fontsource/big-shoulders-stencil-display/800';
import './styles.css';
import './identidad.css';
import 'sonner/dist/styles.css';
import './usabilidad.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/><Avisos/></React.StrictMode>);
