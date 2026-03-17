import React from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import { pluralizeContributorType } from '../../utils';
import typeSummarySectionStyles from './styles';

const TypeSummarySection = ({ classes, typeCounts }) => (
    <Grid container className={classes.typeSummary}>
        {typeCounts.map(({ type, count }) => (
            <Typography key={type} className={classes.typeChip} component="p">
                <strong>{count}</strong> {pluralizeContributorType(type, count)}
            </Typography>
        ))}
    </Grid>
);

export default withStyles(typeSummarySectionStyles)(TypeSummarySection);
