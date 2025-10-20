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

import COLOURS from '../../../util/COLOURS';

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

const BusinessStep = ({ classes, formData, handleChange, errors, touched }) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="h6">
                            <Language className={classes.headerIcon} />
                            Business Information
                        </Typography>
                    }
                />
                <CardContent className={classes.content}>
                    <div className={classes.section}>
                        <Typography
                            variant="subtitle1"
                            className={classes.sectionTitle}
                        >
                            Company Verification
                        </Typography>

                        <Grid container spacing={16}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Business Website"
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
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Company Address Verification Method"
                                    value={
                                        formData.companyAddressVerification ||
                                        ''
                                    }
                                    onChange={e =>
                                        handleChange(
                                            'companyAddressVerification',
                                            e.target.value,
                                        )
                                    }
                                    className={classes.field}
                                    placeholder="Select verification method"
                                    error={
                                        touched.companyAddressVerification &&
                                        !!errors.companyAddressVerification
                                    }
                                    helperText={
                                        touched.companyAddressVerification &&
                                        errors.companyAddressVerification
                                    }
                                />
                            </Grid>
                        </Grid>
                    </div>

                    <Typography variant="caption" color="textSecondary">
                        Note: This is placeholder content. Actual form fields
                        will be implemented in future tasks.
                    </Typography>
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

export default withStyles(businessStepStyles)(BusinessStep);
