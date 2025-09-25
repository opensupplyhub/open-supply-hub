import React from 'react';
import { bool, string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import InputAdornment from '@material-ui/core/InputAdornment';
import Grid from '@material-ui/core/Grid';
import InputErrorText from '../Contribute/InputErrorText';
import { energySourceInputStyles } from './styles.js';

const EnergySourceInput = ({
    source,
    freeEmissionsEstimateForm,
    enabledFieldName,
    valueFieldName,
    disabled,
    classes,
}) => {
    const enabled = freeEmissionsEstimateForm.values[enabledFieldName];
    const value = freeEmissionsEstimateForm.values[valueFieldName];
    const hasError =
        freeEmissionsEstimateForm.touched[valueFieldName] &&
        !!freeEmissionsEstimateForm.errors[valueFieldName];

    return (
        <Grid container alignItems="center">
            <Grid item xs={12} sm={4} md={3}>
                <FormControlLabel
                    className={classes.energyCheckbox}
                    control={
                        <Checkbox
                            id={source.id}
                            name={enabledFieldName}
                            checked={enabled}
                            onChange={freeEmissionsEstimateForm.handleChange}
                            disabled={disabled}
                        />
                    }
                    label={`${source.label}:`}
                />
            </Grid>
            <Grid item xs={12} sm={8} md={9}>
                <TextField
                    variant="outlined"
                    fullWidth
                    name={valueFieldName}
                    value={value}
                    placeholder={source.placeholder}
                    disabled={disabled || !enabled}
                    onChange={event => {
                        freeEmissionsEstimateForm.setFieldValue(
                            valueFieldName,
                            event.target.value,
                        );
                        freeEmissionsEstimateForm.setFieldTouched(
                            valueFieldName,
                            true,
                            false,
                        );
                    }}
                    error={hasError}
                    helperText={
                        hasError && (
                            <InputErrorText
                                text={
                                    freeEmissionsEstimateForm.errors[
                                        valueFieldName
                                    ]
                                }
                            />
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
            </Grid>
        </Grid>
    );
};

EnergySourceInput.propTypes = {
    source: object.isRequired,
    freeEmissionsEstimateForm: object.isRequired,
    enabledFieldName: string.isRequired,
    valueFieldName: string.isRequired,
    disabled: bool.isRequired,
    classes: object.isRequired,
};

export default withStyles(energySourceInputStyles)(EnergySourceInput);
