import React, { useCallback, useEffect, useMemo, useRef } from 'react';
import { arrayOf, func, number, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import { useCountryMapData, useZoomPan } from './hooks';
import { BINS, binFor } from './utils';
import { fetchCountryOptionsIfNeeded } from '../../actions/filterOptions';
import { updateCountryFilter } from '../../actions/filters';

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
    shadedSector,
}) => {
    const svgRef = useRef(null);

    useEffect(() => {
        fetchCountries();
    }, [fetchCountries]);

    const { shapes, byCode, computedAt, loading, error } = useCountryMapData(
        shadedSector,
    );
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
        },
        [clearCountry, select],
    );

    const single = selectedCodes.length === 1 ? selectedCodes[0] : null;

    /*
     * Zoom to whichever country is selected, however it was selected: the
     * picker, a click on the map, the sidebar filter, or a link someone
     * shared. This used to hang off the picker's change handler alone,
     * which meant it read the DOM in the same tick as the dispatch that
     * changes it and left every other route in with no zoom at all.
     *
     * focusOn ignores anything already easy to see, so selecting Brazil
     * does not yank the map about; it is small countries this is for.
     * `shapes` is a dependency because on a first load with a country
     * already in the URL the paths do not exist yet.
     */
    useEffect(() => {
        if (!single || !svgRef.current) {
            return;
        }
        const node = svgRef.current.querySelector(`[data-cc="${single}"]`);
        if (node) {
            focusOn(node.getBBox());
        }
    }, [single, shapes, focusOn]);

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

    // Every filtered country is filled; the card describing it now lives
    // above the results list, so the map keeps its full width.
    const ringed = selectedCodes
        .map(code => shapeByCode[code])
        .filter(Boolean);

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
                    {/* Naming the sector here is what tells you the map
                        reshaded; without it a filtered map and an
                        unfiltered one look like the same picture. */}
                    <span className="country-map__legend-label">
                        {shadedSector ? `${shadedSector} locations` : 'Locations'}
                    </span>
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
                    aria-label={
                        shadedSector
                            ? `World map shaded by number of ${shadedSector} production locations per country`
                            : 'World map shaded by number of production locations per country'
                    }
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
                    {shadedSector
                        ? `Shaded by ${shadedSector} locations`
                        : 'Shaded by all production locations'}{' '}
                    &middot; closed locations excluded &middot; recalculated{' '}
                    {new Date(computedAt).toLocaleDateString()}
                </div>
            )}
        </div>
    );
};

CountryMap.defaultProps = {
    height: null,
    countryOptions: null,
    shadedSector: null,
};

CountryMap.propTypes = {
    height: number,
    countryOptions: arrayOf(shape({ value: string, label: string })),
    fetchCountries: func.isRequired,
    selectedCodes: arrayOf(string).isRequired,
    shadedSector: string,
    selectCountry: func.isRequired,
    clearCountry: func.isRequired,
};

function mapStateToProps({
    filterOptions: { countries },
    filters: { countries: selected, sectors },
}) {
    /*
     * The shading follows one sector at a time, because the rollup it reads
     * is keyed on a single sector. Picking several is a union the cube
     * cannot answer in one lookup, so the map falls back to all-sectors
     * totals rather than showing one of the chosen sectors and implying it
     * is all of them. See OSDEV-3802.
     */
    const chosen = sectors || [];
    return {
        countryOptions: countries.data,
        selectedCodes: (selected || []).map(option => option.value),
        shadedSector: chosen.length === 1 ? chosen[0].value : null,
    };
}

/*
 * Selecting a country sets the country filter and stops there. It does not
 * run the search.
 *
 * It used to, and on a country holding hundreds of thousands of locations
 * that meant a click fired a count, a page and a map extent before the UI
 * could settle, so the sidebar visibly lagged. It was also the odd one out:
 * every other filter on the page waits for the Search button, and the map
 * had no business being different.
 *
 * The feedback that matters is still immediate, because it does not depend
 * on the search: the country fills, its chip appears in the sidebar, and
 * the card opens from the daily rollup. Only the expensive part waits.
 *
 * The URL still follows, because withQueryStringSync writes the query
 * string from the filter state rather than from anything dispatched here.
 *
 * See OSDEV-3802.
 */
function mapDispatchToProps(dispatch) {
    return {
        fetchCountries: () => dispatch(fetchCountryOptionsIfNeeded()),
        selectCountry: option => dispatch(updateCountryFilter([option])),
        clearCountry: () => dispatch(updateCountryFilter([])),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(CountryMap);
