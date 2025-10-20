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

import COLOURS from '../../../util/COLOURS';

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

const ContactStep = ({ classes, formData, handleChange, errors, touched }) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="h6">
                            <People className={classes.headerIcon} />
                            Contact Information
                        </Typography>
                    }
                />
                <CardContent className={classes.content}>
                    <div className={classes.section}>
                        <Typography
                            variant="subtitle1"
                            className={classes.sectionTitle}
                        >
                            Your Information (Claimant)
                        </Typography>

                        <Grid container spacing={16}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Your Name"
                                    value={formData.claimantName || ''}
                                    onChange={e =>
                                        handleChange(
                                            'claimantName',
                                            e.target.value,
                                        )
                                    }
                                    className={classes.field}
                                    placeholder="Enter your full name"
                                    error={
                                        touched.claimantName &&
                                        !!errors.claimantName
                                    }
                                    helperText={
                                        touched.claimantName &&
                                        errors.claimantName
                                    }
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    fullWidth
                                    label="Your Job Title"
                                    value={formData.claimantTitle || ''}
                                    onChange={e =>
                                        handleChange(
                                            'claimantTitle',
                                            e.target.value,
                                        )
                                    }
                                    className={classes.field}
                                    placeholder="e.g., Plant Manager, Safety Director"
                                    error={
                                        touched.claimantTitle &&
                                        !!errors.claimantTitle
                                    }
                                    helperText={
                                        touched.claimantTitle &&
                                        errors.claimantTitle
                                    }
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Your Email"
                                    type="email"
                                    value={formData.claimantEmail || ''}
                                    onChange={e =>
                                        handleChange(
                                            'claimantEmail',
                                            e.target.value,
                                        )
                                    }
                                    className={classes.field}
                                    placeholder="your.email@company.com"
                                    error={
                                        touched.claimantEmail &&
                                        !!errors.claimantEmail
                                    }
                                    helperText={
                                        touched.claimantEmail &&
                                        errors.claimantEmail
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

ContactStep.defaultProps = {
    errors: {},
    touched: {},
};

ContactStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
    errors: object,
    touched: object,
};

export default withStyles(contactStepStyles)(ContactStep);
