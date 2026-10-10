import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="flex min-h-screen items-center justify-center bg-background">
            <div className="text-center">
              <h1 className="text-4xl font-semibold tracking-tight text-foreground">
                CodeMind AI
              </h1>
              <p className="mt-2 text-muted-foreground">scaffold ready</p>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default App
