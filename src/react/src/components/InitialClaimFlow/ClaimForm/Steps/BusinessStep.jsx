import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import Language from '@material-ui/icons/Language';

import COLOURS from '../../../../util/COLOURS';
import withScrollReset from '../../HOCs/withScrollReset';

const businessStepStyles = theme =>
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

const BusinessStep = ({
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
                            <Language className={classes.headerIcon} />
                            Business Details
                        </Typography>
                    }
                />
                <CardContent className={classes.content}>
                    <Typography variant="body1" className={classes.section}>
                        Provide basic business information.
                    </Typography>

                    <Grid container spacing={16}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                required
                                name="businessName"
                                label="Business Name"
                                value={formData.businessName || ''}
                                onChange={e =>
                                    handleChange('businessName', e.target.value)
                                }
                                onBlur={handleBlur}
                                className={classes.field}
                                placeholder="Company or facility name"
                                error={
                                    touched.businessName &&
                                    !!errors.businessName
                                }
                                helperText={
                                    touched.businessName && errors.businessName
                                }
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                name="businessWebsite"
                                label="Business Website (Optional)"
                                value={formData.businessWebsite || ''}
                                onChange={e =>
                                    handleChange(
                                        'businessWebsite',
                                        e.target.value,
                                    )
                                }
                                className={classes.field}
                                placeholder="https://company.com"
                                error={
                                    touched.businessWebsite &&
                                    !!errors.businessWebsite
                                }
                                helperText={
                                    touched.businessWebsite &&
                                    errors.businessWebsite
                                }
                            />
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Grid>
    </Grid>
);

BusinessStep.defaultProps = {
    errors: {},
    touched: {},
};

BusinessStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    errors: object,
    touched: object,
};

// TODO: Retrieve location info from redux store and display it in
// the business step. See how it is done in the
// ProductionLocationInfo component. The data is already prefetched
// in the ClaimForm component.

export default withStyles(businessStepStyles)(withScrollReset(BusinessStep));
