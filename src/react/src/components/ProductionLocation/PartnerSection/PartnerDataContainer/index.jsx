import React from 'react';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import ParentSectionItem from '../ParentSectionItem';

import styles from './styles';

function PartnerDataContainer({ classes }) {
    return (
        <Grid container className={classes.root}>
            <Grid item md={12}>
                <Typography
                    variant="title"
                    className={classes.title}
                    component="h3"
                >
                    Partner Data
                </Typography>
            </Grid>
            <Grid item md={12}>
                <Typography variant="subheading" component="h3">
                    Data provided by third-party integration partners. Use our
                    API to access this data programmatically.
                </Typography>
            </Grid>
            <Grid item md={12}>
                <ParentSectionItem
                    title="Assessments and Audits"
                    tooltipText="(from BE) Assessments provide standardized evaluations of production location practices, helping brands verify compliance and identify areas for improvement."
                    disclaimer="Disclaimer (from BE): Assessment data is provided by third parties and may not reflect current conditions. Always verify critical information independently."
                />
            </Grid>
            <Grid item md={12}>
                <ParentSectionItem
                    title="Certifications"
                    tooltipText="(from BE) Certifications provide third-party verification that production locations meet recognized standards for quality, environmental, and social responsibility."
                    disclaimer="Disclaimer (from BE): Certification status may change. Always verify validity dates and check directly with certifying bodies for the most current information."
                />
            </Grid>
            <Grid item md={12}>
                <ParentSectionItem
                    title="Emissions"
                    tooltipText="(from BE) Environmental metrics help brands assess and reduce the ecological footprint of their supply chains by tracking emissions, resource usage, and waste."
                    disclaimer="Disclaimer (from BE): Environmental data is often self-reported or estimated. Methodologies may vary between sources and should be considered indicative rather than absolute."
                />
            </Grid>
            <Grid item md={12}>
                <ParentSectionItem
                    title="Living Wage"
                    tooltipText="(from BE) Living wage data helps assess whether workers earn enough to meet basic needs, supporting fair compensation practices across supply chains."
                    disclaimer="Disclaimer (from BE): Wage benchmarks are estimates based on regional data and may not reflect actual wages paid at this facility."
                />
            </Grid>
            <Grid item md={12}>
                <ParentSectionItem
                    title="Grievance Mechanism Placeholder Title"
                    tooltipText="(from BE) Grievance mechanisms allow workers to report concerns anonymously. These integrations show which third-party platforms are active at this facility."
                    disclaimer="Disclaimer (from BE): Open Supply Hub does not operate a grievance mechanism and cannot receive or investigate complaints. Information shown is based on partner-submitted sources and may not reflect all available mechanisms, including government or state-based processes. Open Supply Hub does not verify the effectiveness, accessibility, or outcomes of any listed mechanism."
                />
            </Grid>
        </Grid>
    );
}

export default withStyles(styles)(PartnerDataContainer);
