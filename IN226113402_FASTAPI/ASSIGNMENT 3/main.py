from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

app = FastAPI()

# sample data
prods = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "cat": "Electronics", "stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "cat": "Stationery", "stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "cat": "Electronics", "stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "cat": "Stationery", "stock": True}
]

class Prod(BaseModel):
    name: str
    price: int
    cat: str
    stock: bool = True


# helper
def get_p(pid):
    for p in prods:
        if p["id"] == pid:
            return p
    return None


# get all products
@app.get("/products")
def all_p():
    return {"products": prods, "total": len(prods)}


# add product
@app.post("/products")
def add_p(p: Prod, res: Response):

    for x in prods:
        if x["name"].lower() == p.name.lower():
            res.status_code = status.HTTP_400_BAD_REQUEST
            return {"msg": "product exists"}

    new_id = max(i["id"] for i in prods) + 1

    new_p = {
        "id": new_id,
        "name": p.name,
        "price": p.price,
        "cat": p.cat,
        "stock": p.stock
    }

    prods.append(new_p)

    res.status_code = status.HTTP_201_CREATED
    return {"msg": "added", "product": new_p}


# update product
@app.put("/products/{pid}")
def upd_p(pid: int, price: int | None = None, stock: bool | None = None, res: Response = None):

    p = get_p(pid)

    if not p:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {"msg": "not found"}

    if price is not None:
        p["price"] = price

    if stock is not None:
        p["stock"] = stock

    return {"msg": "updated", "product": p}


# delete product
@app.delete("/products/{pid}")
def del_p(pid: int, res: Response):

    p = get_p(pid)

    if not p:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {"msg": "not found"}

    prods.remove(p)

    return {"msg": "deleted", "name": p["name"]}


# audit endpoint
@app.get("/products/audit")
def audit():

    ins = [p for p in prods if p["stock"]]
    outs = [p for p in prods if not p["stock"]]

    total_val = sum(p["price"] * 10 for p in ins)

    max_p = max(prods, key=lambda x: x["price"])

    return {
        "total": len(prods),
        "in_stock": len(ins),
        "out_names": [p["name"] for p in outs],
        "stock_value": total_val,
        "max_price": {"name": max_p["name"], "price": max_p["price"]}
    }


# bonus discount
@app.put("/products/discount")
def disc(cat: str = Query(...), percent: int = Query(..., ge=1, le=99)):

    upd = []

    for p in prods:
        if p["cat"] == cat:
            p["price"] = int(p["price"] * (1 - percent / 100))
            upd.append(p)

    if len(upd) == 0:
        return {"msg": "no products in category"}

    return {
        "msg": f"{percent}% discount applied",
        "count": len(upd),
        "items": upd
    }


# get single product
@app.get("/products/{pid}")
def one_p(pid: int, res: Response):

    p = get_p(pid)

    if not p:
        res.status_code = status.HTTP_404_NOT_FOUND
        return {"msg": "not found"}

    return p