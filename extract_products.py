# Importar las bibliotecas
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Función para obtener la sopa del nombre de ruta introducido
def get_bs_soysuper(hostname="https://soysuper.com", pathname="", parser="html.parser") -> BeautifulSoup:
    # Control de excepciones
    try:
        # Enviar la petición GET
        response = requests.get(url=hostname+pathname)
        # Comprobar el estado de la respuesta
        if response.status_code == 200:
            # Crear un objeto BeautifulSoup con el contenido de la respuesta
            soup = BeautifulSoup(markup=response.content, features=parser)
        else:
            # Mostrar un mensaje de error si la respuesta no es exitosa
            print(f"ConnectionError: No se puede acceder a la página debido a que el código de estado de la respuesta HTTP es {str(response.status_code)}")
        return soup
    except:
        # Mostrar un mensaje de error si el código anterior no se ejecuta
            print("ConnectionError: No se puede acceder a la página web debido a un error tipográfico")

def extract_categories(categories_list=[], url="") -> list:
    # Obtener la sopa de la url introducida
    soup = get_bs_soysuper(pathname=url)
    try:
        # Buscar los elementos que contienen las categorías de los productos
        section = soup.find_all("section", class_="product-nav")[1]
        ul = section.find_all("ul")[0]
        li = ul.find_all("li")
        ul_products = soup.find_all("ul", class_="basiclist productlist grid clearfix")
    except:
        # Mostrar un mensaje de error si no se pueden extraer los datos de la web según el procedimiento anterior
        print("Error al realizar el web scraping a través de section -> ul -> li")

    # Preparar la búsqueda de los datos por categorias y subcategorías
    for index, cat in enumerate(li):
        # Buscar el elemento <a> que contiene la información de la categoría
        category = cat.find("a")
        # Extraer las categorías y subcategorías
        if category is not None:
            try:
                # Extraer el nombre de la categoría, el nombre de la ruta (remodelado, ya que se añade #products y no queremos que pase esto) y el número de productos; y guardarlos como un diccionario en cada elemento de la lista
                categories_list.append({"nombre_de_categoría": category["title"],
                                        "nombre_de_ruta": category["href"].replace("#products", ""),
                                        "numero_de_productos": category.find("span", class_="number").text,
                                        "subcategorías": []})
                #extract_categories(categories_list=categories_list[index]["subcategorías"], url=categories_list[index]['nombre_de_ruta'])
            except:
                # Mostrar un mensaje de error si no se pueden extraer los datos de las categorías
                print(f"Error al realizar el web scraping de las categoría {category['title']}")
        
        # Extraer los productos en cada categoría final
        else:
            try:
                print('last subcategory')
                # Sustituir en la última subcategoría "subcategorías" por "productos"
                # Renombrar 'subcategorías' por 'productos'
                # dict['new_value'] = dict['old_value']
                # del dict['old_value']
            except:
                # Mostrar un mensaje de error si no se pueden extraer los datos de los productos de la categoría
                print(f"Error al realizar el web scraping de las categoría {category['title']}")
            print(categories_list)

    return categories_list

start_time = time.time()

print(extract_categories())

end_time = time.time()
print(f"Tiempo de ejecución: {(end_time-start_time)/60} minutos")