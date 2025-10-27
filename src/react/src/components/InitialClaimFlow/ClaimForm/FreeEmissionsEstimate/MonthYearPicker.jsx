import React from 'react';
import { string, func, bool, node } from 'prop-types';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import LabelWithTooltip from './LabelWithTooltip';
import { MONTHS } from './constants';
import YearPicker from './YearPicker';

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
            <Grid container spacing={8}>
                <Grid item xs={12} md={6}>
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
                <Grid item xs={12} md={6}>
                    <YearPicker
                        value={value}
                        onChange={handleYearChange}
                        error={error}
                        disabled={disabled}
                        placeholder={placeholderYear}
                    />
                </Grid>
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
};

MonthYearPicker.defaultProps = {
    value: '',
    error: false,
    helperText: null,
    disabled: false,
};

export default MonthYearPicker;
