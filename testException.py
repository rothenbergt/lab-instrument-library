def exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            print(f"{func.__name__} only takes numbers as the argument")
    return inner_function


@exception_handler
def area_square(length):
    print(length * length)
    return length * length


@exception_handler
def area_circle(radius):
    print(3.14 * radius * radius)
    return 3.14 * radius * radius


@exception_handler
def area_rectangle(length, breadth):
    print(length * breadth)
    return length * breadth


print(area_square(2))
print(area_circle(2))
area_rectangle(2, 4)
area_square("some_str")
area_circle("some_other_str")