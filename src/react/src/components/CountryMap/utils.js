/*
 * Pure helpers for the country map: an equirectangular/Mercator projection,
 * SVG path building that survives the antimeridian, and the count bins.
 */

export const VIEW_WIDTH = 1000;

/*
 * Mercator only keeps its shapes if the vertical scale matches the
 * horizontal one. The width spans 2*pi radians of longitude over 1000
 * units, so the height has to be the latitude band's Mercator span over
 * the same factor. Picking a round number instead squashed every country
 * by about a third.
 */
export const VIEW_HEIGHT = 668;

// Clipped north and south of the populated band so the frame is not mostly
// empty ocean and ice.
const LAT_TOP = 84;
const LAT_BOTTOM = -58;

const mercator = lat => {
    const r = (Math.max(-85, Math.min(85, lat)) * Math.PI) / 180;
    return Math.log(Math.tan(Math.PI / 4 + r / 2));
};

const M_TOP = mercator(LAT_TOP);
const M_BOTTOM = mercator(LAT_BOTTOM);

export const projectX = lon => ((lon + 180) / 360) * VIEW_WIDTH;

export const projectY = lat =>
    ((M_TOP - mercator(lat)) / (M_TOP - M_BOTTOM)) * VIEW_HEIGHT;

/*
 * Rings that cross the antimeridian arrive with longitude jumping from +180
 * to -180. Drawn as-is that is a line straight across the map, which is what
 * smeared Russia and Fiji edge to edge. Unwrap the jumps into continuous
 * longitudes so the ring can be drawn, then drawn again a turn over.
 */
export const unwrapRing = ring => {
    const out = [[ring[0][0], ring[0][1]]];
    let offset = 0;

    for (let i = 1; i < ring.length; i += 1) {
        const step = ring[i][0] - ring[i - 1][0];
        if (step > 180) {
            offset -= 360;
        } else if (step < -180) {
            offset += 360;
        }
        out.push([ring[i][0] + offset, ring[i][1]]);
    }

    return out;
};

const ringPath = (ring, shift) =>
    `${ring
        .map(
            (point, i) =>
                `${i ? 'L' : 'M'}${projectX(point[0] + shift).toFixed(
                    1,
                )} ${projectY(point[1]).toFixed(1)}`,
        )
        .join('')}Z`;

const ringPaths = raw => {
    const ring = unwrapRing(raw);
    const lons = ring.map(point => point[0]);
    const lo = Math.min(...lons);
    const hi = Math.max(...lons);

    let d = ringPath(ring, 0);
    if (hi > 180) {
        d += ringPath(ring, -360);
    }
    if (lo < -180) {
        d += ringPath(ring, 360);
    }
    return d;
};

export const featurePath = feature => {
    const { type, coordinates } = feature.geometry;

    if (type === 'Polygon') {
        return coordinates.map(ringPaths).join('');
    }
    return coordinates
        .map(polygon => polygon.map(ringPaths).join(''))
        .join('');
};

/*
 * Where a country really sits, for deciding which side of the map the detail
 * card belongs on. A bounding box is no good: Russia wraps the antimeridian,
 * so its box runs from x -424 to 1028 and its centre lands near the middle,
 * which put the card on top of the country.
 */
export const featureAnchor = feature => {
    const { type, coordinates } = feature.geometry;
    const rings =
        type === 'Polygon'
            ? [coordinates[0]]
            : coordinates.map(polygon => polygon[0]);

    const biggest = rings.reduce(
        (a, b) => (b.length > a.length ? b : a),
        rings[0],
    );
    const unwrapped = unwrapRing(biggest);

    let lon =
        unwrapped.reduce((sum, p) => sum + p[0], 0) / unwrapped.length;
    const lat =
        unwrapped.reduce((sum, p) => sum + p[1], 0) / unwrapped.length;

    while (lon > 180) lon -= 360;
    while (lon < -180) lon += 360;

    return { x: projectX(lon), y: projectY(lat) };
};

/*
 * Log-decade bins. Fills are custom properties rather than literals so the
 * ramp follows the theme; hard-coded colours made the densest countries
 * invisible against a dark background.
 */
export const BINS = [
    { max: 9, label: '1–9', fill: 'var(--osh-bin-1)' },
    { max: 99, label: '10–99', fill: 'var(--osh-bin-2)' },
    { max: 999, label: '100–999', fill: 'var(--osh-bin-3)' },
    { max: 9999, label: '1k–9.9k', fill: 'var(--osh-bin-4)' },
    { max: 99999, label: '10k–99k', fill: 'var(--osh-bin-5)' },
    { max: Infinity, label: '100k+', fill: 'var(--osh-bin-6)' },
];

export const binFor = count =>
    BINS.find(bin => count <= bin.max) || BINS[BINS.length - 1];

/*
 * "Unspecified" is the absence of a sector rather than a sector, and it
 * outranks real ones on volume in several countries. Always last, and kept
 * out of the bar scale so it cannot squash the real sectors.
 */
export const isUnspecified = name => /^unspecified$/i.test(name || '');

export const orderSectors = (sectors = []) =>
    [...sectors].sort((a, b) => {
        const au = isUnspecified(a.sector);
        const bu = isUnspecified(b.sector);
        if (au !== bu) {
            return au ? 1 : -1;
        }
        return b.count - a.count;
    });

export const sectorScale = sectors => {
    const real = sectors.filter(s => !isUnspecified(s.sector));
    const pool = real.length ? real : sectors;
    return pool.reduce((max, s) => Math.max(max, s.count), 0) || 1;
};
