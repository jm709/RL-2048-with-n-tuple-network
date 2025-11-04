import React, { useState, useEffect, useRef } from 'react';

const Game2048Viewer = () => {
  const [board, setBoard] = useState(Array(4).fill(null).map(() => Array(4).fill(0)));
  const [score, setScore] = useState(0);
  const [moveCount, setMoveCount] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(500);
  const [gameOver, setGameOver] = useState(false);
  const [stats, setStats] = useState({ maxTile: 0, totalGames: 0 });
  const gameStateRef = useRef({ board: null, score: 0, moves: 0 });

  const COLORS = {
    0: 'bg-gray-300',
    2: 'bg-blue-100',
    4: 'bg-blue-200',
    8: 'bg-orange-200',
    16: 'bg-orange-300',
    32: 'bg-orange-400',
    64: 'bg-red-300',
    128: 'bg-yellow-200',
    256: 'bg-yellow-300',
    512: 'bg-yellow-400',
    1024: 'bg-yellow-500',
    2048: 'bg-yellow-600',
    4096: 'bg-purple-400',
    8192: 'bg-purple-500',
  };

  const TEXT_COLORS = {
    0: 'text-gray-400',
    2: 'text-gray-700',
    4: 'text-gray-700',
    8: 'text-white',
    16: 'text-white',
    32: 'text-white',
    64: 'text-white',
    128: 'text-white',
    256: 'text-white',
    512: 'text-white',
    1024: 'text-white',
    2048: 'text-white',
    4096: 'text-white',
    8192: 'text-white',
  };

  // Initialize board
  const initBoard = () => {
    const newBoard = Array(4).fill(null).map(() => Array(4).fill(0));
    addRandomTile(newBoard);
    addRandomTile(newBoard);
    return newBoard;
  };

  // Add random tile (2 or 4)
  const addRandomTile = (board) => {
    const empty = [];
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        if (board[i][j] === 0) empty.push([i, j]);
      }
    }
    if (empty.length > 0) {
      const [i, j] = empty[Math.floor(Math.random() * empty.length)];
      board[i][j] = Math.random() < 0.9 ? 2 : 4;
    }
    return empty.length > 0;
  };

  // Slide and merge a row
  const slideRow = (row) => {
    let newRow = row.filter(x => x !== 0);
    let score = 0;
    for (let i = 0; i < newRow.length - 1; i++) {
      if (newRow[i] === newRow[i + 1]) {
        newRow[i] *= 2;
        score += newRow[i];
        newRow.splice(i + 1, 1);
      }
    }
    while (newRow.length < 4) newRow.push(0);
    return { row: newRow, score };
  };

  // Move in direction
  const move = (board, direction) => {
    let newBoard = board.map(row => [...row]);
    let totalScore = 0;
    let moved = false;

    if (direction === 'left') {
      for (let i = 0; i < 4; i++) {
        const { row, score } = slideRow(newBoard[i]);
        if (JSON.stringify(row) !== JSON.stringify(newBoard[i])) moved = true;
        newBoard[i] = row;
        totalScore += score;
      }
    } else if (direction === 'right') {
      for (let i = 0; i < 4; i++) {
        const { row, score } = slideRow(newBoard[i].reverse());
        if (JSON.stringify(row.reverse()) !== JSON.stringify(newBoard[i].reverse())) moved = true;
        newBoard[i] = row.reverse();
        totalScore += score;
      }
    } else if (direction === 'up') {
      for (let j = 0; j < 4; j++) {
        const col = [newBoard[0][j], newBoard[1][j], newBoard[2][j], newBoard[3][j]];
        const { row, score } = slideRow(col);
        if (JSON.stringify(row) !== JSON.stringify(col)) moved = true;
        for (let i = 0; i < 4; i++) newBoard[i][j] = row[i];
        totalScore += score;
      }
    } else if (direction === 'down') {
      for (let j = 0; j < 4; j++) {
        const col = [newBoard[3][j], newBoard[2][j], newBoard[1][j], newBoard[0][j]];
        const { row, score } = slideRow(col);
        if (JSON.stringify(row.reverse()) !== JSON.stringify([newBoard[3][j], newBoard[2][j], newBoard[1][j], newBoard[0][j]])) moved = true;
        for (let i = 0; i < 4; i++) newBoard[3 - i][j] = row[i];
        totalScore += score;
      }
    }

    return { board: newBoard, score: totalScore, moved };
  };

  // Check if any moves possible
  const canMove = (board) => {
    for (let dir of ['left', 'right', 'up', 'down']) {
      const { moved } = move(board, dir);
      if (moved) return true;
    }
    return false;
  };

  const boardToLog2 = (board) => {
    const newBoard = board
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++){
        newBoard[i][j] = Math.log2(newBoard[i][j])
      }
    }
    return newBoard
  };

//   const log2ToBoard = (board) => {
//     for (let i = 0; i < 4; i++) {
//       for (let j = 0; j < 4; j++){
//         board[i][j] = 2**(board[i][j])
//       }
//     }
//     return board
  };
  // Simple AI: evaluate each move and pick best
  const getBestMove = async (board) => {
  try {
    const response = await fetch('/api/best_action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board: boardToLog2(board) })
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();
    const actions = ['left', 'right', 'up', 'down'];
    return actions[data.action];
  } catch (error) {
    console.error('API error, using fallback:', error);
    // Use simple heuristic as fallback
    return getBestMoveHeuristic(board);
    }
  };

  // Game loop
  const playStep = async () => {
  const currentBoard = gameStateRef.current.board || board;

    if (!canMove(currentBoard)) {
      setGameOver(true);
      setIsPlaying(false);
      const maxTile = Math.max(...currentBoard.flat());
      setStats(prev => ({
        maxTile: Math.max(prev.maxTile, maxTile),
        totalGames: prev.totalGames + 1
      }));
      return;
    }

    const bestMove = await getBestMove(currentBoard); // Add await here
    if (!bestMove) {
      setGameOver(true);
      setIsPlaying(false);
      return;
    }

    const { board: newBoard, score: moveScore, moved } = move(currentBoard, bestMove);

    if (moved) {
      addRandomTile(newBoard);
      const newScore = gameStateRef.current.score + moveScore;
      const newMoves = gameStateRef.current.moves + 1;

      gameStateRef.current = { board: newBoard, score: newScore, moves: newMoves };
      setBoard(newBoard);
      setScore(newScore);
      setMoveCount(newMoves);
    }
  };

  // Auto-play effect
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      playStep();
    }, speed);

    return () => clearInterval(interval);
  }, [isPlaying, speed]);

  const startGame = () => {
    const newBoard = initBoard();
    gameStateRef.current = { board: newBoard, score: 0, moves: 0 };
    setBoard(newBoard);
    setScore(0);
    setMoveCount(0);
    setGameOver(false);
    setIsPlaying(true);
  };

  const resetGame = () => {
    const newBoard = initBoard();
    gameStateRef.current = { board: newBoard, score: 0, moves: 0 };
    setBoard(newBoard);
    setScore(0);
    setMoveCount(0);
    setGameOver(false);
    setIsPlaying(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-800">2048 AI Player</h1>
        <p className="text-center text-gray-600 mb-6">Watch the AI play 2048 automatically</p>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-sm text-gray-600">Score</div>
              <div className="text-2xl font-bold text-indigo-600">{score}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">Moves</div>
              <div className="text-2xl font-bold text-indigo-600">{moveCount}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">Max Tile</div>
              <div className="text-2xl font-bold text-indigo-600">
                {Math.max(...board.flat())}
              </div>
            </div>
          </div>

          <div className="bg-gray-400 p-3 rounded-lg inline-block w-full">
            <div className="grid grid-cols-4 gap-3">
              {board.map((row, i) =>
                row.map((cell, j) => (
                  <div
                    key={`${i}-${j}`}
                    className={`${COLORS[cell] || 'bg-purple-600'} ${TEXT_COLORS[cell] || 'text-white'}
                      w-full aspect-square rounded-lg flex items-center justify-center
                      text-2xl font-bold transition-all duration-200 transform`}
                  >
                    {cell !== 0 ? cell : ''}
                  </div>
                ))
              )}
            </div>
          </div>

          {gameOver && (
            <div className="mt-4 p-4 bg-red-100 border-2 border-red-400 rounded-lg text-center">
              <div className="text-xl font-bold text-red-700">Game Over!</div>
              <div className="text-red-600">Final Score: {score}</div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex gap-3 mb-4">
            <button
              onClick={startGame}
              disabled={isPlaying}
              className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-300
                text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Start New Game
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex-1 bg-blue-500 hover:bg-blue-600 text-white
                font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {isPlaying ? 'Pause' : 'Resume'}
            </button>
            <button
              onClick={resetGame}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white
                font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Reset
            </button>
          </div>

          <div className="mb-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speed: {speed}ms per move
            </label>
            <input
              type="range"
              min="50"
              max="2000"
              step="50"
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-3 text-gray-800">Session Statistics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">Highest Tile Reached</div>
              <div className="text-xl font-bold text-indigo-600">{stats.maxTile}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Games Played</div>
              <div className="text-xl font-bold text-indigo-600">{stats.totalGames}</div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>This is a demo AI using simple heuristics.</p>
          <p>Replace with your trained n-tuple network for better performance!</p>
        </div>
      </div>
    </div>
  );
};

export default Game2048Viewer;