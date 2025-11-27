from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import Part
from ..schemas import PartResponseModel
from datetime import datetime, date
from peewee import fn

router = APIRouter(prefix='/historial')

#_________________ Part number by day ____________________
#Params: day (default today)
#        part_number_id
# Returns a List of all parts produced on selected day
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
    

#_________________ Device by day _________________________
#Params: day (default today)
#        device_id
#        part_number_id(optional, default 0)
# Returns a List of all parts produced on selected day
@router.get('/device', response_model=List[PartResponseModel])
async def get_device_by_day(date_str:str = date.today().strftime('%Y-%m-%d'), 
                           device_id:int = 0,
                           part_number_id:int = 0,
                           page:int=1, limit:int=10):
    # Validacion del formato de fecha
    try:
        date_n: date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="El formato de la fecha debe ser 'YYYY-MM-DD'.")

    device_n = device_id
    part_n = part_number_id
    
    if part_n == 0:
        part_registers = Part.select().where((Part.device_id == device_n) &
                                            (fn.DATE(Part.datetime_test) == date_n)).paginate(page,limit)
        return [part_register for part_register in part_registers]
    else:
        part_registers = Part.select().where((Part.device_id == device_n) &
                                                (Part.part_number == part_n) &
                                                (fn.DATE(Part.datetime_test) == date_n)).paginate(page,limit)
        return [part_register for part_register in part_registers]
    
