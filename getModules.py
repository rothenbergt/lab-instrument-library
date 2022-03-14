from inspect import getmembers, isfunction

from SMU import SMU

functions_list = getmembers(SMU, isfunction)

for func in functions_list:
    print(f"{func[0]}()")