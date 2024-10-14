import React from 'react';
import { connect } from 'react-redux';
import { bool, arrayOf, shape, string } from 'prop-types';
import StyledSelect from './StyledSelect';

const RECORD_TYPE = 'RECORD_TYPE';
const RecordTypeFilter = ({
    isDisabled,
    recordTypesOptions,
    fetchingRecordTypes,
    // updateRecordType,
    // recordTypes,
}) => {
    console.log('isDisabled >>>', isDisabled);
    console.log('recordTypesOptions >>>', recordTypesOptions);
    console.log('fetchingRecordTypes >>>', fetchingRecordTypes);

    return (
        <div className="form__field">
            <StyledSelect
                label="Record Type"
                name={RECORD_TYPE}
                options={recordTypesOptions || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                // isDisabled={isDisabled}
            />
        </div>
    );
};

RecordTypeFilter.defaultProps = {
    isDisabled: false,
    recordTypesOptions: null,
};

RecordTypeFilter.propTypes = {
    isDisabled: bool,
    recordTypesOptions: arrayOf(
        shape({
            value: string.isRequired,
            label: string.isRequired,
        }),
    ),
    // recordTypesOptions: recordTypesOptionsPropType,
    // updateRecordType: func.isRequired,
    // recordTypes: recordTypesOptionsPropType.isRequired,
    fetchingRecordTypes: bool.isRequired,
};

const mapStateToProps = ({
    // filters: { recordTypes },
    filterOptions: {
        recordTypes: {
            data: recordTypesOptions,
            fetching: fetchingRecordTypes,
        },
    },
}) => ({
    // recordTypes,
    recordTypesOptions,
    fetchingRecordTypes,
});

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(RecordTypeFilter);
