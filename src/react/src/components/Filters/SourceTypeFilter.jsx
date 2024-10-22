import React from 'react';
import { connect } from 'react-redux';
import { bool, string } from 'prop-types';
import StyledSelect from './StyledSelect';
import { SOURCE_TYPES_OPTIONS } from '../../util/constants';

const SOURCE_TYPE = 'SOURCE_TYPE';

const SourceTypeFilter = ({ isDisabled, className }) => {
    console.log('isDisabled >>>', isDisabled);

    return (
        <div className={className}>
            <StyledSelect
                label="Source Type"
                name={SOURCE_TYPE}
                options={SOURCE_TYPES_OPTIONS || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                isDisabled={isDisabled}
            />
        </div>
    );
};

SourceTypeFilter.defaultProps = {
    isDisabled: false,
    className: 'form__field',
};

SourceTypeFilter.propTypes = {
    isDisabled: bool,
    className: string,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(SourceTypeFilter);
