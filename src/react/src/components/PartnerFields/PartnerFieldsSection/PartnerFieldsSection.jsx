import React from 'react';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import partnerFieldsSectionStyles from './styles';
import {
    preparePartnerFields,
    renderPartnerField,
    hasVisiblePartnerFields,
} from './utils.jsx';
import { pilotIntegrationsDocsRoute } from '../../../util/constants';

const PartnerFieldsSection = ({ classes, data }) => {
    const partnerFields = preparePartnerFields(data);

    if (!hasVisiblePartnerFields(partnerFields, data)) return null;

    const renderedPartnerFields = partnerFields.map(field =>
        renderPartnerField({ ...field, data }),
    );

    return (
        <div className={classes.root}>
            <div className={classes.contentContainer}>
                <Grid container>
                    <Grid item xs={12}>
                        <Typography className={classes.partnerFieldsTitle}>
                            New Pilot Data Integrations
                        </Typography>
                    </Grid>
                    <Grid item xs={12} className={classes.partnerFieldsLink}>
                        <a
                            href={pilotIntegrationsDocsRoute}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Learn More
                        </a>
                    </Grid>
                </Grid>
                <Grid container>{renderedPartnerFields}</Grid>
            </div>
        </div>
    );
};

export default withStyles(partnerFieldsSectionStyles)(PartnerFieldsSection);
