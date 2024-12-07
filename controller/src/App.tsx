import React, { useEffect, useState } from 'react';
import { useStatus } from './controller';
import { Scanner } from './Scanner';
import { Pattern } from './pattern';

const SCANNER_URL = "https://slitherin.wilms.ninja";

export function setAddress(host: string) {
    localStorage.setItem("slitherin-host", host);
}

export function getAddress() {
    return localStorage.getItem("slitherin-host") ?? "";
}

function App() {
    const pattern = new URL(window.location.href).searchParams.get("pattern");
    if (pattern) {
        return <SolverApp pattern={pattern} />;
    }

    return <ScannerApp />;
}

function SolverApp({ pattern }: { pattern: string }) {
    const { status, sendCommand, currentCommand } = useStatus();
    function startGame() {
        sendCommand({
            command: "solve",
            pattern: pattern.split("").map(it => +it) as Pattern
        });
    }

    function newGame() {
        window.location.href = SCANNER_URL;
    }

    return (
        <div className="App">
            <h1>Slitherin</h1> 
            {status.status === "no connection" && <h2 className='error'>
                No connection to the robot
            </h2>}
            {status.status === "not running" && <h2 className='error'>
                The motor control on the EV3 is not running.  
            </h2>}
            {currentCommand && <h2 className="info">
                Sent {currentCommand.command}  
            </h2>}
            {status.status === "aborted" && <h2 className="info">Game was aborted</h2>}
            {status.status === "finish" && <h2 className="success">Game was solved in {(status.duration ?? 0)} seconds</h2>}
            {status.status === "solve-failed" && <h2 className="error">Unsolvable Game!</h2>}
            {status.status === "solve" && <h2 className="info">Searching solution (depth: {status.search_depth}, duration: {status.duration ?? 0}ms)</h2>}
            {status.status === "move" && <>
                <h2 className="info">Applying solution</h2>
                <p>
                    {status.text}
                </p>
            </>}
            
            {(status.status === "waiting" || status.status === "finish") && <button onClick={startGame}>Start Game!</button>}
            {(status.status === "solve-failed" || status.status === "waiting" || status.status === "aborted" || status.status === "finish") && <button onClick={newGame}>New Game</button>}
        </div>)
    ;
}

function ScannerApp() {
  const [scanning, setScanning] = useState(false);

  function changeAddress() {
    const address = window.prompt("IP-Address of the EV3");
    if (address) setAddress(address);
  }

  function startGame(pattern: Pattern) {
    window.location.href = `http://${getAddress()}?pattern=${pattern.join("")}`;
  }

  if (scanning) {
    return <Scanner onStart={startGame}/>;
  }

  return (
    <div className="App">
      <h1>Slitherin</h1>        
      <button onClick={() => setScanning(true)}>
          Start Scan
      </button>
      <button onClick={changeAddress}>
        Set address 
      </button>
    </div>
  );
}

export default App;
