import React, { useEffect, useState } from 'react';
import { useStatus, setAddress } from './controller';
import { Scanner } from './Scanner';
import { Pattern } from './pattern';

function App() {
  const { status, sendCommand, currentCommand } = useStatus();
  const [scanning, setScanning] = useState(false);

  function changeAddress() {
    const address = window.prompt("IP-Address of the EV3");
    if (address) setAddress(address);
  }

  function startGame(pattern: Pattern) {
    setScanning(false);

    sendCommand({
        command: "solve",
        pattern
    });
  }

  if (scanning) {
    return <Scanner onStart={startGame}/>;
  }

  return (
    <div className="App">
      <h1>Slitherin</h1>
      {status.status === "no address" && <h2 className='error'>
        No connection set up
      </h2>}
      {status.status === "no connection" && <h2 className='error'>
        No connection to the robot
      </h2>}
      {status.status === "not running" && <h2 className='error'>
        The motor control on the EV3 is not running.  
      </h2>}
      {currentCommand && <h2 className="info">
        Sent {currentCommand.command}  
      </h2>}
      {["no address", "no connection", "not running"].includes(status.status) && <button onClick={changeAddress}>
        Set address 
      </button>}
      {status.status === "waiting" && <h2 className="success">Established Connection</h2>}
        
      {status.status !== "solving" && <button onClick={() => setScanning(true)}>
          Start Scan
      </button>}
    </div>
  );
}

export default App;
