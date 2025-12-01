import React from 'react';
import { string, func, bool, object, node } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Grid from '@material-ui/core/Grid';

import LabelWithTooltip from './LabelWithTooltip.jsx';
import ShowOnly from '../ShowOnly.jsx';
import { useInfiniteYearScroll } from './hooks.js';
import { yearPickerStyles } from './styles.js';

const YearPicker = ({
    value,
    label,
    tooltipText,
    placeholder,
    helperText,
    disabled,
    error,
    onChange,
    showClearButton,
    classes,
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

    const handleClear = event => {
        event.stopPropagation();
        onChange('');
    };

    return (
        <div>
            <ShowOnly when={Boolean(label && tooltipText)}>
                <LabelWithTooltip label={label} tooltipText={tooltipText} />
            </ShowOnly>
            <Grid container spacing={8} className={classes.yearPickerContainer}>
                <Grid item xs={showClearButton ? 9 : 12}>
                    <FormControl fullWidth variant="outlined" error={error}>
                        <Select
                            value={displayYear}
                            onChange={handleYearChange}
                            disabled={disabled}
                            displayEmpty
                            renderValue={selected =>
                                !selected ? placeholder : selected
                            }
                            MenuProps={{
                                PaperProps: {
                                    onScroll: handleScroll,
                                },
                            }}
                        >
                            {years.map(year => (
                                <MenuItem key={year.value} value={year.value}>
                                    {year.label}
                                </MenuItem>
                            ))}
                            {isLoading && (
                                <MenuItem
                                    disabled
                                    className={classes.loadingItem}
                                >
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
                </Grid>
                <ShowOnly
                    when={Boolean(showClearButton && displayYear && !disabled)}
                >
                    <Grid item xs={3}>
                        <IconButton
                            onClick={handleClear}
                            size="small"
                            className={classes.clearButton}
                            aria-label="Clear year selection"
                        >
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </Grid>
                </ShowOnly>
            </Grid>
            {error && helperText}
        </div>
    );
};

YearPicker.propTypes = {
    label: string,
    tooltipText: string,
    value: string,
    onChange: func.isRequired,
    error: bool,
    helperText: node,
    disabled: bool,
    showClearButton: bool,
    classes: object.isRequired,
};

YearPicker.defaultProps = {
    value: '',
    label: null,
    tooltipText: null,
    error: false,
    helperText: null,
    disabled: false,
    showClearButton: true,
};

export default withStyles(yearPickerStyles)(YearPicker);
