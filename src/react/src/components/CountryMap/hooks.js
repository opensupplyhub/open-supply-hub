import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import apiRequest from '../../util/apiRequest';
import {
    VIEW_WIDTH,
    VIEW_HEIGHT,
    featureAnchor,
    featurePath,
} from './utils';

// Borders ship as a static asset rather than through the API: they change
// only when we redeploy, so the browser and the CDN can hold them forever.
const BORDERS_URL = '/geo/world-countries.geo.json';
const STATS_URL = '/api/v1/country-stats/';

const MIN_VIEW_WIDTH = VIEW_WIDTH / 12;

// Rough size of a feature, for picking the main territory out of a country
// that arrives in several pieces. Counting coordinates is enough to tell
// Cyprus from Northern Cyprus; it does not need to be an area.
const pointCount = ({ geometry: { type, coordinates } }) =>
    type === 'Polygon'
        ? coordinates.reduce((sum, ring) => sum + ring.length, 0)
        : coordinates.reduce(
              (sum, polygon) =>
                  sum +
                  polygon.reduce((inner, ring) => inner + ring.length, 0),
              0,
          );

/*
 * The two payloads behind the map. Counts come from the daily rollup, which
 * is a few kilobytes for the whole world; borders are a one-off download.
 *
 * They are fetched separately rather than together because the counts now
 * change with the sector filter while the borders never do: fetching them
 * as a pair would re-download 198kB of geometry every time somebody picked
 * a different sector.
 */
export const useCountryMapData = sector => {
    const [borders, setBorders] = useState(null);
    const [stats, setStats] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        apiRequest
            .get(BORDERS_URL)
            .then(response => {
                if (!cancelled) {
                    setBorders(response.data);
                }
            })
            .catch(requestError => {
                if (!cancelled) {
                    setError(requestError);
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        let cancelled = false;
        const url = sector
            ? `${STATS_URL}?sector=${encodeURIComponent(sector)}`
            : STATS_URL;

        apiRequest
            .get(url)
            // The previous counts stay on screen until the new ones land, so
            // changing sector reshades the map rather than blanking it.
            .then(response => {
                if (!cancelled) {
                    setStats(response.data);
                }
            })
            .catch(requestError => {
                if (!cancelled) {
                    setError(requestError);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [sector]);

    const byCode = useMemo(() => {
        if (!stats) {
            return {};
        }
        return stats.countries.reduce(
            (acc, row) => ({ ...acc, [row.country_code]: row }),
            {},
        );
    }, [stats]);

    /*
     * Paths and anchors are derived from geometry alone, so they are built
     * once rather than on every render or zoom.
     *
     * Several features can share one ISO code: the 50m map units we use for
     * the small countries split Cyprus and Somalia into two pieces each
     * (Northern Cyprus, Somaliland), and both pieces carry the parent code.
     * Left as separate shapes they collide on React key, and only whichever
     * piece won the lookup got the selection ring. Merging their paths draws
     * the whole country and makes the code unique again.
     */
    const shapes = useMemo(() => {
        if (!borders) {
            return [];
        }

        const byId = new Map();
        borders.features
            .filter(feature => feature.id !== 'AQ')
            .forEach(feature => {
                const group = byId.get(feature.id);
                if (group) {
                    group.push(feature);
                } else {
                    byId.set(feature.id, [feature]);
                }
            });

        return Array.from(byId.entries()).map(([code, features]) => ({
            code,
            path: features.map(featurePath).join(''),
            // Anchor on the largest piece, so the card sits beside the
            // mainland rather than beside a breakaway region.
            anchor: featureAnchor(
                features.reduce((biggest, feature) =>
                    pointCount(feature) > pointCount(biggest)
                        ? feature
                        : biggest,
                ),
            ),
        }));
    }, [borders]);

    return {
        shapes,
        byCode,
        computedAt: stats ? stats.computed_at : null,
        total: stats
            ? stats.countries.reduce((sum, row) => sum + row.location_count, 0)
            : 0,
        loading: !error && (!borders || !stats),
        error,
    };
};

/*
 * One country's sectors and Spotlight partners, fetched only when somebody
 * asks for it. The whole-world payload deliberately does not carry these.
 */
export const useCountryDetail = countryCode => {
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!countryCode) {
            setDetail(null);
            return undefined;
        }

        let cancelled = false;
        setLoading(true);

        apiRequest
            .get(`${STATS_URL}${countryCode}/`)
            .then(response => {
                if (!cancelled) {
                    setDetail(response.data);
                    setLoading(false);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setDetail(null);
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [countryCode]);

    return { detail, loading };
};

export const useZoomPan = svgRef => {
    const [view, setView] = useState({
        x: 0,
        y: 0,
        w: VIEW_WIDTH,
        h: VIEW_HEIGHT,
    });
    const dragRef = useRef(null);

    const clamp = useCallback(next => {
        const w = Math.max(MIN_VIEW_WIDTH, Math.min(VIEW_WIDTH, next.w));
        const h = (w * VIEW_HEIGHT) / VIEW_WIDTH;
        return {
            w,
            h,
            x: Math.max(0, Math.min(VIEW_WIDTH - w, next.x)),
            y: Math.max(0, Math.min(VIEW_HEIGHT - h, next.y)),
        };
    }, []);

    const zoomAt = useCallback(
        (factor, originX, originY) => {
            setView(current => {
                const scaled = clamp({ ...current, w: current.w * factor });
                const ratio = scaled.w / current.w;
                return clamp({
                    ...scaled,
                    x: originX - (originX - current.x) * ratio,
                    y: originY - (originY - current.y) * ratio,
                });
            });
        },
        [clamp],
    );

    const reset = useCallback(
        () => setView({ x: 0, y: 0, w: VIEW_WIDTH, h: VIEW_HEIGHT }),
        [],
    );

    /*
     * Pull the view in only for countries too small to find by eye. Yanking
     * the map to Brazil when Brazil is already plainly visible would be
     * worse than leaving it where it is.
     */
    const focusOn = useCallback(
        box => {
            if (!box || box.width > 60) {
                return;
            }
            const w = Math.max(MIN_VIEW_WIDTH, Math.max(box.width, 12) * 14);
            const h = (w * VIEW_HEIGHT) / VIEW_WIDTH;
            setView(
                clamp({
                    w,
                    h,
                    x: box.x + box.width / 2 - w / 2,
                    y: box.y + box.height / 2 - h / 2,
                }),
            );
        },
        [clamp],
    );

    const toSvgPoint = useCallback(
        event => {
            const rect = svgRef.current.getBoundingClientRect();
            return {
                x: view.x + ((event.clientX - rect.left) / rect.width) * view.w,
                y: view.y + ((event.clientY - rect.top) / rect.height) * view.h,
            };
        },
        [svgRef, view],
    );

    const onWheel = useCallback(
        event => {
            event.preventDefault();
            const point = toSvgPoint(event);
            zoomAt(event.deltaY > 0 ? 1.18 : 1 / 1.18, point.x, point.y);
        },
        [toSvgPoint, zoomAt],
    );

    const onMouseDown = useCallback(
        event => {
            if (view.w >= VIEW_WIDTH) {
                return;
            }
            dragRef.current = {
                startX: event.clientX,
                startY: event.clientY,
                viewX: view.x,
                viewY: view.y,
            };
        },
        [view],
    );

    useEffect(() => {
        const move = event => {
            const drag = dragRef.current;
            if (!drag || !svgRef.current) {
                return;
            }
            const rect = svgRef.current.getBoundingClientRect();
            setView(current =>
                clamp({
                    ...current,
                    x:
                        drag.viewX -
                        ((event.clientX - drag.startX) / rect.width) *
                            current.w,
                    y:
                        drag.viewY -
                        ((event.clientY - drag.startY) / rect.height) *
                            current.h,
                }),
            );
        };
        const up = () => {
            dragRef.current = null;
        };

        window.addEventListener('mousemove', move);
        window.addEventListener('mouseup', up);
        return () => {
            window.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', up);
        };
    }, [clamp, svgRef]);

    return {
        view,
        viewBox: `${view.x.toFixed(1)} ${view.y.toFixed(1)} ${view.w.toFixed(
            1,
        )} ${view.h.toFixed(1)}`,
        isZoomed: view.w < VIEW_WIDTH,
        zoomAt,
        reset,
        focusOn,
        onWheel,
        onMouseDown,
    };
};
