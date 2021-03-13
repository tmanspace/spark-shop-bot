from peewee import *
import datetime as d

# db = PostgresqlDatabase('Spark shop', user='postgres', password='root', host='localhost', port='5433')
db = SqliteDatabase('./app.db')

print(db)

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(column_name='user_id', primary_key=True)
    user_name = TextField(column_name='username')

    class Meta:
        table_name = 'Users'


class Product(BaseModel):
    product_id = UUIDField(column_name='product_id', primary_key=True, unique=True)
    desc = TextField(column_name='text')
    product_path = TextField(column_name='path')
    add_date = DateField(column_name='date', default=d.datetime.date(d.datetime.today()))
    category = TextField(column_name="cat")
    price = FloatField(column_name="price")
    name = TextField(column_name='name')
    photo = TextField(column_name='photo')

    class Meta:
        table_name = 'Products'


# class Purchase(BaseModel):
#     purchase_id = UUIDField(column_name='purchase_id', primary_key=True, unique=True)
#     purchase_date = DateTimeField(column_name='purchase_date', default=d.datetime.today())
#     user = ForeignKeyField(User)
#     amount = ForeignKeyField(Product, field="price")
#     product_id = ForeignKeyField(Product)
#
#     class Meta:
#         table_name = 'Purchases'


# class Task(BaseModel):
#     task_id = AutoField(column_name='TaskID', primary_key=True)
#     user_id = TextField(column_name='UserID')
#     task_text = TextField(column_name='TaskText')
#     done = BooleanField(column_name='Done', default=False)
#     task_date = DateField(column_name='Date', default=d.datetime.date(d.datetime.today()))
#     task_desc = TextField(column_name='TaskDesc', default='Тут должно быть описание📝')
#     last_target_list = TextField(column_name='LastTargetList')
#
#     class Meta:
#         table_name = 'Tasks'


#
#
# class Group(BaseModel):
#     group_id = AutoField(column_name='GroupID', primary_key=True)
#     date_created = DateField(column_name='DateCreated', default=d.datetime.date(d.datetime.today()))
#     name = TextField(column_name='Name')
#     unique_id = TextField(column_name='UniqueID')
#
#     class Meta:
#         table_name = 'Groups'
#
#
# class GroupMember(BaseModel):
#     UserID = IntegerField(User)
#     group_id = IntegerField(column_name='GroupID')
#
#     class Meta:
#         primary_key = CompositeKey('UserID', 'group_id')
#         table_name = 'GroupMembers'
