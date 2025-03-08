import React from "react";
import "./App.css";
import ImportAnalyzer from "./components/ImportAnalyzer";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>DutyFlow</h1>
        <p>Import Duty Analysis Tool</p>
      </header>
      
      <main className="App-main">
        <ImportAnalyzer />
      </main>
      
      <footer className="App-footer">
        <p>DutyFlow MVP &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
