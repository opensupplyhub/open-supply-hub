import React, { useState } from 'react';
import { func, oneOf, string } from 'prop-types';

import { useCountryDetail } from './hooks';
import { isUnspecified, orderSectors, sectorScale } from './utils';

const SECTORS_SHOWN = 3;
const PARTNERS_SHOWN = 3;

/*
 * The detail panel, floated over the map on the far side of whatever was
 * clicked so the selection stays visible. Sectors and partners collapse to
 * a few rows so the card fits without scrolling.
 *
 * It deliberately carries no headline count. Clicking a country sets the
 * country filter, so the results list alongside already states the count
 * for the current search — and when another filter is also active the two
 * numbers are not even the same one, because this card describes the whole
 * country while the list describes the search. Showing only what the list
 * cannot show keeps the card small enough to stop covering the map.
 */
const CountryMapCard = ({ countryCode, name, onClose, side }) => {
    const { detail, loading } = useCountryDetail(countryCode);
    const [sectorsOpen, setSectorsOpen] = useState(false);
    const [partnersOpen, setPartnersOpen] = useState(false);

    const sectors = orderSectors(detail ? detail.sectors : []);
    const scale = sectorScale(sectors);
    const partners = detail ? detail.partner_fields : [];

    const visibleSectors = sectorsOpen
        ? sectors
        : sectors.slice(0, SECTORS_SHOWN);
    const visiblePartners = partnersOpen
        ? partners
        : partners.slice(0, PARTNERS_SHOWN);

    return (
        <div className={`country-map__card country-map__card--${side}`}>
            <button
                type="button"
                className="country-map__card-close"
                onClick={onClose}
                aria-label="Close"
            >
                ×
            </button>

            <div className="country-map__card-name">{name}</div>

            {loading && (
                <div className="country-map__card-loading">
                    Loading sectors and partners…
                </div>
            )}

            {detail && (
                <>
                    <div className="country-map__card-section">
                        <h3>
                            Spotlight partners{' '}
                            <span className="country-map__pill">
                                {partners.length}
                            </span>
                        </h3>
                        {partners.length ? (
                            <>
                                <div className="country-map__chips">
                                    {visiblePartners.map(partner => (
                                        <span
                                            className="country-map__chip"
                                            key={partner.name}
                                        >
                                            {partner.label}
                                        </span>
                                    ))}
                                </div>
                                {partners.length > PARTNERS_SHOWN && (
                                    <button
                                        type="button"
                                        className="country-map__more"
                                        onClick={() =>
                                            setPartnersOpen(!partnersOpen)
                                        }
                                    >
                                        {partnersOpen
                                            ? 'Show fewer'
                                            : `Show all ${partners.length} partners`}
                                    </button>
                                )}
                            </>
                        ) : (
                            <p className="country-map__note">
                                No partner data recorded for this country.
                            </p>
                        )}
                    </div>

                    <div className="country-map__card-section">
                        <h3>Sectors represented</h3>
                        {visibleSectors.map(sector => (
                            <div
                                className="country-map__sector"
                                key={sector.sector}
                            >
                                <div className="country-map__sector-line">
                                    <span
                                        className={
                                            isUnspecified(sector.sector)
                                                ? 'country-map__unspecified'
                                                : undefined
                                        }
                                    >
                                        {sector.sector}
                                    </span>
                                    <span className="country-map__sector-count">
                                        {sector.count.toLocaleString()}
                                    </span>
                                </div>
                                <div className="country-map__bar">
                                    <i
                                        style={{
                                            width: `${Math.max(
                                                1,
                                                (100 * sector.count) / scale,
                                            )}%`,
                                            opacity: isUnspecified(
                                                sector.sector,
                                            )
                                                ? 0.45
                                                : 1,
                                        }}
                                    />
                                </div>
                            </div>
                        ))}
                        {sectors.length > SECTORS_SHOWN && (
                            <button
                                type="button"
                                className="country-map__more"
                                onClick={() => setSectorsOpen(!sectorsOpen)}
                            >
                                {sectorsOpen
                                    ? 'Show fewer'
                                    : `Show all ${sectors.length} sectors`}
                            </button>
                        )}
                        {/* "The total" used to mean the headline count above.
                            With that gone the note has to name its own scope,
                            and say that these are whole-country figures rather
                            than counts for the current search. */}
                        <p className="country-map__note">
                            Counts for the whole country. A location can report
                            more than one sector, so they do not sum to its
                            total.
                        </p>
                    </div>
                </>
            )}
        </div>
    );
};

CountryMapCard.propTypes = {
    countryCode: string.isRequired,
    name: string.isRequired,
    onClose: func.isRequired,
    side: oneOf(['left', 'right']).isRequired,
};

export default CountryMapCard;
