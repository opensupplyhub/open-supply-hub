import COLOURS from '../../util/COLOURS';
import { primaryButtonStyles } from '../InitialClaimFlow/ClaimForm/styles';

const CONFETTI_FALL = 'claim-live-check-confetti-fall';
const SPINNER_SIZE = 20;

const panel = Object.freeze({
    border: `2px solid ${COLOURS.GREY}`,
    padding: '24px',
    display: 'grid',
    gap: '12px',
    textAlign: 'left',
});

export const claimLiveCheckStyles = theme =>
    Object.freeze({
        panel,
        panelPassed: Object.freeze({
            ...panel,
            borderColor: COLOURS.MATERIAL_GREEN,
            backgroundColor: COLOURS.LIGHT_GREEN,
        }),
        panelNotPassed: Object.freeze({
            ...panel,
            borderColor: theme.palette.action.dark,
            backgroundColor: COLOURS.LIGHT_AMBER,
        }),
        panelUnavailable: Object.freeze({
            ...panel,
            backgroundColor: theme.palette.background.grey,
        }),
        title: Object.freeze({
            fontSize: '28px',
            lineHeight: 1.1,
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        text: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        label: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        progress: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        spinner: Object.freeze({
            flex: `0 0 ${SPINNER_SIZE}px`,
            color: COLOURS.JET_BLACK,
        }),
        fixes: Object.freeze({
            margin: 0,
            paddingLeft: '24px',
            display: 'grid',
            gap: '6px',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        choices: Object.freeze({
            display: 'grid',
            gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
            gap: '16px',
            [theme.breakpoints.down('sm')]: {
                gridTemplateColumns: 'minmax(0, 1fr)',
            },
        }),
        choice: Object.freeze({
            display: 'grid',
            gap: '8px',
            alignContent: 'start',
            fontSize: '16px',
        }),
        actions: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: '16px',
            marginTop: '8px',
        }),
        primaryButton: Object.freeze({
            ...primaryButtonStyles(theme),
            width: 'auto',
            minWidth: '200px',
        }),
        secondaryButton: Object.freeze({
            minWidth: '200px',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            border: `1px solid ${COLOURS.JET_BLACK}`,
            backgroundColor: COLOURS.WHITE,
            boxShadow: 'none',
            [theme.breakpoints.down('sm')]: {
                width: '100%',
            },
        }),
    });

export const confettiStyles = Object.freeze({
    [`@keyframes ${CONFETTI_FALL}`]: Object.freeze({
        to: Object.freeze({
            transform: 'translateY(110vh) rotate(720deg)',
        }),
    }),
    confetti: Object.freeze({
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        left: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
        zIndex: 1300,
        '@media (prefers-reduced-motion: reduce)': Object.freeze({
            display: 'none',
        }),
    }),
    piece: Object.freeze({
        position: 'absolute',
        top: '-20px',
        width: '10px',
        height: '16px',
        animationName: CONFETTI_FALL,
        animationTimingFunction: 'linear',
        animationFillMode: 'forwards',
    }),
});

export const SPINNER_SIZE_PX = SPINNER_SIZE;
