import { Routes, Route } from 'react-router-dom'
import Game from './components/Game'
import Home from './components/Home'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/game" element={<Game />} />
    </Routes>
  )
}

export default App 