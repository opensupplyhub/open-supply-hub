import React from 'react';
import { object } from 'prop-types';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';

import EmbedFieldValue from './EmbedFieldValue';
import generalFieldsStyles from './ProductionLocation/ProductionLocationDetailsGeneralFields/styles';
import { getEmbedLocationFields } from '../util/embeddedMap';

const explanationStyles = Object.freeze({
    description: Object.freeze({
        marginTop: '4px',
        fontSize: '14px',
        color: 'rgba(0, 0, 0, 0.65)',
    }),
    list: Object.freeze({
        margin: '8px 0 0',
        padding: '8px 12px',
        background: 'rgba(0, 0, 0, 0.03)',
    }),
    item: Object.freeze({
        padding: '4px 0',
        fontSize: '14px',
    }),
    term: Object.freeze({
        fontWeight: 700,
    }),
    text: Object.freeze({
        margin: 0,
        color: 'rgba(0, 0, 0, 0.75)',
    }),
});

/*
The contributor's own fields for a location, on their embedded map: the
fields they chose to show, as text, tags or a blurb, in a card that matches
the others on the location page. Renders nothing when the location has no
value for any of them.
*/
function EmbedLocationFields({ classes, data, embedConfig, theme }) {
    const fields = getEmbedLocationFields(embedConfig, data);
    if (!fields.length) return null;
    // The explanations are set in the map's own font, like the values.
    const fontFamily = theme?.typography?.fontFamily;

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
                    {fields.map(
                        ({
                            columnName,
                            label,
                            value,
                            displayAs,
                            description,
                            explanations,
                        }) => (
                            <Grid
                                item
                                xs={12}
                                md={
                                    displayAs === 'blurb' ||
                                    description ||
                                    explanations.length
                                        ? 12
                                        : 6
                                }
                                key={columnName}
                            >
                                <EmbedFieldValue
                                    label={label}
                                    value={value}
                                    displayAs={displayAs}
                                />
                                {/* The contributor's own explanations of
                                    the field and of its values here. */}
                                {description ? (
                                    <div
                                        style={{
                                            ...explanationStyles.description,
                                            fontFamily,
                                        }}
                                        data-testid="embed-field-description"
                                    >
                                        {description}
                                    </div>
                                ) : null}
                                {explanations.length ? (
                                    <dl
                                        style={{
                                            ...explanationStyles.list,
                                            fontFamily,
                                        }}
                                        data-testid="embed-field-explanations"
                                    >
                                        {explanations.map(item => (
                                            <div
                                                key={item.value}
                                                style={explanationStyles.item}
                                            >
                                                <dt
                                                    style={
                                                        explanationStyles.term
                                                    }
                                                >
                                                    {item.value}
                                                </dt>
                                                <dd
                                                    style={
                                                        explanationStyles.text
                                                    }
                                                >
                                                    {item.text}
                                                </dd>
                                            </div>
                                        ))}
                                    </dl>
                                ) : null}
                            </Grid>
                        ),
                    )}
                </Grid>
            </Grid>
        </Grid>
    );
}

EmbedLocationFields.propTypes = {
    classes: object.isRequired,
    data: object,
    embedConfig: object,
    theme: object,
};

EmbedLocationFields.defaultProps = {
    data: null,
    embedConfig: null,
    theme: null,
};

export default withStyles(generalFieldsStyles, { withTheme: true })(
    EmbedLocationFields,
);
