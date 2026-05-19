def word_ending(number:int ):
    "Выбор окончания"

    result = ""
    if number % 10 == 1:
        result = "та"
    elif number % 10 == 2 or number % 10 == 3 or number % 10 == 4:
        result = "ты"
    elif number % 10 >= 5:
        result = "т"
    return result
