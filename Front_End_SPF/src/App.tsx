import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Game from './components/Game'
import Home from './components/Home'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/game" element={<Game />} />
      </Routes>
    </ThemeProvider>
  )
}

export default App 