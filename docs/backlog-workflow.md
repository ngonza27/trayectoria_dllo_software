# 📋 GitHub Issues como Backlog de un RFP

Guía para transformar las necesidades de un RFP en un backlog estructurado usando Issues, Labels y Milestones de GitHub.

---

## Tabla de contenidos

- [La idea central](#la-idea-central)
- [Estructura de un Issue](#estructura-de-un-issue)
- [Labels recomendados](#labels-recomendados)
- [Milestones recomendados](#milestones-recomendados)
- [Flujo de trabajo](#flujo-de-trabajo)
- [GitHub Projects (Kanban)](#github-projects-kanban)
- [Convención de títulos](#convención-de-títulos)
- [Referencia rápida](#referencia-rápida)

---

## La idea central

Cada necesidad del RFP se convierte en un **Issue**. Los **Labels** clasifican de qué tipo es, y los **Milestones** agrupan por fase o entrega. El tablero Kanban (**Projects**) muestra el estado en tiempo real.

```
RFP  →  Issues  →  Labels + Milestones  →  Propuesta técnica y económica
```

---

## Estructura de un Issue

Cada issue representa **un requerimiento o tarea derivada del RFP**. Crea una plantilla en `.github/ISSUE_TEMPLATE/rfp.md`:

```markdown
## Descripción
¿Qué necesita el cliente? (en lenguaje del RFP)

## Requerimiento formal
El sistema SHALL [verbo + descripción + tolerancia].

## Criterios de aceptación
- [ ] Criterio 1
- [ ] Criterio 2

## Referencias
RFP sección:
```

> **Regla:** si no puedes redactar el `SHALL`, el issue no está listo — usa el label `clarificacion-pendiente` hasta tener la información del cliente.

---

## Labels recomendados

Crea estos labels desde **Issues → Labels → New label**.

| Label | Color | Uso |
|---|---|---|
| `rfp-funcional` | `#0075ca` | Capacidad que el sistema debe tener |
| `rfp-no-funcional` | `#7057ff` | Rendimiento, seguridad, disponibilidad |
| `rfp-restriccion` | `#e4820e` | Limitaciones técnicas o contractuales |
| `rfp-interfaz` | `#028090` | Integraciones con sistemas externos |
| `clarificacion-pendiente` | `#f9c513` | Necesidad ambigua — falta info del cliente |
| `tbd` | `#d93f0b` | Valor o criterio aún no definido |
| `propuesta` | `#0e8a16` | Issue incluido en la propuesta al cliente |

### Crear todos los labels de una vez (GitHub CLI)

```bash
gh label create "rfp-funcional"           --color "0075ca"
gh label create "rfp-no-funcional"        --color "7057ff"
gh label create "rfp-restriccion"         --color "e4820e"
gh label create "rfp-interfaz"            --color "028090"
gh label create "clarificacion-pendiente" --color "f9c513"
gh label create "tbd"                     --color "d93f0b"
gh label create "propuesta"               --color "0e8a16"
```

---

## Milestones recomendados

Crea los milestones desde **Issues → Milestones → New milestone**. Asígnales una fecha límite real.

| Milestone | Contenido |
|---|---|
| `M1 – Análisis del RFP` | Lectura del RFP, dudas, clarificaciones al cliente |
| `M2 – Requerimientos baseline` | Todos los SHALL definidos y aprobados |
| `M3 – Propuesta técnica` | Issues listos para incluir en la propuesta |
| `M4 – Propuesta económica` | Estimaciones de esfuerzo y costo por issue |
| `M5 – Entrega v1.0` | Primer conjunto de entregables del contrato |

### Crear milestones con GitHub CLI

```bash
gh api repos/:owner/:repo/milestones \
  --method POST \
  --field title="M1 – Análisis del RFP" \
  --field due_on="2026-07-15T00:00:00Z"
```

---

## Flujo de trabajo

```
RFP recibido
    │
    ▼
Leer sección del RFP
    │
    ▼
Crear Issue con título normalizado
    │
    ├── Asignar label (tipo)
    └── Asignar milestone (fase)
    │
    ▼
¿El requerimiento es claro?
    │
    ├── No ──→ label: clarificacion-pendiente
    │            └── Abrir hilo con el cliente en comentarios del issue
    │
    └── Sí ──→ Redactar SHALL en el issue
                └── Mover a M2 – Requerimientos baseline
                        │
                        ▼
                ¿Aprobado por el equipo?
                        │
                        └── Sí ──→ label: propuesta
                                    └── Incluir en M3 / M4
```

---

## GitHub Projects (Kanban)

Crea un **Project** vinculado al repositorio con estas columnas:

| Columna | Descripción |
|---|---|
| `Por revisar` | Issues recién creados desde el RFP |
| `En análisis` | Siendo estudiados por el equipo |
| `SHALL redactado` | Requerimiento formal escrito |
| `Aprobado` | Validado por el equipo o el cliente |
| `En propuesta` | Incluido en la propuesta técnica/económica |
| `Cerrado` | Entregado o descartado con justificación |

**Tips:**
- Filtra por label para ver solo un tipo (ej. todos los `rfp-no-funcional`).
- Filtra por milestone para ver el avance de una fase.
- Usa **Insights → Charts** para ver la velocidad de cierre de issues.

---

## Convención de títulos

Un título bien escrito evita confusión al leer el backlog:

```
[FUNCIONAL]      Procesamiento de pagos en tiempo real
[NO-FUNCIONAL]   Disponibilidad mínima del 99.5%
[INTERFAZ]       Integración con API bancaria externa
[RESTRICCIÓN]    Datos almacenados solo en servidores colombianos
[DUDA]           Sección 4.1 — ¿el cliente incluye soporte post-entrega?
```

### Crear un issue desde la terminal

```bash
gh issue create \
  --title "[FUNCIONAL] Procesamiento de pagos en tiempo real" \
  --label "rfp-funcional,propuesta" \
  --milestone "M2 – Requerimientos baseline" \
  --body "## Descripción
El RFP (sección 3.2) indica que el sistema debe procesar pagos sin intervención manual.

## Requerimiento formal
El sistema SHALL procesar transacciones de pago en tiempo real con una latencia máxima de 2 segundos.

## Criterios de aceptación
- [ ] Latencia medida bajo carga normal (≤ 200 transacciones/min)
- [ ] Prueba de integración con pasarela de pago aprobada

## Referencias
RFP sección: 3.2"
```

---

## Referencia rápida

| Elemento | Para qué sirve |
|---|---|
| **Issue** | Una necesidad o requerimiento del RFP |
| **Label** | Clasificar por tipo de requerimiento |
| **Milestone** | Agrupar por fase del proyecto |
| **Project** | Ver el estado global del backlog |
| **SHALL** | La única forma válida de redactar un requerimiento |
| **`clarificacion-pendiente`** | Señal de que el issue no puede avanzar sin respuesta del cliente |
| **`tbd`** | Valor o criterio que debe resolverse antes del baseline |

---

> Fuente de referencia: [NASA Systems Engineering Handbook — Apéndice C](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/)
