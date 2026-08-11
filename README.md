# Reservation Management Web Application

Aplicación web de gestión de reservas para **Fresh Fork Restaurant Group**, un grupo de tres restaurantes que hoy coordina reservas por teléfono, WhatsApp y cuadernos en papel. El proyecto responde a **RFP-001** y busca eliminar los dobles cupos y reducir el trabajo manual del personal de recepción, dando a cada sucursal un calendario compartido y un historial de clientes común.

## Estructura del repositorio

```
/src    → código fuente de la aplicación
/docs   → documentos de desarrollo (SOW, diagramas, backlog); docs/README.md es la tabla de contenido
/tests  → pruebas automatizadas
```

## Requisitos

El alcance, los objetivos de negocio y las métricas de éxito están definidos en el **Statement of Work**: [docs/SOW.md](./docs/SOW.md). Los requerimientos detallados se gestionan como GitHub Issues (`SHALL` + criterios de aceptación), trazados desde el SOW en su sección [Planning → Requirements](./docs/SOW.md#requirements).

Los diagramas de diseño (casos de uso, componentes, arquitectura AWS y modelo de datos) están en [docs/diagramas/](./docs/diagramas/).

## Cómo colaborar

1. Revisa [docs/SOW.md](./docs/SOW.md) para entender alcance y restricciones antes de proponer cambios.
2. Cada necesidad del RFP se traduce en un GitHub Issue siguiendo la convención descrita en [docs/backlog-workflow.md](./docs/backlog-workflow.md) (labels, milestones, plantilla de issue).
3. El código de la aplicación vive en `/src`; toda funcionalidad nueva debe venir acompañada de pruebas en `/tests`.
4. El trabajo se organiza en ramas `entregables/lab-XX` por entrega del curso; los documentos y diagramas correspondientes se agregan a `/docs` en la misma rama.
5. Abre un Pull Request contra `main` cuando el entregable esté listo para revisión.
