from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import User, Part, ProcessConstantRegister
from ..schemas import PartRequestModel, PartResponseModel, DeviceRequestModel
from ..schemas import PartInDeviceRequestModel, RegisterRequestModel
from ..schemas import ProcessRequestModel, ProcessResponseModel, DeviceResponseModel
from ..common import get_current_user
from datetime import datetime
from peewee import fn

router = APIRouter(prefix='/registers')

@router.post('', response_model=PartResponseModel)
async def create_part_register(new_part_request: PartRequestModel):

    # Comprobar existencia en base de datos del numero de parte:
    #if Part.select().where(Part.serial_number == new_part_request.serial_number).first() is None:
    #    # Cambiar Part por el esquema de la base de datos que contenga los datos de los proyectos dados de alta
    #    raise HTTPException(status_code=404, detail='El numero de parte no existe')

    # Comprobar la existencia de ese numero de parte en la tabla de proyectos dados de alta
    # Comprobar que ese numero serial no se encuentra repetido para ese dispositivo ese mismo dia
    # Insertar en la base de datos
    try:
        new_part = Part.create(
            device_id = new_part_request.device_id,
            part_number = new_part_request.part_number,
            serial_number = new_part_request.serial_number,
            leak_value = new_part_request.leak_value,
            operator_id = new_part_request.operator_id,
            status = new_part_request.status
        )

        return new_part
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

# Obtener un registro en especifico
    # /part_register
    # Model(cabine_id, dia, no_parte, serial_number) -> RegisterRequestModel()
    # Return (id, supplier_id, no_parte, cabine_id, serial_number, leak_value, operator_id, status, datetime)
@router.get('/part_register', response_model= PartResponseModel)
async def get_part_register(params:RegisterRequestModel = Depends()):

    date_n = datetime.strptime(params.datetime_test, '%Y-%m-%d').date()
    part_n = params.part_number
    device_n = params.device_id
    serial_n = params.serial_number
    
    part_register = Part.select().where((Part.device_id == device_n) &
                                         (Part.part_number == part_n) &
                                         (Part.serial_number == serial_n) &
                                         (fn.DATE(Part.datetime_test) == date_n)).first()
    if part_register is None:
        raise HTTPException(status_code=404, detail= 'La pieza consultada no existe')
    
    return part_register