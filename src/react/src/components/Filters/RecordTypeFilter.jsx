import React from 'react';
import { connect } from 'react-redux';
import { bool } from 'prop-types';
import StyledSelect from './StyledSelect';
import { RECORD_TYPES_OPTIONS } from '../../util/constants';

const RECORD_TYPE = 'RECORD_TYPE';

const RecordTypeFilter = ({ isDisabled }) => {
    console.log('isDisabled >>>', isDisabled);

    return (
        <div className="form__field">
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
};

RecordTypeFilter.propTypes = {
    isDisabled: bool,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(RecordTypeFilter);
