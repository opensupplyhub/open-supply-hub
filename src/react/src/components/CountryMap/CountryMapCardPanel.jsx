import React from 'react';
import { arrayOf, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import CountryMapCard from './CountryMapCard';
import { updateCountryFilter } from '../../actions/filters';
import { fetchFacilities } from '../../actions/facilities';

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
 * Closing the card clears the country filter and reruns the search, the same
 * two steps the map takes. `redirectOnSingleResult` is off for the same
 * reason it is off there: clearing a filter should not navigate anywhere.
 */
function mapDispatchToProps(dispatch, { history: { push } }) {
    return {
        clearCountry: () => {
            dispatch(updateCountryFilter([]));
            return dispatch(
                fetchFacilities({
                    pushNewRoute: push,
                    redirectOnSingleResult: false,
                }),
            );
        },
    };
}

/*
 * withRouter, because this is mounted inside the results list rather than
 * by a Route, so it is handed no history of its own and mapDispatchToProps
 * reads push off ownProps.
 */
export default withRouter(
    connect(mapStateToProps, mapDispatchToProps)(CountryMapCardPanel),
);
