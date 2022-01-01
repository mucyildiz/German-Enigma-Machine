import click

class Rotor:
    
    def __init__(self, rotor, offset_tracker):
        self.rotor = rotor 
        self.offset_tracker = offset_tracker

    def __str__(self):
        return self.rotor
    
    def set_start_position(self, index=0):
        self.rotor = self.rotor[index:] + self.rotor[:index]
        return self.rotor

    def rotate_rotor(self):
        self.rotor = self.rotor[1:] + self.rotor[:1]
        self.offset_tracker = self.offset_tracker[1:] + self.offset_tracker[:1]
    

def go_thru_plugboard(letter, plugboard):
    if letter not in plugboard:
        return letter
    
    plugboard_list = list(plugboard)
    index_of_letter = plugboard.index(letter)

    #edge cases where the passed in letter is the first or last letter in the plugboard string
    if index_of_letter == 0:
        return plugboard_list[1]

    if index_of_letter + 1 == len(plugboard):
        return plugboard_list[-2]

    char_after = plugboard[plugboard.index(letter) + 1]
    char_before = plugboard[plugboard.index(letter) - 1]

    #if the character after the letter is a space, then the letter the inputted letter is paired with is the one before it
    if char_after == ' ':
        return char_before
    
    return char_after

def shift_keyboard(ring_setting):
    keyboard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # shift keyboard according to ring_setting
    rotate = 1 - ring_setting
    shifted_keyboard = keyboard[rotate:] + keyboard[:rotate]
    return shifted_keyboard


def enigma_encryption(message, left_rotor, middle_rotor, right_rotor, plugboard, reflector):

    encrypted_message = ''
    
    original_keyboard = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    list_reflector = list(reflector)

    right_rotor_shift_count = 0

    for letter in message:
        right_rotor.rotate_rotor()
        right_rotor_shift_count += 1

        if right_rotor_shift_count % 26 == 0:
            middle_rotor.rotate_rotor()
            
        if right_rotor_shift_count % (26 ** 2) == 0:
            left_rotor.rotate_rotor()

        right_offset = right_rotor.offset_tracker
        mid_offset = middle_rotor.offset_tracker
        left_offset = left_rotor.offset_tracker

        r_rotor = right_rotor.rotor
        m_rotor = middle_rotor.rotor
        l_rotor = left_rotor.rotor

        post_plugboard = go_thru_plugboard(letter, plugboard)
        key_index = original_keyboard.index(post_plugboard) 
        key_map = right_offset[key_index] 
        key_index = right_offset.index(key_map)
        
        # encrypting key in right_rotor before it goes to mid rotor 
        key_map = r_rotor[key_index]
        key_index = right_offset.index(key_map)
        key_map = mid_offset[key_index]
        key_index = mid_offset.index(key_map)
        key_map = m_rotor[key_index]
        
        # store offset index of mid_encrypt before passing it through left rotor
        key_index = left_offset.index(key_map)
        key_map = l_rotor[key_index]

        keyboard_pos = original_keyboard.index(key_map)
        thru_reflector = list_reflector[keyboard_pos]

        # now we do the inverse of all the operations to follow the letter back and retrieve our output
        key_index = l_rotor.index(thru_reflector)
        key_map = left_offset[key_index]
        key_index = m_rotor.index(key_map)
        key_map = mid_offset[key_index]

        key_index = mid_offset.index(key_map)
        key_map = right_offset[key_index]
        key_index = r_rotor.index(key_map)
        key_map = right_offset[key_index]
        key_index = right_offset.index(key_map)

        output = original_keyboard[key_index]

        #send output through plugboard again
        output = go_thru_plugboard(output, plugboard)

        encrypted_message += output
    return encrypted_message


@click.command()
@click.option('--message', prompt='Enter message to encrypt (No spaces allowed for historic accuracy): ', help='Enter message to encrypt: ')
@click.option('--plugboard', prompt='Enter plugboard (5 pairs of letters eg AB CD ...): ', help='Enter plugboard: ')
@click.option('--reflector', prompt='Enter reflector (A through C): ', help='Enter reflector: ')
@click.option('--left_rotor', prompt='Enter left rotor index (1 through 5): ', help='Enter left rotor: ')
@click.option('--middle_rotor', prompt='Enter middle rotor index (1 through 5): ', help='Enter middle rotor: ')
@click.option('--right_rotor', prompt='Enter right rotor index (1 through 5): ', help='Enter right rotor: ')
@click.option('--left_start_letter', prompt='Enter left rotor start index (A through Z): ', help='Enter left rotor start letter: ', default='A')
@click.option('--middle_start_letter', prompt='Enter middle rotor start index (A through Z): ', help='Enter middle rotor start letter: ', default='A')
@click.option('--right_start_letter', prompt='Enter right rotor start index (A through Z): ', help='Enter right rotor start letter: ', default='A')
def main(message, plugboard, reflector, left_rotor, middle_rotor, right_rotor, left_start_letter, middle_start_letter, right_start_letter):

    keyboard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


    # historically, each enigma machine was stocked with 5 rotors, with 3 of them being intended for use on any given day
    rotors = ['EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'AJDKSIRUXBLHWTMCQGZNPYFVOE',
    'BDFHJLCPRTXVZNYEIWGAKMUSQO', 'ESOVPZJAYQUIRHXLNFTGKDCMWB', 'VZBRGITYUPSDNHLXAWMJQOFECK'
    ]

    # it doesn't really matter how many reflectors we have, I'm gonna go with 3
    reflectors = ['EJMZALYXVBWFCRQUONTSPIKHGD', 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
    'FVPJIAOYEDRZXWGCTKUQSBNMHL'    
    ]

    right_rotor = rotors[int(right_rotor) - 1]
    middle_rotor = rotors[int(middle_rotor) - 1]
    left_rotor = rotors[int(left_rotor) - 1]

    right_rotor = Rotor(right_rotor, keyboard)
    middle_rotor = Rotor(middle_rotor, keyboard)
    left_rotor = Rotor(left_rotor, keyboard)

    right_rotor.set_start_position(keyboard.index(right_start_letter))
    middle_rotor.set_start_position(keyboard.index(middle_start_letter))
    left_rotor.set_start_position(keyboard.index(left_start_letter))

    reflector = reflectors[keyboard.index(reflector)]

    message = message.upper()
    message = ''.join(message.split())
    print(enigma_encryption(message, left_rotor, middle_rotor, right_rotor, plugboard, reflector))


if __name__ == "__main__":
    main()



