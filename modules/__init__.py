
from fastapi import APIRouter,Depends,Header,HTTPException


# async def get_token_header(x_token: str = Header(...)):
#     # print(Header(None),x_token)

#     if x_token == "fake-super-secret-token":
#         raise HTTPException(status_code=400, detail="X-Token header invalid")
    
# async def get_query_token(token: str):
#     if token != "jessica":
#         raise HTTPException(status_code=400, detail="No Jessica token provided")



router = APIRouter(prefix="/app",tags=['app'],responses={405: {"description": "Not found"}},)




@router.get("/")
def read_users():
    return "audax_admin"
