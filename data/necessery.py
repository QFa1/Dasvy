from PIL import Image


def transliterate(name):
    """Превращает все английские символы в русские по раскладке qwerty"""
    # Слоаврь с заменами
    slovar = {'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
              '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
              'l': 'д', ';': 'ж', ':': 'ж', "'": 'э', '"': 'э', '{': 'х', '}': 'ъ', 'z': 'я', 'x': 'ч', 'c': 'с',
              'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю', '<': 'б', '>': 'ю', '`': 'ё', '~': 'ё'}

    # Циклически заменяем все буквы в строке
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name


def convert_to_binary_data(filename):
    # Преобразование данных в двоичный формат
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def write_to_file(data, filename):
    # Преобразование двоичных данных в нужный формат
    with open(f'''static/img/product_now/{filename}''', 'wb') as file:
        file.write(data)


def cut_image(filename, where_to_save, crop=True) -> Image:
    # Функция для обрезки изображения по центру.
    img = Image.open(filename)
    w, h = img.size
    if crop:
        img_crop = img.crop(((w - 600) // 2, (h - 600) // 2, (w + 600) // 2, (h + 600) // 2))
        img_crop.save(where_to_save, quality=95)
    else:
        img_cut = img.resize((500, 500))
        img_cut.save(where_to_save)


def reformat_number(number):
    try:
        string = number.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+', '')
        if int(string[0]) == 8 or int(string[0]) == 7:
            if len(string) == 11:
                return string
            else:
                return False
        return False
    except ValueError:
        return False


def convert_datetime(time, year=True):
    month = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
             '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
    date = str(time).split()[0].split('-')
    day = date[2]
    if int(date[2][0]) == 0:
        day = date[2][1]
    return f'{day} {month[date[1]]} {date[0]}' if year else f'{day} {month[date[1]]}'


def order_stage(stage):
    st = {0: 'Собираем заказ', 1: 'Подготовлен к отгрузке', 2: 'В пути', 3: 'Курьер направляется к вам',
          4: 'Заказ доставлен'}
    for i in st:
        if stage == i:
            return st[i]
