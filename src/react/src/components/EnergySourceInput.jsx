import React from 'react';
import { bool, string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import InputAdornment from '@material-ui/core/InputAdornment';
import InputErrorText from './Contribute/InputErrorText';

const energySourceInputStyles = {
    energyInputContainer: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: '12px',
    },
    energyCheckbox: {
        minWidth: '140px',
    },
    energyInput: {
        flex: 1,
        marginLeft: '12px',
    },
    unitText: {
        minWidth: '50px',
        marginLeft: '8px',
        fontSize: '14px',
        color: '#64748b',
    },
};

const EnergySourceInput = ({
    source,
    formik,
    enabledFieldName,
    valueFieldName,
    disabled,
    classes,
}) => {
    const enabled = formik.values[enabledFieldName];
    const value = formik.values[valueFieldName];
    const hasError =
        formik.touched[valueFieldName] && formik.errors[valueFieldName];

    return (
        <div className={classes.energyInputContainer}>
            <FormControlLabel
                className={classes.energyCheckbox}
                control={
                    <Checkbox
                        id={source.id}
                        name={enabledFieldName}
                        checked={enabled}
                        onChange={formik.handleChange}
                        disabled={disabled}
                    />
                }
                label={`${source.label}:`}
            />
            <TextField
                className={classes.energyInput}
                variant="outlined"
                size="small"
                name={valueFieldName}
                value={value}
                placeholder={source.placeholder}
                disabled={disabled || !enabled}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={hasError}
                helperText={
                    hasError && (
                        <InputErrorText text={formik.errors[valueFieldName]} />
                    )
                }
                InputProps={{
                    endAdornment: (
                        <InputAdornment position="end">
                            <Typography className={classes.unitText}>
                                {source.unit}
                            </Typography>
                        </InputAdornment>
                    ),
                }}
            />
        </div>
    );
};

EnergySourceInput.propTypes = {
    source: object.isRequired,
    formik: object.isRequired,
    enabledFieldName: string.isRequired,
    valueFieldName: string.isRequired,
    disabled: bool.isRequired,
    classes: object.isRequired,
};

export default withStyles(energySourceInputStyles)(EnergySourceInput);
