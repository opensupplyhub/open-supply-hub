import React from 'react';
import { arrayOf, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import CountryMapCard from './CountryMapCard';
import { updateCountryFilter } from '../../actions/filters';

import '../../styles/css/countryMap.css';

/*
 * The country card, living above the results list rather than floating over
 * the map.
 *
 * It used to be an overlay pinned to whichever side of the map the country
 * was not on, which meant selecting a country covered roughly a third of the
 * map you had just asked about. Widening the panes could not fix that,
 * because the card floated on top whatever the column was.
 *
 * The card and the results list describe the same thing: clicking a country
 * sets the country filter, so the list beside it is already narrowed to that
 * country. Putting them in one column leaves the map whole.
 *
 * Nothing here needs the map. The selection lives in the country filter, so
 * this reads it straight from the store.
 */
const CountryMapCardPanel = ({
    selectedCodes,
    countryOptions,
    clearCountry,
}) => {
    if (selectedCodes.length !== 1) {
        return null;
    }

    const code = selectedCodes[0];
    const match = (countryOptions || []).find(
        option => option.value === code,
    );

    return (
        <div className="country-map__card-slot">
            <CountryMapCard
                countryCode={code}
                name={match ? match.label : code}
                onClose={clearCountry}
                side="panel"
            />
        </div>
    );
};

CountryMapCardPanel.defaultProps = {
    countryOptions: null,
};

CountryMapCardPanel.propTypes = {
    selectedCodes: arrayOf(string).isRequired,
    countryOptions: arrayOf(shape({ value: string, label: string })),
    clearCountry: func.isRequired,
};

function mapStateToProps({
    filters: { countries },
    filterOptions: { countries: options },
}) {
    return {
        selectedCodes: (countries || []).map(option => option.value),
        countryOptions: options.data,
    };
}

/*
 * Closing the card clears the country filter and stops there, matching the
 * map: the search waits for the Search button like every other filter.
 */
function mapDispatchToProps(dispatch) {
    return {
        clearCountry: () => dispatch(updateCountryFilter([])),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(
    CountryMapCardPanel,
);
