import datetime
from flask import Flask
from flask import render_template, redirect, url_for, request
from data import db_session
from data.users import User
from data.products import Product
from data.baskets import Basket
from data.products_img import Products_img
from data.comments import Comments
from data.order import Order
from forms.user_form import *
from forms.product_form import ProductForm, CommentsForm
from forms.search_form import FindForm
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from api import product_api
from api import user_api
from data.necessery import *
from data.mail_sender import send_email

from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import os
import shutil
import random
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
load_dotenv()  # Для отправки писем на почту

admins = {  # Админы данного сайта, их id и почта
    1: 'kepka9687@gmail.com'
}


# Главная страница
@app.route('/')
@app.route('/index', methods=["GET", "POST"])
def index():
    form = FindForm()
    if form.validate_on_submit():
        return redirect(f'/search/{form.find.data}')
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).all()
    return render_template("index.html", prod=prod, is_active1='active', form=form, admins=admins)


# Страница, где пользователь ищет продукты
@app.route('/search/<string:request>', methods=['GET', 'POST'])
def search(req):
    form = FindForm()
    if form.validate_on_submit():
        return redirect(f'/search/{form.find.data}')
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).all()
    found_prod = []
    for item in prod:
        # item - все продукты в магазине
        for item2 in req.lower().split():
            # item2 - слова в запросе пользователя
            if item.name.lower().find(item2) == -1:  # Если ничего не нашел в запросе,
                new = transliterate(item2)  # то вдруг пользователь не поменял раскладку и переделываем запрос
                if item.name.lower().find(new) != -1:  # и находим его в продуктах
                    found_prod.append(item)
            else:
                found_prod.append(item)
    return render_template("search.html", prod=found_prod, prod2=prod, is_active1='active', form=form,
                           request=req, admins=admins)


# Страница продукта
@app.route('/product/<int:prod_id>', methods=['GET', 'POST'])
def product(prod_id):
    # Очищаем папку
    shutil.rmtree('static/img/product_now')
    os.mkdir('static/img/product_now')
    # Собираем информацию о продукте
    db_sess = db_session.create_session()
    prod = db_sess.query(Product).filter(Product.id == prod_id).first()
    img_prod = db_sess.query(Products_img).filter(Products_img.product_id == prod_id).first()
    prod_in_basket = []
    try:
        basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
        for item in basket.products:
            prod_in_basket.append(item.id)
    except AttributeError:
        pass

    # Собираем все картинки с базы данных
    all_img = [img_prod.img1, img_prod.img2, img_prod.img3, img_prod.img4, img_prod.img5]
    img, prod_name_file, num = {}, prod.image_path.split('/')[-1].split('.')[0], 0
    for item in all_img:
        if item is not None:
            img[f'{str(prod_name_file) + str(num)}.jpg'] = item
            num += 1

    # Комментарии под продуктом
    form = CommentsForm()
    comments = db_sess.query(Comments).filter(Comments.product_id == prod_id).all()
    if form.validate_on_submit():
        uploads_path = join(dirname(realpath(__file__)), 'static\\img\\product_now')
        image = request.files['image']
        binary_image = None
        for word in ['.png', '.jpg', '.gif']:
            if image.filename.find(word) != -1:
                image.save(os.path.join(uploads_path, secure_filename(image.filename)))
                binary_image = convert_to_binary_data(os.path.join(uploads_path, secure_filename(image.filename)))
                break
        comment = Comments(
            product_id=prod_id,
            user_id=current_user.id,
            text=form.comment.data,
            image=binary_image
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/product/{prod_id}')
    return render_template("product.html", prod=prod, img_prod=img_prod, is_active1='active', os=os,
                           write_to_file=write_to_file, all_img=img, first_img=list(img.keys())[0],
                           prod_in_basket=prod_in_basket, comments=comments, form=form, no_footer=True, admins=admins)


# Покупка товаров
@app.route('/buyprod/<string:item>/<int:prod_id>', methods=['GET', 'POST'])
def buy_products(item, prod_id):
    try:
        product_ides = ''
        db_sess = db_session.create_session()
        form = Contacts()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if item == 'basket':  # Если пользователь хочет купить товары с корзины
            basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
            for i in basket.products:
                product_ides += f'{i.id};'
        else:  # Если хочет купить продукт в один клик
            basket = db_sess.query(Product).filter(Product.id == prod_id).first()
            product_ides += f'{basket.id};'
        if form.validate_on_submit():
            phone_number = reformat_number(form.phone_number.data)
            if not phone_number:
                return render_template("buy_products.html", basket=basket, is_active2='active',
                                       form=form, user=user, message=True, where=item, admins=admins)
            else:
                prod_sum = 0
                if item == 'basket':
                    for i in basket.products:
                        prod_sum += i.discount
                else:
                    prod_sum = basket.discount
                db_sess.query(User).filter(User.id == current_user.id).update(
                    {'contact_phone': phone_number,
                     'address': f'{form.district.data} {form.street.data} {form.home.data}',
                     'flat': form.flat.data})
                order = Order(
                    user_id=current_user.id,
                    product_ides=product_ides,
                    full_name=form.full_name.data,
                    amount=prod_sum,
                    comment=form.comment.data
                )
                db_sess.add(order)
                db_sess.commit()
                return render_template("pay.html", is_active2='active', order_id=order.id, where=item)
        return render_template("buy_products.html", basket=basket, is_active2='active',
                               form=form, user=user, where=item, admins=admins)
    except AttributeError:
        return render_template("profile.html", is_active2='active')


# Страница с окончанием покупки
@app.route('/th/<string:where>/<int:order_id>')
def thanks(where, order_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    db_sess.query(Order).filter(Order.id == order_id).update({'payment': 'cash', 'is_ordered': True})

    if where == 'basket':  # Если пользователь заказывал с корзины, то удаляем из корзины продукты, которые он заказал
        order = db_sess.query(Order).filter(Order.id == order_id).first()
        basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
        for j in [i for i in order.product_ides.split(';') if i]:
            basket.products.remove(db_sess.query(Product).filter(Product.id == int(j)).first())
    db_sess.commit()
    return render_template("thanks.html", is_active2='active', user=user, admins=admins)


# Страница с контактами
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', is_active4='active', admins=admins)


# Страница О нас
@app.route('/about')
def about():
    return render_template('about.html', is_active5='active', admins=admins)


# Страница Помощь
@app.route('/help')
def help_():
    return render_template('help.html', is_active6='active', admins=admins)


# Профиль пользователя
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profileImg = f'img/profileImg.jpg'
    try:
        form = RedactProfile()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        # Открываем фото профиля если есть
        if user.photo is not None:
            # Очищаем папку
            shutil.rmtree('static/img/profile_img')
            os.mkdir('static/img/profile_img')
            # И записываем в файл
            with open(f'''static/img/profile_img/{user.name}{user.id}.jpg''', 'wb') as file:
                file.write(user.photo)
            profileImg = f'img/profile_img/{user.name}{user.id}.jpg'
        if form.is_submitted():
            phone_number = reformat_number(form.phone_number.data)
            if not phone_number:  # Если записан неправильный формат телефона
                return render_template("profile.html", is_active3='active', form=form, user=user,
                                       message=True, admins=admins, convert_datetime=convert_datetime,
                                       profileImg=url_for('static', filename=profileImg))
            else:
                # Изменяем информацию о пользователе в профиле
                image = request.files['profile_photo']
                binary_image = None
                if image.filename != '':
                    filepath = f'static/img/profile_img/{image.filename}'
                    image.save(filepath)
                    cut_image(filepath, filepath, False)
                    binary_image = convert_to_binary_data(filepath)
                db_sess.query(User).filter(User.id == current_user.id).update(
                    {'surname': form.surname.data,
                     'name': form.name.data,
                     'patronymic': form.patronymic.data,
                     'contact_phone': phone_number,
                     'address': f'{form.district.data} {form.street.data} {form.home.data}',
                     'flat': form.flat.data,
                     'photo': binary_image})
                db_sess.commit()
        return render_template("profile.html", user=user, is_active3='active', admins=admins,
                               profileImg=url_for('static', filename=profileImg),
                               convert_datetime=convert_datetime, form=form)
    except AttributeError:
        return render_template("profile.html", is_active3='active', admins=admins,
                               profileImg=url_for('static', filename=profileImg))


# Корзина пользователя
@app.route('/view_basket', methods=["GET", "POST"])
def view_basket():
    try:
        db_sess = db_session.create_session()
        basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
        return render_template("view_basket.html", basket=basket, is_active2='active', admins=admins)
    except AttributeError:
        return render_template("profile.html", is_active2='active', admins=admins)


# Показываем заказы пользователя
@app.route('/my_orders', methods=["GET", "POST"])
def my_orders():
    db_sess = db_session.create_session()
    data = db_sess.query(Order).filter(Order.user_id == current_user.id).all()
    return render_template('my_orders.html', is_active3='active', admins=admins, convert_datetime=convert_datetime,
                           orders=data, db_sess=db_sess, Product=Product, order_stage=order_stage)


# Страница приобретённых товаров
@app.route('/purchased', methods=["GET", "POST"])
def purchased():
    db_sess = db_session.create_session()
    data = db_sess.query(Order).filter(Order.user_id == current_user.id).all()
    return render_template('purchased.html', is_active3='active', admins=admins,
                           orders=data, db_sess=db_sess, Product=Product)


# Добавить товар в корзину
@app.route('/buy/<int:id>/<string:bull>', methods=["GET", "POST"])
def buy(id, bull):
    try:
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
        basket.products.append(product)
        db_sess.commit()
        if bull == 'True':
            return redirect(f"/product/{id}")
        return redirect("/#win1")
    except AttributeError:
        return render_template("profile.html", is_active2='active', admins=admins)


# Удалить продукт из корзины
@app.route('/delete_item_from_basket/<int:id>/<int:where>', methods=["GET", "POST"])
def delete_item_from_basket(id, where):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
    basket.products.remove(product)
    db_sess.commit()
    if where == 0:
        return redirect("/view_basket")
    if where == 1:
        return redirect("/buyprod/basket/0")


# Главная
@app.route('/main', methods=["GET", "POST"])
def main():
    db_session.global_init("db/shop.db")
    db_sess = db_session.create_session()
    db_sess.commit()
    app.register_blueprint(product_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Выйти из аккаунта
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")


# Переменные для страницы /register
cod = 000000
datas = []


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    global cod, datas
    form = RegisterForm()
    form2 = RegisterEmail()
    db_sess = db_session.create_session()
    if form.submit.data and form.validate():  # Регистрация и проверка почты
        cod = random.randrange(100000, 999999)
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, is_active1='active',
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, is_active1='active',
                                   message="Такой пользователь уже есть")
        if send_email(form.email.data, 'Подтверждение почты', f'Код для входа: {cod}'):
            datas = datas.clear()
            datas = [form.name.data, form.surname.data, form.email.data, form.password.data]
            return render_template('register.html', title='Registration', form=form, is_active1='active',
                                   send_email=True, message=f'На почту {form.email.data} отправлен код подтверждения', form2=form2)

        return render_template('register.html', title='Registration', form=form, is_active1='active',
                               message='Не удалось отправить письмо на почту')

    if form2.submit2.data and form2.validate():
        if form2.code.data == cod:  # Проверка кода с почты
            user = User(
                name=datas[0],
                surname=datas[1],
                email=datas[2]
            )
            user.set_password(datas[3])
            db_sess.add(user)
            db_sess.commit()
            user_for_basket = db_sess.query(User).filter(User.name == user.name,
                                                         User.surname == user.surname).first()
            basket = Basket(
                user_id=user_for_basket.id
            )
            db_sess.add(basket)
            db_sess.commit()
            return redirect('/login')
        else:
            return render_template('register.html', title='Registration', form=form, is_active1='active',
                                   send_email=True, message=f'Неправильный код', form2=form2)

    return render_template('register.html', title='Registration', form=form, is_active1='active')


# Вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, is_active1='active')
    return render_template('login.html', title='Авторизация', form=form, is_active1='active')


# Страницы админа
# Добавить продукт
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if current_user.id in admins:
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static\\img\\product_now')
        UPLOADS_PATH2 = join(dirname(realpath(__file__)), 'static\\img\\product_img')
        form = ProductForm()
        if form.validate_on_submit():
            # Добавляем продукт
            db_sess = db_session.create_session()
            if db_sess.query(Product).filter(User.name == form.name.data).first():
                return render_template('add_product.html', title='Добавление товара',
                                       form=form,
                                       message="Такой продукт уже есть")
            # Добавляем картинки к продукту
            image1 = request.files['image1']
            image2 = request.files['image2']
            image3 = request.files['image3']
            image4 = request.files['image4']
            image5 = request.files['image5']
            images = [image1, image2, image3, image4, image5]
            binary_images = []
            name_images = []
            for image in images:
                if image.filename != '':
                    image.save(os.path.join(UPLOADS_PATH, secure_filename(image.filename)))
                    name_images.append(image.filename)
                    binary_images.append(convert_to_binary_data(os.path.join(UPLOADS_PATH, secure_filename(image.filename)))
                                         )

            cut_image(f'static/img/product_now/{name_images[0]}',
                      os.path.join(UPLOADS_PATH2, secure_filename(images[0].filename)))
            if len(binary_images) < 5:
                for _ in range(5 - len(binary_images)):
                    binary_images.append(None)
            prod = Product(
                name=form.name.data,
                type=form.type.data,
                price=form.price.data,
                count=form.count.data,
                discount=form.discount.data,
                description=form.description.data,
                image_path=f'/static/img/product_img/{name_images[0]}'
            )
            db_sess.add(prod)
            db_sess.commit()
            print(prod.id)
            prod_images = Products_img(
                product_id=prod.id,
                img1=binary_images[0],
                img2=binary_images[1],
                img3=binary_images[2],
                img4=binary_images[3],
                img5=binary_images[4]
            )
            db_sess.add(prod_images)
            db_sess.commit()

            for image in images:
                if image.filename != '':
                    os.remove(os.path.join(UPLOADS_PATH, secure_filename(image.filename)))
            return redirect('/add_product')
        return render_template('add_product.html', form=form, is_active7='active', admins=admins)


# Удалить продукт
@app.route('/delete_item/<int:id>', methods=["GET", "POST"])
def delete_item(id):
    db_sess = db_session.create_session()
    if current_user.id in admins:
        product = db_sess.query(Product).filter(Product.id == id).first()
        db_sess.delete(product)
        db_sess.commit()
        return redirect("/")


# Удалить комментарий админу
@app.route('/delete_comment/<int:id_comment>/<int:prod_id>', methods=['GET', 'POST'])
def delete_comment(id_comment, prod_id):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        comment = db_sess.query(Comments).filter(Comments.id == id_comment).first()
        db_sess.delete(comment)
        db_sess.commit()
        return redirect(f"/product/{prod_id}")


# Показ товаров
@app.route('/orders/<int:item>', methods=['GET', 'POST'])
def orders(item):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        ords = db_sess.query(Order).all()
        all_ords = 0
        for i in ords:
            if i.is_ordered:
                all_ords += 1
        return render_template('orders.html', is_active8='active', orders=ords, where=item,
                               all_ords=all_ords, admins=admins, convert_datetime=convert_datetime,
                               order_stage=order_stage)


# Взять заказ
@app.route('/take_order/<int:order_id>')
def take_order(order_id):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        admin = db_sess.query(User).filter(User.id == current_user.id).first()
        db_sess.query(Order).filter(Order.id == order_id).update({'take_order_id': current_user.id,
                                                                  'who_ordered': f'{admin.name} {admin.surname}',
                                                                  'stage': 1})
        db_sess.commit()
        return redirect('/orders/1')


# Отменить взятие заказа
@app.route('/not_take_order/<int:order_id>')
def not_take_order(order_id):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        db_sess.query(Order).filter(Order.id == order_id).update({'take_order_id': None,
                                                                  'who_ordered': None,
                                                                  'stage': 0})
        db_sess.commit()
        return redirect('/orders/1')


# Изменить стадию заказа
@app.route('/change_stage/<int:stage>/<int:order_id>')
def change_stage(stage, order_id):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        db_sess.query(Order).filter(Order.id == order_id).update({'stage': stage})
        db_sess.commit()
        return redirect('/orders/4')


# Подтвердить заказ выполненным
@app.route('/order_complete/<int:order_id>')
def order_complete(order_id):
    if current_user.id in admins:
        db_sess = db_session.create_session()
        db_sess.query(Order).filter(Order.id == order_id).update({'is_ordered': False, 'is_paid': True,
                                                                  'should_be_delivered': datetime.datetime.now()})
        db_sess.commit()
        return redirect('/orders/4')


if __name__ == '__main__':
    main()
