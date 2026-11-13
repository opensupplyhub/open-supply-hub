import COLOURS from '../../util/COLOURS';
import { primaryButtonStyles } from '../InitialClaimFlow/ClaimForm/styles';

const CONFETTI_FALL = 'claim-live-check-confetti-fall';

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

const RING_SPIN = 'claim-live-check-ring-spin';
const TICK_POP = 'claim-live-check-tick-pop';
const DOT_SIZE = 20;
const REDUCED_MOTION = '@media (prefers-reduced-motion: reduce)';

const dot = Object.freeze({
    boxSizing: 'border-box',
    width: `${DOT_SIZE}px`,
    height: `${DOT_SIZE}px`,
    borderRadius: '50%',
    border: `2px solid ${COLOURS.GREY}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '13px',
    lineHeight: 1,
    fontWeight: 800,
});

const dotNow = Object.freeze({
    ...dot,
    borderColor: COLOURS.PURPLE,
    borderTopColor: 'transparent',
});

const barFill = Object.freeze({
    height: '100%',
    backgroundColor: COLOURS.PURPLE,
});

const step = Object.freeze({
    display: 'grid',
    gridTemplateColumns: `${DOT_SIZE + 4}px minmax(0, 1fr)`,
    gap: '10px',
    alignItems: 'center',
    fontSize: '18px',
    color: COLOURS.DARK_GREY,
});

export const waitingStyles = theme =>
    Object.freeze({
        [`@keyframes ${RING_SPIN}`]: Object.freeze({
            to: Object.freeze({ transform: 'rotate(360deg)' }),
        }),
        [`@keyframes ${TICK_POP}`]: Object.freeze({
            from: Object.freeze({ transform: 'scale(0.6)' }),
            to: Object.freeze({ transform: 'scale(1)' }),
        }),
        panel: Object.freeze({
            ...panel,
            borderColor: COLOURS.PURPLE,
            backgroundColor: COLOURS.WHITE,
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
        bar: Object.freeze({
            boxSizing: 'border-box',
            height: '12px',
            backgroundColor: COLOURS.PURPLE_TINT,
            border: `1px solid ${COLOURS.PURPLE}`,
        }),
        barFill: Object.freeze({
            ...barFill,
            transition: 'width 0.25s linear',
            [REDUCED_MOTION]: Object.freeze({ transition: 'none' }),
        }),
        barFillStill: barFill,
        steps: Object.freeze({
            listStyle: 'none',
            margin: 0,
            padding: 0,
            display: 'grid',
            gap: '8px',
        }),
        step,
        stepActive: Object.freeze({
            ...step,
            color: COLOURS.JET_BLACK,
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        dot,
        dotNow: Object.freeze({
            ...dotNow,
            animation: `${RING_SPIN} 0.8s linear infinite`,
            [REDUCED_MOTION]: Object.freeze({ animation: 'none' }),
        }),
        dotNowStill: dotNow,
        dotDone: Object.freeze({
            ...dot,
            backgroundColor: COLOURS.MATERIAL_GREEN,
            borderColor: COLOURS.MATERIAL_GREEN,
            color: COLOURS.WHITE,
            animation: `${TICK_POP} 0.3s ease-out`,
            [REDUCED_MOTION]: Object.freeze({ animation: 'none' }),
        }),
        fact: Object.freeze({
            backgroundColor: COLOURS.PURPLE_TINT,
            padding: '12px 14px',
            display: 'grid',
            gap: '2px',
            minHeight: '76px',
            alignContent: 'center',
            fontSize: '18px',
            overflowWrap: 'anywhere',
        }),
        factLabel: Object.freeze({
            fontSize: '13px',
            fontWeight: 800,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            color: COLOURS.PURPLE,
        }),
        visuallyHidden: Object.freeze({
            position: 'absolute',
            width: '1px',
            height: '1px',
            margin: '-1px',
            padding: 0,
            overflow: 'hidden',
            clip: 'rect(0, 0, 0, 0)',
            whiteSpace: 'nowrap',
            border: 0,
        }),
    });
