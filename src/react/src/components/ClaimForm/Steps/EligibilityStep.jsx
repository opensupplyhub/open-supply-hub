import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Security from '@material-ui/icons/Security';

import COLOURS from '../../../util/COLOURS';

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
        checkboxLabel: Object.freeze({
            marginTop: theme.spacing.unit * 2,
            marginBottom: theme.spacing.unit * 2,
        }),
        description: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            color: COLOURS.DARK_GREY,
            fontSize: '0.875rem',
            lineHeight: 1.5,
        }),
    });

const EligibilityStep = ({ classes, formData, handleChange }) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="h6">
                            <Security className={classes.headerIcon} />
                            Eligibility Verification
                        </Typography>
                    }
                />
                <CardContent className={classes.content}>
                    <Typography variant="body1" className={classes.description}>
                        In order to submit a claim request, you must be an owner
                        or senior manager of the production location. By
                        proceeding, you confirm that you have the authority to
                        claim this facility.
                    </Typography>

                    <FormControlLabel
                        className={classes.checkboxLabel}
                        control={
                            <Checkbox
                                checked={formData.eligibilityConfirmed || false}
                                onChange={e =>
                                    handleChange(
                                        'eligibilityConfirmed',
                                        e.target.checked,
                                    )
                                }
                                color="primary"
                            />
                        }
                        label="I confirm that I am an owner or senior manager of this production location and have the authority to claim it"
                    />

                    <Typography variant="caption" color="textSecondary">
                        Note: False claims may result in account suspension. All
                        claims are subject to verification.
                    </Typography>
                </CardContent>
            </Card>
        </Grid>
    </Grid>
);

EligibilityStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
};

export default withStyles(eligibilityStepStyles)(EligibilityStep);
