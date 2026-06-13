# Circular SBS N° B-2251-2024
## Regulación de Operaciones con Dinero Electrónico y Billeteras Digitales
**Fecha de emisión:** 10 de junio de 2024
**Vigencia:** 01 de julio de 2024
**Entidades aplicables:** Empresas de operaciones múltiples, emisores de dinero electrónico y empresas de servicios de pago (ESP)

---

## Artículo 1 — Objeto

La presente Circular regula los límites operativos, controles de seguridad y obligaciones de reporte aplicables a los servicios de dinero electrónico y billeteras digitales ofrecidos por entidades supervisadas por la SBS, en el marco de la Ley N° 29985 — Ley que regula las características básicas del dinero electrónico.

---

## Artículo 2 — Definiciones

**Dinero electrónico:** Valor monetario almacenado en soporte electrónico o magnético representativo de un crédito exigible a su emisor, emitido al recibo de fondos, aceptado como medio de pago y redimible en efectivo.

**Billetera digital:** Aplicación o plataforma que permite al usuario administrar dinero electrónico, realizar pagos, transferencias y consultas de saldo desde un dispositivo móvil o web.

**Operación P2P:** Transferencia de dinero electrónico entre usuarios de la misma plataforma (peer-to-peer) sin intervención de intermediario bancario tradicional.

**Cuenta básica:** Cuenta de dinero electrónico con funcionalidad limitada, asociada a un número de celular, sin requerir documentos adicionales al DNI.

---

## Artículo 3 — Límites operativos para cuentas básicas

Las cuentas básicas de dinero electrónico tendrán los siguientes límites:

| Concepto | Límite mensual | Límite por operación |
|----------|---------------|---------------------|
| Saldo máximo acumulado | S/ 2,000 | — |
| Transferencias enviadas P2P | S/ 1,000 | S/ 500 |
| Pagos a comercios | S/ 1,500 | S/ 500 |
| Retiros en efectivo | S/ 500 | S/ 200 |
| Recargas desde banco | S/ 2,000 | S/ 1,000 |

Las operaciones que superen estos límites requerirán la verificación de identidad reforzada mediante biometría facial y validación contra RENIEC.

---

## Artículo 4 — Límites operativos para cuentas verificadas

Las cuentas verificadas, cuyo titular haya completado el proceso KYC con biometría y validación de ingresos, tendrán los siguientes límites:

| Concepto | Límite mensual | Límite por operación |
|----------|---------------|---------------------|
| Saldo máximo acumulado | S/ 10,000 | — |
| Transferencias enviadas P2P | S/ 8,000 | S/ 3,000 |
| Pagos a comercios | S/ 10,000 | S/ 5,000 |
| Retiros en efectivo | S/ 3,000 | S/ 1,000 |
| Transferencias interbancarias | S/ 10,000 | S/ 5,000 |

---

## Artículo 5 — Controles de seguridad obligatorios

Los emisores de dinero electrónico deben implementar los siguientes controles:

a) **Autenticación de dos factores (2FA)** obligatoria para operaciones superiores a S/ 200 o cuando se detecte un cambio de dispositivo en los últimos 7 días.

b) **Análisis de velocidad (velocity checks):** Bloquear temporalmente la cuenta cuando se detecten más de **10 operaciones en 10 minutos** desde el mismo dispositivo.

c) **Geolocalización:** Para operaciones superiores a S/ 500, registrar la geolocalización del dispositivo y alertar si difiere en más de 100 km del patrón histórico del usuario.

d) **Listas de control:** Verificar en tiempo real contra listas OFAC, ONU y la lista de inhabilitados de la SBS antes de procesar cualquier transferencia internacional.

e) **Cifrado end-to-end** de todos los datos de transacción en tránsito y en reposo, bajo estándar AES-256.

---

## Artículo 6 — Reporte de operaciones inusuales en dinero electrónico

Adicionalmente a las obligaciones de la Circular SBS N° B-2244-2024, los emisores de dinero electrónico reportarán como inusuales:

a) Cuentas básicas que acumulen más de **S/ 1,800 en movimientos diarios** (90% del límite mensual en un día).

b) Patrones de **microtransacciones repetitivas**: más de 20 operaciones de monto inferior a S/ 10 en un período de 2 horas.

c) Transferencias circulares: flujo de fondos que regrese al origen en un plazo menor a 24 horas, involucrando tres (3) o más cuentas intermedias.

d) Operaciones realizadas desde rangos de IP asociados a servicios de anonimización (VPN, TOR).

---

## Artículo 7 — Interoperabilidad y acceso abierto

A partir del **01 de enero de 2025**, todos los emisores de dinero electrónico supervisados deberán:

a) Participar en el sistema de transferencias inmediatas interbancarias habilitado por el BCRP (Transferencias Inmediatas — TI).

b) Permitir transferencias salientes hacia cualquier entidad del sistema financiero nacional sin costo adicional para el usuario final para montos inferiores a S/ 200.

c) Exponer APIs de consulta de saldo bajo el estándar Open Banking definido por la SBS, previo consentimiento explícito del usuario.

---

## Artículo 8 — Protección al usuario

Los emisores de dinero electrónico están obligados a:

a) Responder reclamos de operaciones no reconocidas en un plazo máximo de **8 horas hábiles** para montos superiores a S/ 500.

b) Bloquear preventivamente la cuenta dentro de los **30 minutos** siguientes a la notificación de robo o pérdida de dispositivo por parte del usuario.

c) Mantener un seguro de depósito o fideicomiso equivalente al **100% del dinero electrónico en circulación**, con una entidad aprobada por la SBS.

---

## Artículo 9 — Vigencia

La presente Circular entra en vigencia el **01 de julio de 2024**. Los emisores existentes tendrán hasta el **30 de septiembre de 2024** para adecuarse a los nuevos límites y controles establecidos.

---

*Lima, 10 de junio de 2024*
*Superintendencia de Banca, Seguros y AFP*
