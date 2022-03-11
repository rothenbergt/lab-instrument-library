from inspect import getmembers, isfunction

from Multimeter import Multimeter

functions_list = getmembers(Multimeter, isfunction)

for func in functions_list:
    print(f"{func[0]}()")