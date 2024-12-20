import React from 'react';
import SvgIcon from '@material-ui/core/SvgIcon';

export default function RectangleCardFigure() {
    return (
        <SvgIcon viewBox="0 0 75 75" style={{ width: 75, height: 75 }}>
            <g clipPath="url(#clip0_1799_23237)">
                <path d="M0 0H75V75L0 0Z" fill="#FFA6D0" />
                <path d="M0 37.5H37.5V75L0 37.5Z" fill="#FFA6D0" />
            </g>
            <defs>
                <clipPath id="clip0_1799_23237">
                    <rect
                        width="75"
                        height="75"
                        fill="white"
                        transform="matrix(1 0 0 -1 0 75)"
                    />
                </clipPath>
            </defs>
        </SvgIcon>
    );
}
