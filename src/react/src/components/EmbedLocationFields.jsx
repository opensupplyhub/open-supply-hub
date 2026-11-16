import React from 'react';
import { object } from 'prop-types';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';

import EmbedFieldValue from './EmbedFieldValue';
import generalFieldsStyles from './ProductionLocation/ProductionLocationDetailsGeneralFields/styles';
import { getEmbedLocationFields } from '../util/embeddedMap';

/*
The contributor's own fields for a location, on their embedded map: the
fields they chose to show, as text, tags or a blurb, in a card that matches
the others on the location page. Renders nothing when the location has no
value for any of them.
*/
function EmbedLocationFields({ classes, data, embedConfig }) {
    const fields = getEmbedLocationFields(embedConfig, data);
    if (!fields.length) return null;

    return (
        <Grid
            container
            className={classes.container}
            style={{ marginBottom: '16px' }}
            data-testid="embed-location-fields"
        >
            <Grid item container xs={12} className={classes.titleRow}>
                <Typography
                    variant="title"
                    className={classes.title}
                    component="h3"
                >
                    {embedConfig.contributor_name
                        ? `From ${embedConfig.contributor_name}`
                        : 'More about this location'}
                </Typography>
            </Grid>
            <Divider className={classes.divider} />
            <Grid item xs={12} className={classes.dataList}>
                <Grid container spacing={16}>
                    {fields.map(({ columnName, label, value, displayAs }) => (
                        <Grid
                            item
                            xs={12}
                            md={displayAs === 'blurb' ? 12 : 6}
                            key={columnName}
                        >
                            <EmbedFieldValue
                                label={label}
                                value={value}
                                displayAs={displayAs}
                            />
                        </Grid>
                    ))}
                </Grid>
            </Grid>
        </Grid>
    );
}

EmbedLocationFields.propTypes = {
    classes: object.isRequired,
    data: object,
    embedConfig: object,
};

EmbedLocationFields.defaultProps = {
    data: null,
    embedConfig: null,
};

export default withStyles(generalFieldsStyles)(EmbedLocationFields);
