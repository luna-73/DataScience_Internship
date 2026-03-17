from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel

app = FastAPI()


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "stock": True}
]

orders = []



class Product(BaseModel):
    name: str
    price: int
    category: str
    stock: bool = True



def get_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None



@app.get("/products")
def get_all_products():
    return {"total": len(products), "products": products}


@app.post("/products")
def add_product(p: Product, response: Response):
    for x in products:
        if x["name"].lower() == p.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Product already exists"}

    new_id = max(i["id"] for i in products) + 1

    new_product = {
        "id": new_id,
        "name": p.name,
        "price": p.price,
        "category": p.category,
        "stock": p.stock
    }

    products.append(new_product)
    response.status_code = status.HTTP_201_CREATED
    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(product_id: int, response: Response, price: int = None, stock: bool = None):
    p = get_product(product_id)

    if not p:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}

    if price is not None:
        p["price"] = price
    if stock is not None:
        p["stock"] = stock

    return {"message": "Product updated", "product": p}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    p = get_product(product_id)

    if not p:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}

    products.remove(p)
    return {"message": "Product deleted", "name": p["name"]}


# ------------------ Q1: SEARCH ------------------
# 🚨 MUST BE ABOVE /products/{product_id}

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": f"No products found for: {keyword}"}

    return {"keyword": keyword, "total_found": len(result), "products": result}


# ------------------ Q2: SORT ------------------

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    if sort_by not in ["price", "name"]:
        return {"message": "sort_by must be 'price' or 'name'"}

    result = sorted(products, key=lambda x: x[sort_by], reverse=(order == "desc"))

    return {"sort_by": sort_by, "order": order, "products": result}


# ------------------ Q3: PAGINATION ------------------

@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=20)
):
    start = (page - 1) * limit
    data = products[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": len(products),
        "total_pages": -(-len(products) // limit),
        "products": data
    }


# ------------------ Q4: ORDER SEARCH ------------------

@app.post("/orders")
def add_order(order: dict):
    order["order_id"] = len(orders) + 1
    orders.append(order)
    return order


@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }


# ------------------ Q5: SORT BY CATEGORY ------------------

@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda x: (x["category"], x["price"]))
    return {"total": len(result), "products": result}


# ------------------ Q6: BROWSE ------------------

@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):
    result = products

    # 🔍 Search
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # ⚠️ Validate sort
    if sort_by not in ["price", "name"]:
        return {"message": "sort_by must be 'price' or 'name'"}

    # ↕️ Sort
    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    # 📄 Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }


# ------------------ BONUS ------------------

@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):
    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }


# ------------------ LAST ROUTE ------------------
# 🚨 ALWAYS KEEP THIS AT THE VERY END

@app.get("/products/{product_id}")
def get_one_product(product_id: int, response: Response):
    p = get_product(product_id)

    if not p:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Product not found"}

    return p