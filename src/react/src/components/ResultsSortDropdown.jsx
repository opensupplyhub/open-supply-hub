import React from 'react';
import { withRouter } from 'react-router';
import { connect } from 'react-redux';

import ReactSelect from 'react-select';
import { Grid, withStyles } from '@material-ui/core';
import InputLabel from '@material-ui/core/InputLabel';

import { optionsForSortingResults } from '../util/constants';
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
        if (sortAlgorithm === '') {
            updateSort(optionsForSortingResults[2]);
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

function mapStateToProps({ filters: { sortAlgorithm } }) {
    return {
        sortAlgorithm,
    };
}

function mapDispatchToProps(dispatch, { history: { push } }) {
    return {
        updateSort: v => {
            dispatch(updateSortAlgorithm(v));
            dispatch(fetchFacilities({ pushNewRoute: push }));
        },
    };
}

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(resultsSortDropdownStyles)(ResultsSortDropdown)),
);
