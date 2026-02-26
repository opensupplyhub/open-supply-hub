/**
 * Shared typography style definitions for consistent headings, labels, body text,
 * and inline spans across the app. Use with MUI Typography (variant + component + className).
 *
 * Semantics:
 * - h1: Page title (e.g. facility name)
 * - h2: Major section (e.g. claim intro boxes)
 * - h3: Section title (e.g. "Production Location Contact Person", "Partner Data")
 * - formLabel / formLabelTight: Field labels (e.g. "Your Email", "CLAIMED PROFILE")
 * - sectionDescription / body: Regular paragraphs
 * - inlineHighlight: Emphasized inline span (e.g. contributor name, date)
 *
 * @param {object} theme - MUI theme
 * @returns {object} Style objects to merge into withStyles or use as className
 */
export const getTypographyStyles = theme => {
    const formLabelBase = Object.freeze({
        fontSize: '21px',
        fontWeight: 600,
    });
    return Object.freeze({
        formLabel: Object.freeze({
            ...formLabelBase,
            margin: '24px 0 8px 0',
        }),
        formLabelRoot: Object.freeze({
            ...formLabelBase,
            marginTop: 0,
            marginBottom: '8px',
        }),
        formLabelTight: Object.freeze({
            ...formLabelBase,
        }),
        sectionTitle: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginTop: '25px',
        }),
        sectionDescription: Object.freeze({
            fontSize: '18px',
            marginBottom: '10px',
        }),
        bodyText: Object.freeze({
            fontSize: '18px',
            color: theme.palette.text.secondary,
        }),
        inlineHighlight: Object.freeze({
            fontWeight: 500,
            color: theme.palette.text.primary,
            display: 'inline',
        }),
    });
};

export default getTypographyStyles;
