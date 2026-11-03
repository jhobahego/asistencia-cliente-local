# Tarifas, fletes y cobertura — TransLogix Colombia S.A.S.

> Datos operativos internos. Fuente: `matriz_tarifas_y_fletes.csv` (25 rutas) y `directorio_cobertura_y_tiempos.json` (31 municipios).
> Los valores están en pesos colombianos (COP) y se transcriben tal como aparecen en los archivos de origen. La matriz de tarifas del CSV es la fuente principal para rutas y tiempos de entrega; cuando el directorio de cobertura traía un tiempo distinto para un municipio con ruta en el CSV, se ajustó al valor del CSV.

## Cómo leer el tarifario

### ¿Qué campos trae la matriz de tarifas?

La matriz tiene una fila por ruta y estos campos: código de trayecto, ciudad y departamento de origen, ciudad y departamento de destino, tipo de cobertura, tarifa base de kilo real en COP, tarifa base de kilo volumétrico en COP, factor divisor volumétrico, flete mínimo en COP, porcentaje de seguro, seguro mínimo en COP, recargo de cadena de frío en porcentaje, recargo de mercancía peligrosa en COP, tiempo de entrega estimado en horas y observaciones de la ruta.

### ¿Cuáles son los rangos del tarifario?

Las 25 rutas comparten el mismo factor divisor volumétrico: 4.000. La tarifa de kilo real va de 1.050 COP (Pereira - Manizales) a 2.650 COP (Bogotá - Quibdó), y la de kilo volumétrico va de 1.200 COP a 2.850 COP. El flete mínimo va de 14.000 COP a 30.000 COP. El porcentaje de seguro es del 1% en todas las rutas, con seguro mínimo entre 3.000 COP y 5.000 COP según la ruta. El recargo de cadena de frío va del 20% al 35%, y el recargo de mercancía peligrosa va de 35.000 COP a 75.000 COP. Los tiempos de entrega estimados son de 24, 48, 72 o 96 horas.

### ¿Qué campos trae el directorio de cobertura?

El directorio tiene una fila por municipio y estos campos: código DANE, municipio, departamento, tipo de cobertura, tiempo de entrega estándar en horas, disponibilidad de servicio Same Day, disponibilidad de servicio refrigerado, peso máximo por paquete en kilogramos, volumen máximo en metros cúbicos, hub operativo asignado, frecuencia de despacho y restricciones operativas.

### ¿Qué municipios no tienen Same Day ni servicio refrigerado?

El servicio Same Day no está disponible en Rionegro, Palmira, Buenaventura, Cartagena, Santa Marta, Bucaramanga, Floridablanca, Girón, Manizales, Armenia, Cúcuta, Pasto, Ipiales, Villavicencio, Neiva, Florencia, Montería, Valledupar, Riohacha y Quibdó. El servicio refrigerado no está disponible en Ipiales, Florencia y Quibdó. Los municipios sin servicio refrigerado tampoco tienen Same Day.

## Tarifas por ruta

### Ruta Bogotá D.C. → Medellín (TLX-BOG-MED-001)

De Bogotá D.C. (Cundinamarca) a Medellín (Antioquia), cobertura Urbana Principal. El kilo real cuesta 1.450 COP y el kilo volumétrico 1.600 COP, con divisor volumétrico de 4.000. El flete mínimo es de 18.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Ruta de alto flujo por el corredor Bogotá-Medellín. Admite servicio Same Day si el despacho se realiza antes de las 09:00 a. m.

### Ruta Bogotá D.C. → Cali (TLX-BOG-CLO-002)

De Bogotá D.C. (Cundinamarca) a Cali (Valle del Cauca), cobertura Urbana Principal. El kilo real cuesta 1.500 COP y el kilo volumétrico 1.650 COP, con divisor volumétrico de 4.000. El flete mínimo es de 19.000 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Tránsito continuo vía La Línea. Sujeto a restricciones climáticas en el paso de montaña.

### Ruta Bogotá D.C. → Barranquilla (TLX-BOG-BAQ-003)

De Bogotá D.C. (Cundinamarca) a Barranquilla (Atlántico), cobertura Urbana Principal. El kilo real cuesta 1.850 COP y el kilo volumétrico 2.050 COP, con divisor volumétrico de 4.000. El flete mínimo es de 22.000 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 48 horas.

Corredor Ruta del Sol y Troncal del Magdalena. Requiere monitoreo constante de temperatura por el clima cálido.

### Ruta Bogotá D.C. → Cartagena (TLX-BOG-CTG-004)

De Bogotá D.C. (Cundinamarca) a Cartagena (Bolívar), cobertura Urbana Principal. El kilo real cuesta 1.900 COP y el kilo volumétrico 2.100 COP, con divisor volumétrico de 4.000. El flete mínimo es de 23.000 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 48 horas.

Servicio directo a Zona Franca Mamonal y a bodegas urbanas.

### Ruta Bogotá D.C. → Bucaramanga (TLX-BOG-BGA-005)

De Bogotá D.C. (Cundinamarca) a Bucaramanga (Santander), cobertura Urbana Principal. El kilo real cuesta 1.400 COP y el kilo volumétrico 1.550 COP, con divisor volumétrico de 4.000. El flete mínimo es de 17.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Ruta activa por el Cañón del Chicamocha y Barbosa, con salidas diarias nocturnas.

### Ruta Bogotá D.C. → Pereira (TLX-BOG-PEI-006)

De Bogotá D.C. (Cundinamarca) a Pereira (Risaralda), cobertura Urbana Principal. El kilo real cuesta 1.420 COP y el kilo volumétrico 1.580 COP, con divisor volumétrico de 4.000. El flete mínimo es de 18.000 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Pereira es el hub principal del Eje Cafetero y distribuye regionalmente hacia Manizales y Armenia.

### Ruta Bogotá D.C. → Cúcuta (TLX-BOG-CUC-007)

De Bogotá D.C. (Cundinamarca) a Cúcuta (Norte de Santander), cobertura Frontera. El kilo real cuesta 2.100 COP y el kilo volumétrico 2.300 COP, con divisor volumétrico de 4.000. El flete mínimo es de 25.000 COP. El seguro es del 1% con mínimo de 4.500 COP. El recargo por cadena de frío es del 30% y el recargo por mercancía peligrosa es de 60.000 COP. Tiempo de entrega estimado: 48 horas.

Zona fronteriza. Exige manifiesto de carga detallado para las inspecciones de la DIAN y la Polfa.

### Ruta Bogotá D.C. → Pasto (TLX-BOG-PSO-008)

De Bogotá D.C. (Cundinamarca) a Pasto (Nariño), cobertura Frontera. El kilo real cuesta 2.250 COP y el kilo volumétrico 2.450 COP, con divisor volumétrico de 4.000. El flete mínimo es de 26.000 COP. El seguro es del 1% con mínimo de 4.500 COP. El recargo por cadena de frío es del 30% y el recargo por mercancía peligrosa es de 60.000 COP. Tiempo de entrega estimado: 72 horas.

Corredor Sur, con restricciones frecuentes por paso de montaña y novedades viales.

### Ruta Bogotá D.C. → Ipiales (TLX-BOG-IPI-009)

De Bogotá D.C. (Cundinamarca) a Ipiales (Nariño), cobertura Frontera. El kilo real cuesta 2.400 COP y el kilo volumétrico 2.600 COP, con divisor volumétrico de 4.000. El flete mínimo es de 28.000 COP. El seguro es del 1% con mínimo de 5.000 COP. El recargo por cadena de frío es del 30% y el recargo por mercancía peligrosa es de 65.000 COP. Tiempo de entrega estimado: 72 horas.

Punto fronterizo de Rumichaca, entre Colombia y Ecuador. Exige declaración de tránsito internacional cuando aplique.

### Ruta Bogotá D.C. → Villavicencio (TLX-BOG-VVC-010)

De Bogotá D.C. (Cundinamarca) a Villavicencio (Meta), cobertura Urbana Principal. El kilo real cuesta 1.350 COP y el kilo volumétrico 1.500 COP, con divisor volumétrico de 4.000. El flete mínimo es de 16.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 40.000 COP. Tiempo de entrega estimado: 24 horas.

Puerta de entrada a los Llanos Orientales. Sujeto a cierres preventivos en la vía al Llano.

### Ruta Medellín → Bogotá D.C. (TLX-MED-BOG-011)

De Medellín (Antioquia) a Bogotá D.C. (Cundinamarca), cobertura Urbana Principal. El kilo real cuesta 1.450 COP y el kilo volumétrico 1.600 COP, con divisor volumétrico de 4.000. El flete mínimo es de 18.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Ruta inversa principal, con frecuencia de salida cada 4 horas.

### Ruta Medellín → Cali (TLX-MED-CLO-012)

De Medellín (Antioquia) a Cali (Valle del Cauca), cobertura Urbana Principal. El kilo real cuesta 1.550 COP y el kilo volumétrico 1.700 COP, con divisor volumétrico de 4.000. El flete mínimo es de 19.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Conexión Pacífico-Occidente con cobertura directa.

### Ruta Medellín → Barranquilla (TLX-MED-BAQ-013)

De Medellín (Antioquia) a Barranquilla (Atlántico), cobertura Urbana Principal. El kilo real cuesta 1.750 COP y el kilo volumétrico 1.950 COP, con divisor volumétrico de 4.000. El flete mínimo es de 21.000 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 48 horas.

Corredor Antioquia - Costa Atlántica vía Caucasia y Planeta Rica.

### Ruta Cali → Bogotá D.C. (TLX-CLO-BOG-014)

De Cali (Valle del Cauca) a Bogotá D.C. (Cundinamarca), cobertura Urbana Principal. El kilo real cuesta 1.500 COP y el kilo volumétrico 1.650 COP, con divisor volumétrico de 4.000. El flete mínimo es de 19.000 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Salida desde el hub de Yumbo y Palmira hacia el centro del país.

### Ruta Cali → Buenaventura (TLX-CLO-BUN-015)

De Cali (Valle del Cauca) a Buenaventura (Valle del Cauca), cobertura Trayecto Especial. El kilo real cuesta 1.300 COP y el kilo volumétrico 1.450 COP, con divisor volumétrico de 4.000. El flete mínimo es de 17.000 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 55.000 COP. Tiempo de entrega estimado: 24 horas.

Corredor portuario. Maneja carga de importación y exportación, y contenedores sueltos.

### Ruta Barranquilla → Santa Marta (TLX-BAQ-SMR-016)

De Barranquilla (Atlántico) a Santa Marta (Magdalena), cobertura Urbana Principal. El kilo real cuesta 1.100 COP y el kilo volumétrico 1.250 COP, con divisor volumétrico de 4.000. El flete mínimo es de 15.000 COP. El seguro es del 1% con mínimo de 3.000 COP. El recargo por cadena de frío es del 20% y el recargo por mercancía peligrosa es de 40.000 COP. Tiempo de entrega estimado: 24 horas.

Vía Ciénaga y Troncal del Caribe. Servicio Same Day disponible.

### Ruta Barranquilla → Cartagena (TLX-BAQ-CTG-017)

De Barranquilla (Atlántico) a Cartagena (Bolívar), cobertura Urbana Principal. El kilo real cuesta 1.150 COP y el kilo volumétrico 1.300 COP, con divisor volumétrico de 4.000. El flete mínimo es de 15.500 COP. El seguro es del 1% con mínimo de 3.000 COP. El recargo por cadena de frío es del 20% y el recargo por mercancía peligrosa es de 40.000 COP. Tiempo de entrega estimado: 24 horas.

Vía al Mar y Cordialidad, con conexión interportuaria diaria.

### Ruta Bucaramanga → Cúcuta (TLX-BGA-CUC-018)

De Bucaramanga (Santander) a Cúcuta (Norte de Santander), cobertura Frontera. El kilo real cuesta 1.600 COP y el kilo volumétrico 1.800 COP, con divisor volumétrico de 4.000. El flete mínimo es de 20.000 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 24 horas.

Tránsito por el Páramo de Berlín. Exige embalaje térmico para productos sensibles.

### Ruta Pereira → Manizales (TLX-PEI-MZL-019)

De Pereira (Risaralda) a Manizales (Caldas), cobertura Urbana Principal. El kilo real cuesta 1.050 COP y el kilo volumétrico 1.200 COP, con divisor volumétrico de 4.000. El flete mínimo es de 14.000 COP. El seguro es del 1% con mínimo de 3.000 COP. El recargo por cadena de frío es del 20% y el recargo por mercancía peligrosa es de 35.000 COP. Tiempo de entrega estimado: 24 horas.

Conurbación del Eje Cafetero, con entregas express intradía.

### Ruta Bogotá D.C. → Neiva (TLX-BOG-NVA-020)

De Bogotá D.C. (Cundinamarca) a Neiva (Huila), cobertura Urbana Principal. El kilo real cuesta 1.500 COP y el kilo volumétrico 1.680 COP, con divisor volumétrico de 4.000. El flete mínimo es de 18.500 COP. El seguro es del 1% con mínimo de 3.500 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 45.000 COP. Tiempo de entrega estimado: 24 horas.

Ruta Sur vía Girardot y Espinal, con cobertura completa al Huila.

### Ruta Bogotá D.C. → Florencia (TLX-BOG-FLA-021)

De Bogotá D.C. (Cundinamarca) a Florencia (Caquetá), cobertura Zona ZOMAC. El kilo real cuesta 2.350 COP y el kilo volumétrico 2.550 COP, con divisor volumétrico de 4.000. El flete mínimo es de 27.000 COP. El seguro es del 1% con mínimo de 4.500 COP. El recargo por cadena de frío es del 30% y el recargo por mercancía peligrosa es de 65.000 COP. Tiempo de entrega estimado: 72 horas.

Puerta de la Amazonía. Trayecto ZOMAC con frecuencia de despacho de tres veces por semana.

### Ruta Bogotá D.C. → Montería (TLX-BOG-MTR-022)

De Bogotá D.C. (Cundinamarca) a Montería (Córdoba), cobertura Urbana Principal. El kilo real cuesta 1.800 COP y el kilo volumétrico 1.980 COP, con divisor volumétrico de 4.000. El flete mínimo es de 21.500 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 48 horas.

Conexión agroindustrial del Caribe colombiano.

### Ruta Bogotá D.C. → Valledupar (TLX-BOG-VAL-023)

De Bogotá D.C. (Cundinamarca) a Valledupar (Cesar), cobertura Urbana Principal. El kilo real cuesta 1.850 COP y el kilo volumétrico 2.020 COP, con divisor volumétrico de 4.000. El flete mínimo es de 22.000 COP. El seguro es del 1% con mínimo de 4.000 COP. El recargo por cadena de frío es del 25% y el recargo por mercancía peligrosa es de 50.000 COP. Tiempo de entrega estimado: 48 horas.

Ruta Bosconia - Valledupar, con enlace hacia La Guajira.

### Ruta Bogotá D.C. → Riohacha (TLX-BOG-RIO-024)

De Bogotá D.C. (Cundinamarca) a Riohacha (La Guajira), cobertura Trayecto Especial. El kilo real cuesta 2.200 COP y el kilo volumétrico 2.400 COP, con divisor volumétrico de 4.000. El flete mínimo es de 25.500 COP. El seguro es del 1% con mínimo de 4.500 COP. El recargo por cadena de frío es del 30% y el recargo por mercancía peligrosa es de 60.000 COP. Tiempo de entrega estimado: 72 horas.

Extremo norte de Colombia. Exige embalaje resistente al polvo y a las altas temperaturas.

### Ruta Bogotá D.C. → Quibdó (TLX-BOG-QUI-025)

De Bogotá D.C. (Cundinamarca) a Quibdó (Chocó), cobertura Zona ZOMAC. El kilo real cuesta 2.650 COP y el kilo volumétrico 2.850 COP, con divisor volumétrico de 4.000. El flete mínimo es de 30.000 COP. El seguro es del 1% con mínimo de 5.000 COP. El recargo por cadena de frío es del 35% y el recargo por mercancía peligrosa es de 75.000 COP. Tiempo de entrega estimado: 96 horas.

Zona de difícil acceso por el estado de las vías. Despachos programados los días martes y viernes.

## Cobertura por municipio

### Bogotá D.C. — Cundinamarca

Bogotá D.C. tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.500 kg y el volumen máximo de 45 m³. Se atiende desde el Hub Central Zona Franca Fontibón, con despacho continuo 24/7. Restricción operativa: movilidad restringida para vehículos de carga pesada en zonas urbanas según el horario de pico y placa ambiental.

### Medellín — Antioquia

Medellín tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 40 m³. Se atiende desde el Hub Regional Itagüí, con cuatro salidas diarias. Restricción operativa: no pueden ingresar al centro urbano camiones de más de dos ejes entre las 06:00 y las 20:00.

### Envigado — Antioquia

Envigado tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Regional Itagüí, con dos turnos diarios. Restricción operativa: acceso restringido en zonas residenciales montañosas para vehículos superiores a 5 toneladas.

### Itagüí — Antioquia

Itagüí tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.500 kg y el volumen máximo de 45 m³. Se atiende desde el Hub Regional Itagüí, con despacho continuo 24/7. No tiene restricciones: es zona industrial con libre circulación de vehículos pesados.

### Bello — Antioquia

Bello tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Regional Itagüí, con dos turnos diarios. Restricción operativa: tránsito denso en la autopista Norte en horas pico.

### Rionegro — Antioquia

Rionegro tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 35 m³. Se atiende desde el Sub-Hub Aeropuerto José María Córdova, con tres turnos diarios. Es la conexión estratégica para carga aérea y zonas francas del Oriente antioqueño.

### Cali — Valle del Cauca

Cali tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 40 m³. Se atiende desde el Hub Regional Yumbo, con cuatro salidas diarias. Restricción operativa: control estricto de emisión de gases y pico y placa comercial.

### Yumbo — Valle del Cauca

Yumbo tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 3.000 kg y el volumen máximo de 50 m³. Se atiende desde el Hub Regional Yumbo, con despacho continuo 24/7. Es zona industrial principal, sin restricción de tonelaje.

### Palmira — Valle del Cauca

Palmira tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Regional Yumbo, con dos turnos diarios. Atiende de forma especializada a ingenios azucareros y al sector agroindustrial.

### Buenaventura — Valle del Cauca

Buenaventura tiene cobertura Trayecto Especial con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 3.000 kg y el volumen máximo de 50 m³. Se atiende desde el Nodo Portuario Buenaventura, con dos turnos diarios. Restricción operativa: requiere cita previa de ingreso a las terminales portuarias SPRBUN, Aguadulce y TCBUEN.

### Barranquilla — Atlántico

Barranquilla tiene cobertura Urbana Principal con entrega estándar en 48 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 40 m³. Se atiende desde el Hub Caribe Barranquilla, en la zona de Galapa, con tres salidas diarias. Condiciones de alta humedad: requiere almacenamiento en bodegas climatizadas.

### Soledad — Atlántico

Soledad tiene cobertura Urbana Principal con entrega estándar en 48 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Caribe Barranquilla, en la zona de Galapa, con dos turnos diarios. Restricción operativa: congestión vial en horas pico.

### Cartagena — Bolívar

Cartagena tiene cobertura Urbana Principal con entrega estándar en 48 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 2.500 kg y el volumen máximo de 45 m³. Se atiende desde el Sub-Hub Mamonal Cartagena, con dos turnos diarios. Restricción operativa: prohibido el paso de carga pesada por el Centro Histórico y Bocagrande.

### Santa Marta — Magdalena

Santa Marta tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Caribe Barranquilla, en la zona de Galapa, con un turno nocturno diario. Control ambiental estricto por la proximidad al parque nacional Sierra Nevada.

### Bucaramanga — Santander

Bucaramanga tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.800 kg y el volumen máximo de 35 m³. Se atiende desde el Hub Nororiente Girón, con dos turnos diarios. Geografía accidentada: las entregas de última milla se hacen prioritariamente en vehículos tipo van o turbo.

### Floridablanca — Santander

Floridablanca tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.200 kg y el volumen máximo de 25 m³. Se atiende desde el Hub Nororiente Girón, con dos turnos diarios. Restricción operativa: zona residencial y universitaria, con restricciones para camiones mayores a 3,5 toneladas.

### Girón — Santander

Girón tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 2.500 kg y el volumen máximo de 45 m³. Se atiende desde el Hub Nororiente Girón, con despacho continuo 24/7. Es el centro logístico e industrial del área metropolitana de Bucaramanga.

### Pereira — Risaralda

Pereira tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 1.800 kg y el volumen máximo de 35 m³. Se atiende desde el Hub Eje Cafetero Dosquebradas, con tres turnos diarios. Es el punto neurálgico de distribución interdepartamental del Eje Cafetero.

### Dosquebradas — Risaralda

Dosquebradas tiene cobertura Urbana Principal con entrega estándar en 24 horas. Dispone de servicio Same Day y de servicio refrigerado. El peso máximo por paquete es de 2.500 kg y el volumen máximo de 45 m³. Se atiende desde el Hub Eje Cafetero Dosquebradas, con despacho continuo 24/7. Allí están las bodegas principales de almacenamiento y consolidación.

### Manizales — Caldas

Manizales tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Eje Cafetero Dosquebradas, con dos turnos diarios. Restricción operativa: topografía empinada; requiere flota especializada con tracción 4x2 reforzada y freno de ahogo.

### Armenia — Quindío

Armenia tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Eje Cafetero Dosquebradas, con dos turnos diarios. Operación regular, sin novedades especiales de movilidad.

### Cúcuta — Norte de Santander

Cúcuta tiene cobertura Frontera con entrega estándar en 48 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 40 m³. Se atiende desde el Nodo Fronterizo Cúcuta, con un turno diario. Restricción operativa: inspecciones aduaneras frecuentes de la DIAN y la Polfa en las vías de acceso.

### Pasto — Nariño

Pasto tiene cobertura Frontera con entrega estándar en 72 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Nodo Sur Pasto, con despacho interdiario los lunes, miércoles y viernes. Sujeto a derrumbes o cierres eventuales en la vía Panamericana.

### Ipiales — Nariño

Ipiales tiene cobertura Frontera con entrega estándar en 72 horas. No dispone de servicio Same Day ni de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Nodo Sur Pasto, con despacho interdiario los lunes, miércoles y viernes. Restricción operativa: paso fronterizo de Rumichaca, con validación de guías de carga internacional.

### Villavicencio — Meta

Villavicencio tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 2.000 kg y el volumen máximo de 35 m³. Se atiende desde el Sub-Hub Llanos Villavicencio, con dos turnos diarios. Sujeto a cierres preventivos en la vía al Llano por desprendimientos de tierra.

### Neiva — Huila

Neiva tiene cobertura Urbana Principal con entrega estándar en 24 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.800 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Sur Neiva, con un turno diario. Clima cálido extremo: exige empaque protector para insumos sensibles al calor.

### Florencia — Caquetá

Florencia tiene cobertura Zona ZOMAC / Difícil Acceso, con entrega estándar en 72 horas. No dispone de servicio Same Day ni de servicio refrigerado. El peso máximo por paquete es de 800 kg y el volumen máximo de 15 m³. Se atiende desde el Hub Sur Neiva, con despacho tres veces por semana. Zona ZOMAC con vías secundarias restringidas durante la temporada invernal.

### Montería — Córdoba

Montería tiene cobertura Urbana Principal con entrega estándar en 48 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Caribe Barranquilla, en la zona de Galapa, con un turno nocturno diario. Atiende a los sectores ganaderos y agroindustriales del Sinú.

### Valledupar — Cesar

Valledupar tiene cobertura Urbana Principal con entrega estándar en 48 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.500 kg y el volumen máximo de 30 m³. Se atiende desde el Hub Caribe Barranquilla, en la zona de Galapa, con un turno nocturno diario. Es punto de distribución hacia la alta y la baja Guajira.

### Riohacha — La Guajira

Riohacha tiene cobertura Trayecto Especial con entrega estándar en 72 horas. No dispone de servicio Same Day, pero sí de servicio refrigerado. El peso máximo por paquete es de 1.000 kg y el volumen máximo de 20 m³. Se atiende desde el Nodo La Guajira Riohacha, con despacho interdiario los lunes, miércoles y viernes. Altas temperaturas y polvo: el empaque antipolvo industrial es obligatorio.

### Quibdó — Chocó

Quibdó tiene cobertura Zona ZOMAC / Difícil Acceso, con entrega estándar en 96 horas. No dispone de servicio Same Day ni de servicio refrigerado. El peso máximo por paquete es de 500 kg y el volumen máximo de 10 m³. Se atiende desde el Hub Regional Itagüí, con despacho semanal los martes y viernes. La vía terrestre tiene alto riesgo climático y las entregas dependen del estado de la carretera Ciudad Bolívar - Quibdó.
