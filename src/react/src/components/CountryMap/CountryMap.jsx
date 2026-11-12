import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { arrayOf, func, number, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import CountryMapCard from './CountryMapCard';
import { useCountryMapData, useZoomPan } from './hooks';
import { BINS, binFor, VIEW_WIDTH } from './utils';
import { fetchCountryOptionsIfNeeded } from '../../actions/filterOptions';

import '../../styles/css/countryMap.css';

/*
 * Country-level replacement for the vector tile map.
 *
 * The whole world is a few kilobytes of counts plus a border file cached
 * once, where the tile map built a megabyte-scale tile per viewport and
 * could cache none of it, because every filter produced a different tile.
 * Behind the `country_map` switch until the search page reads from it.
 */
const CountryMap = ({ onSelectCountry, height, countryOptions, fetchCountries }) => {
    const svgRef = useRef(null);
    const [selected, setSelected] = useState(null);

    useEffect(() => {
        fetchCountries();
    }, [fetchCountries]);

    const { shapes, byCode, computedAt, loading, error } = useCountryMapData();
    const {
        viewBox,
        view,
        isZoomed,
        zoomAt,
        reset,
        focusOn,
        onWheel,
        onMouseDown,
    } = useZoomPan(svgRef);

    // Names come from the country filter options the app already loads, so
    // the map says the same thing as the rest of the site and the rollup
    // endpoint stays down to codes and counts.
    const names = useMemo(
        () =>
            (countryOptions || []).reduce(
                (acc, option) => ({ ...acc, [option.value]: option.label }),
                {},
            ),
        [countryOptions],
    );

    const nameFor = useCallback(code => names[code] || code, [names]);

    const shapeByCode = useMemo(
        () => shapes.reduce((acc, s) => ({ ...acc, [s.code]: s }), {}),
        [shapes],
    );

    const select = useCallback(
        code => {
            if (!byCode[code]) {
                return;
            }
            setSelected(code);
            if (onSelectCountry) {
                // The search page will use this to filter its list. Nothing
                // listens yet, so the map stands alone for now.
                onSelectCountry(code);
            }
        },
        [byCode, onSelectCountry],
    );

    const handleFind = useCallback(
        event => {
            const code = event.target.value;
            if (!code) {
                setSelected(null);
                return;
            }
            select(code);
            const node = svgRef.current.querySelector(`[data-cc="${code}"]`);
            if (node) {
                focusOn(node.getBBox());
            }
        },
        [focusOn, select],
    );

    const sortedCountries = useMemo(
        () =>
            Object.keys(byCode).sort((a, b) =>
                nameFor(a).localeCompare(nameFor(b)),
            ),
        [byCode, nameFor],
    );

    if (error) {
        return (
            <div className="country-map country-map--message">
                Country figures could not be loaded. Please try again shortly.
            </div>
        );
    }

    const selectedShape = selected ? shapeByCode[selected] : null;
    const cardOnLeft =
        selectedShape && selectedShape.anchor.x >= VIEW_WIDTH / 2;

    return (
        <div className="country-map" style={height ? { height } : undefined}>
            <div className="country-map__toolbar">
                <label className="country-map__find" htmlFor="country-map-find">
                    Find a country
                </label>
                <select
                    id="country-map-find"
                    value={selected || ''}
                    onChange={handleFind}
                    disabled={loading}
                >
                    <option value="">Select a country…</option>
                    {sortedCountries.map(code => (
                        <option key={code} value={code}>
                            {nameFor(code)}
                        </option>
                    ))}
                </select>

                <div className="country-map__legend" aria-hidden="true">
                    <span className="country-map__legend-label">Locations</span>
                    {BINS.map(bin => (
                        <span className="country-map__swatch" key={bin.label}>
                            <i style={{ background: bin.fill }} />
                            <span>{bin.label}</span>
                        </span>
                    ))}
                </div>
            </div>

            <div className="country-map__body">
                <svg
                    ref={svgRef}
                    className="country-map__svg"
                    viewBox={viewBox}
                    role="img"
                    aria-label="World map shaded by number of production locations per country"
                    onWheel={onWheel}
                    onMouseDown={onMouseDown}
                    style={{ cursor: isZoomed ? 'grab' : 'default' }}
                >
                    <defs>
                        <pattern
                            id="country-map-nodata"
                            width="5"
                            height="5"
                            patternUnits="userSpaceOnUse"
                            patternTransform="rotate(45)"
                        >
                            <rect width="5" height="5" fill="var(--osh-nodata)" />
                            <line
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="5"
                                stroke="var(--osh-nodata-line)"
                                strokeWidth="1.4"
                            />
                        </pattern>
                    </defs>

                    {shapes.map(shape_ => {
                        const row = byCode[shape_.code];
                        const label = row
                            ? `${nameFor(
                                  shape_.code,
                              )}, ${row.location_count.toLocaleString()} production locations`
                            : undefined;
                        return (
                            <path
                                key={shape_.code}
                                d={shape_.path}
                                data-cc={shape_.code}
                                className={`country-map__country${
                                    row ? '' : ' country-map__country--empty'
                                }`}
                                fill={
                                    row
                                        ? binFor(row.location_count).fill
                                        : 'url(#country-map-nodata)'
                                }
                                tabIndex={row ? 0 : undefined}
                                role={row ? 'button' : undefined}
                                aria-label={label}
                                onClick={
                                    row ? () => select(shape_.code) : undefined
                                }
                                onKeyDown={
                                    row
                                        ? event => {
                                              if (
                                                  event.key === 'Enter' ||
                                                  event.key === ' '
                                              ) {
                                                  event.preventDefault();
                                                  select(shape_.code);
                                              }
                                          }
                                        : undefined
                                }
                            />
                        );
                    })}

                    {/* Drawn last so the ring sits above neighbouring shapes */}
                    {selectedShape && (
                        <path
                            d={selectedShape.path}
                            className="country-map__selected"
                        />
                    )}
                </svg>

                {selected && (
                    <CountryMapCard
                        countryCode={selected}
                        name={nameFor(selected)}
                        summary={byCode[selected]}
                        onClose={() => setSelected(null)}
                        side={cardOnLeft ? 'left' : 'right'}
                    />
                )}

                <div className="country-map__zoom">
                    <button
                        type="button"
                        onClick={() =>
                            zoomAt(
                                1 / 1.6,
                                view.x + view.w / 2,
                                view.y + view.h / 2,
                            )
                        }
                        aria-label="Zoom in"
                    >
                        +
                    </button>
                    <button
                        type="button"
                        onClick={() =>
                            zoomAt(1.6, view.x + view.w / 2, view.y + view.h / 2)
                        }
                        aria-label="Zoom out"
                    >
                        −
                    </button>
                    <button
                        type="button"
                        onClick={reset}
                        disabled={!isZoomed}
                        aria-label="Reset zoom"
                    >
                        Reset
                    </button>
                </div>
            </div>

            {computedAt && (
                <div className="country-map__asof">
                    Figures recalculated{' '}
                    {new Date(computedAt).toLocaleDateString()}
                </div>
            )}
        </div>
    );
};

CountryMap.defaultProps = {
    onSelectCountry: null,
    height: null,
    countryOptions: null,
};

CountryMap.propTypes = {
    // Called with an ISO alpha-2 code. The search page will use this to
    // filter its list; nothing listens until that is wired up.
    onSelectCountry: func,
    height: number,
    countryOptions: arrayOf(
        shape({ value: string, label: string }),
    ),
    fetchCountries: func.isRequired,
};

function mapStateToProps({ filterOptions: { countries } }) {
    return { countryOptions: countries.data };
}

function mapDispatchToProps(dispatch) {
    return {
        fetchCountries: () => dispatch(fetchCountryOptionsIfNeeded()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(CountryMap);
