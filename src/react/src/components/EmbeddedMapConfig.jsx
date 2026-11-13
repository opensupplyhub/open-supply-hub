import React, { useEffect, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { func, shape, string, bool } from 'prop-types';
import { Link } from 'react-router-dom';

import { userPropType } from '../util/propTypes';
import { getEmbeddedMapSrc, makeContributorEmbedConfigURL } from '../util/util';
import apiRequest from '../util/apiRequest';
import {
    EmbeddedMapInfoLink,
    minimum100PercentWidthEmbedHeight,
    USER_DEFAULT_STATE,
} from '../util/constants';

import AppGrid from './AppGrid';
import EmbeddedMapFieldsConfig from './EmbeddedMapFieldsConfig';
import EmbeddedMapListOrderConfig from './EmbeddedMapListOrderConfig';
import EmbeddedMapThemeConfig from './EmbeddedMapThemeConfig';
import EmbeddedMapSizeConfig from './EmbeddedMapSizeConfig';
import EmbeddedMapCode from './EmbeddedMapCode';
import EmbeddedMapUnauthorized from './EmbeddedMapUnauthorized';

const styles = {
    container: {
        marginBottom: '200px',
    },
    section: {
        marginTop: '40px',
    },
    previewHeader: {
        marginBottom: '20px',
        color: 'rgb(0, 0, 0)',
        fontSize: '24px',
    },
    code: {
        marginTop: '30px',
    },
    nav: {
        display: 'flex',
        flexWrap: 'wrap',
        borderBottom: '1px solid rgb(214, 216, 221)',
    },
    navButton: {
        border: 0,
        borderBottom: '3px solid transparent',
        background: 'none',
        padding: '10px 16px',
        marginBottom: '-1px',
        fontFamily: 'inherit',
        fontSize: '16px',
        fontWeight: 700,
        color: 'rgba(0, 0, 0, 0.55)',
        cursor: 'pointer',
    },
    navButtonActive: {
        color: 'rgb(0, 0, 0)',
        borderBottomColor: 'rgb(0, 0, 0)',
    },
    preview: {
        position: 'sticky',
        top: '20px',
    },
    previewFrame: {
        overflow: 'auto',
        border: '1px solid rgb(214, 216, 221)',
    },
};

// The settings are split into sections, shown one at a time beside the
// preview, so a change can be seen without scrolling past the other settings.
const SECTIONS = [
    { id: 'style', label: 'Style' },
    { id: 'fields', label: 'Fields' },
    { id: 'code', label: 'Size and embed code' },
];

// This must be kept in sync with createIFrameHTML in util.js
// We use a separate function to avoid using dangerouslySetInnerHTML
const renderEmbeddedMap = ({ fullWidth, mapSettings, height, width }) =>
    fullWidth ? (
        <div>
            <style>
                {`\
                #oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48 {\
                    position: relative;\
                    padding-top: ${height}%;\
                }\
                @media (max-width: 600px) { /* mobile breakpoint */\
                    #oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48 {\
                        padding-top: ${minimum100PercentWidthEmbedHeight}\
                    }\
                }`}
            </style>
            <div id="oar-embed-0d4dc3a7-e3cd-4acc-88f0-422f5aeefa48">
                <iframe
                    src={getEmbeddedMapSrc(mapSettings)}
                    frameBorder="0"
                    allowFullScreen
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                    }}
                    title="embedded-map"
                />
            </div>
        </div>
    ) : (
        <iframe
            src={getEmbeddedMapSrc(mapSettings)}
            frameBorder="0"
            style={{
                width: `${width}px`,
                height: `${height}px`,
            }}
            title="embedded-map"
        />
    );

function EmbeddedMapConfig({
    user,
    embedConfig: {
        color,
        font,
        width,
        fullWidth,
        textSearchLabel,
        height,
        preferContributorName,
        hideSectorData,
        mapStyle,
        accentColor,
        headingFont,
        cornerRadius,
        colorByField,
        colorByColors,
        defaultSort,
        allowVisitorSort,
    },
    setEmbedConfig,
    fields,
    setFields,
    errors,
    timestamp,
}) {
    const [section, setSection] = useState(SECTIONS[0].id);

    // The values of the field the markers are colored by come from the saved
    // config, so they are fetched again after each save (`timestamp`).
    const [colorByOptions, setColorByOptions] = useState([]);
    const contributorId = user?.contributor_id;
    useEffect(() => {
        if (!colorByField || !contributorId) {
            setColorByOptions([]);
            return;
        }
        apiRequest
            .get(makeContributorEmbedConfigURL(contributorId))
            .then(({ data }) => {
                if (data.color_by_field === colorByField) {
                    setColorByOptions(data.color_by_options || []);
                }
            })
            .catch(() => setColorByOptions([]));
    }, [colorByField, contributorId, timestamp]);

    if (!user.embed_level) return <EmbeddedMapUnauthorized isSettings />;

    const updateEmbedConfig = field => value =>
        setEmbedConfig(config => ({
            ...config,
            [field]: value,
        }));

    const minimumConfigurationIsComplete = !!(width && height && color);

    const mapSettings = {
        width,
        height,
        fullWidth,
        contributor: [user?.contributor_id],
        timestamp,
        minimumConfigurationIsComplete,
    };

    return (
        <AppGrid style={styles.container} title="">
            <Typography paragraph>
                Generate a customized OS Hub Embedded Map for your website.
            </Typography>
            <Typography paragraph>
                To begin,{' '}
                <Link to="/contribute" className="inline-link">
                    upload your supplier data
                </Link>{' '}
                (via upload or API) to OS Hub with all of the data fields you
                wish to have displayed on your map using the template supplied
                to you by the OS Hub Team.{' '}
                <strong>
                    This list must include any additional data points you would
                    like to display on your customized map, such as facility
                    type, number of workers etc.
                </strong>{' '}
                The Embedded Map will display all facilities included in your
                lists.
            </Typography>
            <Typography paragraph>
                Adjust the below settings to your liking, such as the map color
                and size. Once complete, copy the Embed Code to add to your
                website.
            </Typography>
            <Typography paragraph style={{ width: '100%' }}>
                <strong>Have questions?</strong> Check out the FAQs on our{' '}
                <a
                    href={EmbeddedMapInfoLink}
                    className="inline-link"
                    target="_blank"
                    rel="noreferrer"
                >
                    Embedded Map info page
                </a>{' '}
                or email{' '}
                <a href="mailto:info@opensupplyhub.org" className="inline-link">
                    info@opensupplyhub.org
                </a>
                .
            </Typography>
            <Grid container spacing={40}>
                <Grid item xs={12} md={6} lg={5}>
                    <div style={styles.nav} role="tablist">
                        {SECTIONS.map(({ id, label }) => (
                            <button
                                key={id}
                                type="button"
                                role="tab"
                                aria-selected={section === id}
                                onClick={() => setSection(id)}
                                style={
                                    section === id
                                        ? {
                                              ...styles.navButton,
                                              ...styles.navButtonActive,
                                          }
                                        : styles.navButton
                                }
                            >
                                {label}
                            </button>
                        ))}
                    </div>
                    {section === 'style' ? (
                        <EmbeddedMapThemeConfig
                            color={color}
                            setColor={updateEmbedConfig('color')}
                            font={font}
                            setFont={updateEmbedConfig('font')}
                            mapStyle={mapStyle}
                            setMapStyle={updateEmbedConfig('mapStyle')}
                            accentColor={accentColor}
                            setAccentColor={updateEmbedConfig('accentColor')}
                            headingFont={headingFont}
                            setHeadingFont={updateEmbedConfig('headingFont')}
                            cornerRadius={cornerRadius}
                            setCornerRadius={updateEmbedConfig('cornerRadius')}
                            fields={fields}
                            colorByField={colorByField}
                            colorByColors={colorByColors}
                            colorByOptions={colorByOptions}
                            setColorBy={({ field, colors }) =>
                                setEmbedConfig(config => ({
                                    ...config,
                                    colorByField: field,
                                    colorByColors: colors,
                                }))
                            }
                            errors={errors}
                            embedLevel={user.embed_level}
                        />
                    ) : null}
                    {section === 'fields' ? (
                        <EmbeddedMapListOrderConfig
                            fields={fields}
                            defaultSort={defaultSort}
                            setDefaultSort={updateEmbedConfig('defaultSort')}
                            allowVisitorSort={allowVisitorSort}
                            setAllowVisitorSort={updateEmbedConfig(
                                'allowVisitorSort',
                            )}
                            errors={errors}
                        />
                    ) : null}
                    {section === 'fields' ? (
                        <EmbeddedMapFieldsConfig
                            fields={fields}
                            setFields={setFields}
                            preferContributorName={preferContributorName}
                            setPreferContributorName={updateEmbedConfig(
                                'preferContributorName',
                            )}
                            hideSectorData={hideSectorData}
                            setShowSectorData={updateEmbedConfig(
                                'hideSectorData',
                            )}
                            textSearchLabel={textSearchLabel}
                            setTextSearchLabel={updateEmbedConfig(
                                'textSearchLabel',
                            )}
                            anyFieldSearchable={fields.some(
                                field => field.searchable,
                            )}
                            errors={errors}
                            userEmbedLevel={user.embed_level}
                        />
                    ) : null}
                    {section === 'code' ? (
                        <>
                            <EmbeddedMapSizeConfig
                                width={width}
                                setWidth={updateEmbedConfig('width')}
                                height={height}
                                setHeight={updateEmbedConfig('height')}
                                fullWidth={fullWidth}
                                setFullWidth={updateEmbedConfig('fullWidth')}
                            />
                            <div style={styles.code}>
                                <EmbeddedMapCode {...mapSettings} />
                            </div>
                        </>
                    ) : null}
                </Grid>
                <Grid item xs={12} md={6} lg={7}>
                    <div style={styles.preview}>
                        <Typography style={styles.previewHeader}>
                            Preview
                        </Typography>
                        {minimumConfigurationIsComplete ? (
                            <div style={styles.previewFrame}>
                                {renderEmbeddedMap({
                                    fullWidth,
                                    mapSettings,
                                    height,
                                    width,
                                })}
                            </div>
                        ) : (
                            <Typography paragraph>
                                Choose a color and enter a width and height to
                                see a preview.
                            </Typography>
                        )}
                    </div>
                </Grid>
            </Grid>
        </AppGrid>
    );
}

EmbeddedMapConfig.defaultProps = {
    user: USER_DEFAULT_STATE,
};

EmbeddedMapConfig.propTypes = {
    user: userPropType,
    embedConfig: shape({
        color: string.isRequired,
        font: string.isRequired,
        width: string.isRequired,
        height: string.isRequired,
        fullWidth: bool.isRequired,
        textSearchLabel: string.isRequired,
        mapStyle: string.isRequired,
    }).isRequired,
    setEmbedConfig: func.isRequired,
    setFields: func.isRequired,
};

export default EmbeddedMapConfig;
