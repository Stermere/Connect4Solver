# TheConnector: A Connect4 Solver

Welcome to **TheConnector**, a high-performance Connect4 solver designed to run seamlessly in your terminal. This project showcases efficient algorithm implementation and Python-C integration to deliver a quick and accurate Connect4 solver.

## Features

- **Optimized Solver**: Leverages advanced techniques to determine the optimal move, ensuring the first player wins by force.
- **Python-C Integration**: Uses Python's `ctypes` to interface with a C engine, combining the strengths of both languages.
- **Opening Book**: Includes a 5-move opening book to accelerate the initial game phase.
- **Automated Move Input**: Uses Python to simulate user input on a digital Connect4 board. (specifically made for papergames.io performance on other sites may vary)

## Getting Started

### Prerequisites

- **Compiler**: Ensure a C compiler is installed (e.g., GCC).
- **Python**: Python 3.x with `ctypes` module.

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Stermere/Connect4Solver
    cd Connect4Solver
    ```

2. **Compile the C Code**:
    ```bash
    make
    ```

Alternatively, you can download the latest release from [GitHub Releases](https://github.com/Stermere/Connect4Solver/releases) and extract it to your desired directory making sure the opening book is in the same directory.
    
### Running the Solver

- Play in the terminal:
    ```bash
    ./TheConnector.exe
    ```

- Use the automated input program:
    ```bash
    python Main.py
    ```

## Code Structure

- **HashTable.c / HashTable.h**: Implements efficient hash table for game state storage.
- **Main.c / Main.h**: Core game logic and solver algorithm.
- **Main.py**: Python script to automate move input on a digital board.
- **fast_get_pixel.py**: Utility for pixel-level operations.
- **makefile**: Instructions for compiling the C code.
- **README.md**: Project documentation.
