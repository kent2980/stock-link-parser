import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import StockList from './pages/StockList';
import StockDetail from './pages/StockDetail';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<StockList />} />
            <Route path="/stock/:headItemKey" element={<StockDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
