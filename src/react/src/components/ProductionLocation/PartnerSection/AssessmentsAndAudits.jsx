import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

const assessmentsAndAuditsStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
    });

const AssessmentsAndAudits = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Assessments and Audits
        </Typography>
    </div>
);

export default withStyles(assessmentsAndAuditsStyles)(
    AssessmentsAndAudits,
);
