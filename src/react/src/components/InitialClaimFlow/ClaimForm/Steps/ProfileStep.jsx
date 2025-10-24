import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import Business from '@material-ui/icons/Business';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';

const profileStepStyles = theme =>
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

const ProfileStep = ({ classes, formData, handleChange, errors, touched }) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="title">
                            <Business className={classes.headerIcon} />
                            Production Location Details
                        </Typography>
                    }
                    subheader="All fields are optional"
                />
                <CardContent className={classes.content}>
                    <Typography variant="body1" className={classes.description}>
                        Add additional details about this production location
                        (optional).
                    </Typography>

                    <Grid container spacing={16}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                name="numberOfWorkers"
                                label="Number of Workers (Optional)"
                                value={formData.numberOfWorkers || ''}
                                onChange={e =>
                                    handleChange(
                                        'numberOfWorkers',
                                        e.target.value,
                                    )
                                }
                                error={
                                    touched.numberOfWorkers &&
                                    !!errors.numberOfWorkers
                                }
                                helperText={
                                    touched.numberOfWorkers &&
                                    errors.numberOfWorkers
                                }
                                className={classes.field}
                                placeholder="e.g., 150"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                multiline
                                rows={3}
                                name="additionalNotes"
                                label="Additional Notes (Optional)"
                                value={formData.additionalNotes || ''}
                                onChange={e =>
                                    handleChange(
                                        'additionalNotes',
                                        e.target.value,
                                    )
                                }
                                error={
                                    touched.additionalNotes &&
                                    !!errors.additionalNotes
                                }
                                helperText={
                                    touched.additionalNotes &&
                                    errors.additionalNotes
                                }
                                className={classes.field}
                                placeholder="Any additional information about the facility"
                            />
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Grid>
    </Grid>
);

ProfileStep.defaultProps = {
    errors: {},
    touched: {},
};

ProfileStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    errors: object,
    touched: object,
};

// TODO: Retrieve countries, location/processing type from redux store
// and display it in the dropdowns in the profile step. See how
// it is done in the ProductionLocationInfo component. The data is
// already prefetched in the ClaimForm component.
export default withStyles(profileStepStyles)(withScrollReset(ProfileStep));
