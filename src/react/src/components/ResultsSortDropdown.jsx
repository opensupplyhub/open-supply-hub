import React from 'react';
import { string, func, shape, oneOfType, node } from 'prop-types';
import { withRouter } from 'react-router';
import { connect } from 'react-redux';

import ReactSelect from 'react-select';
import { Grid, withStyles } from '@material-ui/core';
import InputLabel from '@material-ui/core/InputLabel';

import {
    optionsForSortingResults,
    DEFAULT_SORT_OPTION_INDEX,
} from '../util/constants';
import { updateSortAlgorithm } from '../actions/filters';
import { fetchFacilities } from '../actions/facilities';

const selectStyles = {
    control: provided => ({
        ...provided,
        minHeight: 0,
        boxShadow: 'none',
        border: 'none',
    }),
    dropdownIndicator: provided => ({
        ...provided,
        padding: '0',
        color: '#1C1B1F',
        '&:hover': {
            color: '#1C1B1F',
        },
    }),
    valueContainer: provided => ({
        ...provided,
        padding: '0 0 0 7px',
    }),
    singleValue: provided => ({
        ...provided,
        color: '#000000',
        fontWeight: 800,
    }),
};

const resultsSortDropdownStyles = theme =>
    Object.freeze({
        selectLabel: {
            fontWeight: 600,
            color: '#000000',
        },
        selectWrapper: {
            width: '150px',
        },
        select: {
            fontFamily: theme.typography.fontFamily,
        },
    });

const ResultsSortDropdown = ({ classes, sortAlgorithm, updateSort }) => {
    React.useEffect(() => {
        if (!sortAlgorithm) {
            updateSort(optionsForSortingResults[DEFAULT_SORT_OPTION_INDEX]);
        }
    }, [sortAlgorithm, updateSort]);

    return (
        <Grid container>
            <Grid item>
                <InputLabel
                    shrink={false}
                    htmlFor="sort-select"
                    className={classes.selectLabel}
                >
                    Sort By:
                </InputLabel>
            </Grid>
            <Grid item className={classes.selectWrapper}>
                <ReactSelect
                    id="sort-select"
                    name="sort-select"
                    className={`notranslate ${classes.select}`}
                    classNamePrefix="select"
                    styles={selectStyles}
                    components={{
                        IndicatorSeparator: null,
                    }}
                    isSearchable={false}
                    value={sortAlgorithm}
                    options={optionsForSortingResults}
                    onChange={updateSort}
                />
            </Grid>
        </Grid>
    );
};

ResultsSortDropdown.propTypes = {
    classes: shape({
        selectLabel: string.isRequired,
        selectWrapper: string.isRequired,
        select: string.isRequired,
    }).isRequired,
    sortAlgorithm: oneOfType([
        shape({
            value: string.isRequired,
            label: oneOfType([node, string]).isRequired,
        }).isRequired,
        string,
    ]).isRequired,
    updateSort: func.isRequired,
};

const mapStateToProps = ({ filters }) => ({
    sortAlgorithm: filters.sortAlgorithm,
});

const mapDispatchToProps = (dispatch, { history: { push } }) => ({
    updateSort: v => {
        dispatch(updateSortAlgorithm(v));
        dispatch(fetchFacilities({ pushNewRoute: push }));
    },
});

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(resultsSortDropdownStyles)(ResultsSortDropdown)),
);
