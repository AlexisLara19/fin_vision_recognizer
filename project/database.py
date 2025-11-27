from peewee import *
from datetime import datetime
import hashlib
import os
from dotenv import load_dotenv

if not os.getenv("RUNNING_IN_DOCKER"):
    load_dotenv()  

DB_NAME = os.getenv("DB_NAME", "default_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))


database = MySQLDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


#___________________ Process ___________________#
class ProcessConstantRegister(Model):
    process_description = TextField()
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = database # La de arriba
        table_name = 'process'

#___________________ Client ___________________#
class ClientConstantRegisters(Model):
    client_name = CharField(max_length=50, unique=True)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = database # La de arriba
        table_name = 'clients'

#___________________ User ___________________#
class User(Model):
    username = CharField(max_length=50, unique=True)
    password = CharField(max_length=50)
    created_at = DateTimeField(default=datetime.now)

    def __str__(self):
        return self.username
    
    class Meta:
        database = database # La de arriba
        table_name = 'users'

    @classmethod
    def authenticate(cls, username, password):
        user = cls.select().where(User.username == username).first()

        if user and user.password == cls.create_password(password):
            return user

    @classmethod
    def create_password(cls, password: str):
        h = hashlib.md5()
        password = h.update(password.encode('utf-8'))
        return h.hexdigest()

#___________________ Projects ___________________#
class ProjectConstantRegisters(Model):
    client_id = ForeignKeyField(ClientConstantRegisters, backref='projects', on_delete='CASCADE')
    project_name = CharField(max_length=50, unique=True)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = database # La de arriba
        table_name = 'projects'

#___________________ Products ___________________#
class ProductConstantRegisters(Model):
    project_id = ForeignKeyField(ProjectConstantRegisters, backref='products')
    part_number = CharField(max_length=50, unique=True)
    description = CharField(max_length=50)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = database # La de arriba
        table_name = 'products'

#___________________ Devices ___________________#
class DeviceConstantRegisters(Model):
    device_name = CharField(max_length=50)
    project_id = ForeignKeyField(ProjectConstantRegisters, backref='devices')
    process_id = ForeignKeyField(ProcessConstantRegister, backref='devices')
    class Meta:
        database = database # La de arriba
        table_name = 'devices'

# Tomar como referencia para crear bases de datos independientes por modelo
# Crear metodo de CREATE NEW TABLE que tome como referencia 
#___________________ Parts ___________________#
class Part(Model):
    #supplier_id = IntegerField()
    #device_id = ForeignKeyField(DeviceConstantRegisters, backref='parts', on_delete='CASCADE')

    #part_number = ForeignKeyField(ProductConstantRegisters, backref='parts', on_delete='CASCADE')

    device_id = ForeignKeyField(DeviceConstantRegisters, backref='parts')
    part_number = ForeignKeyField(ProductConstantRegisters, backref='parts')
    serial_number = TextField()
    leak_value = TextField()
    operator_id = ForeignKeyField(User, backref='parts')
    status = IntegerField()
    datetime_test = DateTimeField(default=datetime.now)

    def __str__(self) :
        return self.part_number + ' - ' + self.serial_number
    
    class Meta:
        database = database # La de arriba
        table_name = 'product_registers'

