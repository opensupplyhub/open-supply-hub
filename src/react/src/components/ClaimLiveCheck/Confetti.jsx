import React, { useEffect, useMemo, useState } from 'react';
import { object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import COLOURS from '../../util/COLOURS';
import { confettiStyles } from './styles';

const PIECE_COUNT = 60;
const SHOW_FOR_MS = 4200;
const PIECE_COLOURS = Object.freeze([
    COLOURS.AMBER,
    COLOURS.PURPLE,
    COLOURS.MATERIAL_GREEN,
    COLOURS.JET_BLACK,
    COLOURS.RED,
]);

// A short burst of falling paper for an approved claim. Decoration
// only: the styles hide it from people who ask for reduced motion.
const Confetti = ({ classes }) => {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        if (!visible) {
            return undefined;
        }
        const timer = setTimeout(() => setVisible(false), SHOW_FOR_MS);
        return () => clearTimeout(timer);
    }, [visible]);

    const pieces = useMemo(
        () =>
            Array.from({ length: PIECE_COUNT }, (piece, index) => ({
                key: index,
                style: {
                    left: `${Math.random() * 100}%`,
                    backgroundColor:
                        PIECE_COLOURS[index % PIECE_COLOURS.length],
                    animationDuration: `${1.6 + Math.random() * 1.8}s`,
                    animationDelay: `${Math.random() * 0.5}s`,
                },
            })),
        [],
    );

    if (!visible) {
        return null;
    }

    return (
        <div
            className={classes.confetti}
            aria-hidden="true"
            data-testid="claim-live-check-confetti"
        >
            {pieces.map(piece => (
                <i
                    key={piece.key}
                    className={classes.piece}
                    style={piece.style}
                />
            ))}
        </div>
    );
};

Confetti.propTypes = {
    classes: object.isRequired,
};

export default withStyles(confettiStyles)(Confetti);
