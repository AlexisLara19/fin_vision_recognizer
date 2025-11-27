from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import Part
from ..schemas import PartResponseModel
from datetime import datetime, date
from peewee import fn


router = APIRouter(prefix='/indicators')

#_________________ number of pieces, number of cycles by day  of a part number ____________________
# Params: part_number_id
#         day (default today)
# Return: List[cycles, pz_ok]
@router.get('/parts', response_model=List[PartResponseModel])
async def get_parts_by_day(date_str:str = date.today().strftime('%Y-%m-%d'), 
                           part_number_id:int = 0, 
                           page:int=1, limit:int=10):
   
    # Validacion del formato de fecha
    try:
        date_n: date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="El formato de la fecha debe ser 'YYYY-MM-DD'.")

    part_n = part_number_id
    
    part_registers = Part.select().where((Part.part_number == part_n) &
                                         (fn.DATE(Part.datetime_test) == date_n)).paginate(page,limit)
    
    return [part_register for part_register in part_registers]
    
#_________________ number of pieces, number of cycles by device of a device ____________________



#_________________ number of pieces, number of cycles by project of a project____________________

