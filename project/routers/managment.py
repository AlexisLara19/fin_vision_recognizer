from fastapi import APIRouter, HTTPException, Depends
from ..schemas import ProcessResponseModel,ProcessRequestModel, ClientRequestModel, ClientResponseModel
from ..schemas import ProjectRequestModel, ProjectResponsetModel, DeviceRequestModel, DeviceResponseModel
from ..schemas import ProductRequestModel, ProductResponsetModel
from ..database import ProcessConstantRegister, ClientConstantRegisters, ProjectConstantRegisters, DeviceConstantRegisters, ProductConstantRegisters
from typing import List
from datetime import datetime
from peewee import fn

router = APIRouter(prefix='/managment')

#_______________  Clients register endopints ___________________________________
@router.post('/clients', response_model=ClientResponseModel)
async def create_client_register(new_client_request: ClientRequestModel):
    try:
        new_client = ClientConstantRegisters.create(
            client_name = new_client_request.client_name
        )
        return new_client
        
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

@router.get('/clients', response_model=List[ClientResponseModel])
async def get_all_client_registers(page:int=1, limit:int=10):
    clients = ClientConstantRegisters.select().paginate(page,limit)

    return [client for client in clients]

#_______________ Process register endpoints ______________________________________
@router.post('/process', response_model=ProcessResponseModel)
async def create_process_register(new_process_request: ProcessRequestModel):

    # Comprobar la existencia de ese numero de parte en la tabla de proyectos dados de alta
    # Comprobar que ese numero serial no se encuentra repetido para ese dispositivo ese mismo dia
    # Insertar en la base de datos
    try:
        new_process = ProcessConstantRegister.create(
            process_description = new_process_request.process_description
        )
        return new_process
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

@router.get('/process', response_model=List[ProcessResponseModel])
async def get_all_process_registers(page:int=1, limit:int=10):
    processes = ProcessConstantRegister.select().paginate(page,limit)

    return [process for process in processes]

#_______________  Project register endpoints ______________________________________
@router.post('/projects', response_model=ProjectResponsetModel)
async def create_project_register(new_project_request: ProjectRequestModel):
    try:
        new_project = ProjectConstantRegisters.create(
            client_id = new_project_request.client_id,
            project_name = new_project_request.project_name
        )
        return new_project
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

@router.get('/projects', response_model=List[ProjectResponsetModel])
async def get_all_projects_registers(page:int=1, limit:int=10):
    projects = ProjectConstantRegisters.select().paginate(page,limit)

    return [project for project in projects]

#_______________  Device register endpoints ______________________________________
@router.post('/devices', response_model=DeviceResponseModel)
async def create_device_register(new_device_request: DeviceRequestModel):

    # Comprobar la existencia de ese numero de parte en la tabla de proyectos dados de alta
    # Comprobar que ese numero serial no se encuentra repetido para ese dispositivo ese mismo dia
    # Insertar en la base de datos
    try:
        new_device = DeviceConstantRegisters.create(
            project_id = new_device_request.project_id,
            process_id = new_device_request.process_id,
            device_name = new_device_request.device_name
        )

        return new_device
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

@router.get('/devices', response_model=List[DeviceResponseModel])
async def get_all_devices_registers(page:int=1, limit:int=10):
    devices = DeviceConstantRegisters.select().paginate(page,limit)

    return [device for device in devices]

#_______________  Product register endpoints ______________________________________
@router.post('/products', response_model=ProductResponsetModel)
async def create_product_register(new_product_request: ProductRequestModel):

    # Comprobar la existencia de ese numero de parte en la tabla de proyectos dados de alta
    # Comprobar que ese numero serial no se encuentra repetido para ese dispositivo ese mismo dia
    # Insertar en la base de datos
    try:
        new_product = ProductConstantRegisters.create(

            project_id = new_product_request.project_id,
            part_number = new_product_request.part_number,
            description = new_product_request.description
        )

        return new_product
    except Exception as e:
        raise HTTPException(status_code=500, detail= f'Error en database: {e}')

@router.get('/products', response_model=List[ProductResponsetModel])
async def get_all_products_registers(page:int=1, limit:int=10):
    products = ProductConstantRegisters.select().paginate(page,limit)

    return [product for product in products]

    