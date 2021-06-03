import rtmidi
import time

midiin = rtmidi.RtMidiIn()

def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())

def open_device(cb, port_num=1):
    """
    Open the midi device
    this has been tested with an Akai MPKmini. You might need to change the port number, etc.
    """
    ports = range(midiin.getPortCount())
    if ports:
        for i in ports:
            print(midiin.getPortName(i))
        i = 1
        midiin.openPort(port_num)
        midiin.setCallback(cb)
#        while True:
#            m = midiin.getMessage(25) # some timeout in ms
#            if m:
#                print_message(m)
    else:
        print('NO MIDI INPUT PORTS!')

def note_callback(note):
    print(note)
    print(type(note))
    print(note.getNoteNumber())

def main():
    open_device(note_callback)
    while True:
        time.sleep(0.001)

if __name__ == "__main__":
    main()
