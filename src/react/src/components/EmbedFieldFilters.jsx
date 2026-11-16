import React from 'react';
import { arrayOf, bool, func, object } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './Filters/StyledSelect';
import { updateEmbedFilter } from '../actions/filters';
import { getEmbedFieldFilters } from '../util/embeddedMap';

/*
The filters a contributor has made from their own columns, shown on their
embedded map: one dropdown per visible, filterable embed field. Renders
nothing outside embed mode or when the contributor has none.
*/
function EmbedFieldFilters({
    embed,
    embedFields,
    filterOptions,
    embedFilters,
    updateFilter,
    disabled,
    isSideBarSearch,
}) {
    if (!embed) return null;

    return getEmbedFieldFilters(embedFields, filterOptions).map(
        ({ columnName, label, options }) => (
            <div className="form__field" key={columnName}>
                <StyledSelect
                    label={label}
                    id={`embed-filter-${columnName}`}
                    name={`embed-filter-${columnName}`}
                    isMulti={false}
                    isClearable
                    options={options}
                    value={
                        options.find(
                            option => option.value === embedFilters[columnName],
                        ) || null
                    }
                    onChange={option =>
                        updateFilter({
                            column: columnName,
                            value: option ? option.value : '',
                        })
                    }
                    disabled={disabled}
                    isSideBarSearch={isSideBarSearch}
                />
            </div>
        ),
    );
}

EmbedFieldFilters.propTypes = {
    embed: bool.isRequired,
    embedFields: arrayOf(object),
    filterOptions: object,
    embedFilters: object,
    updateFilter: func.isRequired,
    disabled: bool,
    isSideBarSearch: bool,
};

EmbedFieldFilters.defaultProps = {
    embedFields: [],
    filterOptions: {},
    embedFilters: {},
    disabled: false,
    isSideBarSearch: false,
};

function mapStateToProps({
    embeddedMap: { embed, config },
    filters: { embedFilters },
}) {
    return {
        embed: !!embed,
        embedFields: config?.embed_fields,
        filterOptions: config?.filter_options,
        embedFilters,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateFilter: payload => dispatch(updateEmbedFilter(payload)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(EmbedFieldFilters);
