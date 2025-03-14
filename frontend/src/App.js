import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import './App.css';
import DrawbackWizard from './components/DrawbackWizard';
import DocumentUpload from './components/DocumentUpload';
import DocumentManagement from './components/DocumentManagement';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header">
          <h1>DutyFlow</h1>
          <p>Duty Drawback Eligibility Scanner</p>
        </header>
        
        <nav className="App-nav">
          <ul>
            <li><NavLink to="/" end>Home</NavLink></li>
            <li><NavLink to="/documents">Document Library</NavLink></li>
          </ul>
        </nav>
        
        <main className="App-main">
          <Routes>
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/documents" element={<DocumentManagement />} />
            <Route path="/" element={<DrawbackWizard />} />
          </Routes>
        </main>
        
        <footer className="App-footer">
          <p>DutyFlow MVP &copy; {new Date().getFullYear()}</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
