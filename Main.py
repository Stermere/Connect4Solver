import ctypes
import os
from fast_get_pixel import PixelReader
import mouse as Mouse
import time
import random

DELTA_RANGE = (0.0, 0.0)
BOARD_SIZE = (7, 6)  # Default board size

class Connect4Engine:
    def __init__(self, lib_path):
        self.book_path = "OpeningBook5"

        # Load the shared library
        self.lib = ctypes.CDLL(lib_path, winmode=0)

        # Define argument and return types for the shared library functions
        self.lib.initHashTable.argtypes = []
        self.lib.initHashTable.restype = ctypes.POINTER(HashTable)
        self.lib.getInitBoard.argtypes = []
        self.lib.getInitBoard.restype = ctypes.POINTER(BoardState)
        self.lib.initBoard.argtypes = [ctypes.POINTER(BoardState)]
        self.lib.printBoard.argtypes = [BoardState]
        self.lib.getMove.restype = ctypes.c_int
        self.lib.makeMove.argtypes = [ctypes.POINTER(BoardState), ctypes.c_ulonglong, ctypes.c_int, ctypes.POINTER(HashTable)]
        self.lib.generateMoves.argtypes = [ctypes.POINTER(BoardState)]
        self.lib.generateMoves.restype = ctypes.c_ulonglong
        self.lib.solve.argtypes = [ctypes.POINTER(BoardState), ctypes.c_int, ctypes.POINTER(HashTable), ctypes.c_int]
        self.lib.solve.restype = ctypes.c_int
        self.lib.getEntry.argtypes = [ctypes.POINTER(HashTable), ctypes.c_ulong]
        self.lib.getEntry.restype = ctypes.POINTER(Entry)
        self.lib.findBookMove.argtypes = [ctypes.c_char_p, ctypes.POINTER(BoardState)]
        self.lib.findBookMove.restype = ctypes.c_int
        self.lib.computeWinningPosition.argtypes = [ctypes.c_ulonglong, ctypes.c_ulonglong]
        self.lib.computeWinningPosition.restype = ctypes.c_ulonglong

        # Initialize board and hash table
        self.board = self.lib.getInitBoard()
        self.hash_table = self.lib.initHashTable()

    def print_board(self):
        self.lib.printBoard(self.board.contents)

    def reset_board(self):
        self.board = self.lib.getInitBoard()
        self.hash_table = self.lib.initHashTable()

    def get_move(self):
        return self.lib.getMove()

    def make_move(self, move, player):
        self.lib.makeMove(self.board, move, player, self.hash_table)

    def generate_moves(self):
        return self.lib.generateMoves(self.board)

    def solve(self, player, weak_solver):
        return self.lib.solve(self.board, player, self.hash_table, weak_solver)
    
    def get_entry(self, hash_):
        return self.lib.getEntry(self.hash_table, hash_)
    
    def get_move(self):
        entry_p = self.get_entry(self.board.contents.hash)
        return int.from_bytes(entry_p.contents.move, byteorder='big')
    
    def compute_winning_position(self, last_move, last_player):
        win_mask = self.lib.computeWinningPosition(self.board.contents.p2 if last_player else self.board.contents.p1, (self.board.contents.p2 | self.board.contents.p1) ^ last_move)
        if win_mask & last_move:
            return True
        return False

    def find_book_move(self, book_path):
        return self.lib.findBookMove(book_path.encode("utf-8"), self.board)

class BoardState(ctypes.Structure):
    _fields_ = [
        ("p1", ctypes.c_ulonglong),
        ("p2", ctypes.c_ulonglong),
        ("nodes", ctypes.c_ulonglong),
        ("hash", ctypes.c_ulong)
    ]

class Entry(ctypes.Structure):
    _fields_ = [
        ("hash", ctypes.c_ulong),
        ("value", ctypes.c_char),
        ("move", ctypes.c_char),
        ("flag", ctypes.c_char)
    ]

class HashTable(ctypes.Structure):
    _fields_ = [
        ("entries", ctypes.POINTER(Entry)),
        ("zobrist", ctypes.POINTER(ctypes.c_ulong)),
        ("size", ctypes.c_ulonglong)
    ]


class ScreenReader:
    def __init__(self, board_size=BOARD_SIZE, delay=0.01, delta_range=DELTA_RANGE):
        self.pixel_reader = PixelReader()
        self.board_size = board_size
        self.board_size_px = None
        self.base_color = None
        self.top_left = None
        self.bottom_right = None
        self.delay = delay
        self.delta_range = delta_range
        self.board = None
        self.player = None

    def get_board_position(self, i, j):
        # Calculate the position of a cell on the board
        return (self.top_left[0] + (i * (self.board_size_px[0] // (self.board_size[0] - 1))),
                self.top_left[1] + (j * (self.board_size_px[1] // (self.board_size[1] - 1))))

    def get_board(self):
        # Read the current state of the board
        board = [[True for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                board[i][j] = self.pixel_reader.get_pixel_rgb(*self.get_board_position(i, j)) == self.base_color
        return board

    def get_move(self, board):
        board = self.get_board()
        changes = []
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if board[i][j] != self.board[i][j]:
                    changes.append(i)
        if len(changes) > 1:
            print("Multiple changes detected. reseting the board.")
            return -2
        elif len(changes) == 1:
            self.board = board
            print("Found move", changes[0])
            return changes[0]
        else:
            return -1

    def make_move(self, move):
        move = self.board_size[0] - 1 - move
        for i in range(self.board_size[1] - 1, -1, -1):
            if self.board[move][i]:
                Mouse.move(*self.get_board_position(move, i))
                time.sleep(self.delay + random.uniform(*self.delta_range))
                Mouse.click()
                time.sleep(self.delay)
                Mouse.move(self.top_left[0] - (self.board_size_px[0] // self.board_size[0] - 1), self.top_left[1])
                break
        time.sleep(self.delay)
        self.board = self.get_board()
        self.player = 1 - self.player

    def calibrate(self):
        # Calibrate the screen reader
        input("Place mouse at top left of board and press enter")
        self.top_left = Mouse.get_position()
        input("Place mouse at bottom right of board and press enter")
        self.bottom_right = Mouse.get_position()

        self.board_size_px = (self.bottom_right[0] - self.top_left[0], self.bottom_right[1] - self.top_left[1])
        self.base_color = self.pixel_reader.get_pixel_rgb(self.top_left[0], self.top_left[1])
        Mouse.move(self.top_left[0] - (self.board_size_px[0] // (self.board_size[0] - 1)), self.top_left[1])

        self.board = self.get_board()
        assert sum(row.count(False) for row in self.board) in [0, 1], "Invalid calibration. Please try again."
        self.player = self.find_player()

    def reset(self):
        # Reset the screen reader
        self.board = self.get_board()
        self.player = self.find_player()

    def getFirstMove(self):
        # Get the first move made on the board
        for i in range(7):
            for j in range(6):
                if not self.board[i][j]:
                    return self.board_size[0] - 1 - i
        return -1

    def find_player(self):
        # Find the current player
        for i in range(7):
            for j in range(6):
                if self.pixel_reader.get_pixel_rgb(*self.get_board_position(i, j)) != self.base_color:
                    return 1
        return 0

    def get_move_from_screen(self):
        # Get the move made by the opponent from the screen
        move = -1
        while move == -1:
            move = self.get_move(self.board)
            time.sleep(0.1)
        self.player = 1 - self.player

        if move == -2:
            return -1

        return 6 - move
    

if __name__ == "__main__":
    # Path to the compiled shared library
    lib_path = "./TheConnector.dll"
    engine = Connect4Engine(lib_path)
    moveMask = 0b10000000100000001000000010000000100000001
    screen_reader = ScreenReader()
    screen_reader.calibrate()
    while True:
        input("Press enter to start")
        screen_reader.reset()
        in_book = True
        in_first_move = True
        bot_player = screen_reader.player
        cur_player = bot_player
        solve_type = 1

        # Pre Play the oponents first move
        if bot_player != 0:
            move = screen_reader.getFirstMove()
            possibleMoves = engine.generate_moves()
            engine.make_move(possibleMoves & (moveMask << move), 1 - bot_player)

        while True:
            if cur_player == bot_player:
                # look in the book
                if in_first_move:
                    move = random.randint(0, 6)
                    possibleMoves = engine.generate_moves()
                    engine.make_move(possibleMoves & (moveMask << move), cur_player)
                    screen_reader.make_move(move)
                    in_first_move = False

                elif in_book:
                    move = engine.find_book_move(engine.book_path)
                    if move != -1:
                        possibleMoves = engine.generate_moves()
                        engine.make_move(possibleMoves & (moveMask << move), cur_player)
                        screen_reader.make_move(move)
                    else:
                        in_book = False
                if not in_book:
                    eval_ = engine.solve(cur_player, solve_type)
                    move = engine.get_move()
                    possibleMoves = engine.generate_moves()
                    engine.make_move(possibleMoves & (moveMask << move), cur_player)
                    screen_reader.make_move(move)
                engine.print_board()
                print()

            elif cur_player != bot_player:
                move = screen_reader.get_move_from_screen()
                if move == -1:
                    engine.reset_board()
                    break

                possibleMoves = engine.generate_moves()
                engine.make_move(possibleMoves & (moveMask << move), cur_player)
                engine.print_board()
                print()

            if engine.compute_winning_position(possibleMoves & (moveMask << move), cur_player):
                print("Player", cur_player, "wins!")
                engine.reset_board()
                break

            if engine.board.contents.p1 | engine.board.contents.p2 == 0xffffffffffff:
                print("Draw!")
                engine.reset_board()
                break

            # if there is more than 9 pieces on the board change solve to 0
            if (engine.board.contents.p1 | engine.board.contents.p2).bit_count() > 6:
                solve_type = 0
                engine.hash_table = engine.lib.initHashTable()

            cur_player = 1 - cur_player