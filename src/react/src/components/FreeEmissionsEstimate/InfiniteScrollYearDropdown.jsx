import React from 'react';
import { string, func, bool, object, node } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import { useInfiniteYearScroll } from './hooks.js';
import { infiniteScrollYearDropdownStyles } from './styles.js';

const InfiniteScrollYearDropdown = ({
    label,
    name,
    value,
    onChange,
    error,
    helperText,
    disabled,
    classes,
    ...rest
}) => {
    const {
        years,
        hasMore,
        isLoading,
        loadMoreYears,
    } = useInfiniteYearScroll();

    // Extract year from ISO date string for display.
    const displayYear = value ? new Date(value).getFullYear() : '';

    const handleYearChange = event => {
        const selectedYear = event.target.value;
        if (selectedYear) {
            // Convert year to January 1st ISO date string.
            const isoDate = `${selectedYear}-01-01`;
            onChange(isoDate);
        } else {
            onChange('');
        }
    };

    const handleScroll = event => {
        const { target } = event;
        const threshold = 50; // Pixels from bottom.

        // Check if scrolled near bottom.
        if (
            target.scrollTop + target.clientHeight >=
            target.scrollHeight - threshold
        ) {
            loadMoreYears();
        }
    };

    return (
        <div>
            <FormControl fullWidth variant="outlined" error={error}>
                <InputLabel>{label}</InputLabel>
                <Select
                    value={displayYear}
                    onChange={handleYearChange}
                    disabled={disabled}
                    label={label}
                    MenuProps={{
                        PaperProps: {
                            onScroll: handleScroll,
                        },
                    }}
                    {...rest}
                >
                    {years.map(year => (
                        <MenuItem key={year.value} value={year.value}>
                            {year.label}
                        </MenuItem>
                    ))}
                    {isLoading && (
                        <MenuItem disabled className={classes.loadingItem}>
                            <CircularProgress
                                size={8}
                                className={classes.loadingSpinner}
                            />
                            <Typography
                                variant="body2"
                                className={classes.loadingText}
                            >
                                Loading more years...
                            </Typography>
                        </MenuItem>
                    )}
                    {!hasMore && years.length > 0 && (
                        <MenuItem disabled className={classes.endItem}>
                            <Typography
                                variant="body2"
                                className={classes.endText}
                            >
                                Reached minimum year (1000)
                            </Typography>
                        </MenuItem>
                    )}
                </Select>
            </FormControl>
            {error && helperText}
        </div>
    );
};

InfiniteScrollYearDropdown.propTypes = {
    label: string.isRequired,
    name: string.isRequired,
    value: string,
    onChange: func.isRequired,
    error: bool,
    helperText: node,
    disabled: bool,
    classes: object.isRequired,
};

InfiniteScrollYearDropdown.defaultProps = {
    value: '',
    error: false,
    helperText: null,
    disabled: false,
};

export default withStyles(infiniteScrollYearDropdownStyles)(
    InfiniteScrollYearDropdown,
);
