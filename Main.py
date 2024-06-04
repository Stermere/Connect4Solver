import ctypes
import os

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

if __name__ == "__main__":
    # Path to the compiled shared library
    lib_path = "./TheConnector.dll"
    engine = Connect4Engine(lib_path)
    in_book = True

    # Example usage:0
    player = int(input("Enter player (0 or 1): "))
    moveMask = 0b10000000100000001000000010000000100000001
    while True:
        if player == 0:
            # look in the book
            if in_book:
                move = engine.find_book_move(engine.book_path)
                if move != -1:
                    possibleMoves = engine.generate_moves()
                    engine.make_move(possibleMoves & (moveMask << move), player)
                else:
                    in_book = False
            if not in_book:
                eval_ = engine.solve(player, 1)
                move = engine.get_move()
                possibleMoves = engine.generate_moves()
                print("Move: ", move)
                engine.make_move(possibleMoves & (moveMask << move), player)

        elif player == 1:
            move = int(input("Enter move: "))
            possibleMoves = engine.generate_moves()
            engine.make_move(possibleMoves & (moveMask << move), player)
        engine.print_board()
        print()
        player = 1 - player