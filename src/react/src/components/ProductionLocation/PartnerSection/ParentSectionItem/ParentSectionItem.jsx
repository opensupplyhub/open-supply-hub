import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import InfoIcon from '@material-ui/icons/Info';
import DialogTooltip from '../../../../components/Contribute/DialogTooltip';

import parentSectionItemStyles from './styles';

const ParentSectionItem = ({ classes, title, tooltipText, disclaimer }) => (
    <div className={classes.container}>
        <Grid container>
            <Typography
                variant="title"
                className={classes.title}
                component="h3"
            >
                {title}
            </Typography>
            <DialogTooltip text={tooltipText} childComponent={<InfoIcon />} />
            <Switch
                color="primary"
                onChange={() => {}}
                checked={false}
                className={classes.switchWrapper}
            />
        </Grid>
        <Typography
            variant="subheading"
            className={classes.title}
            component="h3"
        >
            {disclaimer}
        </Typography>
    </div>
);

export default withStyles(parentSectionItemStyles)(ParentSectionItem);
