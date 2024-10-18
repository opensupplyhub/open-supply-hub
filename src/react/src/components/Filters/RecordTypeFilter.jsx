import React from 'react';
import { connect } from 'react-redux';
import { bool, string } from 'prop-types';
import StyledSelect from './StyledSelect';
import { RECORD_TYPES_OPTIONS } from '../../util/constants';

const RECORD_TYPE = 'RECORD_TYPE';

const RecordTypeFilter = ({ isDisabled, className }) => {
    console.log('isDisabled >>>', isDisabled);

    return (
        <div className={className}>
            <StyledSelect
                label="Record Type"
                name={RECORD_TYPE}
                options={RECORD_TYPES_OPTIONS || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                isDisabled={isDisabled}
            />
        </div>
    );
};

RecordTypeFilter.defaultProps = {
    isDisabled: false,
    className: 'form__field',
};

RecordTypeFilter.propTypes = {
    isDisabled: bool,
    className: string,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(RecordTypeFilter);
