
from pydantic import BaseModel, validator
from pydantic.utils import GetterDict
from peewee import ModelSelect #Peewee es un ORM

from typing import Any

#____________________Clases Base ____________#

class PeeweeGetterDict(GetterDict):
    """
    Esta funcion realiza el mapeo de atributos 
    del ORM (resultantes de una consulta a una db) a los de los modelos 
    """
    def get(self, key:Any, default: Any = None):
        
        #obtenemos los atributos del Objeto Model(id,name, password, created_at) y los 
        # coomparamos con los atributos del ResponseModel (id, name)
        res = getattr(self._obj, key, default)
        
        if isinstance(res, ModelSelect):
            return list(res)  # Convertir a lista si es una consulta de Peewee
        
        return res
    
class ResponseModel(BaseModel):
    """utilizamos esta clase para 
    mapear los atributos del objeto proveniente de la base de datos
    a los del modelo de respuesta en Pydantic"""
    class Config:
        orm_mode = True # Indica que el modelo puede ser poblado por un ORM
        getter_dict = PeeweeGetterDict # Usamos la clase personalizada para mapear los atributos del modelo ORM a los del modelo Pydantic


#____________________User____________________#

class UserRequestModel(BaseModel):
    """
    Esta clase sirve para definir un modelo a acomprobar
    al recibir datos en un endpoint"""
    username: str
    password: str

    @validator('username')
    def username_validator(cls, username):
        """
        Validamos una longitud minima y maxima del username
        """
        if len(username) < 3 or len(username) > 50:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')  
        return username
    
    @validator('password')
    def password_validator(cls, password):
        """
        Validamos una longitud minima y maxima del username
        """
        if len(password) < 3 or len(password) > 12:
            raise ValueError('La contrasenia de usuario debe tener un minimo de 3 caracteres \n y un maximo 12')
        return password

class UserResponseModel(ResponseModel):
    """ Se define un modelo de respuesta para 
    las solicitudes de usuario"""
    id: int
    username: str



#___________________Process ___________________#
class ProcessRequestModel(BaseModel):
    """
    Modelo de recepcion de datos desde 
    el dispositivo
    """
    process_description: str

class ProcessResponseModel(ResponseModel):
    """
    Modelo de respuesta despues de la recepcion de 
    de datos desde el dispositivo
    """
    # Return (id, supplier_id, part_number, device_id, serial_number, leak_value, operator_id, status, datetime)
    id: int
    process_description: str

#___________________ Client ___________________#
class ClientRequestModel(BaseModel):
    client_name: str

class ClientResponseModel(ResponseModel):
    id: int
    client_name: str
#___________________ Project ___________________#
class ProjectRequestModel(BaseModel):
    client_id: int
    project_name: str

class ProjectResponsetModel(ResponseModel):
    id: int
    client_id: ClientResponseModel
    project_name: str

#___________________ Device ___________________#
class DeviceRequestModel(BaseModel):
    
    project_id: int
    process_id: int
    device_name: str

class DeviceResponseModel(ResponseModel):
    id: int
    project_id: ProjectResponsetModel
    process_id: ProcessResponseModel
    device_name: str

#___________________ Product ___________________#
class ProductRequestModel(BaseModel):
    project_id: int
    part_number: str
    description: str

class ProductResponsetModel(ResponseModel):
    id: int
    project_id: ProjectResponsetModel
    part_number: str
    description: str

#____________________Part____________________#
class PartRequestModel(BaseModel):
    """
    Modelo de recepcion de datos desde 
    el dispositivo
    """
    device_id: int
    part_number: int
    serial_number: str
    leak_value: str
    operator_id: int
    status: int

    # Agregar validador para serial number y para leak value (solo numeros)
    # Agregar validador de device_id segun la IP
    # Agregar validador de operador

class PartResponseModel(ResponseModel):
    """
    Modelo de respuesta despues de la recepcion de 
    de datos desde el dispositivo
    """
    # Return (id, supplier_id, part_number, device_id, serial_number, leak_value, operator_id, status, datetime)
    id: int
    device_id: DeviceResponseModel
    part_number: ProductResponsetModel
    serial_number: str
    leak_value: str
    #operator_id: int
    status: int

#____________________DashBoard________________#
class DashBoardUpdateResponseModel(ResponseModel):
    pass

# Model(device_id, dia, no_parte) -> PartInDeviceRequestModel()
class PartInDeviceRequestModel(BaseModel):
    device_id: int
    part_number: str
    datetime_test: str

# Model(device_id, dia, no_parte, serial_number) -> RegisterRequestModel()
class RegisterRequestModel(BaseModel):
    device_id: int
    part_number: str
    serial_number: str
    datetime_test: str
