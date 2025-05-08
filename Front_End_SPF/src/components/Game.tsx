import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Container,
  Paper,
  Grid,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

interface GameState {
  roundNum: number;
  pointNum: number;
  curPointNum: number;
  multiplier: number;
  isRound: boolean;
  isCompleteTitle: boolean;
  timeLeft: number;
  isGameOver: boolean;
}

interface ImageData {
  url: string;
  title: string;
  truncatedTitle: string;
}

// Utility to get the correct API base URL
const getApiBaseUrl = () => {
  if (window.location.hostname === 'localhost') {
    return import.meta.env.VITE_API_URL || 'http://localhost:5000';
  }
  // In production, use relative path (same domain)
  return '';
};

const API_BASE_URL = getApiBaseUrl();

const Game: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    roundNum: 1,
    pointNum: 0,
    curPointNum: 0,
    multiplier: 0,
    isRound: true,
    isCompleteTitle: false,
    timeLeft: 60,
    isGameOver: false
  });

  const [images, setImages] = useState<ImageData[]>([]);
  const [currentImage, setCurrentImage] = useState<ImageData | null>(null);
  const [guessedWords, setGuessedWords] = useState<Set<string>>(new Set());
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const timerRef = useRef<number>();

  useEffect(() => {
    const settings = JSON.parse(localStorage.getItem('gameSettings') || '{}');
    setGameState(prev => ({
      ...prev,
      timeLeft: settings.timeLimit || 60
    }));
    fetchImages();
  }, []);

  useEffect(() => {
    if (gameState.isRound && gameState.timeLeft > 0) {
      timerRef.current = window.setInterval(() => {
        setGameState(prev => ({
          ...prev,
          timeLeft: prev.timeLeft - 1
        }));
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
    };
  }, [gameState.isRound]);

  useEffect(() => {
    if (gameState.timeLeft === 0) {
      reveal();
    }
  }, [gameState.timeLeft]);

  const fetchImages = async () => {
    try {
      const settings = JSON.parse(localStorage.getItem('gameSettings') || '{}');
      const response = await axios.get(`${API_BASE_URL}/api/get_random_images`, {
        params: {
          query: settings.searchType === 'random' ? 'random' : settings.searchTerm,
          numImages: settings.rounds || 10,
          titleLength: settings.difficulty === 'easy' ? 50 : settings.difficulty === 'medium' ? 100 : 200
        }
      });
      
      if (!response.data || response.data.length === 0) {
        throw new Error('No images received from API');
      }
      
      setImages(response.data);
      setCurrentImage(response.data[0]);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching images:', error);
      setLoading(false);
      setGameState(prev => ({
        ...prev,
        isRound: false
      }));
    }
  };

  const checkGuess = (guess: string) => {
    if (!currentImage?.title || !gameState.isRound) return;

    const words = currentImage.title.toLowerCase().split(' ');
    const guessLower = guess.toLowerCase().trim();

    if (words.includes(guessLower) && !guessedWords.has(guessLower)) {
      const newGuessedWords = new Set(guessedWords);
      newGuessedWords.add(guessLower);
      setGuessedWords(newGuessedWords);

      const points = guessLower.length * (gameState.multiplier + 1);
      setGameState(prev => ({
        ...prev,
        pointNum: prev.pointNum + points,
        curPointNum: prev.curPointNum + points,
        multiplier: prev.multiplier + 1
      }));

      if (words.length === newGuessedWords.size) {
        setGameState(prev => ({
          ...prev,
          pointNum: prev.pointNum + 100,
          curPointNum: prev.curPointNum + 100,
          isCompleteTitle: true
        }));
        reveal();
      }
    }

    setInputValue('');
  };

  const reveal = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
    }
    setGameState(prev => ({
      ...prev,
      isRound: false
    }));
  };

  const startNewRound = () => {
    const nextRoundNum = gameState.roundNum + 1;
    
    if (nextRoundNum > images.length) {
      setGameState(prev => ({
        ...prev,
        isGameOver: true
      }));
      return;
    }

    const nextImage = images[nextRoundNum - 1];
    if (!nextImage) {
      console.error('No image found for round', nextRoundNum);
      return;
    }

    setCurrentImage(nextImage);
    setGuessedWords(new Set());
    const settings = JSON.parse(localStorage.getItem('gameSettings') || '{}');
    
    setGameState(prev => ({
      ...prev,
      roundNum: nextRoundNum,
      curPointNum: 0,
      multiplier: 0,
      isRound: true,
      isCompleteTitle: false,
      timeLeft: settings.timeLimit || 60
    }));
  };

  const handleInputKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && inputValue.trim()) {
      checkGuess(inputValue);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (gameState.isGameOver) {
    return (
      <Container maxWidth="lg">
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h4" gutterBottom align="center">
            Game Over!
          </Typography>
          <Typography variant="h5" align="center">
            Final Score: {gameState.pointNum}
          </Typography>
          <Box display="flex" justifyContent="center" mt={3}>
            <Button
              variant="contained"
              onClick={() => window.location.href = '/'}
            >
              Play Again
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h4" gutterBottom>
              Round: {gameState.roundNum} of {images.length} | Points: {gameState.pointNum} | Time: {gameState.timeLeft}s
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            {currentImage?.url ? (
              <Box
                component="img"
                src={currentImage.url}
                alt="Stock photo"
                sx={{
                  width: '100%',
                  maxHeight: '400px',
                  objectFit: 'contain'
                }}
              />
            ) : (
              <Typography variant="h6" color="error" align="center">
                Error loading image. Please try refreshing the page.
              </Typography>
            )}
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleInputKeyPress}
                disabled={!gameState.isRound || !currentImage?.title}
                placeholder="Type your guess here..."
                inputRef={inputRef}
                autoFocus
              />
              <Button
                variant="contained"
                onClick={() => checkGuess(inputValue)}
                disabled={!gameState.isRound || !currentImage?.title}
              >
                Guess
              </Button>
              <Button
                variant="outlined"
                onClick={reveal}
                disabled={!gameState.isRound || !currentImage?.title}
              >
                Forfeit
              </Button>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6">
              {gameState.isRound ? (
                `Guessed words: ${Array.from(guessedWords).join(', ')}`
              ) : (
                `Full title: ${currentImage?.title || 'No title available'}`
              )}
            </Typography>
          </Grid>

          {!gameState.isRound && !gameState.isGameOver && (
            <Grid item xs={12}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">
                  Points this round: {gameState.curPointNum}
                </Typography>
                <Button
                  variant="contained"
                  onClick={startNewRound}
                  disabled={gameState.roundNum >= images.length}
                >
                  {gameState.roundNum >= images.length ? 'Game Over' : 'Next Round'}
                </Button>
              </Box>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Container>
  );
};

export default Game; 