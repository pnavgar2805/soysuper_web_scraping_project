from bs4 import BeautifulSoup
import utils
import requests
import os


## Esta función es la función principal del proyecto, ya que se encarga de extraer los datos de los productos de una categoría
def get_dictionaries(hostname: str, data_dirname: str, pathname: str = "", current_list: list = [], current_dictionary: dict = {}, current_dir: str = "") -> list:

    # Crear la carpeta data donde se van a guardar los datos
    if len(current_dictionary) == 0:
        current_dir = utils.create_directory(data_dirname=data_dirname)

    # Obtener la sopa principal del nombre de ruta introducido
    main_soup = get_main_soup(hostname=hostname, pathname=pathname)
    
    # Obtener la sopa específica para cada categoría
    categories_soup_array = get_soup_array(main_soup=main_soup, extract_mode="categories", pathname=pathname)

    # Preparar la búsqueda de los datos para cada categoría
    for obj in categories_soup_array:
        # Buscar el elemento <a> que contiene la información de la categoría
        category = obj.find("a")
        
        # Registrar los datos de las categorías, excepto la última, que no tendrá más categorías posteriores
        if category != (-1):
            # Registrar el nombre de la categoría, el nombre de la ruta y el número de productos; y guardarlos en un diccionario
            current_list.append({
                "nombre_de_categoría": category["title"].strip(),
                "nombre_de_ruta": category["href"].replace("#products", "").strip(),
                "numero_de_productos": category.find("span", class_="number").text.strip(),
                "subcategorías": []
                })
            
            # Crear un directorio para cada categoría
            current_dir = utils.create_directory(data_dirname=data_dirname, current_dir=current_dir, current_category_name=current_list[-1]["nombre_de_categoría"])
            
            # Mostrar mensaje de carga
            print(f"Extrayendo categoría {current_list[-1]['nombre_de_categoría']} ...")
            
            # Realizar el web scraping de las categorías aguas abajo
            get_dictionaries(hostname=hostname, data_dirname=data_dirname, pathname=current_list[-1]["nombre_de_ruta"], current_list=current_list[-1]["subcategorías"], current_dictionary=current_list[-1], current_dir=current_dir)
            
            # Mostrar mensaje de éxito
            print(f"¡Categoría {current_list[-1]['nombre_de_categoría']} extraída con éxito!")
            
        # Registrar los datos de los productos de cada categoría final (la última contendrá los datos de los productos) y guardarlos en un JSON
        else:
            # Comprobar si ya se han extraído los datos de cada producto
            if not utils.is_data_extracted(current_dir=current_dir, current_category_name=current_dictionary["nombre_de_categoría"]):
                
                # Registrar los datos de los productos de cada categoría final en el diccionario
                extract_products(current_dictionary=current_dictionary, main_soup=main_soup, hostname=hostname, pathname=pathname)
                
                # Registrar los datos obtenidos en un JSON al terminar una categoría
                utils.write_json(data_input=current_dictionary, current_dir=current_dir, data_dirname=data_dirname)
            
        # Obtener la ruta del directorio anterior (parent_dir) para las siguientes categorías
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    return current_list  


## Esta función se utiliza para obtener una sopa HTML del nombre de ruta introducido
def get_main_soup(hostname: str, pathname: str = "", parser: str = "html.parser") -> BeautifulSoup:

    # Control de excepciones
    try:
        # Enviar una petición GET
        response = requests.get(url=hostname+pathname)
        
        # Comprobar el estado de la respuesta
        if response.status_code == 200:
            # Crear un objeto BeautifulSoup con el contenido de la respuesta
            main_soup = BeautifulSoup(markup=response.content, features=parser)

        else:
            # Mostrar un mensaje de error si la respuesta no es exitosa
            print(f"Error en la función get_main_soup(). No se puede acceder a la página debido a que el código de estado de la respuesta HTTP es {str(response.status_code)}")
        
        return main_soup
    
    except:
        # Mostrar un mensaje de error si el código anterior no se ejecuta por completo
            print("Error en la función get_main_soup(). No se puede acceder a la página web debido a un error tipográfico")


## Esta función se utiliza para obtener un array de objetos BeautifulSoup de una sopa HTML
def get_soup_array(main_soup: BeautifulSoup, extract_mode: str = "categories" or "products" or "supermarkets", pathname: str = "") -> any:
    
    # Extraer los datos de la categorías
    if extract_mode == "categories":
        # Control de excepciones
        try:
            # Buscar los elementos que contienen las categorías de los productos
            product_nav = main_soup.find_all("section", class_="product-nav")[1]
            categories_section = product_nav.find("div", class_="hidden-t")
            
            # Arreglar un problema ocasional relacionado con la estructura del código HTML
            if (categories_section.find("h4") is None) and (len(pathname) != 0):
                soup_array = [" "]
            
            else:
                all_categories = categories_section.find("ul")
                soup_array = all_categories.find_all("li")
         
        except:
            # Mostrar un mensaje de error si no se pueden extraer los datos de la web según el procedimiento anterior
            print("Error en la función get_soup.array(). No se puede realizar el web scraping de categorías a través de: section(class=product-nav) -> ul -> li")

    # Extraer los datos de los productos de cada categoría final
    elif extract_mode == "products":
        try:
            # Encontrar la sección donde se encuentran los productos
            products_section = main_soup.find("section", id="main")
            
            # Obtener los datos de todos los productos en cada página
            products_list = products_section.find("ul", class_="basiclist productlist grid clearfix")
            soup_array = products_list.find_all("li", itemtype="http://schema.org/Product")

        except:
            # Mostrar un mensaje de error si no se pueden extraer los datos de la web según el procedimiento anterior
            print("Error en la función get_soup_array(). No se puede realizar el web scraping de productos a través de: section(class=main) -> ul(class=basiclist productlist grid clearfix) -> li(itemtype=http://schema.org/Product)")

    # Extraer los datos de los supermercados de cada producto
    elif extract_mode == "supermarkets":
        try:
            # Obtener los datos de todos los supermercados que incluyen un producto
            soup_array = main_soup.find("section", class_="superstable")

        except:
            # Mostrar un mensaje de error si no se pueden extraer los datos de la web según el procedimiento anterior
            print("Error en la función get_soup_array(). No se puede realizar el web scraping de supermercados a través de: section(class=superstable) -> tr")
        
    return soup_array


## Esta función se utiliza para extraer los datos de los productos de una categoría
def extract_products(current_dictionary: dict, main_soup: any, hostname: str, pathname: str) -> dict:
    
    # Mostrar mensaje de carga
    print(f"Extrayendo productos de la categoría {current_dictionary['nombre_de_categoría']} ...")
    
    # Cambiar la clave "subcategorías" por "productos"
    current_dictionary["productos"] = []
    del current_dictionary["subcategorías"]
    
    # Encontrar la sección donde se encuentran los productos
    main_section = main_soup.find("section", id="main")
    
    # Definir el número total de páginas
    pager_section = main_section.find("section", id="pager")
    
    if pager_section is None:
        total_number_of_pages = "1"
    else:
        total_number_of_pages = pager_section.find_all("a")[-2].text.strip()

    # Obtener la sopa específica para los productos
    products_soup_array = get_soup_array(main_soup=main_soup, extract_mode="products")
    
    # Registrar en el diccionario todos los productos de la primera página (siempre va a haber una primera página)
    extract_products_from_page(hostname=hostname, products_soup_array=products_soup_array, current_dictionary=current_dictionary)
    
    # Registrar en el diccionario todos los productos del resto de páginas (si existen)
    if total_number_of_pages != "1":
        for number_of_page in range(2, int(total_number_of_pages)+1):
            # Extraer la sopa principal en cada página
            new_soup = get_main_soup(hostname=hostname, pathname=pathname+"?page="+str(number_of_page)+"#products")
            
            # Extraer la sopa específica para los productos
            new_soup_array = get_soup_array(main_soup=new_soup, extract_mode="products")
            
            # Extraer
            extract_products_from_page(hostname=hostname, products_soup_array=new_soup_array, current_dictionary=current_dictionary)

    print(f"¡Productos de la categoría {current_dictionary['nombre_de_categoría']} extraídos con éxito!")


## Esta función se utiliza para extraer los datos de los productos de una categoría por cada página de productos
def extract_products_from_page(hostname: str, products_soup_array: any, current_dictionary: dict):
    
    # Obtener los datos de los productos en cada página
    for product in products_soup_array:
        # Extraer una parte de la sopa en la que se va a encontrar ciertos valores
        main_info = product.find("a", class_="btn btn-primary newproduct btn-block")
        
        # Extraer el id del producto
        product_id = main_info["data-product_id"].strip()
        if len(product_id) == 0:
            product_id = None
            
        # Extraer el nombre del producto
        product_name = main_info["data-name"].strip()
        if len(product_name) == 0:
            product_name = None
            
        # Extraer la marca del producto
        try:
            product_brand = main_info["data-brand"].strip()
            if len(product_brand) == 0:
                product_brand = None
                
        except:
            try:
                product_brand = product.find("a", class_="brand").text.strip()
            except:
                product_brand = None
                
        # Extraer la variante del producto
        product_variant = main_info["data-variant"].strip()
        if len(product_variant) == 0:
            product_variant = None
            
        # Extraer el nombre de la ruta del producto
        product_pathname = product.find("a")["href"].strip()
        if len(product_pathname) == 0:
            product_pathname = None
            
        # Extraer el nombre de la ruta de la imagen del producto
        try:
            product_image_url = product.find("img")["src"].strip()
        except:
            product_image_url = None
            
        # Extraer el precio medio del producto (en relación a los supermercados en los que aparece el producto)
        try:
            product_average_price = product.find("meta", itemprop="price")["content"].strip()
        except:
            product_average_price = None
            
        # Extraer la moneda (divisa) del precio del producto
        try:
            product_price_currency = product.find("meta", itemprop="priceCurrency")["content"].strip()
        except:
            product_price_currency = None
            
        # Extraer el precio del producto por variante del producto
        try:
            product_price_per_variant = product.find("span", class_="price").text.strip()
        except:
            product_price_per_variant = None
            
        # Extraer el precio del producto por variante estándar (precio unitario)
        try:
            product_unitprice = product.find("span", class_="unitprice").text.strip()
        except:
            product_unitprice = None
            
        # Registrar los datos del producto en el diccionario
        current_dictionary["productos"].append({
            "product_id": product_id,
            "product_name": product_name,
            "product_brand": product_brand,
            "product_variant": product_variant,
            "product_pathname": product_pathname,
            "product_image_url": product_image_url,
            "product_average_price": product_average_price,
            "product_price_currency": product_price_currency,
            "product_price_per_variant": product_price_per_variant,
            "product_unitprice": product_unitprice
            })

        # Registrar los supermercados del producto en cada página
        extract_supermarkets_from_product_page(hostname=hostname, current_dictionary=current_dictionary["productos"][-1])


## Esta función se utiliza para extraer los datos de los supermercados de un producto
def extract_supermarkets_from_product_page(hostname: str, current_dictionary: dict):
    
        # Extraer la sopa principal de los supermercados
        supermarket_main_soup = get_main_soup(hostname=hostname, pathname=current_dictionary["product_pathname"])
        
        # Extraer la sopa específica de los supermercados del producto
        supermarket_soup_array = get_soup_array(main_soup=supermarket_main_soup, extract_mode="supermarkets")
        
        # Inicializar clave donde se van a guardar los datos de los supermercados
        current_dictionary["product_in_supermarkets"] = []
        
        # Controlar el caso de que algún producto, por alguna razón, no aparezca en ningún supermercado
        try:
            # Extraer la sopa donde se encuentran los datos de los supermercados
            supermarket_list = supermarket_soup_array.find_all("tr")
            
            # Registrar los datos de los supermercados en el diccionario
            for supermarket in supermarket_list:
                # Extraer el nombre del supermercado en el que aparece el producto
                supermarket_name = supermarket.find("i")["title"].strip()
                
                # Extraer el precio del producto en ese supermercado
                supermarket_product_price = supermarket.find("td").text.strip()
                
                # Registrar los datos en el diccionario
                current_dictionary["product_in_supermarkets"].append({
                    "supermarket_name": supermarket_name,
                    "supermarket_product_price": supermarket_product_price
                    })
                
        except:
            current_dictionary["product_in_supermarkets"].append(None)
