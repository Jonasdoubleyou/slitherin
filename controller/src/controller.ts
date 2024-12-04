import { useEffect, useState } from "react";
import { Pattern } from "./pattern";

export interface Status {
    status: "no connection" | "not running" | "waiting" | "solving"; // ...
    state?: string;
}

export interface Command {
    "command": "solve";
    "pattern"?: Pattern;
}


export async function getStatus(): Promise<Status> {
    return await (await fetch(`/status`)).json();
}

export function useStatus() {
    const [status, setStatus] = useState<Status>({ "status": "no connection" });
    const [currentCommand, setCurrentCommand] = useState<Command | null>(null);

    async function sendCommand(command: Command): Promise<void> {
        setCurrentCommand(command);

        await fetch(`/command`, {
            method: "POST",
            body: JSON.stringify(command),
        });
    }

    useEffect(() => {
        let cancel = false;

        (async function() {
            while (true) {
                if (cancel) return;

                try {
                    const newStatus = await getStatus();
                    // Reset current command if the bot reacted
                    const change = newStatus.status !== status.status;
                    if (currentCommand && change) setCurrentCommand(null);

                    setStatus(newStatus);
                } catch (error) {
                    setStatus({ "status": "no connection" });
                }

                await new Promise(res => setTimeout(res, 1000));
            }
        })();
        return () => { cancel = true; };
    }, []);

    return { status, sendCommand, currentCommand } ;
}

