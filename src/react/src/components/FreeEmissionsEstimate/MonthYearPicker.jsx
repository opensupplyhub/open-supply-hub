import React from 'react';
import { string, func, bool, object, node } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import Grid from '@material-ui/core/Grid';
import { MONTHS } from './constants.js';
import { monthYearPickerStyles } from './styles.js';
import InfiniteScrollYearDropdown from './InfiniteScrollYearDropdown.jsx';

const MonthYearPicker = ({
    label,
    name,
    value,
    onChange,
    error,
    helperText,
    disabled,
    placeholder,
    classes,
    ...rest
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
        // VirtualizedYearSelect already provides ISO date
        // Extract the year and combine with current month
        const selectedYear = new Date(isoDate).getFullYear();
        if (selectedYear && displayMonth) {
            updateDate(displayMonth, selectedYear);
        } else if (selectedYear) {
            // If only year is selected, default to January.
            updateDate(1, selectedYear);
        }
    };

    return (
        <div>
            <InputLabel className={classes.monthYearPickerLabel}>
                {label}
            </InputLabel>
            <Grid container spacing={8}>
                <Grid item xs={6}>
                    <FormControl fullWidth variant="outlined" error={error}>
                        <InputLabel>Month</InputLabel>
                        <Select
                            value={displayMonth}
                            onChange={handleMonthChange}
                            disabled={disabled}
                            label="Month"
                        >
                            {MONTHS.map(month => (
                                <MenuItem key={month.value} value={month.value}>
                                    {month.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={6}>
                    <InfiniteScrollYearDropdown
                        label="Year"
                        name={`${name}-year`}
                        value={value}
                        onChange={handleYearChange}
                        error={error}
                        disabled={disabled}
                        {...rest}
                    />
                </Grid>
            </Grid>
            {error && helperText}
        </div>
    );
};

MonthYearPicker.propTypes = {
    label: string.isRequired,
    name: string.isRequired,
    value: string,
    onChange: func.isRequired,
    error: bool,
    helperText: node,
    disabled: bool,
    placeholder: string,
    classes: object.isRequired,
};

MonthYearPicker.defaultProps = {
    value: '',
    error: false,
    helperText: null,
    disabled: false,
    placeholder: '',
};

export default withStyles(monthYearPickerStyles)(MonthYearPicker);
