import React from 'react';
import { arrayOf, bool, func, object } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './Filters/StyledSelect';
import { updateEmbedFilter } from '../actions/filters';
import {
    getEmbedFieldFilters,
    EMBED_SPOTLIGHT_FILTER,
    getEmbedSpotlight,
    getSpotlightFilterOptions,
} from '../util/embeddedMap';

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
    spotlightOptions,
}) {
    if (!embed) return null;

    const fieldFilters = getEmbedFieldFilters(embedFields, filterOptions).map(
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

    // Partner data the contributor has chosen to show and to offer as a
    // filter.
    const spotlightFilter = spotlightOptions.length ? (
        <div className="form__field" key={EMBED_SPOTLIGHT_FILTER}>
            <StyledSelect
                label="Spotlight Data"
                id="embed-filter-spotlight"
                name="embed-filter-spotlight"
                isMulti={false}
                isClearable
                options={spotlightOptions}
                value={
                    spotlightOptions.find(
                        option =>
                            option.value ===
                            embedFilters[EMBED_SPOTLIGHT_FILTER],
                    ) || null
                }
                onChange={option =>
                    updateFilter({
                        column: EMBED_SPOTLIGHT_FILTER,
                        value: option ? option.value : '',
                    })
                }
                disabled={disabled}
                isSideBarSearch={isSideBarSearch}
            />
        </div>
    ) : null;

    return (
        <>
            {fieldFilters}
            {spotlightFilter}
        </>
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
    spotlightOptions: arrayOf(object),
};

EmbedFieldFilters.defaultProps = {
    embedFields: [],
    filterOptions: {},
    embedFilters: {},
    disabled: false,
    isSideBarSearch: false,
    spotlightOptions: [],
};

function mapStateToProps({
    embeddedMap: { embed, config },
    filters: { embedFilters },
}) {
    return {
        embed: !!embed,
        embedFields: config?.embed_fields,
        filterOptions: config?.filter_options,
        spotlightOptions: getSpotlightFilterOptions(
            getEmbedSpotlight(!!embed, config),
        ),
        embedFilters,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateFilter: payload => dispatch(updateEmbedFilter(payload)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(EmbedFieldFilters);
