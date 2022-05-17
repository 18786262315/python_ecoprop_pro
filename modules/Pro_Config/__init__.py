
from fastapi import APIRouter,Form,HTTPException,Body

from logging import exception
from comm.logger import logger






router = APIRouter(prefix="/project",tags=['project'],responses={405: {"description": "Not found"}},)



@router.get("/")
def read_users():
    return "res_data"

