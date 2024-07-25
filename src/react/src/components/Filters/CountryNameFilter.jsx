import React from 'react';
import { bool, func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateCountryFilter } from '../../actions/filters';

import { countryOptionsPropType } from '../../util/propTypes';

const COUNTRIES = 'COUNTRIES';

function CountryNameFilter({
    isDisabled,
    countryOptions,
    countries,
    updateCountry,
    fetching,
}) {
    return (
        <div className="form__field">
            <StyledSelect
                label="Country Name"
                name={COUNTRIES}
                options={countryOptions || []}
                value={countries}
                onChange={updateCountry}
                disabled={fetching}
                isDisabled={isDisabled}
            />
        </div>
    );
}

CountryNameFilter.defaultProps = {
    isDisabled: false,
    countryOptions: null,
};

CountryNameFilter.propTypes = {
    isDisabled: bool,
    countryOptions: countryOptionsPropType,
    updateCountry: func.isRequired,
    countries: countryOptionsPropType.isRequired,
    fetching: bool.isRequired,
};

function mapStateToProps({
    filterOptions: {
        countries: { data: countryOptions, fetching: fetchingCountries },
    },
    filters: { countries },
    facilities: {
        facilities: { fetching: fetchingFacilities },
    },
}) {
    return {
        countryOptions,
        countries,
        fetching: fetchingCountries || fetchingFacilities,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateCountry: v => dispatch(updateCountryFilter(v)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(CountryNameFilter);
