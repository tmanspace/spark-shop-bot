import os
import telebot
from peewee import IntegrityError
from telebot.types import InlineKeyboardButton
import config
import funcs as f
import static
import db
from telegram_bot_pagination import InlineKeyboardPaginator

bot = telebot.TeleBot(config.TG_TOKEN)
main_menu = f.create_keyboard(
    static.start_markup, row_width=3, one_time_keyboard=True)
channel_id = -418014092  # Chanel for shopping


# FUNCS

def get_page(message, array, name, page=1):
    try:
        paginator = InlineKeyboardPaginator(
            len(array),
            current_page=page,
            data_pattern=f"{name}" + "#{page}"
        )
        print(page)

        buy_key = f"buy_{array[page - 1].product_id}"
        paginator.add_after(InlineKeyboardButton('🔙', callback_data='back'),
                            InlineKeyboardButton('🤑 Купить 🤑', callback_data=buy_key), )
        # paginator.add_after()

        bot.send_photo(
            message.chat.id,
            array[page - 1].photo,
            reply_markup=paginator.markup
        )
    except IndexError:
        bot.send_message(message.chat.id, "Что-то пошло не так, попробуйте заново")
        bot.send_message(message.chat.id, f"Выберите категорию для просмотра товаров",
                         reply_markup=f.create_inline_keyboard(static.cat_dict))


make_up_arr = []
d_arr = []
esthetic_arr = []
presets_arr = []
random_arr = []

# BACK


def back_main(m):
    bot.send_message(m.chat.id, 'Что будем делать дальше?', reply_markup=main_menu)


@bot.callback_query_handler(func=lambda q: q.data == 'back')
def back_shop(q):
    bot.delete_message(
        q.message.chat.id,
        q.message.message_id
    )
    bot.send_message(q.message.chat.id, f"Выберите категорию для просмотра товаров",
                     reply_markup=f.create_inline_keyboard(static.cat_dict))


@bot.callback_query_handler(func=lambda q: q.data == 'back_main')
def back_main_menu(q):
    bot.delete_message(
        q.message.chat.id,
        q.message.message_id
    )
    back_main(q.message)


# START

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id, f"<b>Привет, {message.from_user.first_name}!</b>\n\nЭто магазин с масками:"
                         f" здесь вы найдете то, что вас точно заинтересует, а если нет, то мы вам обязательно поможем."
                         f"\n\nТакже если вам нужен сайт, бот или магазин в Инстаграмм, то вы можете обратиться к нам😉",
        reply_markup=main_menu, parse_mode='html')
    bot.send_message(channel_id, f"Пользователь {message.from_user.username} зашел в магазин")
    try:
        db.User.get(db.User.user_id == message.chat.id)
    except Exception:
        db.User.create(user_id=message.chat.id,
                       user_name=message.from_user.username)


#  ADDITIONAL

@bot.message_handler(func=lambda m: m.text == static.start_markup[1])
def get_billing(message):
    text = f"Для того, чтобы купить нужную вам маску - выберите ее в каталоге и " \
           f"нажмите на кнопку купить.\nМы свяжемся с вами в течение 5 минут и уточним все детали! 💳"
    try:
        db.User.create(user_id=message.chat.id,
                       user_name=message.from_user.username)
    except IntegrityError:
        pass
    bot.send_message(message.chat.id, text,
                     reply_markup=f.create_inline_keyboard(static.cat_dict))


@bot.message_handler(func=lambda m: m.text == static.start_markup[2])
def get_contacts(message):
    text = f"По всем вопросам сюда:\n🐺 <b>@artwallter</b>"
    try:
        db.User.create(user_id=message.chat.id,
                       user_name=message.from_user.username)
    except IntegrityError:
        pass
    bot.send_message(message.chat.id, text, reply_markup=main_menu, parse_mode='html')


@bot.message_handler(func=lambda m: m.text == static.start_markup[3])
def get_new_offers(message):
    text = f"<b>Мы также можем быстро и качественно:</b>\n\n" \
           f"💻 - <b>Создать сайт</b> самой разной сложности и под любые задачи\n\n" \
           f"🤖 - <b>Создать бота</b> для ваших нужд, который может решать задачи и оптимизировать процессы\n\n" \
           f"🎁 - <b>Создать магазин</b> в Инстаграмм и помочь вам в продвижении ваших продуктов\n\n" \
           f"🎭 - <b>Создать маску</b>, которая нужна именно вам"
    markup = f.create_inline_keyboard(static.want_dict, 2)
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='html')


#
# ADMIN COMMAND
#


@bot.message_handler(commands=['add'])
def add_products(m):
    if m.from_user.username == 'tmanspace':
        bot.send_message(channel_id, 'Закачиваю файлы...')
        print("Закачиваю файлы")
        query = db.Product.delete()
        amount = query.execute()
        for cat in os.listdir('files/'):
            for name in os.listdir(f"files/{cat}"):
                product = f.Product(name, cat)
                for file in os.listdir(f"files/{cat}/{name}"):
                    if file.split('.')[-1] == 'arexport' or file.split('.')[-1] == 'arproj':
                        document = open(f"files/{cat}/{name}/{file}", 'rb')
                        doc = bot.send_document(m.chat.id, document)
                        product.doc_id = doc.document.file_id
                    if file.split('.')[-1] == 'png' or file.split('.')[-1] == 'jpg':
                        document = open(f"files/{cat}/{name}/{file}", 'rb')
                        photo = bot.send_photo(m.chat.id, document)
                        product.photo = photo.photo[0].file_id
                    if file.split('.')[-1] == 'txt':
                        document = open(f"files/{cat}/{name}/{file}", encoding='utf-8', mode='r')
                        arr = document.read().split("\\")
                        product.desc = arr[0]
                        product.price = arr[1]
                if product.price:
                    p = f.add_product(product)
    else:
        return


#
# SHOP
#

@bot.message_handler(func=lambda m: m.text == static.start_markup[0])
def get_shop(m):
    try:
        db.User.create(user_id=m.chat.id,
                       user_name=m.from_user.username)
    except IntegrityError:
        pass
    bot.send_message(m.chat.id, f"Выберите категорию для просмотра товаров",
                     reply_markup=f.create_inline_keyboard(static.cat_dict))


# CALLBACKS


@bot.callback_query_handler(func=lambda q: q.data[:3] == "cat")
def get_products(q):
    cat_name = q.data[4:]
    sql_query = db.Product.select().where(db.Product.category == cat_name)
    bot.delete_message(q.message.chat.id, q.message.message_id)
    if cat_name == 'MakeUp':
        global make_up_arr
        make_up_arr = sql_query[:]
        get_page(q.message, make_up_arr, 'make_up', 1)
    elif cat_name == '3D':
        global d_arr
        d_arr = sql_query[:]
        get_page(q.message, d_arr, '3d', 1)
    elif cat_name == 'Esthetic':
        global esthetic_arr
        esthetic_arr = sql_query[:]
        get_page(q.message, esthetic_arr, 'esthetic', 1)
    elif cat_name == 'Presets':
        global presets_arr
        presets_arr = sql_query[:]
        get_page(q.message, presets_arr, 'presets', 1)
    elif cat_name == 'Random':
        global random_arr
        random_arr = sql_query[:]
        get_page(q.message, random_arr, 'random', 1)


# BUY


@bot.callback_query_handler(func=lambda q: q.data[:3] == "buy")
def buy_product(q):
    product = db.Product.get(db.Product.product_id == q.data[4:])
    bot.delete_message(
        q.message.chat.id,
        q.message.message_id
    )
    try:
        user = db.User.get(db.User.user_id == q.message.chat.id)
        text = f"Вы выбрали продукт {product.name}\n" \
               f"Мы свяжемся с вами по поводу покупки данного товара в ближайшее время.\nСпасибо за ожидание!"
        back_keyboard = f.create_inline_keyboard({'back': '🔙'}, row_width=1)
        bot.send_message(q.message.chat.id, text, reply_markup=back_keyboard)
        bot.send_message(channel_id, f"Новый покупатель @{user.user_name}\nХочет преобрести {product.name}")
        bot.send_document(channel_id, product.product_path)
    except Exception:
        bot.send_message(q.message.chat.id, 'Попробуйте заново! Что-то пошло не так...', reply_markup=main_menu)


#
# LISTING
#


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'make_up')
def show_make_up_image(call):
    page = int(call.data.split('#')[1])
    global make_up_arr
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    get_page(call.message, make_up_arr, 'make_up', page)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'esthetic')
def show_esthetic_image(call):
    page = int(call.data.split('#')[1])
    global esthetic_arr
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    get_page(call.message, esthetic_arr, 'esthetic', page)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'presets')
def show_presets_image(call):
    page = int(call.data.split('#')[1])
    global presets_arr
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    get_page(call.message, presets_arr, 'presets', page)


# WANT

@bot.callback_query_handler(func=lambda q: q.data.split('_')[0] == 'want')
def send_wanted(q):
    data = q.data.split('_')[1]
    service_wanted = ''
    if data == 'site':
        service_wanted += 'Сайт!'
    elif data == 'bot':
        service_wanted += 'Бот!'
    elif data == 'shop':
        service_wanted += 'Магазин Inst!'
    else:
        service_wanted += 'Маска!'
    bot.delete_message(
        q.message.chat.id,
        q.message.message_id
    )
    try:
        user = db.User.get(db.User.user_id == q.message.chat.id)
        bot.send_message(channel_id, f"<b>{service_wanted}</b>\n\nНовый покупатель @{user.user_name}", parse_mode='html')
        back_keyboard = f.create_inline_keyboard({'back': '🔙'}, row_width=1)
        bot.send_message(q.message.chat.id, 'Спасибо за заявку! Мы скоро с вами свяжемся!', reply_markup=back_keyboard)
    except Exception:
        bot.send_message(q.message.chat.id, 'Попробуйте заново! Что-то пошло не так...', reply_markup=main_menu)

bot.polling()
