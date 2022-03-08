from inspect import getmembers, isfunction

from Supply import Supply

functions_list = getmembers(Supply, isfunction)

for func in functions_list:
    print(f"{func[0]}()")