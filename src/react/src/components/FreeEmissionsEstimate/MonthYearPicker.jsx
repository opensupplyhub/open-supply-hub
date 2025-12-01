import React from 'react';
import { string, func, bool, node, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

import LabelWithTooltip from './LabelWithTooltip.jsx';
import YearPicker from './YearPicker.jsx';
import ShowOnly from '../ShowOnly.jsx';
import { MONTHS } from './constants.jsx';
import { monthYearPickerStyles } from './styles.js';

const MonthYearPicker = ({
    value,
    label,
    tooltipText,
    placeholderMonth,
    placeholderYear,
    helperText,
    disabled,
    error,
    onChange,
    classes,
}) => {
    // Extract month and year from ISO date string (YYYY-MM-DD) for display.
    const date = value ? new Date(value) : null;
    const displayMonth = date ? date.getMonth() + 1 : '';
    const displayYear = date ? date.getFullYear() : '';

    const currentYear = new Date().getFullYear();

    const updateDate = (month, year) => {
        if (
            month &&
            year &&
            !Number.isNaN(Number(month)) &&
            !Number.isNaN(Number(year))
        ) {
            // Convert to first day of selected month/year in proper ISO format.
            const paddedMonth = String(month).padStart(2, '0');
            const isoDate = `${year}-${paddedMonth}-01`;
            onChange(isoDate);
        }
    };

    const handleMonthChange = event => {
        const selectedMonth = event.target.value;
        if (selectedMonth && displayYear) {
            updateDate(selectedMonth, displayYear);
        } else if (selectedMonth) {
            // If only month is selected, default to current year.
            updateDate(selectedMonth, currentYear);
        }
    };

    const handleYearChange = isoDate => {
        // Extract the year and combine with current month.
        const selectedYear = new Date(isoDate).getFullYear();
        if (selectedYear && displayMonth) {
            updateDate(displayMonth, selectedYear);
        } else if (selectedYear) {
            // If only year is selected, default to January.
            updateDate(1, selectedYear);
        }
    };

    const handleClear = event => {
        event.stopPropagation();
        onChange('');
    };

    const renderMonthValue = selected => {
        if (!selected) {
            return placeholderMonth;
        }
        // Find the month object and return its label.
        const monthObj = MONTHS.find(month => month.value === selected);
        return monthObj.label;
    };

    return (
        <div>
            <LabelWithTooltip label={label} tooltipText={tooltipText} />
            <Grid
                container
                spacing={8}
                className={classes.monthYearPickerContainer}
            >
                <Grid item xs={5}>
                    <FormControl fullWidth variant="outlined" error={error}>
                        <Select
                            value={displayMonth}
                            onChange={handleMonthChange}
                            disabled={disabled}
                            displayEmpty
                            renderValue={renderMonthValue}
                        >
                            {MONTHS.map(month => (
                                <MenuItem key={month.value} value={month.value}>
                                    {month.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={5}>
                    <YearPicker
                        value={value}
                        onChange={handleYearChange}
                        error={error}
                        disabled={disabled}
                        placeholder={placeholderYear}
                        showClearButton={false}
                    />
                </Grid>
                <ShowOnly
                    when={Boolean(displayMonth && displayYear && !disabled)}
                >
                    <Grid item xs={2}>
                        <IconButton
                            onClick={handleClear}
                            size="small"
                            className={classes.clearButton}
                            aria-label="Clear date selection"
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

MonthYearPicker.propTypes = {
    label: string.isRequired,
    tooltipText: string.isRequired,
    value: string,
    onChange: func.isRequired,
    error: bool,
    helperText: node,
    disabled: bool,
    placeholderMonth: string.isRequired,
    placeholderYear: string.isRequired,
    classes: object.isRequired,
};

MonthYearPicker.defaultProps = {
    value: '',
    error: false,
    helperText: null,
    disabled: false,
};

export default withStyles(monthYearPickerStyles)(MonthYearPicker);
