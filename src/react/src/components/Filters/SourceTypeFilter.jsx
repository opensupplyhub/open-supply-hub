import React from 'react';
import { bool, string, func } from 'prop-types';
import { connect } from 'react-redux';
import { updateSourceTypeFilter } from '../../actions/filters';
import { defaultOptionsPropType } from '../../util/propTypes';
import { SOURCE_TYPES_OPTIONS } from '../../util/constants';
import StyledSelect from './StyledSelect';

const SOURCE_TYPE = 'SOURCE_TYPE';

const SourceTypeFilter = ({
    updateSource,
    sourceTypes,
    isDisabled,
    className,
}) => (
    <div className={className}>
        <StyledSelect
            label="Source Type"
            name={SOURCE_TYPE}
            options={SOURCE_TYPES_OPTIONS || []}
            value={sourceTypes}
            onChange={updateSource}
            isDisabled={isDisabled}
        />
    </div>
);

SourceTypeFilter.defaultProps = {
    isDisabled: false,
    className: 'form__field',
};

SourceTypeFilter.propTypes = {
    updateSource: func.isRequired,
    sourceTypes: defaultOptionsPropType.isRequired,
    isDisabled: bool,
    className: string,
};

const mapStateToProps = ({ filters: { sourceTypes } }) => ({
    sourceTypes,
});

const mapDispatchToProps = dispatch => ({
    updateSource: value => dispatch(updateSourceTypeFilter(value)),
});

export default connect(mapStateToProps, mapDispatchToProps)(SourceTypeFilter);
