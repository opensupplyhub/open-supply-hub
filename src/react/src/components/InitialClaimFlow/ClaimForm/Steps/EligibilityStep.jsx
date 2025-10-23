import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import Security from '@material-ui/icons/Security';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';

const eligibilityStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
        }),
        cardHeader: Object.freeze({
            backgroundColor: '#f9fafb',
            paddingTop: theme.spacing.unit * 2,
            paddingBottom: theme.spacing.unit * 2,
        }),
        headerIcon: Object.freeze({
            marginRight: theme.spacing.unit,
            verticalAlign: 'middle',
            fontSize: '1.25rem',
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
        description: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            color: COLOURS.DARK_GREY,
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
    });

const EligibilityStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
}) => {
    console.log('errors', errors);
    console.log('touched', touched);
    return (
        <Grid container spacing={24}>
            <Grid item xs={12}>
                <Card className={classes.card}>
                    <CardHeader
                        className={classes.cardHeader}
                        title={
                            <Typography variant="title">
                                <Security className={classes.headerIcon} />
                                Eligibility Check
                            </Typography>
                        }
                    />
                    <CardContent className={classes.content}>
                        <Typography
                            variant="body1"
                            className={classes.description}
                        >
                            Confirm your eligibility to claim this facility.
                        </Typography>

                        <Grid container spacing={16}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    required
                                    name="position"
                                    label="Your Position/Title"
                                    value={formData.position || ''}
                                    onChange={e =>
                                        handleChange('position', e.target.value)
                                    }
                                    onBlur={handleBlur}
                                    className={classes.field}
                                    placeholder="e.g., Owner, General Manager, CEO"
                                    error={
                                        touched.position && !!errors.position
                                    }
                                    helperText={
                                        touched.position && errors.position
                                    }
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    name="yearsAtCompany"
                                    label="Years at Company (Optional)"
                                    value={formData.yearsAtCompany || ''}
                                    onChange={e =>
                                        handleChange(
                                            'yearsAtCompany',
                                            e.target.value,
                                        )
                                    }
                                    className={classes.field}
                                    placeholder="e.g., 5"
                                    error={
                                        touched.yearsAtCompany &&
                                        !!errors.yearsAtCompany
                                    }
                                    helperText={
                                        touched.yearsAtCompany &&
                                        errors.yearsAtCompany
                                    }
                                />
                            </Grid>
                        </Grid>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

EligibilityStep.defaultProps = {
    errors: {},
    touched: {},
};

EligibilityStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    errors: object,
    touched: object,
};

export default withStyles(eligibilityStepStyles)(
    withScrollReset(EligibilityStep),
);
