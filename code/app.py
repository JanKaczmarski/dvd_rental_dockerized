from flask import Flask, render_template, request
import psycopg2


app = Flask(__name__)

# Unchangeable variables
DELIMITER = ","

def get_db_connection():
    """Connects to the database on given variables

    Returns:
        variable: conn - psycopg2 object, connection to the database, cursor can be called upon it to interact with database
    """
    conn = psycopg2.connect(host="postgresql",
                            port="5432",
                            user="postgres",
                            password="password",
                            dbname="dvd_rental")
    return conn

def param_to_id(param):
    """Converts given parameter so next function can easily work with given data 

    Args:
        param (str): parameters given in query ex. id=1&6

    Returns:
        tuple: (tuple_of_data, connector - "IN" or "="
    """
    id = ""
    converted_param = []
    for i in param:
        if i != "&":
            id += i
        else:
            converted_param.append(id)
            id = ""
    converted_param.append(id)
    if len(converted_param) == 1:
        return converted_param[0], "="
    else:
        return tuple(converted_param), "IN"
     
# MAKE data_to_dic function more universal so it can be used with every given data from dvd_rental tables  
def data_to_dic_nested(data, poss_var:list):
    """Converts data from the database so the return can give format that can be displayed in json format

    Args:
        data (list): list with data from database

    Returns:
        dict: dict with converted data
    """
    output = []
    poss_var.append("last_update")
    for item in data:
        for item_property in item:
            item_data = {poss_var[i][:-1]:item_property[i] for i in range(len(item_property))} 
            #item_data = {"category_id":item_property[0], "name": item_property[1], "last_update":item_property[2]}
            output.append(item_data)
        
    return {"data": output}

def data_to_dic(data, poss_var:list):
    output = []
    poss_var.append("last_update")
    for item_property in data:
        item_data = {poss_var[i][:-1]:item_property[i] for i in range(len(item_property))} 
        #item_data = {"category_id":item_property[0], "name": item_property[1], "last_update":item_property[2]}
        output.append(item_data)
    
    return {"data": output}

def extract_data_from_db(sliced_param, poss_var:list, table_name:str):
    """Gets list of sliced params and extract data from the database

    Args:
        sliced_param (list): list with queries ex. ["category_id"=1&7, "name"='Children']
        poss_var (tuple): tuple with possible variables ex. ("category_id=", "name=")
        table_name (str): name of the table that operation has to be done

    Returns:
        list: list with converted data so data_to_dic function can work easily
    """
    poss_var += "limit=", "offset="
    var_query = {}
    if sliced_param:
        for param in sliced_param:
            for var in poss_var:
                if param[:len(var)] == var:
                    id, connector = param_to_id(param[len(var):])
                    var_query[var[:-1]] = (id,connector)

    data = []

    for key in var_query: # key is the type of parameter ex. category_id=
        selector = var_query[key][1] # IN or =
        values = var_query[key][0] # '0' '4' 'Action'
        conn = get_db_connection()
        cur = conn.cursor()
        #print(key,var_query[key])
        cur.execute(f"SELECT * FROM {table_name} WHERE {key} {selector} {values};")
        data.append(cur.fetchall())
        
        cur.close()
        conn.close()

    return data

def get_all_data(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name};")
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    return data

@app.route("/")
def base():
    return render_template("base.html")

@app.route("/company/")
def get_companies():
    poss_var = ["ID=", "NAME=", "AGE=", "ADDRESS=", "SALARY=", "JOIN_DATE="]
    data = get_all_data("COMPANY")
    return data_to_dic(data, poss_var)

@app.route("/category/")
def get_categories():
    poss_var = ["film_id=", "category_id="]
    data = get_all_data("category")
    return data_to_dic(data, poss_var)

@app.route("/category/<params>")
def get_category(params):
    table_name = "category" # table name on which operation will be done
    poss_var = ["category_id=", "name="] # variables than can be included in given parameter
    sliced_params = params.split(DELIMITER)#slice_param(params,DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data,poss_var)

@app.route("/film_category/<params>")
def get_film_category(params):
    table_name = "film_category"
    poss_var = ["film_id=", "category_id="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data,poss_var)

@app.route("/film_category/")
def get_film_categories():
    poss_var = ["film_id=", "category_id="]
    data = get_all_data("film_category")
    
    return data_to_dic(data, poss_var)
    
@app.route("/film/<params>")
def get_film(params):
    table_name = "film"
    # pos_var are the keys that user can search by
    poss_var = ["film_id=", "title=", "description=", "release_year=", "language_id=", "rental_duration=", "rental_rate=", "length=", "replacement_cost=", "rating=", "last_update=", "special_features=", "fulltext="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/film/")
def get_films():
    data = get_all_data("film")
    poss_var = ["film_id=", "title=", "description=", "release_year=", "language_id=", "rental_duration=", "rental_rate=", "length=", "replacement_cost=", "rating=", "last_update=", "special_features=", "fulltext="]
    return data_to_dic(data, poss_var)


@app.route("/language/")
def get_languages():
    data = get_all_data("language")
    poss_var = ["language_id=", "name=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/language/<params>")
def get_language(params):
    table_name = "language"
    poss_var = ["language_id=", "name=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/actor/")
def get_actors():
    data = get_all_data("actor")
    poss_var = ["actor_id=", "first_name=", "last_name=" "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/actor/<params>")
def get_actor(params):
    table_name = "actor"
    poss_var = ["actor_id=", "first_name=", "last_name=" "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/film_actor/")
def get_film_actors():
    data = get_all_data("film_actor")
    poss_var = ["actor_id=", "film_id=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/film_actor/<params>")
def get_film_actor(params):
    table_name = "film_actor"
    poss_var = ["actor_id=", "film_id=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/inventory/")
def get_inventory():
    data = get_all_data("inventory")
    poss_var = ["inventory_id=", "film_id=", "store_id=" "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/inventory/<params>")
def get_inventory_item(params):
    table_name = "inventory"
    poss_var = ["inventory_id=", "film_id=", "store_id=" "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/staff/")
def get_staff():
    data = get_all_data("staff")
    poss_var = ["staff_id=", "first_name=", "last_name=", "address_id=", "email=", "store_id=", "active=", "username=", "password=", "last_update=", "picture="]
    return data_to_dic(data, poss_var)

@app.route("/staff/<params>")
def get_employee(params):
    table_name = "staff"
    poss_var = ["staff_id=", "first_name=", "last_name=", "address_id=", "email=", "store_id=", "active=", "username=", "password=", "last_update=", "picture="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/payment/")
def get_payments():
    data = get_all_data("payment")
    poss_var = ["payment_id=", "customer_id=", "staff_id=", "rental_id=", "amount=", "payment_date="]
    return data_to_dic(data, poss_var)

@app.route("/payment/<params>")
def get_payment(params):
    table_name = "payment"
    poss_var = ["payment_id=", "customer_id=", "staff_id=", "rental_id=", "amount=", "payment_date="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/rental/")
def get_rentals():
    data = get_all_data("rental")
    poss_var = ["rental_id=", "rental_date=", "inventory_id=", "customer_id=", "return_date=", "staff_id=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/rental/<params>")
def get_rental(params):
    table_name = "rental"
    poss_var = ["rental_id=", "rental_date=", "inventory_id=", "customer_id=", "return_date=", "staff_id=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/customer/")
def get_customers():
    data = get_all_data("customer")
    poss_var = ["customer_id=", "store_id=", "first_name=", "last_name=", "email=", "address_id=", "activebool=", "create_date=", "last_update=", "active="]
    return data_to_dic(data, poss_var)

@app.route("/customer/<params>")
def get_customer(params):
    table_name = "customer"
    poss_var = ["customer_id=", "store_id=", "first_name=", "last_name=", "email=", "address_id=", "activebool=", "create_date=", "last_update=", "active="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/address/")
def get_addresses():
    data = get_all_data("address")
    poss_var = ["address_id=", "address=", "address2=", "district=", "city_id=", "postal_code=", "phone=" "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/address/<params>")
def get_address(params):
    table_name = "address"
    poss_var = ["address_id=", "address=", "address2=", "district=", "city_id=", "postal_code=", "phone=" "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/city/")
def get_cities():
    data = get_all_data("city")
    poss_var = ["city_id=", "city=", "country_id=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/city/<params>")
def get_city(params):
    table_name = "city"
    poss_var = ["city_id=", "city=", "country_id=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/country/")
def get_countries():
    data = get_all_data("country")
    poss_var = ["country_id=", "country=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/country/<params>")
def get_country(params):
    table_name = "country"
    poss_var = ["country_id=", "country=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)

@app.route("/store/")
def get_stores():
    data = get_all_data("store")
    poss_var = ["store_id=", "manager_staff_id=", "address_id=", "last_update="]
    return data_to_dic(data, poss_var)

@app.route("/store/<params>")
def get_store(params):
    table_name = "store"
    poss_var = ["store_id=", "manager_staff_id=", "address_id=", "last_update="]
    sliced_params = params.split(DELIMITER)
    data = extract_data_from_db(sliced_params, poss_var, table_name)
    return data_to_dic_nested(data, poss_var)




# Every query that base on searching like id=2 or name=Action&Children are done, 
# problem is when user want to get every film which description is longer thant 300 character,
# or the length of film is greater than avg 
# it is a good feature to add and then send it back to the boss
