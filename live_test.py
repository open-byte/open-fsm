from src.open_fsm.states import StateField


class FSMTest:
    state = StateField(states=('initial', 'finished'), default='initial')

    @state.transition(source='initial', target='finished')
    def finish(self) -> None:
        print('Finishing the process...')


fsm = FSMTest()

print(fsm.state)  # This will trigger the __get__ method of StateField
fsm.state = 'finished'  # This will trigger the __set__ method of StateField
fsm.finish()  # This will trigger the transition decorator and print the transition message
print(fsm.state)  # This will trigger the __get__ method of StateField
