def theme_ending(number:int)->str:
    '''Функция возвращающая строковую переменную окончания слова тем в зависимости от количества'''
    endings = {'1':'а','2':'ы','3':'ы','4':'ы','5':'','6':'','7':'','8':'','9':'','0':''}
    if number > 5 and number < 20:
        ending = ''
    else:
        ending = endings[str(number)[-1]]
    return ending


for page in range(1,200):
    print(page,' тем'+theme_ending(page))