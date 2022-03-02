from inspect import getmembers, isfunction

from NetworkAnalyzer import NetworkAnalyzer

functions_list = getmembers(NetworkAnalyzer, isfunction)

for func in functions_list:
    print(f"{func[0]}()")