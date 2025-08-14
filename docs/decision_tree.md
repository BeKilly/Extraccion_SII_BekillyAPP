# Bekilly-sii — Árbol de decisiones

Este documento describe el flujo de decisiones que sigue Bekilly-sii para ejecutar la extracción, consolidación y cálculo de libros RCV y F29 desde el SII.

---

## Diagrama de flujo

```mermaid
flowchart TD
  A[Inicio: comando] -->|make run / venta / compra / ambos| B[Cargar .env y flags]
  B --> C{¿CLI/Makefile trae --no-headless,<br/>--rut o --tipos?}
  C -->|Sí| C1[Prioridad CLI sobre YAML]
  C -->|No| C2[Usar valores del YAML]
  C1 --> D[Leer YAML config]
  C2 --> D
  D --> E{¿paths/chrome definidos?}
  E -->|Sí| E1[Usar rutas provistas]
  E -->|No| E2[Autodetectar CHROME_BIN y chromedriver]
  E1 --> F
  E2 --> F[Normalizar rutas Windows→WSL y crear .venv si falta]
  F --> G{¿credenciales válidas? (cliente único o lista)}
  G -->|No| Gx[Error: sin credenciales] --> Z[Fin]
  G -->|Sí| H[Validar rango fechas]
  H --> I{¿anho_ini/mes_ini > anho_fin/mes_fin?}
  I -->|Sí| I1[Swap de rangos]
  I -->|No| I2[Continuar]
  I1 --> J
  I2 --> J
  J --> K{Seleccionar tipos: VENTA, COMPRA}
  K --> L[Loop clientes]
  L --> M[Loop tipos]
  M --> N[Inicializar Chrome (headless según flag)]
  N --> O[Ir a RCV y asegurar sesión]
  O --> P[Loop meses del rango]
  P --> Q[Set periodo y Consultar]
  Q --> R[Activar pestaña (VENTA/COMPRA)]
  R --> S{¿Panel visible?}
  S -->|No| S1[Reintentar activar] --> S
  S -->|Sí| T[Snapshot nombres previos en carpeta]
  T --> U[Descargar Resumen + Detalle]
  U --> V{¿Aparecieron archivos nuevos? (hasta 10s)}
  V -->|No| V1[Reintentar descarga]
  V -->|Sí| W[OK mes] 
  V1 --> V
  W --> P
  P -->|Terminan meses| X{¿Hubo error en algún mes?}
  X -->|Sí| X1[Guardar HTML/PNG debug y continuar]
  X -->|No| Y[Consolidación]
  Y --> Y1{¿Hay CSV en carpeta tipo?}
  Y1 -->|No| YN[Advertir sin CSV] --> AA[Fin cliente/tipo]
  Y1 -->|Sí| Y2[Unir, limpiar encabezados, convertir numéricos]
  Y2 --> Z1[Exportar Excel Consolidado]
  Z1 --> Z2{¿Archivo consolidado existe?}
  Z2 -->|Sí| Z3[Calcular: Total Neto, Signo Doc, Efecto Neto]
  Z2 -->|No| Z4[Omitir cálculo]
  Z3 --> AA[Fin cliente/tipo]
  Z4 --> AA
  AA --> AB{¿Quedan tipos/clientes?}
  AB -->|Sí| M
  AB -->|No| Z[Fin]
Reglas clave
Prioridad de parámetros: CLI > YAML > autodetección.

Rutas: convertir Windows a WSL si es necesario.

Credenciales: aceptar lista o único cliente, filtrar por --rut.

Rangos: intercambiar si están invertidos.

Extracción: reintentar activación de pestaña y descarga.

Consolidación: usar Encabezados.xlsx para reordenar.

Cálculo: aplicar signo negativo a notas de crédito (tipo doc 61).

Checklist rápido
Antes de correr:

Revisar sample_config.yaml (paths, chrome, credenciales).

Confirmar rango de fechas y tipos a procesar.

Durante la ejecución:

Usar --no-headless si necesitas ver el navegador.

Filtrar con --rut si solo es un cliente.

Después:

Revisar carpeta debug/ si hubo fallos.

Validar consolidado y cálculo en Excel generado.

markdown
Copiar
Editar

Con este formato, en GitHub se renderiza bonito: título, diagrama, reglas y checklist bien organizados.  
¿Quieres que te lo pase ya con **este formato exacto** para pegarlo en tu archivo?