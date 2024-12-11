import React, { useEffect, useState } from 'react';
import { useStatus } from './controller';
import { Scanner } from './Scanner';
import { isValidPattern, Pattern } from './pattern';
import { PuzzleSolver, PuzzleState } from './algorithm';

const SCANNER_URL = "https://slitherin.wilms.ninja";

export function setAddress(host: string) {
    localStorage.setItem("slitherin-host", host);
}

export function getAddress() {
    return localStorage.getItem("slitherin-host") ?? "";
}

function App() {
    const params = new URL(window.location.href).searchParams;
    const pattern = params.get("pattern");
    const solution = params.get("solution");

    if (pattern) {
        return <SolverApp pattern={pattern} solution={solution} />;
    }

    return <ScannerApp />;
}

function SolverApp({ pattern, solution }: { pattern: string, solution: string | null }) {
    const { status, sendCommand, currentCommand } = useStatus();
    function startGame() {
        if (solution) {
            sendCommand({
                command: "apply",
                pattern: pattern.split("").map(it => +it) as Pattern,
                solution: solution
            });
        } else {
            sendCommand({
                command: "solve",
                pattern: pattern.split("").map(it => +it) as Pattern
            });
        }
    }

    async function newGame() {
        if (status.status === "finish") {
            await sendCommand({ command: "reset" });
        } else if (status.status === "move") {
            window.alert("Also abort the EV3 by holding a button")
        }

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
                <p>
                    {solution ?? ""}
                </p>
            </>}
            
            {(status.status === "waiting") && <>
                <p>Are you ready?</p>
                <button onClick={startGame}>Start Game!</button>
            </>}
            {(status.status === "solve-failed" || status.status === "waiting" || status.status === "aborted" || status.status === "finish") && <button onClick={newGame}>{status.status === "finish" ? "New Game" : "Scan again"}</button>}
        </div>)
    ;
}

function ScannerApp() {
  const [state, setState] = useState<'start' | 'scanning' | 'solving' | 'starting'>('start');
  const [description, setDescription] = useState("");

  function changeAddress() {
    const address = window.prompt("IP-Address of the EV3");
    if (address) setAddress(address);
  }

  function startGame(pattern: Pattern) {
    window.location.href = `http://${getAddress()}?pattern=${pattern.join("")}`;
  }

  function enterManually() {
    let pattern: Pattern;
    do {
        let value = window.prompt("Enter the pattern (0-8):");
        if (!value) return;
        pattern = value.split("").map(it => +it) as Pattern;
    } while(!isValidPattern(pattern));
   
    solve(pattern);
  }

  function solve(pattern: Pattern) {
    setDescription("Solving Pattern " + pattern.join(""));
    // Want to solve the pattern on the robot? Just send it
    // window.location.href = `http://${getAddress()}?pattern=${pattern.join("")}`;
    // return

    setState('solving');

    const solver = new PuzzleSolver(new PuzzleState(pattern));
    (async function() {

        
        for (const depth of [5, 10, 15, 24]) {
            setDescription(it => it + `\nSearching at depth ${depth}`);
            const start = Date.now();
            solver.solve(depth);
            const duration = Date.now() - start;
            setDescription(it => it + `\nSearched depth ${depth} in ${duration}ms`);
            if (solver.solution) {
                console.log(solver.solution);
                setDescription(it => it + `\nSolved ${solver.solution!.toString()}`);

                const check = new PuzzleState(pattern);
                solver.solution.apply(check);
                setDescription(it => it + `\nCheck: ${check.toString()}`);
                
                setDescription(it => it + "\nSending to Robot...");
                window.location.href = `http://${getAddress()}?pattern=${pattern.join("")}&solution=${solver.solution.toString()}`;
                return;
            }
        }

        setDescription(it => it + '\nCould not find a solution :/');
    })();
  }

  if (state === "scanning") {
    return <Scanner onStart={solve}/>;
  }

  if (state === "solving") {
    return <div>
        <h1>Slitherin</h1>        
        <p>{description}</p>
    </div>
  }

  return (
    <div className="App">
      <h1>Slitherin</h1>        
      <button onClick={() => setState('scanning')}>
          Start Scan
      </button>
      <button onClick={enterManually}>
           Enter manually
      </button>
      <button onClick={changeAddress}>
        Set address 
      </button>
    </div>
  );
}

export default App;
