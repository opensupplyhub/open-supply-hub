import React, { useEffect } from 'react';
import { arrayOf, bool, func, number, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import { fetchIsic4MappedExtraCount } from '../../../actions/filterOptions';
import { updateIsic4IncludeMappedFilter } from '../../../actions/filters';

export const ISIC4_MAPPED_TOGGLE_LABEL =
    'Also show facilities whose ISIC value was mapped from OS Hub data';

/*
Opt-in for ISIC values mapped from a location's Facility Type or Processing
Type through the OS Hub crosswalk (OSDEV-3382). Off by default, so results
only show ISIC values contributors reported. With a selection, the label
shows how many more locations ticking the box adds.
*/
export function IsicMappedValuesToggle({
    isic4,
    includeMapped,
    extraCount,
    disabled,
    onToggle,
    fetchExtraCount,
}) {
    useEffect(() => {
        if (isic4.length) {
            fetchExtraCount(isic4);
        }
    }, [isic4, fetchExtraCount]);

    const showExtraCount = isic4.length > 0 && extraCount != null;

    return (
        <FormControlLabel
            control={
                <Checkbox
                    checked={includeMapped}
                    onChange={event => onToggle(event.target.checked)}
                    color="primary"
                    disabled={disabled}
                    inputProps={{ 'data-testid': 'isic4-include-mapped' }}
                />
            }
            label={
                showExtraCount
                    ? `${ISIC4_MAPPED_TOGGLE_LABEL} (+${extraCount.toLocaleString()})`
                    : ISIC4_MAPPED_TOGGLE_LABEL
            }
        />
    );
}

IsicMappedValuesToggle.defaultProps = {
    isic4: [],
    includeMapped: false,
    extraCount: null,
    disabled: false,
};

IsicMappedValuesToggle.propTypes = {
    isic4: arrayOf(shape({ value: string.isRequired })),
    includeMapped: bool,
    extraCount: number,
    disabled: bool,
    onToggle: func.isRequired,
    fetchExtraCount: func.isRequired,
};

function mapStateToProps({
    filters: { isic4, isic4IncludeMapped },
    filterOptions: { isic4MappedExtraCount },
}) {
    return {
        isic4,
        includeMapped: isic4IncludeMapped,
        extraCount: isic4MappedExtraCount?.count ?? null,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        onToggle: checked => dispatch(updateIsic4IncludeMappedFilter(checked)),
        fetchExtraCount: isic4 => dispatch(fetchIsic4MappedExtraCount(isic4)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(IsicMappedValuesToggle);
