import logging
import queue
import threading
import time
import typing
import random
from dataclasses import dataclass

import library
from matrix_button_led_controller import MatrixButtonLEDController

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
USE_LED_HAT = True

@dataclass
class ButtonInfo:
    color: str
    sound: str
    matched: bool


class Game:
    def __init__(self, button_pad: MatrixButtonLEDController):
        self.button_pad = button_pad
        self.button_pad.assign_button_events(self.when_pressed, self.when_held, self.when_released)
        self.buttons: typing.List[ButtonInfo] = []
        self.soundslist: typing.List[str] = []
        self.colors: typing.List[str] = []
        self.sounds: typing.List[str] = []
        self.speaker = library.speaker.Speaker()
        self.initialize_button_pad()
        self.started = False
        self.play_game = True
        self.queue = queue.Queue()
        self.counter = 0
        self.first_button = 0


    @property
    def correct_sound(self):
        """The sound that is played when player gets a pair"""
        # OPTIONAL: change this to a different sound if you want
        return "correct_answer"

    @property
    def incorrect_sound(self):
        """The sound that is played when player makes an incorrect guess"""
        # OPTIONAL: change this to a different sound if you want
        return "incorrect"

    @property
    def end_of_game_sound(self):
        """The sound that is played when the game ends."""
        # OPTIONAL: change this to a different sound if you want
        return "end_of_game"

    def _background_logic_checker(self):
        count = 0
        while self.play_game:
            time.sleep(0.005)  # Prevents busy-waiting
            if self.queue.empty():
                continue
            button_number = self.queue.get()
            print(f"Handling button {button_number}")

            # Example logic: light up the button that was pressed with a constant color
            button = self.button_pad.get_button(button_number)
            self.button_pad.set_button_led_color(button, "black")
#            self.speaker.play_preloaded_wav("gasp_x", wait_until_done=True)  # Play a sound when button is pressed
            # TODO: check your game state, and update things
 #           self.button_pad.get_button(5).color
            
            if self.counter == 1:
                first_button = button_number
                print(first_button)
                print(button_number)
                self.button_pad.set_button_led_color(self.button_pad.get_button(first_button), self.colors[first_button-1])
                self.speaker.play_preloaded_wav(self.sounds[first_button-1], wait_until_done=False) 

            elif (self.counter == 2) and ((self.colors[button_number-1]) == (self.colors[first_button-1])) and button_number != first_button:
                self.button_pad.set_button_led_color(self.button_pad.get_button(button_number), self.colors[button_number-1])
                self.speaker.play_preloaded_wav(self.sounds[button_number-1], wait_until_done=False) 
                self.speaker.play_preloaded_wav(self.correct_sound, wait_until_done=False)

                self.counter = 0
                print(first_button)
                print(button_number)
                count += 1
                print(count)
                if count == 8:
                    self.speaker.play_preloaded_wav(self.end_of_game_sound, wait_until_done=True)

            else:
                self.counter = 0
                self.button_pad.set_button_led_color(self.button_pad.get_button(button_number), self.colors[button_number-1])
                time.sleep(1)
                self.button_pad.set_button_led_color(self.button_pad.get_button(first_button), "black")
                self.button_pad.set_button_led_color(self.button_pad.get_button(button_number), "black")
                self.speaker.play_preloaded_wav(self.incorrect_sound, wait_until_done=False)
                print(first_button)
                print(button_number)

    def when_pressed(self, button):
        # TODO: this is called when a button is pressed. Add what you need to here
        _logger.info(f"Button {button.pin.info.number} pressed")
        self.queue.put(button.pin.info.number)
        self.counter += 1

    def when_held(self, button):
        # TODO: this is called when a button is held. Add what you need to here
        pass

    def when_released(self, button):
        # TODO: this is called when a button is released. Add what you need to here
        pass

    def initialize_button_pad(self):
        self.button_pad.clear_button_pad()
        # TODO: Set all buttons to a color, List of colors to choose from: https://github.com/waveform80/colorzero/blob/master/colorzero/tables.py#L315
        colors_constant = ["aqua", "white", "red", "lime", "brown", "magenta", "orange", "midnightblue"]
        colorslist = colors_constant * 2
        random.shuffle(colorslist)
        



        # sounds are available in the sounds directory
        self.soundslist = [
            "thunder2",
            "fart_z",
            "baby_x",
            "slide_whistle_x",
            "arrow2",
            "phone_pay",
            "bloop_x",
            "car_horn_x",
        ]
        random.shuffle(self.sounds)

        # TODO: assign to buttons
        # button1 = ButtonInfo("Alice", 20)
        # print(self.buttons)

        # keys = ['color', 'sound']
        n=16
        buttonsdict = [{'color':'', 'sound':''}for i in range(n)]
        uniquecolor = 0

        # create dicitonary with randomized colors and unique sounds
        for i in range (len(colorslist)):
            
            # code to add colors
            button = self.button_pad.get_button(i + 1)
            self.button_pad.set_button_led_color(button, colorslist[i])

            currentcolor = colorslist[i]

            # adding color to dictionary
            buttonsdict[i]["color"] = currentcolor
            self.colors.append(currentcolor)
            
            # looping though color constants to check for unique colors
            for j in range(len(colors_constant)):
                print(currentcolor,colors_constant[j])
                if currentcolor == colors_constant[j]:
                    print("match found")
                    
                    uniquecolor = j
                    print(uniquecolor)
                    break

            buttonsdict[i]["sound"] = str(self.soundslist[uniquecolor])
            self.sounds.append(str(self.soundslist[uniquecolor]))

            

        
        time.sleep(3)

        self.button_pad.clear_button_pad()
        print(self.colors)
        print(self.sounds)



    def _start_game(self):
        self.thread = threading.Thread(target=self._background_logic_checker)
        self.thread.start()
        # TODO: play a sound to start the game
        self.started = True

    def play(self):
        self._start_game()
        try:
            input("Press Enter to exit the game...")
        except KeyboardInterrupt:
            print("Exiting game...")
        finally:
            self.play_game = False
            self.thread.join()
            self.button_pad.cleanup()


def _main():
    button_pad = MatrixButtonLEDController(
        scan_delay=0.020, pwm_freq=10000, display_pause=0.001, use_led_hat=USE_LED_HAT
    )
    game = Game(button_pad)
    game.play()


if __name__ == "__main__":
    _main()
