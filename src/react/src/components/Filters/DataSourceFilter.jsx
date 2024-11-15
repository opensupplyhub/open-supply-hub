import React from 'react';
import { bool, string, func } from 'prop-types';
import { connect } from 'react-redux';
import { updateDataSourceFilter } from '../../actions/filters';
import { dataSourceOptionsPropType } from '../../util/propTypes';
import { DATA_SOURCES_ENUM } from '../../util/constants';
import { createOptionsFromConstants } from '../../util/util';
import StyledSelect from './StyledSelect';

const DATA_SOURCE = 'DATA_SOURCE';
const DATA_SOURCES_OPTIONS = Object.freeze(
    createOptionsFromConstants(DATA_SOURCES_ENUM),
);

const DataSourceFilter = ({
    updateSource,
    dataSources,
    isDisabled,
    className,
    origin,
}) => (
    <div className={className}>
        <StyledSelect
            label="Data Source"
            name={DATA_SOURCE}
            options={DATA_SOURCES_OPTIONS}
            value={dataSources}
            onChange={updateSource}
            isDisabled={isDisabled}
            origin={origin}
        />
    </div>
);

DataSourceFilter.defaultProps = {
    isDisabled: false,
    className: 'form__field',
    origin: null,
};

DataSourceFilter.propTypes = {
    updateSource: func.isRequired,
    dataSources: dataSourceOptionsPropType.isRequired,
    isDisabled: bool,
    className: string,
    origin: string,
};

const mapStateToProps = ({ filters: { dataSources } }) => ({
    dataSources,
});

const mapDispatchToProps = dispatch => ({
    updateSource: value => dispatch(updateDataSourceFilter(value)),
});

export default connect(mapStateToProps, mapDispatchToProps)(DataSourceFilter);
