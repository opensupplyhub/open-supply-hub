import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import People from '@material-ui/icons/People';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';

const contactStepStyles = theme =>
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
        section: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        sectionTitle: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            fontWeight: 600,
            fontSize: '1rem',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
    });

const ContactStep = ({
    classes,
    formData,
    handleChange,
    handleBlur,
    errors,
    touched,
}) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="title">
                            <People className={classes.headerIcon} />
                            Contact Information
                        </Typography>
                    }
                />
                <CardContent className={classes.content}>
                    <Typography variant="body1" className={classes.section}>
                        Provide contact information for this facility.
                    </Typography>

                    <Grid container spacing={16}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                required
                                name="contactEmail"
                                label="Contact Email"
                                type="email"
                                value={formData.contactEmail || ''}
                                onChange={e =>
                                    handleChange('contactEmail', e.target.value)
                                }
                                onBlur={handleBlur}
                                className={classes.field}
                                placeholder="contact@facility.com"
                                error={
                                    touched.contactEmail &&
                                    !!errors.contactEmail
                                }
                                helperText={
                                    touched.contactEmail && errors.contactEmail
                                }
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                name="contactPhone"
                                label="Contact Phone (Optional)"
                                value={formData.contactPhone || ''}
                                onChange={e =>
                                    handleChange('contactPhone', e.target.value)
                                }
                                className={classes.field}
                                placeholder="+1 (555) 123-4567"
                                error={
                                    touched.contactPhone &&
                                    !!errors.contactPhone
                                }
                                helperText={
                                    touched.contactPhone && errors.contactPhone
                                }
                            />
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Grid>
    </Grid>
);

ContactStep.defaultProps = {
    errors: {},
    touched: {},
};

ContactStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    handleBlur: func.isRequired,
    errors: object,
    touched: object,
};

// TODO: Retrieve user info from redux store and display it in
// the eligibility step. The data is already prefetched.

export default withStyles(contactStepStyles)(withScrollReset(ContactStep));
