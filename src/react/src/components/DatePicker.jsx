import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import { makeDatePickerStyles } from '../util/styles';

const DatePicker = ({ label, value, onChange, name, classes, ...rest }) => (
    <div className={classes.datePickerContainer}>
        <Typography className={classes.datePickerLabel}>{label}</Typography>
        <TextField
            id={name}
            type="date"
            value={value}
            onChange={e => onChange(e.target.value)}
            InputProps={{
                classes: {
                    input: classes.dateInputStyles,
                    notchedOutline: classes.notchedOutlineStyles,
                },
            }}
            variant="outlined"
            {...rest}
        />
    </div>
);

DatePicker.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    name: PropTypes.string.isRequired,
    classes: PropTypes.object.isRequired,
};

export default withStyles(makeDatePickerStyles)(DatePicker);
