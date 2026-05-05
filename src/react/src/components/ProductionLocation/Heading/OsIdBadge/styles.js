import COLOURS from '../../../../util/COLOURS';
import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        osIdRow: {
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: `${spacing}px ${spacing * 2}px`,
            padding: '12px 20px',
            border: `1px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
            backgroundColor: 'rgba(128, 64, 191, 0.05)',
            marginBottom: theme.spacing.unit * 2,
            [theme.breakpoints.down(450)]: {
                padding: '12px 14px',
            },
        },
        osIdValueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
        }),
        osIdLabel: Object.freeze({
            fontWeight: 'bold',
            ...typography.formLabelTight,
        }),
        osIdValue: {
            fontWeight: 'bold',
            fontSize: '1.75rem',
            [theme.breakpoints.down(450)]: {
                fontSize: '1.25rem',
                wordBreak: 'break-all',
            },
        },
        osIdInfoButton: Object.freeze({
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        osIdActions: {
            display: 'inline-flex',
            flexWrap: 'wrap',
            marginLeft: 'auto',
            [theme.breakpoints.down(450)]: {
                marginLeft: 0,
                width: '100%',
                justifyContent: 'center',
                gap: spacing,
                marginTop: spacing,
            },
        },
        copyButtonWrap: {
            backgroundColor: COLOURS.WHITE,
            display: 'inline-flex',
            marginLeft: spacing * 2,
            [theme.breakpoints.down(450)]: {
                marginLeft: 0,
                flex: 1,
            },
        },
        copyButtonWrapFirst: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            marginLeft: 0,
        }),
        copyButton: {
            textTransform: 'none',
            minWidth: 'auto',
            [theme.breakpoints.down(450)]: {
                flex: 1,
                width: '100%',
                borderRight: '0px',
            },
        },
        buttonText: Object.freeze({
            marginLeft: spacing * 0.5,
            fontSize: '14px',
        }),
    });
};
