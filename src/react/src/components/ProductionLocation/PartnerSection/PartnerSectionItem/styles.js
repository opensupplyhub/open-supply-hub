import { getTypographyStyles } from '../../../../util/typographyStyles';
import COLOURS from '../../../../util/COLOURS';
import commonStyles from '../../commonStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            border: `1px solid ${COLOURS.ACCENT_GREY}`,
            borderRadius: 0,
            marginBottom: spacing * 2,
            overflow: 'hidden',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `${spacing * 2}px ${spacing * 3}px`,
            cursor: 'pointer',
            '&:focus': {
                outline: 'none',
            },
        }),
        headerOpen: Object.freeze({
            borderBottom: `1px solid ${COLOURS.ACCENT_GREY}`,
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing}px`,
        }),
        headerRight: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing * 0.5}px`,
        }),
        iconImage: Object.freeze({
            flexShrink: 0,
        }),
        title: Object.freeze({
            ...typography.sectionTitle,
            fontSize: '1.125rem',
            marginTop: 0,
            marginBottom: 0,
        }),
        infoIcon: Object.freeze({
            fontSize: '1.25rem',
            color: theme.palette.text.secondary,
            cursor: 'pointer',
        }),
        toggleLabel: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.875rem',
        }),
        switchWrapper: Object.freeze({
            zIndex: 1,
        }),
        contentArea: Object.freeze({
            padding: `0 ${spacing * 3}px ${spacing * 3}px`,
        }),
        disclaimer: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREY,
            borderRadius: '0',
            padding: `${spacing * 2}px`,
            marginTop: spacing * 3,
        }),
        disclaimerText: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.875rem',
            color: COLOURS.JET_BLACK,
            '& p': {
                margin: 0,
                display: 'inline',
            },
        }),
        fieldItem: Object.freeze({
            '&:not(:first-child)': {
                marginTop: spacing * 2,
            },
        }),
        contributorLink: Object.freeze({
            textDecoration: 'none',
            color: theme.palette.primary.main,
        }),
    });
};
