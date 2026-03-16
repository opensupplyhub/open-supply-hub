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
        titleIcon: Object.freeze({
            flexShrink: 0,
            fontSize: 20,
            color: COLOURS.DARK_GREEN,
        }),
        title: Object.freeze({
            ...typography.sectionTitle,
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
        dataPointsList: Object.freeze({
            padding: '20px',
        }),
    });
};
