import { getTypographyStyles } from '../../../../util/typographyStyles';
import COLOURS from '../../../../util/COLOURS';
import commonStyles from '../../commonStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            padding: '20px',
        }),
        titleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
        }),
        titleIcon: Object.freeze({
            flexShrink: 0,
            fontSize: 20,
            color: COLOURS.DARK_GREEN,
            marginRight: spacing * 1.5,
        }),
        sectionTitle: Object.freeze({
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
        }),
        infoButton: Object.freeze({
            marginLeft: spacing * 0.5,
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        switchWrap: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            marginLeft: 'auto',
        }),
        switchLabel: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.875rem',
        }),
        switch: Object.freeze({}),
        dataPointsList: Object.freeze({
            borderTop: `1px solid ${theme.palette.divider}`,
            marginTop: spacing * 2.5,
            marginLeft: -(spacing * 2.5),
            marginRight: -(spacing * 2.5),
            paddingTop: spacing * 2.5,
            paddingLeft: spacing * 2.5 + 16,
            paddingRight: spacing * 2.5,
        }),
    });
};
