from enum import Enum

import uvicorn
from pyngrok import ngrok
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class NeedyStr(str, Enum):
    d: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result |= {"q": q}
    return result


@app.get("/items/{item_id}")
async def read_user_item(
    item_id: ModelName, needy: NeedyStr, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/newmodels/{model_name}")
async def get_model_10(model_name):
    match model_name:
        case "alexnet":
            return {"model_name": model_name, "message": "Deep Learning FTW!"}
        case "lenet":
            return {"model_name": model_name, "message": "LeCNN all the images"}
        case "resnet":
            return {"model_name": model_name, "message": "Have some residuals"}


if __name__ == "__main__":
    port = 8000
    uvicorn.run(app, port=port)
    # ngrok_tunnel = ngrok.connect(port)
    # print('ngrok's URL:', ngrok_tunnel.public_url)
