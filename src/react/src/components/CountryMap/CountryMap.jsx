import React, { useCallback, useEffect, useMemo, useRef } from 'react';
import { arrayOf, func, number, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import CountryMapCard from './CountryMapCard';
import { useCountryMapData, useZoomPan } from './hooks';
import { BINS, binFor, VIEW_WIDTH } from './utils';
import { fetchCountryOptionsIfNeeded } from '../../actions/filterOptions';
import { updateCountryFilter } from '../../actions/filters';
import { fetchFacilities } from '../../actions/facilities';

import '../../styles/css/countryMap.css';

/*
 * Country-level replacement for the vector tile map.
 *
 * The whole world is a few kilobytes of counts plus a border file cached
 * once, where the tile map built a megabyte-scale tile per viewport and
 * could cache none of it, because every filter produced a different tile.
 * Behind the `country_map` switch until the search page reads from it.
 */
const CountryMap = ({
    height,
    countryOptions,
    fetchCountries,
    selectedCodes,
    selectCountry,
    clearCountry,
}) => {
    const svgRef = useRef(null);

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

    // Selecting a country sets the country filter, which is what the
    // sidebar reads. Clicking the country that is already filtered clears
    // it again, so the map can undo itself.
    const select = useCallback(
        code => {
            if (!byCode[code]) {
                return;
            }
            if (selectedCodes.length === 1 && selectedCodes[0] === code) {
                clearCountry();
                return;
            }
            selectCountry({ value: code, label: names[code] || code });
        },
        [byCode, clearCountry, names, selectCountry, selectedCodes],
    );

    const handleFind = useCallback(
        event => {
            const code = event.target.value;
            if (!code) {
                clearCountry();
                return;
            }
            select(code);
            const node = svgRef.current.querySelector(`[data-cc="${code}"]`);
            if (node) {
                focusOn(node.getBBox());
            }
        },
        [clearCountry, focusOn, select],
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

    // Every filtered country gets a ring; the card describes the one
    // country if the filter names exactly one.
    const ringed = selectedCodes
        .map(code => shapeByCode[code])
        .filter(Boolean);
    const single = selectedCodes.length === 1 ? selectedCodes[0] : null;
    const singleShape = single ? shapeByCode[single] : null;
    const cardOnLeft = singleShape && singleShape.anchor.x >= VIEW_WIDTH / 2;

    return (
        <div className="country-map" style={height ? { height } : undefined}>
            <div className="country-map__toolbar">
                <label className="country-map__find" htmlFor="country-map-find">
                    Find a country
                </label>
                <select
                    id="country-map-find"
                    value={single || ''}
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

                    {/* Drawn last so rings sit above neighbouring shapes */}
                    {ringed.map(shape_ => (
                        <path
                            key={`ring-${shape_.code}`}
                            d={shape_.path}
                            className="country-map__selected"
                        />
                    ))}
                </svg>

                {single && byCode[single] && (
                    <CountryMapCard
                        countryCode={single}
                        name={nameFor(single)}
                        summary={byCode[single]}
                        onClose={clearCountry}
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
                    Closed locations excluded &middot; recalculated{' '}
                    {new Date(computedAt).toLocaleDateString()}
                </div>
            )}
        </div>
    );
};

CountryMap.defaultProps = {
    height: null,
    countryOptions: null,
};

CountryMap.propTypes = {
    height: number,
    countryOptions: arrayOf(shape({ value: string, label: string })),
    fetchCountries: func.isRequired,
    selectedCodes: arrayOf(string).isRequired,
    selectCountry: func.isRequired,
    clearCountry: func.isRequired,
};

function mapStateToProps({
    filterOptions: { countries },
    filters: { countries: selected },
}) {
    return {
        countryOptions: countries.data,
        selectedCodes: (selected || []).map(option => option.value),
    };
}

/*
 * Rerunning the search is the same two steps the sidebar's own search
 * button takes: update the filters, then put the resulting query string in
 * the URL. Going through the URL rather than fetching directly keeps the
 * back button and shareable links working.
 */
/*
 * fetchFacilities already builds the query string from the filters,
 * requests the results and pushes the new route, which is how the sidebar
 * and the sort dropdown run a search. Reusing it keeps the map on exactly
 * the same path as every other way of searching, back button included.
 */
function mapDispatchToProps(dispatch, { history: { push } }) {
    const runSearch = () => dispatch(fetchFacilities({ pushNewRoute: push }));

    return {
        fetchCountries: () => dispatch(fetchCountryOptionsIfNeeded()),
        selectCountry: option => {
            dispatch(updateCountryFilter([option]));
            return runSearch();
        },
        clearCountry: () => {
            dispatch(updateCountryFilter([]));
            return runSearch();
        },
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(CountryMap);
