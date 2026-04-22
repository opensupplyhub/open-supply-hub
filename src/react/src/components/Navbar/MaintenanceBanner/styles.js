import COLOURS from '../../../util/COLOURS';
import getTypographyStyles from '../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    return {
        banner: {
            width: '100%',
            boxSizing: 'border-box',
            backgroundColor: COLOURS.NAVIGATION,
            textAlign: 'center',
            padding: '12px 16px',
            [theme.breakpoints.down('sm')]: {
                padding: '8px 12px',
            },
        },
        headline: {
            ...typography.formLabelTight,
            color: COLOURS.PURPLE,
            marginBottom: '15px',
            [theme.breakpoints.down('sm')]: {
                fontSize: typography.bodyText.fontSize,
                marginBottom: 0,
            },
        },
        body: {
            ...typography.sectionDescription,
            color: COLOURS.JET_BLACK,
            fontWeight: theme.typography.fontWeightBold,
            marginBottom: 0,
        },
    };
};
