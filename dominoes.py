from random import choice, randint, shuffle
from itertools import chain


class Field:

    def __init__(self, number='001'):
        self.number = number
        self.stock_set = []
        self.snake_set = []

    def stock_emptying(self):
        if self.stock_set:
            piece = choice(self.stock_set)
            self.stock_set.remove(piece)
            return piece

    def snake_update(self, direction, piece):
        old_snake_len = len(self.snake_set)
        head, tail = self.find_desired_numbers(old_snake_len)

        if head == -1:
            head, tail = piece.value[0], piece.value[-1]

        # print('head: {}, tail: {}'.format(head, tail))
        if direction == '+':
            if piece.value[0] == tail:
                self.snake_set.append(piece)
            elif piece.value[-1] == tail:
                piece.rotate_piece()
                self.snake_set.append(piece)
        elif direction == '-':
            if piece.value[-1] == head:
                self.snake_set.insert(0, piece)
            elif piece.value[0] == head:
                piece.rotate_piece()
                self.snake_set.insert(0, piece)

        if len(self.snake_set) == old_snake_len:
            for piece_part, snake_part, position in zip([0, -1], [tail, head], [old_snake_len, 0]):
                if piece.value[piece_part] != snake_part:
                    piece.rotate_piece()
                    if piece.value[piece_part] != snake_part:
                        continue
                    else:
                        self.snake_set.insert(position, piece)
                        break
                else:
                    self.snake_set.insert(position, piece)
                    break

    def find_desired_numbers(self, snake_len):  # head and tail of the snake
        if snake_len in range(2, 29):
            head_n_tail = [self.snake_set[0].value[0], self.snake_set[-1].value[-1]]
        elif snake_len == 1:
            head_n_tail = [self.snake_set[0].value[0], self.snake_set[0].value[-1]]
        elif snake_len == 0:
            head_n_tail = [-1] * 2
        else:
            raise RuntimeError('Wrong snake lens.')
        # print('i find' + str(head_n_tail))
        return head_n_tail


class Piece:

    PIECE_STATUSES = {
        'New Born': 'Generated',
        'In Stock': 'Waiting',
        'In Game': 'Playing',
        'On Table': 'Part of Snake',
        'The End': 'For Delete'
    }
    PIECE_STATUSES_KEYS = list(PIECE_STATUSES)

    PIECE_OWNERS = ['Field {}', 'Stock', 'Player {}', 'Snake']

    def __init__(self, value, rotated_value, field):
        self.value = value
        self.rotated_value = rotated_value
        self.field = field
        self.PIECE_OWNERS[0] = self.PIECE_OWNERS[0].format(self.field.number)
        self.owner = self.PIECE_OWNERS[0]
        self.status = self.PIECE_STATUSES['New Born']

    def rotate_piece(self):  # swap data of two variables between them
        self.value, self.rotated_value = self.rotated_value, self.value

    def change_status(self):
        for key in self.PIECE_STATUSES_KEYS:
            if key == 'The End' and self.owner == self.PIECE_OWNERS[0]:
                del self
                break
            elif key == self.status:
                index = self.PIECE_STATUSES_KEYS.index(key)
                next_key = self.PIECE_STATUSES_KEYS[index + 1]
                self.status = self.PIECE_STATUSES[next_key]
                break

    def change_owner(self, new_owner, player_name=None):
        if new_owner == self.PIECE_OWNERS[1]:
            self.owner = self.PIECE_OWNERS[1]
            self.change_status()
        elif player_name is not None:
            self.owner = self.PIECE_OWNERS[2].format(player_name)
            self.change_status()
        elif new_owner == self.PIECE_OWNERS[-1]:
            self.owner = self.PIECE_OWNERS[-1]
            self.change_status()
        elif new_owner == self.PIECE_OWNERS[0]:
            self.owner = self.PIECE_OWNERS[0]
            self.change_status()
        else:
            print('Wrong owner')
    # def __str__(self):
    #     return 'Piece value: {}\nCurrent owner: {}\nIt\'status: {}'.format(self.vl, self.own, self.st)


class DominoesGameSet:
    LIST_OF_ALL_PIECES = []

    def __init__(self, field):
        self.field = field
        self.generate_set()

    def generate_set(self):
        num_limits = range(1, 7)
        count_limits = 28

        # generating pieces without order
        while len(self.LIST_OF_ALL_PIECES) != count_limits:
            x, y = randint(0, choice(num_limits)), randint(0, choice(num_limits))
            if not self.piece_in_set([x, y]):
                new_piece = Piece([x, y], [y, x], self.field)
                self.LIST_OF_ALL_PIECES.append(new_piece)

    def piece_in_set(self, piece):
        for obj in self.LIST_OF_ALL_PIECES:
            if piece in [obj.value, obj.rotated_value]:
                return True
        return False

    def divide_the_set_into_3(self, players):  # gamer objects go to 'players'

        def check_sets_limits(player_name, limit):
            if len(players_set[player_name]) == limit:
                try:
                    player_s_names.remove(player_name)
                except ValueError:
                    pass

        shuffle(self.LIST_OF_ALL_PIECES)
        stock_pieces = self.LIST_OF_ALL_PIECES
        players_set, player_s_names = {}, []
        for player in players:
            players_set.update({player.username: player.gamer_s_set})
            player_s_names.append(player.username)
        stock_limits = 14
        player_s_set_limit = 7
        player_s_names_backup = player_s_names
        i, j = 0, 0

        while len(stock_pieces) != stock_limits:
            # checks if computer's n player's sets are full.
            for key in players_set.keys():
                check_sets_limits(key, player_s_set_limit)

            # give the first piece from stock
            #  to one of the sets by random.choice.
            #  then remove it from stock-list.
            cur_piece = stock_pieces[0]

            cur_pl_set = choice(player_s_names)
            if cur_pl_set == player_s_names_backup[0]:
                j += 1
                cur_num = j
            elif cur_pl_set == player_s_names_backup[1]:
                i += 1
                cur_num = i
            else:
                cur_num = None

            players_set[cur_pl_set].update({cur_num: cur_piece})
            stock_pieces.remove(cur_piece)

        # if both sets is full, change stock-set and exit from the loop.
        if player_s_names:
            self.field.stock_set = stock_pieces
            for pl in players:
                pl.gamer_s_set = players_set[pl.username]

    def redistribute_set(self, players):
        self.divide_the_set_into_3(players)


class Gamer:

    EMPTY_COUNTER = {key: 0 for key in range(7)}

    def __init__(self, field, dominoes_set, username='Sumskyj Traktor'):
        self.username = username
        self.field = field
        self.dominoes_set = dominoes_set
        self.gamer_s_set = {}

    def set_s_nums_recalc(self):
        old_set = self.gamer_s_set
        new_set = {}
        counter = 0
        for piece in old_set.values():
            counter += 1
            new_set.update({counter: piece})

        if len(self.gamer_s_set.items()) == len(new_set.items()):
            self.gamer_s_set = new_set

    def pl_input_validation(self, pl_input, checks, suitable_pieces):
        # check input lens
        if len(pl_input) > 2 or pl_input == '':
            checks['errors'].append(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['IncorLens'])
            return checks

        # check input consistence
        direction = pl_input[0]
        try:
            piece_num = int(pl_input[1])
        except IndexError:
            direction = '+'
            try:
                piece_num = int(pl_input[0])
            except ValueError:
                checks['errors'].append(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['IncorValue'])
                return checks
        except ValueError:
            checks['errors'].append(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['IncorValue'])
            return checks

        # check input direction
        if direction not in ['-', '+']:
            checks['errors'].append(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['WrongDirection'])
            return checks

        if piece_num != 0:
            # check does piece can be used
            piece = self.find_player_s_piece(piece_num)
            if piece not in suitable_pieces.values():
                checks['errors'].append(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['ImpossibleMove'])
                return checks
        else:
            piece = 0

        checks['result'].append([direction, piece_num, piece])
        return checks

    def clear_player_s_input(self, suitable_pieces):
        msg = Game.GAME_INFO['UI_BLOCKS']['InputErrors']['Standard']

        while True:
            checks = {'errors': [], 'result': []}
            pl_input = input()
            checks = self.pl_input_validation(pl_input, checks, suitable_pieces)
            if not checks['errors']:
                break
            else:
                if Game.GAME_INFO['UI_BLOCKS']['InputErrors']['ImpossibleMove'] in checks['errors']:
                    print(Game.GAME_INFO['UI_BLOCKS']['InputErrors']['ImpossibleMove'])
                else:
                    print(msg)
                # print(msg, *checks['errors'], sep='\n')
        return checks['result'][0]

    def find_player_s_piece(self, num_player_piece):
        for piece_num, piece in self.gamer_s_set.items():
            if piece_num == num_player_piece:
                return piece

    def calc_variants(self, sut_pieces):
        counter = self.EMPTY_COUNTER
        sut_p_to_iter_obj = sut_pieces.items()
        variants = {}

        for piece_num, piece in sut_p_to_iter_obj:
            variants[piece_num] = 0  # register number of piece in variants dict.
            for number in piece.value:
                counter[number] += 1

        for piece in self.field.snake_set:
            for number in piece.value:
                counter[number] += 1

        for piece_num, piece in sut_p_to_iter_obj:
            for number in piece.value:
                variants[piece_num] += counter[number]

        find_max = max(variants, key=variants.get)
        return find_max

    def player_step(self, direction, piece_num, piece):
        if piece_num != 0:
            self.field.snake_update(direction, piece)
            if piece in self.field.snake_set:
                del self.gamer_s_set[piece_num]
        elif piece_num == 0:
            piece_from_stock = self.field.stock_emptying()
            if piece_from_stock is not None:
                new_piece_num = list(self.gamer_s_set.keys())[-1] + 1
                self.gamer_s_set.update({new_piece_num: piece_from_stock})

        self.set_s_nums_recalc()

    def find_suitable_pieces(self, desired_numbers):
        suitable_pieces = {}
        for desired_num in desired_numbers:
            for num_piece, piece in self.gamer_s_set.items():
                if desired_num in piece.value:
                    suitable_pieces.update({num_piece: piece})
        return suitable_pieces

    # def __str__(self):
    #     return 'Gamer name: {}'.format(self.username)


class Game:

    GAME_INFO = {
        'HISTORY': [],
        'GAME_RESULTS': {
            'Win': 'The game is over. You won!',
            'Lose': 'The game is over. The computer won!',
            'Draw': 'The game is over. It\'s a draw!'
        },
        'UI_BLOCKS': {
            'PlayerTurn': 'It\'s your turn to make a move. Enter your command.',
            'ComputerTurn': 'Computer is about to make a move. Press Enter to continue...',
            'InputErrors': {
                'Standard': 'Invalid input. Please try again.',
                'IncorLens': 'Input has incorrect lens.',
                'IncorValue': 'Maybe input has no integer number.',
                'WrongDirection': 'Direction should be "-" or "+".',
                'ImpossibleMove': 'Illegal move. Please try again.'
                # 'ImpossibleMove': 'Piece, you selected can\'t be used here.'
            }
        }
    }

    UI_BLOCKS = {
        'Separator': '{}{}',
        'Stock size': '{}: {}',  # all elements
        'Computer pieces': '{}: {}',
        'Domino snake': '{}{}',
        'Player pieces': '{}: {}',
        'Status': '{}: {}'  # the player that goes next
    }

    def __init__(self):
        self.field = Field('001')
        self.status = ''
        self.dominoes_set = DominoesGameSet(self.field)
        self.players = (
            Gamer(self.field, self.dominoes_set, 'player'),
            Gamer(self.field, self.dominoes_set, 'computer')
        )
        self.dominoes_set.divide_the_set_into_3(self.players)
        self.game_flow()

    def who_play_first(self):
        # check_list = [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6]]
        pairs = {}

        for gamer in self.players:
            name = gamer.username
            pairs[name] = []
            values = list(gamer.gamer_s_set.values())
            pairs[name] = [
                piece.value[0] for piece in values if piece.value[0] == piece.value[1] and piece.value[0] < 7
            ]
            try:
                pairs[name] = max(pairs[name])
            except ValueError:
                pairs[name] = -1

        gamers = list(pairs.keys())

        if sum(pairs.values()) == -2:
            self.dominoes_set.redistribute_set(self.players)
            nexter = self.who_play_first()
        elif pairs[gamers[0]] > pairs[gamers[1]]:
            max_num = pairs[gamers[0]]
            identify = [
                gamers[0],
                [max_num, max_num]
            ]
        else:
            max_num = pairs[gamers[1]]
            identify = [
                gamers[1],
                [max_num, max_num]
            ]
        for gamer, label in zip(self.players, ['PlayerTurn', 'ComputerTurn']):
            if gamer.username == identify[0]:
                for piece_num, piece in gamer.gamer_s_set.items():
                    if piece.value == identify[1]:
                        # print('first ' + gamer.username)
                        gamer.player_step('+', piece_num, piece)
                        break
            elif gamer.username != identify[0]:
                nexter = gamer
                self.status = self.GAME_INFO['UI_BLOCKS'][label]
                # print('next be ' + gamer.username)
        return nexter

    def step(self, player_name):
        for player in self.players:
            snake_lens = len(self.field.snake_set)
            if player.username == player_name and player_name == 'computer':
                suitable_pieces = player.find_suitable_pieces(
                    self.field.find_desired_numbers(snake_lens)

                )
                self.terminal_ui()
                pause = input()
                plyr = player
                if not suitable_pieces:  # if dict is empty
                    direction, piece_num, piece = [0] * 3
                else:
                    piece_num = player.calc_variants(suitable_pieces)
                    piece = suitable_pieces[piece_num]
                    direction = choice(['+', '-'])
                # try:
                #     piece_num, piece = choice(list(suitable_pieces.items()))
                #     direction = choice(['+', '-'])
                # except IndexError:
                #     direction, piece_num, piece = [0] * 3
            elif player.username == player_name and player_name == 'player':
                suitable_pieces = player.find_suitable_pieces(
                    self.field.find_desired_numbers(snake_lens)
                )
                self.terminal_ui()
                plyr = player
                if suitable_pieces is not {}:
                    direction, piece_num, piece = player.clear_player_s_input(suitable_pieces)
                else:
                    direction, piece_num, piece = [0] * 3

        plyr.player_step(direction, piece_num, piece)
        self.GAME_INFO['HISTORY'].append({plyr: piece})

    def game_flow(self):
        nexter = self.who_play_first()  # nexter is player who will make next step
        while self.game_end()[0] is False:
            nexter_name = nexter.username
            self.status = self.GAME_INFO['UI_BLOCKS'][nexter_name.title() + 'Turn']
            self.step(nexter_name)
            for player in self.players:
                if player.username != nexter_name:
                    nexter = player
                    # print('nexter ' + player.username)
                    break

        self.status = self.game_end()[1]
        self.terminal_ui()

    def game_end(self):
        # if one of the players runs out of pieces
        for gamer in self.players:
            if not gamer.gamer_s_set:
                if gamer.username == 'computer':
                    status = self.GAME_INFO['GAME_RESULTS']['Lose']
                elif gamer.username == 'player':
                    status = self.GAME_INFO['GAME_RESULTS']['Win']
                else:
                    status = None
                return [True, status]

        # if the numbers on the ends of the snake are identical
        #  and appear within the snake 8 times.

        pieces_elems = list(chain.from_iterable([obj.value for obj in self.field.snake_set]))
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
        try:
            max_occurrence = max(pieces_elems, key=pieces_elems.count)
        except ValueError:
            return [False] * 2
        # https://stackoverflow.com/questions/6987285/find-the-item-with-maximum-occurrences-in-a-list
        num_of_occur = pieces_elems.count(max_occurrence)
        if num_of_occur >= 8:
            head, tail = self.field.find_desired_numbers(len(self.field.snake_set))
            if head == max_occurrence and tail == max_occurrence:
                return [True, self.GAME_INFO['GAME_RESULTS']['Draw']]

        return [False] * 2

    def terminal_ui(self):
        # function to print data and supplement info.
        def counter(need_count):
            return len(need_count)

        pl_in_r_order = []
        for pl in self.players:
            if pl.username == 'player':
                pl_in_r_order.append(pl)
            else:
                pl_in_r_order.insert(0, pl)

        snake = ''
        for piece in self.field.snake_set:
            snake += str(piece.value)

        pre_info = [
            '=' * 70,
            counter(self.field.stock_set),
            counter(pl_in_r_order[0].gamer_s_set),
            snake,
            pl_in_r_order[1].gamer_s_set,
            self.status
        ]
        ui_info = []
        new_line = '\n'

        for key, value in zip(Game.UI_BLOCKS.keys(), pre_info):
            if key in ('Separator', 'Domino snake'):
                placeholder = ''
                if key == 'Domino snake':
                    if len(value) > 36:
                        value = new_line + value[:18] + '...' + value[-18:] + new_line
                    else:
                        value = new_line + value + new_line
            elif key == 'Player pieces':
                placeholder = key
                value = new_line
                for n, p in pre_info[4].items():
                    value += '{}: {}'.format(n, p.value) + new_line
            else:
                placeholder = key

            ui_info.append(Game.UI_BLOCKS[key].format(placeholder, value))

        print(*ui_info, sep='\n')


### GAME ###

if __name__ == "__main__":
    test_game = Game()
