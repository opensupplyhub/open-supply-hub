import React from 'react';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import Button from '@material-ui/core/Button';
import Radio from '@material-ui/core/Radio';
import Typography from '@material-ui/core/Typography';
import Select from 'react-select';

import { arrayOf, func, number, object, oneOfType, string } from 'prop-types';

import { OARFont, OARColor } from '../util/constants';
import { getColorByLegend } from '../util/embeddedMap';

const styles = {
    section: {
        marginTop: '30px',
    },
    sectionHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '24px',
        margin: '10px 0',
    },
    subsection: {
        marginTop: '20px',
    },
    subsectionHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '15px',
        fontWeight: 'bold',
        margin: '10px 0',
    },
    colorContainer: {
        display: 'flex',
        marginTop: '10px',
        alignItems: 'center',
    },
    radios: {
        display: 'flex',
        flexDirection: 'row',
    },
    radioItem: {
        marginRight: '30px',
    },
    radio: {
        color: 'rgb(0, 0, 0)',
    },
    colorBySelect: {
        marginTop: '10px',
        padding: '8px',
        width: '100%',
        fontSize: '14px',
    },
    colorByNote: {
        marginTop: '10px',
        color: 'rgba(0, 0, 0, 0.6)',
    },
};

const fontOptions = [
    { label: 'OS Hub Website Font', value: OARFont },
    { label: 'Arial', value: 'Arial,Helvetica,sans-serif' },
    { label: 'Tahoma', value: 'Tahoma,Verdana,sans-serif' },
    { label: 'Trebuchet MS', value: '"Trebuchet MS",Helvetica,sans-serif' },
    { label: 'Times New Roman', value: '"Times New Roman",Times,serif' },
    { label: 'Georgia', value: 'Georgia,serif' },
    { label: 'Garamond', value: 'Garamond,serif' },
    { label: 'Courier New', value: '"Courier New",Courier,monospace' },
    { label: 'Brush Script', value: 'Brush Script,cursive' },
    { label: 'Copperplate', value: 'Copperplate,Papyrus,fantasy' },
];

// '' is "not set": headings then use the body font.
const headingFontOptions = [
    { label: 'Same as body font', value: '' },
    ...fontOptions,
];

// '' is "not set": each element keeps its own corner style.
export const cornerStyleOptions = [
    { label: 'Default', value: '' },
    { label: 'Square', value: 0 },
    { label: 'Slightly rounded', value: 4 },
    { label: 'Rounded', value: 8 },
];

const fontSelectStyles = {
    option: (provided, { data }) => ({
        ...provided,
        fontFamily: data.value,
    }),
    control: provided => ({
        ...provided,
        marginTop: '10px',
    }),
};

function EmbeddedMapThemeConfig({
    color,
    setColor,
    font,
    setFont,
    errors,
    embedLevel,
    mapStyle,
    setMapStyle,
    accentColor,
    setAccentColor,
    headingFont,
    setHeadingFont,
    cornerRadius,
    setCornerRadius,
    fields,
    colorByField,
    setColorBy,
    colorByColors,
    colorByOptions,
    markerColor,
    setMarkerColor,
}) {
    const colorLegend = getColorByLegend(colorByOptions, colorByColors);
    const colorFields = fields.filter(f => f.visible && f.hasData !== false);
    const value = fontOptions.find(f => font === f.value) || OARFont;
    const headingFontValue =
        headingFontOptions.find(f => headingFont === f.value) ||
        headingFontOptions[0];
    return (
        <div style={styles.section}>
            <Typography style={styles.sectionHeader}>Theme</Typography>
            <Typography>
                Availability of theme customization will depend on your Embedded
                Map package.{' '}
            </Typography>
            <div style={styles.subsection}>
                <Typography style={styles.subsectionHeader}>Color</Typography>
                {embedLevel === 1 ? (
                    <>
                        <Typography>
                            Choose the primary color for the embedded map.
                        </Typography>
                        <FormControl style={styles.radios}>
                            <FormControlLabel
                                value="#00000"
                                label="Black"
                                style={styles.radioItem}
                                control={
                                    <Radio
                                        checked={color === '#000000'}
                                        onChange={e => setColor(e.target.value)}
                                        value="#000000"
                                        name="theme-color"
                                        inputProps={{ 'aria-label': 'Black' }}
                                        style={styles.radio}
                                    />
                                }
                            />
                            <FormControlLabel
                                value={OARColor}
                                label="OS Hub Green"
                                style={styles.radioItem}
                                control={
                                    <Radio
                                        checked={color === OARColor}
                                        onChange={e => setColor(e.target.value)}
                                        value={OARColor}
                                        name="theme-color"
                                        inputProps={{
                                            'aria-label': 'OS Hub Green',
                                        }}
                                        style={styles.radio}
                                    />
                                }
                            />
                        </FormControl>
                    </>
                ) : (
                    <>
                        <Typography>
                            Use a color with sufficient contrast against white
                            backgrounds & labels.
                        </Typography>
                        {errors?.color && (
                            <Typography style={{ color: 'red' }}>
                                Error: {errors.color.join(', ')}
                            </Typography>
                        )}
                        <div style={styles.colorContainer}>
                            <input
                                type="color"
                                value={color}
                                onChange={e => setColor(e.target.value)}
                                style={{ marginRight: '10px' }}
                            />
                            <Typography>{color}</Typography>
                        </div>
                    </>
                )}
            </div>
            {embedLevel === 3 ? (
                <div style={styles.subsection}>
                    <Typography style={styles.subsectionHeader}>
                        Font
                    </Typography>
                    <Typography>
                        If no font is selected, the OS Hub font will be used.
                    </Typography>
                    {errors?.font && (
                        <Typography style={{ color: 'red' }}>
                            Error: {errors.font.join(', ')}
                        </Typography>
                    )}
                    <Select
                        styles={fontSelectStyles}
                        options={fontOptions}
                        id="font"
                        value={value}
                        onChange={item => setFont(item.value)}
                        placeholder="Select a font"
                    />
                </div>
            ) : null}
            {embedLevel === 3 ? (
                <>
                    <div style={styles.subsection}>
                        <Typography style={styles.subsectionHeader}>
                            Accent Color
                        </Typography>
                        <Typography>
                            If no accent color is chosen, the primary color will
                            be used.
                        </Typography>
                        {errors?.accent_color && (
                            <Typography style={{ color: 'red' }}>
                                Error: {errors.accent_color.join(', ')}
                            </Typography>
                        )}
                        <div style={styles.colorContainer}>
                            <input
                                type="color"
                                aria-label="Accent color"
                                value={accentColor || color}
                                onChange={e => setAccentColor(e.target.value)}
                                style={{ marginRight: '10px' }}
                            />
                            <Typography>
                                {accentColor || 'Same as primary color'}
                            </Typography>
                            {accentColor ? (
                                <Button
                                    onClick={() => setAccentColor('')}
                                    style={{ marginLeft: '10px' }}
                                >
                                    Use primary color
                                </Button>
                            ) : null}
                        </div>
                    </div>
                    <div style={styles.subsection}>
                        <Typography style={styles.subsectionHeader}>
                            Heading Font
                        </Typography>
                        <Typography>
                            If no heading font is selected, headings will use
                            the same font as the rest of the map.
                        </Typography>
                        {errors?.heading_font && (
                            <Typography style={{ color: 'red' }}>
                                Error: {errors.heading_font.join(', ')}
                            </Typography>
                        )}
                        <Select
                            styles={fontSelectStyles}
                            options={headingFontOptions}
                            id="heading-font"
                            value={headingFontValue}
                            onChange={item => setHeadingFont(item.value)}
                            placeholder="Select a heading font"
                        />
                    </div>
                    <div style={styles.subsection}>
                        <Typography style={styles.subsectionHeader}>
                            Corner Style
                        </Typography>
                        <Typography>
                            Choose how rounded buttons and inputs are.
                        </Typography>
                        {errors?.corner_radius && (
                            <Typography style={{ color: 'red' }}>
                                Error: {errors.corner_radius.join(', ')}
                            </Typography>
                        )}
                        <FormControl style={styles.radios}>
                            {cornerStyleOptions.map(option => (
                                <FormControlLabel
                                    key={option.label}
                                    value={String(option.value)}
                                    label={option.label}
                                    style={styles.radioItem}
                                    control={
                                        <Radio
                                            checked={
                                                String(cornerRadius) ===
                                                String(option.value)
                                            }
                                            onChange={() =>
                                                setCornerRadius(option.value)
                                            }
                                            value={String(option.value)}
                                            name="corner-style"
                                            inputProps={{
                                                'aria-label': option.label,
                                            }}
                                            style={styles.radio}
                                        />
                                    }
                                />
                            ))}
                        </FormControl>
                    </div>
                </>
            ) : null}
            {embedLevel === 3 ? (
                <div style={styles.subsection}>
                    <Typography style={styles.subsectionHeader}>
                        Marker Colors
                    </Typography>
                    <Typography>
                        Choose one color for every location&apos;s marker, or
                        color each marker by one of the fields you show, such as
                        a tier.
                    </Typography>
                    {errors?.color_by_colors && (
                        <Typography style={{ color: 'red' }}>
                            Error: {errors.color_by_colors.join(', ')}
                        </Typography>
                    )}
                    <select
                        aria-label="Color markers by"
                        value={colorByField}
                        onChange={e =>
                            setColorBy({ field: e.target.value, colors: {} })
                        }
                        style={styles.colorBySelect}
                    >
                        <option value="">One color for all locations</option>
                        {colorFields.map(f => (
                            <option key={f.columnName} value={f.columnName}>
                                {f.displayName}
                            </option>
                        ))}
                    </select>
                    {!colorByField ? (
                        <div style={styles.colorContainer}>
                            <input
                                type="color"
                                aria-label="Marker color"
                                value={markerColor || color}
                                onChange={e => setMarkerColor(e.target.value)}
                                style={{ marginRight: '10px' }}
                            />
                            <Typography>
                                {markerColor || 'Same as primary color'}
                            </Typography>
                            {markerColor ? (
                                <Button
                                    onClick={() => setMarkerColor('')}
                                    style={{ marginLeft: '10px' }}
                                >
                                    Use primary color
                                </Button>
                            ) : null}
                        </div>
                    ) : null}
                    {colorByField && colorLegend.length === 0 ? (
                        <Typography style={styles.colorByNote}>
                            The values of this field will be listed here once
                            your choice is saved.
                        </Typography>
                    ) : null}
                    {colorLegend.map(entry => (
                        <div key={entry.value} style={styles.colorContainer}>
                            <input
                                type="color"
                                aria-label={`Color for ${entry.value}`}
                                value={entry.color}
                                onChange={e =>
                                    setColorBy({
                                        field: colorByField,
                                        colors: {
                                            ...colorByColors,
                                            [entry.value]: e.target.value,
                                        },
                                    })
                                }
                                style={{ marginRight: '10px' }}
                            />
                            <Typography>
                                {entry.value} ({entry.count}{' '}
                                {entry.count === 1 ? 'location' : 'locations'})
                            </Typography>
                        </div>
                    ))}
                </div>
            ) : null}
            {embedLevel >= 2 ? (
                <div style={styles.subsection}>
                    <Typography style={styles.subsectionHeader}>
                        Map Style
                    </Typography>
                    <Typography>Choose the style for the base map</Typography>
                    <FormControl style={styles.radios}>
                        <FormControlLabel
                            value="default"
                            label="Default"
                            style={styles.radioItem}
                            control={
                                <Radio
                                    checked={mapStyle === 'default'}
                                    onChange={e => setMapStyle(e.target.value)}
                                    value="default"
                                    name="theme-color"
                                    inputProps={{ 'aria-label': 'Default' }}
                                    style={styles.radio}
                                />
                            }
                        />
                        <FormControlLabel
                            value="silver"
                            label="Silver"
                            style={styles.radioItem}
                            control={
                                <Radio
                                    checked={mapStyle === 'silver'}
                                    onChange={e => setMapStyle(e.target.value)}
                                    value="silver"
                                    name="theme-color"
                                    inputProps={{
                                        'aria-label': 'Silver',
                                    }}
                                    style={styles.radio}
                                />
                            }
                        />
                    </FormControl>
                </div>
            ) : null}
        </div>
    );
}

EmbeddedMapThemeConfig.propTypes = {
    color: string.isRequired,
    setColor: func.isRequired,
    font: string.isRequired,
    setFont: func.isRequired,
    accentColor: string,
    setAccentColor: func,
    headingFont: string,
    setHeadingFont: func,
    cornerRadius: oneOfType([number, string]),
    setCornerRadius: func,
    fields: arrayOf(object),
    colorByField: string,
    setColorBy: func,
    colorByColors: object,
    colorByOptions: arrayOf(object),
    markerColor: string,
    setMarkerColor: func,
};

EmbeddedMapThemeConfig.defaultProps = {
    accentColor: '',
    setAccentColor: () => {},
    headingFont: '',
    setHeadingFont: () => {},
    cornerRadius: '',
    setCornerRadius: () => {},
    fields: [],
    colorByField: '',
    setColorBy: () => {},
    colorByColors: {},
    colorByOptions: [],
    markerColor: '',
    setMarkerColor: () => {},
};

export default EmbeddedMapThemeConfig;
