from subprocess import Popen

clients = []

n = int(input('Сколько клиентских приложений необходимо запустить?'))

for _ in range(n):
    # mode = input('В каком режиме должен быть запущен клиент (r/w)?')
    # while mode not in ('r', 'w'):
    #     mode = input('Введите корректное значение режима клиента (r/w)')
    # path = 'python chat.py ' + mode
    # clients.append(Popen(path,
    #                      creationflags=CREATE_NEW_CONSOLE))

    path = 'python chat.py'
    clients.append(Popen(path, shell=True))
print('Запущено {} клиента(ов)'.format(n))
