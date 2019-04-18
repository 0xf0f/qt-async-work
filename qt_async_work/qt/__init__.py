ui_module = None

supported_modules = [
    'PyQt5',
    'PySide2'
]

for module in supported_modules:
    try:
        __import__(module)
        ui_module = module
        break
    except ModuleNotFoundError:
        pass

if ui_module == 'PyQt5':
    from .pyqt5_imports import *
elif ui_module == 'PySide2':
    from .pyside2_imports import *
else:
    print(
        'Please install either',
        ' or '.join(
            (', '.join(supported_modules[:-1]), supported_modules[-1])
        ),
        'to use this application.')
    from sys import exit
    exit(1)
