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
            borderBottom: `1px solid ${theme.palette.divider}`,
            paddingBottom: theme.spacing.unit * 1.5,
            marginBottom: theme.spacing.unit * 2,
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
            paddingLeft: '16px',
        }),
        divider: Object.freeze({
            backgroundColor: theme.palette.divider,
        }),
    });
};
