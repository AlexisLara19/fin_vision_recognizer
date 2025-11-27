
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .routers import user_router, part_router, managment_router, historial_router
from .database import database as connection
from .database import ClientConstantRegisters, ProjectConstantRegisters, ProductConstantRegisters, ProcessConstantRegister, DeviceConstantRegisters, User, Part
from .common import create_access_token
from peewee import Model
import time
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title='Production Manager',
              description= 'Piezas de produccion',
              version='1.1')

api_v1 = APIRouter(prefix='/api/v1')

api_v1.include_router(user_router)
api_v1.include_router(part_router)
api_v1.include_router(managment_router)
api_v1.include_router(historial_router)


# VALIDACION CON STANDAR OAUTH
@api_v1.post('/auth')
async def auth(data: OAuth2PasswordRequestForm = Depends()):
    user =  User.authenticate(data.username, data.password)

    if user:
        return {
            #'username' : data.username,
            #'password' : data.password
            'access_token' : create_access_token(user),
            'token_type' : 'Bearer'  # QUE ES ESTO?
        }
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= 'Username o Password incorrectos',
            headers={'WWW-Autenticate' : 'Bearer'}
        )

app.include_router(api_v1)

@app.get('/')
async def index(): # endpoint que se ejecuta de forma asincrona. Si se llegara a tardar mucho en responder o tuviera muchas solicitudes, no bloquea el servidor
    return {'message': 'Servidor en fastapi'}

@app.get('/about')
async def about():
    return {'message': 'Acerca de...'}

#Eventos Startup (cuando el servidor este por comenzar) and Shutdown (cuando el servidor este por cerrar)
"""@app.on_event('startup')
def startup():
    print('Iniciando Servidor...')
    try:
        if connection.is_closed():
            connection.connect()
            print('Conexión exitosa a la base de datos')
        
            connection.create_tables([User, Part]) # Crea las tablas si no existen
    except Exception as e:
        print(f'Error creando las bases de datos {e}')"""

CLIENT_REGISTERS = [
    {'client_name': 'VolksWagen'},
    {'client_name': 'Nissan'},
    {'client_name': 'Caterpillar'}
]

PROJECT_REGISTERS = [
    {'client_id': 1, 'project_name': 'EA211'},
    {'client_id': 1, 'project_name': 'ATLAS'},
    {'client_id': 1, 'project_name': 'LTR'},
    {'client_id': 1, 'project_name': 'EA888'},
    {'client_id': 2, 'project_name': 'L02BE'},
    {'client_id': 3, 'project_name': 'HORIZON'}    
]

PRODUCT_REGISTERS = [
    {'project_id': 1, 'part_number': '04E145785AE', 'description': 'CACEA211 04003CA15(258)'},
    {'project_id': 1, 'part_number': '04E145785L', 'description': 'CACEA211 04003CA11(258)'},
    {'project_id': 2, 'part_number': '3QF121251E', 'description': 'ATLAS 04003RA35(261)'},
    {'project_id': 3, 'part_number': '5QM121251P', 'description': 'LTR P 04003RA09(234)'},
    {'project_id': 3, 'part_number': '5QM121251R', 'description': 'LTR R 04003RA12(234)'},
    {'project_id': 3, 'part_number': '5QM121251Q', 'description': 'LTR Q 04003RA10(234)'},
    {'project_id': 4, 'part_number': '06K117021K', 'description': 'EA888 04003EA08(228)'},
    {'project_id': 5, 'part_number': '214039KZ0A', 'description': 'ECM CON AC 04004ECM1 (270)'},
    {'project_id': 5, 'part_number': '214039KZ1A', 'description': 'ECM SIN AC 04004ECM2 (270)'}
]

PROCESS_REGISTERS = [
    {'process_description': 'Modificado - Inactivo'},
    {'process_description': 'Aprobado en  Maquina'},
    {'process_description': 'Escaneado - Empacado Merida'},
    {'process_description': 'Crimpado'},
    {'process_description': 'Fuga Burda'},
    {'process_description': 'Ensamble de Core'},
    {'process_description': '------'},
    {'process_description': 'Escaneado - Empacado Puebla'}
]

DEVICE_REGISTERS = [
    {'device_name': 'Fuga Fina VIC LTR Camara 1', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Fuga Fina VIC LTR Camara 2', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Fuga Fina ATEQ LTR 1', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Fuga Fina ATEQ LTR 2', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Fuga Fina ATEQ LTR 3', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Fuga Fina ATEQ LTR 4', 'project_id': 3, 'process_id': 2},
    {'device_name': 'Re-Etiquetado LTR P/R', 'project_id': 3, 'process_id': 8},
    {'device_name': 'Ensamble Final ECM 1', 'project_id': 5, 'process_id': 2},
    {'device_name': 'Ensamble Final ECM 2', 'project_id': 5, 'process_id': 2},
    {'device_name': 'Escaneo CAC', 'project_id': 1, 'process_id': 3},
    {'device_name': 'Escaneo ATLAS', 'project_id': 2, 'process_id': 3},
    {'device_name': 'Escaneo  LTR P/R', 'project_id': 3, 'process_id': 3},
    {'device_name': 'Escaneo LTR Q', 'project_id': 3, 'process_id': 3},
    {'device_name': 'Escaneo OIL COOLER EA888', 'project_id': 4, 'process_id': 3},
    {'device_name': 'Escaneo ECM', 'project_id': 5, 'process_id': 3},
    {'device_name': 'Crimper CAC', 'project_id': 1, 'process_id': 4},
    {'device_name': 'Crimper ATLAS', 'project_id': 2, 'process_id': 4},
    {'device_name': 'Crimper LTR P/R', 'project_id': 3, 'process_id': 4},
    {'device_name': 'Crimper Q', 'project_id': 3, 'process_id': 4},
    {'device_name': 'Crimper ECM', 'project_id': 5, 'process_id': 4},
    {'device_name': 'Fuga Burda CAC', 'project_id': 1, 'process_id': 5},
    {'device_name': 'Fuga Burda ATLAS', 'project_id': 2, 'process_id': 5},
    {'device_name': 'Fuga Burda LTR P/R', 'project_id': 3, 'process_id': 5},
    {'device_name': 'Fuga Burda Q', 'project_id': 3, 'process_id': 5},
    {'device_name': 'Fug Burda OC EA888', 'project_id': 4, 'process_id': 5},
    {'device_name': 'Fuga Burda ECM', 'project_id': 5, 'process_id': 5},
    {'device_name': 'Core Builder CAC', 'project_id': 1, 'process_id': 6},
    {'device_name': 'Core Builder ATLAS', 'project_id': 2, 'process_id': 6},
    {'device_name': 'Core Builder LTR P', 'project_id': 3, 'process_id': 6},
    {'device_name': 'Core Builder LTR R', 'project_id': 3, 'process_id': 6},
    {'device_name': 'Core Builder LTR Q', 'project_id': 3, 'process_id': 6}, 
    {'device_name': 'Core Builder LTR ECM', 'project_id': 5, 'process_id': 6}
]

def create_tables(table:Model, data:list):
    
    if table._meta.table_name not in connection.get_tables():
        logging.info(f'Tabla {table} no encontrada, creando...')
        connection.create_tables([table,])
        
        # Insertar datos en la tabla
        if data:
            table.insert_many(data).execute()
            
            #with db.atomic():
            #   for data_dict in CLIENT_REGISTERS:
                #       ClientConstantRegisters.create(**data_dict)

        logging.info(f'Tabla {table} creada')
    else:
        logging.info(f'Tabla {table} OK ')


@app.on_event('startup')
def startup():
    print('Iniciando Servidor...')
    max_retries = 10
    for attempt in range(max_retries):
        try:
            if connection.is_closed():
                connection.connect()
                logging.info('Conexión exitosa a la base de datos')
                
                create_tables(ClientConstantRegisters, CLIENT_REGISTERS)
                create_tables(ProjectConstantRegisters, PROJECT_REGISTERS)
                create_tables(ProductConstantRegisters, PRODUCT_REGISTERS)
                create_tables(ProcessConstantRegister, PROCESS_REGISTERS)
                create_tables(DeviceConstantRegisters, DEVICE_REGISTERS)
                create_tables(Part, None)
                create_tables(User, None)

                logging.info('Las tablas han sido cargadas en el sistema')

                break
            
        except Exception as e:
            #print(f'Intento {attempt+1}/{max_retries} - Error conectando o creando tablas: {e}')
            logging.info(f'Error conectando o creando tablas: {e}')
            time.sleep(3)


@app.on_event('shutdown')
def shutdown():
    print('Cerrando Servidor...')
    if not connection.is_closed():
        connection.close()
        print('Conexión cerrada a la base de datos')


