"""
=============================================================================
EJERCICIO INTEGRADOR - SISTEMA DE GESTIÓN DE BIBLIOTECA
=============================================================================

OBJETIVO: Crear un sistema completo de gestión de biblioteca que integre todos
los conceptos aprendidos en el repaso de Python.

CONCEPTOS A PRACTICAR:
- Variables y tipos de datos
- String formatting
- Listas, sets, tuplas y diccionarios
- Condicionales (if/else)
- Bucles (for/while)
- Funciones
- POO: Clases, herencia, polimorfismo, composición
- Atributos privados y públicos
- Métodos estáticos y de clase

=============================================================================
REQUERIMIENTOS DEL EJERCICIO:
=============================================================================

1. CLASE BASE: Item
   - Atributos privados: __id, __titulo, __año_publicacion
   - Atributos públicos: disponible (boolean), ubicacion (string)
   - Método constructor que inicialice todos los atributos
   - Métodos getter para los atributos privados
   - Método abstracto: obtener_info() que debe ser implementado por las clases hijas
   - Método: prestar() - marca el item como no disponible
   - Método: devolver() - marca el item como disponible

2. CLASES HIJAS (herencia de Item):
   
   a) Libro:
      - Atributos adicionales: autor, num_paginas, genero
      - Implementar obtener_info() mostrando toda la información del libro
      - Método especial: es_largo() - retorna True si tiene más de 300 páginas
   
   b) Revista:
      - Atributos adicionales: numero_edicion, mes_publicacion, editor
      - Implementar obtener_info() mostrando toda la información de la revista
      - Método especial: es_reciente() - retorna True si es del año actual (2025)
   
   c) DVD:
      - Atributos adicionales: director, duracion_minutos, formato (ej: "BluRay", "DVD")
      - Implementar obtener_info() mostrando toda la información del DVD
      - Método especial: es_pelicula_larga() - retorna True si dura más de 120 minutos

3. CLASE COMPOSICIÓN: Miembro
   - Atributos privados: __id_miembro, __nombre, __email
   - Atributos públicos: items_prestados (lista de Items prestados)
   - Atributo de clase: total_miembros (contador de miembros creados)
   - Método constructor (incrementa total_miembros)
   - Métodos getter para atributos privados
   - Método: prestar_item(item) - añade el item a items_prestados si está disponible
   - Método: devolver_item(item) - remueve el item de items_prestados
   - Método: mostrar_items_prestados() - imprime todos los items que tiene prestados
   - Método de clase: obtener_total_miembros() - retorna el número total de miembros

4. CLASE PRINCIPAL: Biblioteca
   - Atributos:
     * nombre (string)
     * catalogo (diccionario con el id como key y el Item como value)
     * miembros (diccionario con id_miembro como key y Miembro como value)
   
   - Métodos:
     * agregar_item(item) - añade un item al catálogo
     * agregar_miembro(miembro) - añade un miembro
     * buscar_por_titulo(titulo) - retorna lista de items que coincidan con el título
     * buscar_por_tipo(tipo) - retorna lista de items del tipo especificado (Libro, Revista, DVD)
     * listar_items_disponibles() - muestra todos los items disponibles
     * listar_items_prestados() - muestra todos los items no disponibles
     * generar_reporte() - muestra estadísticas:
       · Total de items en el catálogo
       · Total de libros, revistas y DVDs
       · Porcentaje de items prestados vs disponibles
       · Total de miembros registrados
     * prestar_item_a_miembro(id_item, id_miembro) - realiza el préstamo
     * devolver_item_de_miembro(id_item, id_miembro) - realiza la devolución

5. FUNCIÓN PRINCIPAL: main()
   Crear un programa interactivo que:
   - Cree una biblioteca con un nombre
   - Agregue al menos 3 libros, 2 revistas y 2 DVDs
   - Cree al menos 2 miembros
   - Realice al menos 3 préstamos
   - Realice al menos 1 devolución
   - Muestre el reporte de la biblioteca
   - Use búsquedas por título y por tipo
   - Muestre los items prestados de un miembro específico

=============================================================================
EXTRAS (OPCIONAL):
=============================================================================
- Implementar manejo de excepciones para préstamos inválidos
- Agregar validación de input del usuario
- Implementar un menú interactivo con user input
- Agregar funcionalidad para eliminar items y miembros
- Implementar sistema de multas por retraso en devolución
- Usar f-strings para todo el formato de texto
- Implementar búsqueda por múltiples criterios usando filtros

=============================================================================
TIPS:
=============================================================================
- Usa comentarios para explicar tu código
- Usa nombres descriptivos para variables y funciones
- Aprovecha los bucles for para iterar sobre colecciones
- Usa condicionales para validar estados (ej: si un item está disponible)
- Usa diccionarios para búsquedas rápidas por ID
- Usa listas para almacenar colecciones de items
- Usa string formatting (f-strings) para mensajes claros
- Recuerda usar super().__init__() en las clases hijas
- Usa isinstance() para verificar el tipo de un objeto

=============================================================================
"""

# ESCRIBE TU CÓDIGO AQUÍ ABAJO:
