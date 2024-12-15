from fastapi import APIRouter, HTTPException
from app.schemas import ProductRequest
from sendo.sendo_main import process_products

router = APIRouter(prefix="/products", tags=["products"])



@router.post("/")
async def get_product_links(request: ProductRequest):
    """
    FastAPI endpoint to fetch and process products.
    """
    try:
        # Directly await process_products as it is now async
        result = await process_products(request.url, request.reset)
        
        # Validate the result to ensure it is JSON-serializable
        return {"message": "Data fetched and saved successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")