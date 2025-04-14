import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
  FormControlLabel,
  RadioGroup,
  Radio,
  SelectChangeEvent,
} from '@mui/material';

interface GameSettings {
  searchType: 'random' | 'search' | 'build';
  searchTerm: string;
  difficulty: 'easy' | 'medium' | 'hard';
  timeLimit: number;
  rounds: number;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<GameSettings>({
    searchType: 'random',
    searchTerm: '',
    difficulty: 'medium',
    timeLimit: 60,
    rounds: 10,
  });

  const handleSearchTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings({
      ...settings,
      searchType: event.target.value as 'random' | 'search' | 'build',
      searchTerm: '',
    });
  };

  const handleDifficultyChange = (event: SelectChangeEvent<string>) => {
    setSettings({
      ...settings,
      difficulty: event.target.value as 'easy' | 'medium' | 'hard',
    });
  };

  const handleTimeLimitChange = (event: SelectChangeEvent<number>) => {
    setSettings({
      ...settings,
      timeLimit: event.target.value as number,
    });
  };

  const handleRoundsChange = (event: SelectChangeEvent<number>) => {
    setSettings({
      ...settings,
      rounds: event.target.value as number,
    });
  };

  const handleStartGame = () => {
    localStorage.setItem('gameSettings', JSON.stringify(settings));
    navigate('/game');
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ p: 4, mt: 8 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Stock Photo Frenzy
        </Typography>

        <Box component="form" sx={{ mt: 4 }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <RadioGroup
              value={settings.searchType}
              onChange={handleSearchTypeChange}
            >
              <FormControlLabel
                value="random"
                control={<Radio />}
                label="Random Photos"
              />
              <FormControlLabel
                value="search"
                control={<Radio />}
                label="Search Term"
              />
              <FormControlLabel
                value="build"
                control={<Radio />}
                label="Build Word"
                disabled
              />
            </RadioGroup>
          </FormControl>

          {settings.searchType === 'search' && (
            <TextField
              fullWidth
              label="Search Term"
              value={settings.searchTerm}
              onChange={(e) => setSettings({ ...settings, searchTerm: e.target.value })}
              sx={{ mb: 3 }}
            />
          )}

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Difficulty</InputLabel>
            <Select
              value={settings.difficulty}
              label="Difficulty"
              onChange={handleDifficultyChange}
            >
              <MenuItem value="easy">Easy</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="hard">Hard</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Time Limit (seconds)</InputLabel>
            <Select
              value={settings.timeLimit}
              label="Time Limit (seconds)"
              onChange={handleTimeLimitChange}
            >
              <MenuItem value={30}>30</MenuItem>
              <MenuItem value={60}>60</MenuItem>
              <MenuItem value={90}>90</MenuItem>
              <MenuItem value={120}>120</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 4 }}>
            <InputLabel>Number of Rounds</InputLabel>
            <Select
              value={settings.rounds}
              label="Number of Rounds"
              onChange={handleRoundsChange}
            >
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={15}>15</MenuItem>
              <MenuItem value={20}>20</MenuItem>
            </Select>
          </FormControl>

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleStartGame}
            disabled={settings.searchType === 'search' && !settings.searchTerm}
          >
            Start Game
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Home; 