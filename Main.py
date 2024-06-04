import ctypes
import os
from fast_get_pixel import PixelReader
import mouse as Mouse
import time

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

        # Initialize board and hash table
        self.board = self.lib.getInitBoard()
        self.hash_table = self.lib.initHashTable()

    def print_board(self):
        self.lib.printBoard(self.board.contents)

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
    def __init__(self, board_size=(7, 6)):
        self.pixel_reader = PixelReader()
        self.board_size = board_size
        self.board_size_px = None
        self.base_color = None
        self.top_left = None
        self.bottom_right = None

        self.board1 = None
        self.player = None

    def get_board_position(self, i, j):
        return self.top_left[0] + (i * (self.board_size_px[0] // (self.board_size[0] - 1))), self.top_left[1] + (j * (self.board_size_px[1] // (self.board_size[1] - 1)))

    def get_board(self):
        board = [[0 for _ in range(self.board_size[1])] for _ in range(self.board_size[0])]
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                board[i][j] = self.pixel_reader.get_pixel_rgb(*self.get_board_position(i, j)) == self.base_color
        return board

    def get_move(self, board):
        board = self.get_board()
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if board[i][j] != self.board[i][j]:
                    self.board = board
                    print("Found move", i)
                    return i

        return False
    
    def make_move(self, move):
        move = 6 - move
        for i in range(self.board_size[1] - 1, -1, -1):
            if self.board[move][i]:
                Mouse.move(*self.get_board_position(move, i))
                Mouse.click()
                time.sleep(0.1)
                Mouse.move(self.top_left[0] - (self.board_size_px[0] // self.board_size[0] - 1), self.top_left[1])
                break
        # set the position just plaied to True
        self.board = self.get_board()
        self.player = 1 - self.player

    def calibrate(self):
        input("Place mouse at top left of board and press enter")
        self.top_left = Mouse.get_position()
        input("Place mouse at bottom right of board and press enter")
        self.bottom_right = Mouse.get_position()

        self.board_size_px = (self.bottom_right[0] - self.top_left[0], self.bottom_right[1] - self.top_left[1])
        self.base_color = self.pixel_reader.get_pixel_rgb(self.top_left[0], self.top_left[1])
        Mouse.move(self.top_left[0] - (self.board_size_px[0] // self.board_size[0] - 1), self.top_left[1])

        self.board = self.get_board()
        self.player = self.find_player()

    def reset(self):
        self.board = self.get_board()
        self.player = self.find_player()

    def find_player(self):
        for i in range(7):
            for j in range(6):
                if self.pixel_reader.get_pixel_rgb(*self.get_board_position(i, j)) != self.base_color:
                    return 1
        return 0
    
    def get_move_from_screen(self):
        move = False
        while move == False:
            move = self.get_move(self.board)
            time.sleep(0.1)
        self.player = 1 - self.player
        return 6 - move


if __name__ == "__main__":
    # Path to the compiled shared library
    lib_path = "./TheConnector.dll"
    engine = Connect4Engine(lib_path)
    moveMask = 0b10000000100000001000000010000000100000001
    in_book = True
    screen_reader = ScreenReader()
    screen_reader.calibrate()
    while True:
        input("Press enter to start")
        screen_reader.reset()
        bot_player = screen_reader.player
        cur_player = bot_player
        while True:
            if cur_player == bot_player:
                # look in the book
                if in_book:
                    move = engine.find_book_move(engine.book_path)
                    if move != -1:
                        possibleMoves = engine.generate_moves()
                        engine.make_move(possibleMoves & (moveMask << move), cur_player)
                        screen_reader.make_move(move)
                    else:
                        in_book = False
                if not in_book:
                    eval_ = engine.solve(cur_player, 1)
                    move = engine.get_move()
                    possibleMoves = engine.generate_moves()
                    engine.make_move(possibleMoves & (moveMask << move), cur_player)
                    screen_reader.make_move(move)

            elif cur_player != bot_player:
                move = screen_reader.get_move_from_screen()
                possibleMoves = engine.generate_moves()
                engine.make_move(possibleMoves & (moveMask << move), cur_player)
            engine.print_board()
            print()
            cur_player = 1 - cur_player