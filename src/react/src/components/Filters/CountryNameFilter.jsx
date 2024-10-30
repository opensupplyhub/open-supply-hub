import React from 'react';
import { bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { updateCountryFilter } from '../../actions/filters';
import { countryOptionsPropType } from '../../util/propTypes';
import StyledSelect from './StyledSelect';

const COUNTRIES = 'COUNTRIES';

const CountryNameFilter = ({
    isDisabled,
    countryOptions,
    countries,
    updateCountry,
    fetching,
    className,
    origin,
}) => (
    <div className={className}>
        <StyledSelect
            label="Country Name"
            name={COUNTRIES}
            options={countryOptions || []}
            value={countries}
            onChange={updateCountry}
            disabled={fetching}
            isDisabled={isDisabled}
            origin={origin}
        />
    </div>
);

CountryNameFilter.defaultProps = {
    isDisabled: false,
    countryOptions: null,
    className: 'form__field',
    origin: null,
};

CountryNameFilter.propTypes = {
    isDisabled: bool,
    countryOptions: countryOptionsPropType,
    updateCountry: func.isRequired,
    countries: countryOptionsPropType.isRequired,
    fetching: bool.isRequired,
    className: string,
    origin: string,
};

const mapStateToProps = ({
    filterOptions: {
        countries: { data: countryOptions, fetching: fetchingCountries },
    },
    filters: { countries },
    facilities: {
        facilities: { fetching: fetchingFacilities },
    },
}) => ({
    countryOptions,
    countries,
    fetching: fetchingCountries || fetchingFacilities,
});

const mapDispatchToProps = dispatch => ({
    updateCountry: v => dispatch(updateCountryFilter(v)),
});

export default connect(mapStateToProps, mapDispatchToProps)(CountryNameFilter);
