import React, { useEffect, useRef, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { func, shape, string, bool } from 'prop-types';
import { Link } from 'react-router-dom';

import { userPropType } from '../util/propTypes';
import { getEmbeddedMapSrc, makeContributorEmbedConfigURL } from '../util/util';
import apiRequest from '../util/apiRequest';
import { EmbeddedMapInfoLink, USER_DEFAULT_STATE } from '../util/constants';

import EmbeddedMapFieldsConfig from './EmbeddedMapFieldsConfig';
import EmbeddedMapListOrderConfig from './EmbeddedMapListOrderConfig';
import EmbeddedMapThemeConfig from './EmbeddedMapThemeConfig';
import EmbeddedMapSizeConfig from './EmbeddedMapSizeConfig';
import EmbeddedMapCode from './EmbeddedMapCode';
import EmbeddedMapUnauthorized from './EmbeddedMapUnauthorized';

const styles = {
    page: {
        padding: '0 24px 120px',
    },
    intro: {
        maxWidth: '900px',
        marginBottom: '24px',
    },
    previewNote: {
        marginTop: '8px',
        color: 'rgba(0, 0, 0, 0.6)',
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
        width: '100%',
        overflow: 'hidden',
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

// The preview shows the map as a visitor sees it on a desktop screen: the
// filters, the list and the map side by side. The map only lays itself out
// that way when it is wide enough, so it is rendered at a desktop width and
// scaled down to fit the space beside the settings.
const PREVIEW_WIDTH = 1280;
const PREVIEW_HEIGHT = 780;

function EmbeddedMapPreview({ src }) {
    const frameRef = useRef(null);
    const [scale, setScale] = useState(0.5);

    useEffect(() => {
        const fit = () => {
            if (frameRef.current) {
                setScale(
                    Math.min(1, frameRef.current.offsetWidth / PREVIEW_WIDTH),
                );
            }
        };
        fit();
        window.addEventListener('resize', fit);
        return () => window.removeEventListener('resize', fit);
    }, []);

    return (
        <div
            ref={frameRef}
            style={{ ...styles.previewFrame, height: PREVIEW_HEIGHT * scale }}
        >
            <iframe
                src={src}
                frameBorder="0"
                title="embedded-map"
                style={{
                    width: `${PREVIEW_WIDTH}px`,
                    height: `${PREVIEW_HEIGHT}px`,
                    transform: `scale(${scale})`,
                    transformOrigin: '0 0',
                }}
            />
        </div>
    );
}

EmbeddedMapPreview.propTypes = {
    src: string.isRequired,
};

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
        markerColor,
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
        <div style={styles.page}>
            <div style={styles.intro}>
                <Typography paragraph>
                    Generate a customized OS Hub Embedded Map for your website.
                </Typography>
                <Typography paragraph>
                    To begin,{' '}
                    <Link to="/contribute" className="inline-link">
                        upload your supplier data
                    </Link>{' '}
                    (via upload or API) to OS Hub with all of the data fields
                    you wish to have displayed on your map using the template
                    supplied to you by the OS Hub Team.{' '}
                    <strong>
                        This list must include any additional data points you
                        would like to display on your customized map, such as
                        facility type, number of workers etc.
                    </strong>{' '}
                    The Embedded Map will display all facilities included in
                    your lists.
                </Typography>
                <Typography paragraph>
                    Adjust the below settings to your liking, such as the map
                    color and size. Once complete, copy the Embed Code to add to
                    your website.
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
                    <a
                        href="mailto:info@opensupplyhub.org"
                        className="inline-link"
                    >
                        info@opensupplyhub.org
                    </a>
                    .
                </Typography>
            </div>
            <Grid container spacing={40}>
                <Grid item xs={12} md={5} lg={4}>
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
                            markerColor={markerColor}
                            setMarkerColor={updateEmbedConfig('markerColor')}
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
                <Grid item xs={12} md={7} lg={8}>
                    <div style={styles.preview}>
                        <Typography style={styles.previewHeader}>
                            Preview
                        </Typography>
                        {minimumConfigurationIsComplete ? (
                            <>
                                <EmbeddedMapPreview
                                    src={getEmbeddedMapSrc(mapSettings)}
                                />
                                <Typography style={styles.previewNote}>
                                    Shown as on a desktop screen, scaled to fit.
                                    The size you choose under Size and embed
                                    code applies on your own website.
                                </Typography>
                            </>
                        ) : (
                            <Typography paragraph>
                                Choose a color and enter a width and height to
                                see a preview.
                            </Typography>
                        )}
                    </div>
                </Grid>
            </Grid>
        </div>
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
