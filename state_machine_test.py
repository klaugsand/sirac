from transitions import Machine, State

'''
class Matter(object):

    def say_hello(self):
        print("hello, new state!")

    def say_goodbye(self):
        print("goodbye, old state!")


lump = Matter()

states = [
    State(name='solid', on_exit=['say_goodbye']),
    'liquid',
    {'name': 'gas'}
    ]

machine = Machine(lump, states=states)
machine.add_transition('sublimate', 'solid', 'gas')

# Callbacks can also be added after initialization using
# the dynamically added on_enter_ and on_exit_ methods.
# Note that the initial call to add the callback is made
# on the Machine and not on the model.
machine.on_enter_gas('say_hello')

# Test out the callbacks...
print('{}'.format(lump.state))
machine.set_state('solid')
print('{}'.format(lump.state))
lump.sublimate()
print('{}'.format(lump.state))

'''


class Matter(object):
    def __init__(self):
        self.set_environment()

    def set_environment(self, temp=0, pressure=101.325):
        self.temp = temp
        self.pressure = pressure

    def print_temperature(self):
        print("Current temperature is %d degrees celsius." % self.temp)

    def print_pressure(self):
        print("Current pressure is %.2f kPa." % self.pressure)


lump = Matter()
machine = Machine(lump, ['solid', 'liquid'], initial='solid')
machine.add_transition('melt', 'solid', 'liquid', before='set_environment')

lump.melt(45)  # positional arg;
# equivalent to lump.trigger('melt', 45)
lump.print_temperature()

machine.set_state('solid')  # reset state so we can melt again
lump.melt(pressure=300.23)  # keyword args also work
lump.print_pressure()
