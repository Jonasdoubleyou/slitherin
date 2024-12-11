import { DecodedPng, decode as decodePNG, encode as encodePNG } from "fast-png";

type Pixel = {
    x: number,
    y: number,

    r: number, g: number, b: number, a: number;
    setR(v: number): void;
    setG(v: number): void;
    setB(v: number): void;
    setA(v: number): void;
};

const rgba = (img: DecodedPng, x: number, y: number): Pixel => {
    const pos = (y * img.width + x) * 4;
    const r = pos, g = pos + 1, b = pos + 2, a = pos + 3;
    return {
        x, y,
        r: img.data[r],
        g: img.data[g],
        b: img.data[b],
        a: img.data[a],
        setR(v: number) { img.data[r] = v; },
        setG(v: number) { img.data[g] = v; },
        setB(v: number) { img.data[b] = v; },
        setA(v: number) { img.data[a] = v; },
    };
}

function isYellow(px: Pixel) {
    const isYellow = px.r > 140 && px.g > 150 && px.g < 240 && px.b < 120;
    return isYellow;
}

// Maps Tiles to a 3x3 pattern, where 1 means "contains yellow"
const mappings = [
    {
        id: 1,
        part: [1, 1, 0,
               1, 0, 0,
               0, 0, 0],
    },
    {
        id: 2,
        part: [1, 1, 1,
               0, 0, 0,
               0, 0, 0],
    },
    {
        id: 3,
        part: [0, 1, 1,
               0, 0, 1,
               0, 0, 0],
    },
    {
        id: 4,
        part: [1, 0, 0,
               1, 0, 0,
               1, 0, 0],
    },
    {
        id: 5,
        part: [1, 1, 1,
               1, 0, 1,
               1, 1, 1],
    },
    {
        id: 6,
        part: [0, 0, 1,
               0, 0, 1,
               0, 0, 1],
    },
    {
        id: 7,
        part: [0, 0, 0,
               1, 0, 0,
               1, 1, 0],
    },
    {
        id: 8,
        part: [0, 0, 0,
               0, 0, 0,
               1, 1, 1],
    },
    /* {
        id: 9,
        part: [0, 0, 0,
               0, 0, 1,
               0, 1, 1],
    }, */
];

export function isValidPattern(pattern: Pattern) {
    const positions = Array.from({ length: 9 }, () => -1);

    for (const [idx, tile] of pattern.entries()) {
        // Duplicate tile
        if (positions[tile] !== -1) return false;
        positions[tile] = idx;
    }

    for (const pos of positions)
        if (pos === -1) return false;

    return true;
}

// Maps an image to the most likely 3x3 tiles - The returned tile pattern might be invalid,
// e.g. it might contain duplicates or missing tiles
export type Pattern = (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8)[];
export function analyzeRaster(img: DecodedPng) {
    const TILES = 3, PER_TILE = 3;
    let raster = Array.from({ length: (TILES * PER_TILE) ** 2 }, () => 0);

    // (1) Determine the smallest box in the image that contains all yellow pixels
    // -> This "zooms into" the image onto the pattern
    // -> TODO: It is highly sensitive to outlier yellow pixels
    // -> TODO: This does not consider a rotation

    const yellowBox = { minX: img.width, minY: img.height, maxX: 0, maxY: 0, width: 0, height: 0 };

    for (let y = 0; y < img.height; y++) {
        for (let x = 0; x < img.width; x++) {
            const px = rgba(img, x, y);
            if (isYellow(px)) {
                if (x < yellowBox.minX) yellowBox.minX = x;
                if (x > yellowBox.maxX) yellowBox.maxX = x;
                if (y < yellowBox.minY) yellowBox.minY = y;
                if (y > yellowBox.maxY) yellowBox.maxY = y;
            } else {
                px.setA(100);
            }
        }
    }

    yellowBox.width = yellowBox.maxX - yellowBox.minX;
    yellowBox.height = yellowBox.maxY - yellowBox.minY;

    // (2) Split up the box into 3x3 TILES with a 3x3 raster each,
    //  count the number of yellow pixels per raster
    const xPerRaster = yellowBox.width / (TILES * PER_TILE);
    const yPerRaster = yellowBox.height / (TILES * PER_TILE);

    let total = 0;
    for (let y = 0; y < yellowBox.height; y++) {
        for (let x = 0; x < yellowBox.width; x++) {
            const px = rgba(img, yellowBox.minX + x, yellowBox.minY + y);
            const xRaster = Math.floor(x / xPerRaster);
            const yRaster = Math.floor(y / yPerRaster);
            const rasterPos = xRaster +  yRaster * (TILES * PER_TILE);
            if (isYellow(px)) {
                raster[rasterPos] += 1;
                total += 1;
            }
        }
    }

    raster = raster.map(it => it / total * (TILES * PER_TILE));

    // (3) For each tile, search for the tile that best matches the 3x3 raster
    const result: Pattern = [];

    for (let y = 0; y < TILES; y++) {
        for (let x = 0; x < TILES; x++) {
            let bestMatch: Pattern[number] = 0;
            let bestScore = 0;

            checkTile: for (const mapping of mappings) {
                let scoreSum = 0;

                for (let mX = 0; mX < PER_TILE; mX++) {
                    for (let mY = 0; mY < PER_TILE; mY++) {
                        const position = (y * PER_TILE + mY) * (TILES * PER_TILE) + (x * PER_TILE + mX);
                        const score = raster[position];
                        const expected = mapping.part[mY * PER_TILE + mX];
                        const matches = expected ? (score > 0.1) : (score < 0.3);
                        if (!matches) {
                            continue checkTile;
                        }

                        scoreSum += expected ? score : -score;
                    }    
                }

                if (scoreSum > bestScore) bestMatch = mapping.id as Pattern[number];
            }

            result.push(bestMatch);
        }
    }

    return { result, raster, TILES, PER_TILE, yellowBox };
}

// Scans the image for a pattern, and prints the image with the analysis to the canvas (if given)
// Returns a valid pattern, if found
export async function findPatternInFrame(image: Blob, resultCanvas: HTMLCanvasElement, forceResult: boolean): Promise<Pattern | null> {
    // (1) Decode the PNG into a pixel array
    const png = await image.arrayBuffer();
    const img = decodePNG(png, { checkCrc: true });

    // (2) Find a raster in the 
    console.time("analyzeRaster");
    const { result, raster, PER_TILE, TILES, yellowBox } = analyzeRaster(img);
    console.timeEnd("analyzeRaster");

    const isValid = isValidPattern(result);
    console.log(result, isValid);


    // (3) Show the result in the canvas
    if (isValid || forceResult) {
        const encoded = encodePNG(img);
        const encodedBlob = new Blob([encoded], { type: "image/png" });
        const imageBitmap = await createImageBitmap(encodedBlob); 
        const ctx = resultCanvas.getContext('2d')!;   
        
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, resultCanvas.width, resultCanvas.height);
        
        ctx.drawImage(imageBitmap, 0, 0);
        
        const tileWidth = yellowBox.width / (TILES * PER_TILE);
        const tileHeight = yellowBox.height / (TILES * PER_TILE);
        
        ctx.strokeStyle = `rgba(255, 255, 255, 0.5)`;

        for (const [idx, out] of raster.entries()) {
            const x = idx % (TILES * PER_TILE);
            const y = Math.floor(idx / (TILES * PER_TILE));

            ctx.strokeRect(yellowBox.minX + x * tileWidth, yellowBox.minY + y * tileHeight, tileWidth, tileWidth);
        }


        ctx.fillStyle = `rgba(255, 255, 255, 1)`;
        ctx.font = "50px Verdana";

        for (const [idx, tile] of result.entries()) {
            const x = idx % TILES;
            const y = Math.floor(idx / TILES);

            ctx.fillText(`${tile}`, yellowBox.minX + (x + 0.3) * tileWidth * PER_TILE, yellowBox.minY + (y + 0.6) * tileHeight * PER_TILE);
        }
    }

    if (!isValid) return null;

    return result;
}

type Triggers = {
    cancel: () => void;
    makePhoto: () => void;
    resume(): void;
};

export function scanStream(video: HTMLVideoElement, resultCanvas: HTMLCanvasElement, found: (result: Pattern | null) => void): Triggers {
    let stop = true, triggerPhoto = false;

    async function start() {
        if (!stop && !triggerPhoto) return;
        stop = false; triggerPhoto = false;

        // Continouosly scan the video stream for patterns
        while (!stop && !triggerPhoto) {
            // (1) Make a "screenshot" of the video stream and copy it to the canvas
            const ctx = resultCanvas.getContext('2d');
            ctx!.drawImage(video, 0, 0, resultCanvas.width, resultCanvas.height);
            
            // (2) Convert the canvas to a PNG, decode it, and scan for a pattern
            const image = await new Promise<Blob>(res => resultCanvas.toBlob(it => res(it!), "image/png"));
            const pattern = await findPatternInFrame(image, resultCanvas, triggerPhoto);
            if (pattern || triggerPhoto) {
                found(pattern);
                stop = true;
            }
        }
    }

    start();

    return {
        resume: start,
        cancel: () => stop = true,
        makePhoto: () => triggerPhoto = true,
    };
}